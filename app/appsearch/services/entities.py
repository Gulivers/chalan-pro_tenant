import re
from difflib import SequenceMatcher

from apptransactions.models import DocumentType, WorkAccount
from appsearch.models import BuilderAlias
from ctrctsapp.models import Builder

MIN_ENTITY_SCORE = 30
TOKEN_FUZZY_RATIO = 0.72
STRING_FUZZY_RATIO = 0.82

# Tokens for ad-hoc / custom transaction type names (e.g. "Missing Material").
EXTRA_TRANSACTION_VOCAB = frozenset({
    'missing', 'shortage', 'loss', 'adjustment', 'transfer', 'stock', 'material',
})

# Parsed by intent.py — not standalone document type names.
INTENT_ONLY_TOKENS = frozenset({
    'purchase', 'purchases', 'compra', 'compras',
    'sale', 'sales', 'venta', 'ventas',
})


def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '').strip())


def _token_fuzzy_match(left: str, right: str) -> bool:
    if not left or not right:
        return False
    if left == right:
        return True
    min_len = min(len(left), len(right))
    if min_len >= 4 and (left in right or right in left):
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


def _score_document_type(query_lower: str, doc_type: DocumentType) -> int:
    type_code = (doc_type.type_code or '').strip()
    if not type_code:
        return 0

    code_lower = type_code.lower()
    if re.search(rf'\b{re.escape(code_lower)}\b', query_lower):
        return len(code_lower) + 200

    description = (doc_type.description or '').strip()
    if description:
        desc_lower = description.lower()
        if desc_lower in query_lower:
            return len(desc_lower) + 180
        if query_lower in desc_lower:
            return len(query_lower) + 120

        query_tokens = [token for token in query_lower.split() if token]
        desc_tokens = [token for token in desc_lower.split() if token]
        if query_tokens and desc_tokens:
            matched_query_tokens = sum(
                1
                for query_token in query_tokens
                if any(_token_fuzzy_match(query_token, desc_token) for desc_token in desc_tokens)
            )
            if matched_query_tokens == len(query_tokens):
                bonus = 20 if matched_query_tokens == len(desc_tokens) else 0
                return matched_query_tokens * 35 + len(desc_lower) + bonus

    if len(code_lower) >= 4:
        code_fuzzy_score = _score_match(query_lower, code_lower)
        if code_fuzzy_score >= MIN_ENTITY_SCORE:
            return code_fuzzy_score

    return 0


def _pick_document_type(query_lower: str, doc_types) -> tuple[DocumentType | None, int]:
    scored: list[tuple[int, DocumentType]] = []
    for doc_type in doc_types:
        score = _score_document_type(query_lower, doc_type)
        if score >= MIN_ENTITY_SCORE:
            scored.append((score, doc_type))

    if not scored:
        return None, 0

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score = scored[0][0]
    best = [doc_type for score, doc_type in scored if score == best_score]
    if len(best) != 1:
        return None, 0
    return best[0], best_score


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


def _strip_document_type_mention(remaining: str, doc_type: DocumentType, query_lower: str) -> str:
    text = remaining
    if doc_type.type_code:
        text = re.sub(
            rf'\b{re.escape(doc_type.type_code)}\b',
            ' ',
            text,
            flags=re.IGNORECASE,
        )
    if doc_type.description:
        text = _strip_entity_mention(text, doc_type.description, query_lower)
    return _normalize(text)


def _tokenize_vocab(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z']+", (text or '').lower()) if token]


def _transaction_vocabulary() -> frozenset[str]:
    tokens = set(EXTRA_TRANSACTION_VOCAB)
    for doc_type in DocumentType.objects.filter(is_active=True):
        for part in (doc_type.type_code or '', doc_type.description or ''):
            tokens.update(_tokenize_vocab(part))
    return frozenset(tokens)


def looks_like_unresolved_document_type(
    query: str,
    *,
    document_type_resolved: bool,
    has_purchase_sales_intent: bool = False,
) -> bool:
    """
    True when the query reads like a transaction type label but no DocumentType matched.

    Example: "missing material" with no such type → avoid semantic fallback on "material".
    Counter-example: "construction material" → product/category search, not a type name.
    """
    if document_type_resolved:
        return False

    text = _normalize(query)
    if not text:
        return False

    tokens = _tokenize_vocab(text)
    if not tokens or len(tokens) > 6:
        return False

    if all(token in INTENT_ONLY_TOKENS for token in tokens):
        return False
    if has_purchase_sales_intent and not (query or '').strip():
        return False

    vocab = _transaction_vocabulary()
    return all(token in vocab for token in tokens)


def resolve_entities(query: str) -> tuple[dict, str]:
    """
    Resolve DocumentType, WorkAccount and Builder mentions in the query.
    Returns resolved entity metadata and the query with matched phrases removed.
    """
    resolved: dict = {}
    remaining = _normalize(query)

    query_lower = remaining.lower()
    document_type, best_doc_type_score = _pick_document_type(
        query_lower,
        DocumentType.objects.filter(is_active=True),
    )

    if document_type:
        resolved['document_type'] = {
            'id': document_type.id,
            'type_code': document_type.type_code,
            'description': document_type.description,
        }
        remaining = _strip_document_type_mention(remaining, document_type, query_lower)

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
    matched_builder_label = None
    for item in Builder.objects.filter(is_active=True):
        score = _score_match(query_lower, item.name or '')
        if score > best_builder_score:
            best_builder_score = score
            builder = item
            matched_builder_label = item.name

    for alias_row in BuilderAlias.objects.filter(is_active=True).select_related('builder'):
        builder_obj = alias_row.builder
        if not builder_obj or not builder_obj.is_active:
            continue
        score = _score_match(query_lower, alias_row.alias or '')
        if score > best_builder_score:
            best_builder_score = score
            builder = builder_obj
            matched_builder_label = alias_row.alias

    if work_account and best_wa_score >= MIN_ENTITY_SCORE:
        resolved['work_account'] = {
            'id': work_account.id,
            'title': work_account.title,
        }
        remaining = _strip_entity_mention(remaining, work_account.title, query_lower)

    query_lower = remaining.lower()
    if builder and best_builder_score >= MIN_ENTITY_SCORE:
        if not work_account or builder.id != getattr(work_account, 'builder_id', None):
            resolved['builder'] = {
                'id': builder.id,
                'name': builder.name,
                'is_supplier': builder.is_supplier(),
                'is_customer': builder.is_customer(),
            }
            if matched_builder_label and matched_builder_label.lower() != (builder.name or '').lower():
                resolved['builder']['matched_alias'] = matched_builder_label
            strip_label = matched_builder_label or builder.name
            remaining = _strip_entity_mention(remaining, strip_label, query_lower)
            if matched_builder_label and matched_builder_label.lower() != (builder.name or '').lower():
                remaining = _strip_entity_mention(remaining, builder.name, query_lower)

    remaining = _normalize(remaining)
    return resolved, remaining
