from pgvector.django import CosineDistance

from appsearch.models import SearchIndex
from appsearch.services.indexer import assert_tenant_schema
from appsearch.services.search import _aggregate_by_document, _build_snippet


class SimilarSearchError(Exception):
    pass


def _get_seed_index(*, document_id: int | None, document_line_id: int | None) -> SearchIndex:
    if document_line_id is not None:
        seed = SearchIndex.objects.filter(
            source_type=SearchIndex.SOURCE_DOCUMENT_LINE,
            source_id=document_line_id,
            embedding__isnull=False,
        ).first()
        if seed is None:
            raise SimilarSearchError(f'Document line {document_line_id} is not indexed for search.')
        return seed

    if document_id is None:
        raise SimilarSearchError('Provide document_id or document_line_id.')

    seeds = list(
        SearchIndex.objects.filter(
            source_type=SearchIndex.SOURCE_DOCUMENT_LINE,
            embedding__isnull=False,
            metadata__document_id=document_id,
            metadata__is_active=True,
        ).order_by('-updated_at')[:5]
    )
    if not seeds:
        raise SimilarSearchError(f'Document {document_id} has no indexed lines.')

    return seeds[0]


def find_similar_transactions(
    *,
    document_id: int | None = None,
    document_line_id: int | None = None,
    limit: int = 20,
) -> dict:
    assert_tenant_schema()

    seed = _get_seed_index(document_id=document_id, document_line_id=document_line_id)
    seed_document_id = seed.metadata.get('document_id') or document_id
    candidate_limit = max(limit * 4, 20)

    base_qs = SearchIndex.objects.filter(
        source_type=SearchIndex.SOURCE_DOCUMENT_LINE,
        embedding__isnull=False,
        metadata__is_active=True,
    )
    if seed_document_id is not None:
        base_qs = base_qs.exclude(metadata__document_id=seed_document_id)

    similar_qs = (
        base_qs
        .annotate(distance=CosineDistance('embedding', seed.embedding))
        .order_by('distance')[:candidate_limit]
    )

    rows = []
    for item in similar_qs:
        distance = float(item.distance or 1.0)
        score = max(0.0, 1.0 - distance)
        rows.append({
            'document_line_id': item.source_id,
            'document_id': item.metadata.get('document_id'),
            'score': round(score, 4),
            'snippet': _build_snippet(item.chunk_text),
            'metadata': item.metadata,
        })

    results = _aggregate_by_document(rows, limit=limit)
    document_ids = [row['document_id'] for row in results if row.get('document_id')]

    return {
        'seed': {
            'document_id': seed_document_id,
            'document_line_id': seed.source_id,
            'snippet': _build_snippet(seed.chunk_text),
        },
        'results': results,
        'document_ids': document_ids,
        'count': len(results),
    }
