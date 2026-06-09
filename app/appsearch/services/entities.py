import re
from difflib import SequenceMatcher

from apptransactions.models import WorkAccount
from ctrctsapp.models import Builder

MIN_ENTITY_SCORE = 30
TOKEN_FUZZY_RATIO = 0.72
STRING_FUZZY_RATIO = 0.82


def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '').strip())


def _token_fuzzy_match(left: str, right: str) -> bool:
    if not left or not right:
        return False
    if left == right or left in right or right in left:
        return True
    return SequenceMatcher(None, left, right).ratio() >= TOKEN_FUZZY_RATIO


def _score_match(query_lower: str, candidate: str) -> int:
    candidate_lower = candidate.lower().strip()
    if not candidate_lower or not query_lower:
        return 0

    if candidate_lower in query_lower:
        return len(candidate_lower) + 100
    if query_lower in candidate_lower:
        return len(query_lower) + 50

    string_ratio = SequenceMatcher(None, candidate_lower, query_lower).ratio()
    if string_ratio >= STRING_FUZZY_RATIO:
        return int(string_ratio * 100) + 40

    candidate_tokens = candidate_lower.split()
    query_tokens = query_lower.split()
    if candidate_tokens and query_tokens:
        matched_tokens = 0
        for candidate_token in candidate_tokens:
            if any(_token_fuzzy_match(candidate_token, query_token) for query_token in query_tokens):
                matched_tokens += 1
        if matched_tokens == len(candidate_tokens):
            return matched_tokens * 30 + len(candidate_lower)

    return 0


def _strip_entity_mention(remaining: str, entity_name: str, query_lower: str) -> str:
    text = remaining
    if entity_name:
        text = re.sub(re.escape(entity_name), ' ', text, flags=re.IGNORECASE)

    entity_tokens = entity_name.lower().split()
    for entity_token in entity_tokens:
        text = re.sub(rf'\b{re.escape(entity_token)}\b', ' ', text, flags=re.IGNORECASE)

    for query_token in query_lower.split():
        if any(_token_fuzzy_match(entity_token, query_token) for entity_token in entity_tokens):
            text = re.sub(rf'\b{re.escape(query_token)}\b', ' ', text, flags=re.IGNORECASE)

    return _normalize(text)


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

    if work_account and best_wa_score >= MIN_ENTITY_SCORE:
        resolved['work_account'] = {
            'id': work_account.id,
            'title': work_account.title,
        }
        remaining = _strip_entity_mention(remaining, work_account.title, query_lower)

    if builder and best_builder_score >= MIN_ENTITY_SCORE:
        if not work_account or builder.id != getattr(work_account, 'builder_id', None):
            resolved['builder'] = {
                'id': builder.id,
                'name': builder.name,
                'is_supplier': builder.is_supplier(),
                'is_customer': builder.is_customer(),
            }
            remaining = _strip_entity_mention(remaining, builder.name, query_lower)

    remaining = _normalize(remaining)
    return resolved, remaining
