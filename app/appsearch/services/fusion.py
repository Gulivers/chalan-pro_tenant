from django.conf import settings


def _fusion_settings() -> dict:
    mode = getattr(settings, 'SEARCH_FUSION_MODE', 'weighted').lower()
    return {
        'mode': mode if mode in ('weighted', 'rrf') else 'weighted',
        'vector_weight': float(getattr(settings, 'SEARCH_FUSION_VECTOR_WEIGHT', 0.6)),
        'fts_weight': float(getattr(settings, 'SEARCH_FUSION_FTS_WEIGHT', 0.4)),
        'rrf_k': int(getattr(settings, 'SEARCH_FUSION_RRF_K', 60)),
    }


def _weighted_score(*, vector_distance: float | None, fts_rank: float | None, cfg: dict) -> float:
    distance = vector_distance if vector_distance is not None else 1.0
    fts = fts_rank if fts_rank is not None else 0.0
    vector_score = max(0.0, 1.0 - distance)
    fts_score = min(max(fts, 0.0), 1.0)
    return max(
        0.0,
        vector_score * cfg['vector_weight'] + fts_score * cfg['fts_weight'],
    )


def fuse_hybrid_candidates(
    vector_hits: list[dict],
    fts_hits: list[dict],
) -> list[dict]:
    """
    Merge vector (cosine distance) and FTS ranked lists.

    Each hit dict must include:
      - key: stable id (SearchIndex pk)
      - item: SearchIndex instance
      - vector_distance (optional)
      - fts_rank (optional)
    """
    cfg = _fusion_settings()

    if cfg['mode'] == 'rrf':
        return _fuse_rrf(vector_hits, fts_hits, cfg)

    merged: dict[int, dict] = {}

    for hit in vector_hits + fts_hits:
        key = hit['key']
        current = merged.get(key)
        if current is None:
            merged[key] = {
                'item': hit['item'],
                'vector_distance': hit.get('vector_distance'),
                'fts_rank': hit.get('fts_rank'),
            }
            continue
        if hit.get('vector_distance') is not None:
            current['vector_distance'] = hit['vector_distance']
        if hit.get('fts_rank') is not None:
            current['fts_rank'] = hit['fts_rank']

    fused_rows = []
    for payload in merged.values():
        score = _weighted_score(
            vector_distance=payload.get('vector_distance'),
            fts_rank=payload.get('fts_rank'),
            cfg=cfg,
        )
        fused_rows.append({
            'item': payload['item'],
            'score': round(score, 4),
            'vector_distance': payload.get('vector_distance'),
            'fts_rank': payload.get('fts_rank'),
        })

    fused_rows.sort(key=lambda row: row['score'], reverse=True)
    return fused_rows


def _fuse_rrf(vector_hits: list[dict], fts_hits: list[dict], cfg: dict) -> list[dict]:
    k = cfg['rrf_k']
    scores: dict[int, float] = {}
    payloads: dict[int, dict] = {}

    for rank, hit in enumerate(vector_hits):
        key = hit['key']
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
        payloads.setdefault(key, {'item': hit['item'], 'vector_distance': hit.get('vector_distance')})
        if hit.get('vector_distance') is not None:
            payloads[key]['vector_distance'] = hit['vector_distance']

    for rank, hit in enumerate(fts_hits):
        key = hit['key']
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
        payload = payloads.setdefault(key, {'item': hit['item']})
        if hit.get('fts_rank') is not None:
            payload['fts_rank'] = hit['fts_rank']

    fused_rows = []
    for key, score in scores.items():
        payload = payloads[key]
        fused_rows.append({
            'item': payload['item'],
            'score': round(score, 6),
            'vector_distance': payload.get('vector_distance'),
            'fts_rank': payload.get('fts_rank'),
        })

    fused_rows.sort(key=lambda row: row['score'], reverse=True)
    return fused_rows
