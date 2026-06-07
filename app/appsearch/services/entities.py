import re

from apptransactions.models import WorkAccount
from ctrctsapp.models import Builder


def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '').strip())


def _score_match(query_lower: str, candidate: str) -> int:
    candidate_lower = candidate.lower()
    if candidate_lower in query_lower:
        return len(candidate_lower) + 100
    if query_lower in candidate_lower:
        return len(query_lower) + 50
    return 0


def resolve_entities(query: str) -> tuple[dict, str]:
    """
    Resolve WorkAccount and Builder mentions in the query.
    WorkAccount titles take priority over builder names when both match.
    Returns resolved entity metadata and the query with matched phrases removed.
    """
    resolved: dict = {}
    remaining = _normalize(query)
    query_lower = remaining.lower()

    work_account = None
    best_wa_score = 0
    for wa in WorkAccount.objects.filter(is_active=True).select_related('builder'):
        score = _score_match(query_lower, wa.title or '')
        if score > best_wa_score:
            best_wa_score = score
            work_account = wa

    builder = None
    best_builder_score = 0
    for item in Builder.objects.filter(is_active=True):
        score = _score_match(query_lower, item.name or '')
        if score > best_builder_score:
            best_builder_score = score
            builder = item

    if work_account and best_wa_score >= 3:
        resolved['work_account'] = {
            'id': work_account.id,
            'title': work_account.title,
        }
        remaining = re.sub(re.escape(work_account.title), ' ', remaining, flags=re.IGNORECASE)

    if builder and best_builder_score >= 3:
        if not work_account or builder.id != getattr(work_account, 'builder_id', None):
            resolved['builder'] = {
                'id': builder.id,
                'name': builder.name,
                'is_supplier': builder.is_supplier(),
                'is_customer': builder.is_customer(),
            }
            remaining = re.sub(re.escape(builder.name), ' ', remaining, flags=re.IGNORECASE)

    remaining = _normalize(remaining)
    return resolved, remaining
