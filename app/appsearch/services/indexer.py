import logging

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db import connection, transaction
from django.utils import timezone

from appsearch.models import IndexOutbox, SearchIndex
from appsearch.services.chunk import (
    build_document_line_chunk,
    content_hash_for_text,
    get_document_line_queryset,
)
from appsearch.services.embeddings import EmbeddingServiceError, embed_texts

logger = logging.getLogger(__name__)


def assert_tenant_schema():
    schema_name = connection.schema_name
    if schema_name in ('public', None):
        raise RuntimeError(
            f'Search indexing must run inside a tenant schema, not "{schema_name}".'
        )
    return schema_name


def enqueue_index_job(source_type: str, source_id: int, action: str = IndexOutbox.ACTION_UPSERT):
    if not getattr(settings, 'SEARCH_INDEXING_ENABLED', True):
        return

    IndexOutbox.objects.create(
        source_type=source_type,
        source_id=source_id,
        action=action,
    )


def enqueue_document_line_upsert(line_id: int):
    enqueue_index_job(SearchIndex.SOURCE_DOCUMENT_LINE, line_id, IndexOutbox.ACTION_UPSERT)


def enqueue_document_line_delete(line_id: int):
    enqueue_index_job(SearchIndex.SOURCE_DOCUMENT_LINE, line_id, IndexOutbox.ACTION_DELETE)


def enqueue_document_lines_for_document(document_id: int):
    line_ids = list(
        get_document_line_queryset()
        .filter(document_id=document_id)
        .values_list('id', flat=True)
    )
    for line_id in line_ids:
        enqueue_document_line_upsert(line_id)


def enqueue_document_lines_for_builder(builder_id: int):
    line_ids = list(
        get_document_line_queryset()
        .filter(document__builder_id=builder_id)
        .values_list('id', flat=True)
    )
    for line_id in line_ids:
        enqueue_document_line_upsert(line_id)


def delete_search_index(source_type: str, source_id: int):
    SearchIndex.objects.filter(source_type=source_type, source_id=source_id).delete()


def _update_search_vector(search_index_id: int):
    SearchIndex.objects.filter(pk=search_index_id).update(
        search_vector=SearchVector('chunk_text', config='english'),
    )


def upsert_document_line_index(line, *, embed: bool = True) -> SearchIndex | None:
    chunk_text, metadata = build_document_line_chunk(line)
    if not chunk_text.strip():
        delete_search_index(SearchIndex.SOURCE_DOCUMENT_LINE, line.id)
        return None

    content_hash = content_hash_for_text(chunk_text)
    existing = SearchIndex.objects.filter(
        source_type=SearchIndex.SOURCE_DOCUMENT_LINE,
        source_id=line.id,
    ).first()

    if existing and existing.content_hash == content_hash and existing.embedding is not None:
        if existing.metadata != metadata:
            existing.metadata = metadata
            existing.save(update_fields=['metadata', 'updated_at'])
        return existing

    embedding = None
    indexed_at = None
    embedding_model = getattr(settings, 'SEARCH_EMBEDDING_MODEL', 'text-embedding-3-small')

    if embed:
        embedding = embed_texts([chunk_text])[0]
        indexed_at = timezone.now()

    search_index, _created = SearchIndex.objects.update_or_create(
        source_type=SearchIndex.SOURCE_DOCUMENT_LINE,
        source_id=line.id,
        defaults={
            'chunk_text': chunk_text,
            'metadata': metadata,
            'content_hash': content_hash,
            'embedding_model': embedding_model,
            'embedding': embedding,
            'indexed_at': indexed_at,
        },
    )
    _update_search_vector(search_index.id)
    return search_index


