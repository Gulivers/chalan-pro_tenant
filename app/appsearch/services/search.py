import logging

from django.contrib.postgres.search import SearchQuery, SearchRank
from pgvector.django import CosineDistance

from appsearch.models import SearchIndex
from appsearch.services.embeddings import EmbeddingServiceError, embed_texts
from appsearch.services.entities import resolve_entities
from appsearch.services.intent import parse_search_intent
from appsearch.services.indexer import assert_tenant_schema

logger = logging.getLogger(__name__)

NUMERIC_JSON_PATTERN = r"^-?[0-9]+(\.[0-9]+)?$"


def _apply_metadata_filters(queryset, filters: dict):
    queryset = queryset.filter(metadata__is_active=True)

    if filters.get('builder_id') is not None:
        queryset = queryset.filter(metadata__builder_id=filters['builder_id'])

    if filters.get('work_account_id') is not None:
        queryset = queryset.filter(metadata__work_account_id=filters['work_account_id'])

    if filters.get('document_type_id') is not None:
        queryset = queryset.filter(metadata__document_type_id=filters['document_type_id'])

    if filters.get('is_purchase') is True:
        queryset = queryset.filter(metadata__is_purchase=True)

    if filters.get('is_sales') is True:
        queryset = queryset.filter(metadata__is_sales=True)

    date_from = filters.get('date_from')
    date_to = filters.get('date_to')
    if date_from:
        queryset = queryset.filter(metadata__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(metadata__date__lte=date_to)

    line_final_price_gte = filters.get('line_final_price_gte')
    if line_final_price_gte is not None:
        queryset = queryset.extra(
            where=[
                f"(metadata->>'final_price') ~ '{NUMERIC_JSON_PATTERN}' "
                "AND (metadata->>'final_price')::numeric >= %s"
            ],
            params=[line_final_price_gte],
        )

    document_total_gte = filters.get('document_total_gte')
    if document_total_gte is not None:
        queryset = queryset.extra(
            where=[
                "(metadata->>'document_id') ~ '^[0-9]+$' AND "
                "(metadata->>'document_id')::bigint IN ("
                "SELECT id FROM apptransactions_document "
                "WHERE is_active = TRUE AND total_amount >= %s)"
            ],
            params=[document_total_gte],
        )

    return queryset


def _apply_amount_filter(filters: dict, semantic_query: str) -> dict:
    """
    Route amount intent to document total vs line price.

    Document total: party/type queries without product text (e.g. purchases over $6000).
    Line price: product/concept queries (e.g. Cable 10/3 over $100).
    """
    amount_gte = filters.pop('amount_gte', None)
    if amount_gte is None:
        return filters

    if (semantic_query or '').strip():
        filters['line_final_price_gte'] = amount_gte
    else:
        filters['document_total_gte'] = amount_gte
    return filters


def _build_snippet(chunk_text: str, max_len: int = 180) -> str:
    text = (chunk_text or '').strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + '…'


def _aggregate_by_document(rows, *, limit: int) -> list[dict]:
    best_by_document: dict[int, dict] = {}

    for row in rows:
        metadata = row.get('metadata') or {}
        document_id = metadata.get('document_id')
        if not document_id:
            continue

        current = best_by_document.get(document_id)
        if current is None or row['score'] > current['score']:
            best_by_document[document_id] = row

    ordered = sorted(best_by_document.values(), key=lambda item: item['score'], reverse=True)
    return ordered[:limit]


def search_transactions(
    query: str,
    *,
    extra_filters: dict | None = None,
    limit: int = 50,
) -> dict:
    assert_tenant_schema()

    raw_query = (query or '').strip()
    extra_filters = extra_filters or {}

    intent_filters, semantic_query = parse_search_intent(raw_query)
    resolved_entities, semantic_query = resolve_entities(semantic_query)

    merged_filters = {**intent_filters, **extra_filters}
    if resolved_entities.get('builder'):
        merged_filters['builder_id'] = resolved_entities['builder']['id']
    if resolved_entities.get('work_account'):
        merged_filters['work_account_id'] = resolved_entities['work_account']['id']
    if resolved_entities.get('document_type'):
        merged_filters['document_type_id'] = resolved_entities['document_type']['id']

    merged_filters = _apply_amount_filter(merged_filters, semantic_query)

    base_qs = SearchIndex.objects.filter(
        source_type=SearchIndex.SOURCE_DOCUMENT_LINE,
        embedding__isnull=False,
    )
    base_qs = _apply_metadata_filters(base_qs, merged_filters)

    rows: list[dict] = []

    if semantic_query:
        try:
            query_embedding = embed_texts([semantic_query])[0]
        except EmbeddingServiceError:
            logger.exception('Failed to embed search query')
            raise

        vector_qs = (
            base_qs
            .annotate(distance=CosineDistance('embedding', query_embedding))
            .annotate(
                fts_rank=SearchRank('search_vector', SearchQuery(semantic_query, config='english')),
            )
            .order_by('distance')[: limit * 4]
        )

        for item in vector_qs:
            distance = float(item.distance or 1.0)
            fts_rank = float(item.fts_rank or 0.0)
            score = max(0.0, (1.0 - distance) * 0.75 + min(fts_rank, 1.0) * 0.25)
            rows.append({
                'document_line_id': item.source_id,
                'document_id': item.metadata.get('document_id'),
                'score': round(score, 4),
                'snippet': _build_snippet(item.chunk_text),
                'metadata': item.metadata,
            })
    else:
        fallback_qs = base_qs.order_by('-indexed_at')[: limit * 4]
        for item in fallback_qs:
            rows.append({
                'document_line_id': item.source_id,
                'document_id': item.metadata.get('document_id'),
                'score': 1.0,
                'snippet': _build_snippet(item.chunk_text),
                'metadata': item.metadata,
            })

    results = _aggregate_by_document(rows, limit=limit)
    document_ids = [row['document_id'] for row in results if row.get('document_id')]

    return {
        'query': raw_query,
        'semantic_query': semantic_query,
        'applied_filters': merged_filters,
        'resolved_entities': resolved_entities,
        'results': results,
        'document_ids': document_ids,
        'count': len(results),
    }