def process_outbox_entry(entry: IndexOutbox, *, embed: bool = True) -> None:
    assert_tenant_schema()

    if entry.action == IndexOutbox.ACTION_DELETE:
        delete_search_index(entry.source_type, entry.source_id)
        return

    if entry.source_type != SearchIndex.SOURCE_DOCUMENT_LINE:
        raise ValueError(f'Unsupported source_type for phase 1: {entry.source_type}')

    line = get_document_line_queryset().filter(pk=entry.source_id).first()
    if line is None:
        delete_search_index(entry.source_type, entry.source_id)
        return

    if not line.document.is_active:
        delete_search_index(entry.source_type, entry.source_id)
        return

    upsert_document_line_index(line, embed=embed)


def process_pending_outbox(*, limit: int = 100, embed: bool = True) -> dict:
    assert_tenant_schema()

    pending = list(
        IndexOutbox.objects.filter(processed_at__isnull=True)
        .order_by('created_at')[:limit]
    )
    stats = {'processed': 0, 'failed': 0, 'skipped_embed': 0}

    for entry in pending:
        try:
            with transaction.atomic():
                process_outbox_entry(entry, embed=embed)
                entry.processed_at = timezone.now()
                entry.last_error = ''
                entry.save(update_fields=['processed_at', 'last_error'])
                stats['processed'] += 1
        except EmbeddingServiceError as exc:
            entry.attempts += 1
            entry.last_error = str(exc)[:2000]
            entry.save(update_fields=['attempts', 'last_error'])
            stats['failed'] += 1
            logger.warning('Outbox entry %s failed (embedding): %s', entry.id, exc)
        except Exception as exc:
            entry.attempts += 1
            entry.last_error = str(exc)[:2000]
            entry.save(update_fields=['attempts', 'last_error'])
            stats['failed'] += 1
            logger.exception('Outbox entry %s failed', entry.id)

    return stats


def reindex_document_lines(
    *,
    line_ids=None,
    batch_size: int | None = None,
    embed: bool = True,
) -> dict:
    assert_tenant_schema()

    batch_size = batch_size or getattr(settings, 'SEARCH_INDEX_BATCH_SIZE', 50)
    queryset = get_document_line_queryset().filter(document__is_active=True)
    if line_ids is not None:
        queryset = queryset.filter(id__in=line_ids)

    stats = {'indexed': 0, 'deleted': 0, 'skipped': 0, 'failed': 0}
    ids = list(queryset.values_list('id', flat=True))

    for offset in range(0, len(ids), batch_size):
        batch_ids = ids[offset:offset + batch_size]
        lines = list(get_document_line_queryset().filter(id__in=batch_ids))

        if embed:
            payloads = []
            for line in lines:
                chunk_text, metadata = build_document_line_chunk(line)
                if not chunk_text.strip():
                    delete_search_index(SearchIndex.SOURCE_DOCUMENT_LINE, line.id)
                    stats['deleted'] += 1
                    continue
                payloads.append((line, chunk_text, metadata))

            if not payloads:
                continue

            try:
                embeddings = embed_texts([item[1] for item in payloads])
            except EmbeddingServiceError:
                stats['failed'] += len(payloads)
                raise

            now = timezone.now()
            embedding_model = getattr(settings, 'SEARCH_EMBEDDING_MODEL', 'text-embedding-3-small')

            with transaction.atomic():
                for (line, chunk_text, metadata), embedding in zip(payloads, embeddings):
                    content_hash = content_hash_for_text(chunk_text)
                    search_index, _ = SearchIndex.objects.update_or_create(
                        source_type=SearchIndex.SOURCE_DOCUMENT_LINE,
                        source_id=line.id,
                        defaults={
                            'chunk_text': chunk_text,
                            'metadata': metadata,
                            'content_hash': content_hash,
                            'embedding_model': embedding_model,
                            'embedding': embedding,
                            'indexed_at': now,
                        },
                    )
                    _update_search_vector(search_index.id)
                    stats['indexed'] += 1
        else:
            for line in lines:
                try:
                    result = upsert_document_line_index(line, embed=False)
                    if result is None:
                        stats['deleted'] += 1
                    else:
                        stats['indexed'] += 1
                except Exception:
                    stats['failed'] += 1
                    logger.exception('Failed to index document line %s', line.id)

    return stats
