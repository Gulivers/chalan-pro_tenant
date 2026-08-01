"""
DeterministicRouter — TEMPORARY development baseline (Increment C).

NOT the final Assistant routing experience. Maps a small set of acceptance
prompts (and close variants) to Level-1 spend tools via regex. Will be
replaced by a proper router / LLM planner later. Do not expand into a
general NLU system.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any


# Word numbers used in acceptance-case variants (six/6, three/3, five/5).
_WORD_NUMBERS = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
}

_VENDOR_SUPPLIER = r'(?:vendors?|suppliers?)'
_MONEY = r'\$?\s*([\d,]+(?:\.\d{1,2})?)'

UNSUPPORTED_CLARIFICATION = (
    'This query is not supported yet. Please rephrase using one of these patterns:\n'
    '1. Show me <vendor> transactions over $<amount> this month.\n'
    '2. How much did we spend with <vendor> this month?\n'
    '3. Show purchases by vendor this month.\n'
    '4. Compare purchases by supplier for the last six months.\n'
    '5. Show the five vendors with the highest spending.\n'
    '6. Graph spending for the last three months.'
)


@dataclass
class RouteResult:
    tool_name: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    matched_case: int | None = None
    clarification: str | None = None


def route(message: str) -> RouteResult:
    """
    Map a natural-language message to a tool + params, or clarification.

    Rule order is most-specific first:
      1 list (min_amount) → 2 sum → 6 timeseries → 4 compare → 5 top → 3 by-vendor
    """
    text = (message or '').strip()
    if not text:
        return RouteResult(clarification=UNSUPPORTED_CLARIFICATION)

    normalized = ' '.join(text.lower().split())

    # Case 1 — list_purchase_transactions (before sum: both mention vendor + month)
    # "Show me Harbor Freight transactions over $1,500 this month."
    m = re.search(
        r'(?:show\s+(?:me\s+)?)?'
        r'(.+?)\s+transactions?\s+over\s+' + _MONEY + r'\s+this\s+month',
        normalized,
    )
    if m:
        vendor = _clean_vendor(m.group(1))
        amount = _parse_money(m.group(2))
        if vendor and amount is not None:
            return RouteResult(
                tool_name='list_purchase_transactions',
                params={
                    'vendor': vendor,
                    'min_amount': str(amount),
                    'period': 'this_month',
                },
                matched_case=1,
            )

    # Case 2 — sum_purchase_spending
    # "How much did we spend with Harbor Freight this month?"
    m = re.search(
        r'how\s+much\s+(?:did\s+we\s+|have\s+we\s+)?'
        r'spend(?:ing)?\s+(?:with|at)\s+(.+?)\s+this\s+month',
        normalized,
    )
    if m:
        vendor = _clean_vendor(m.group(1))
        if vendor:
            return RouteResult(
                tool_name='sum_purchase_spending',
                params={'vendor': vendor, 'period': 'this_month'},
                matched_case=2,
            )

    # Case 6 — spending_timeseries (before compare: both use "last N months")
    # "Graph spending for the last three months."
    m = re.search(
        r'(?:graph|chart|plot)\s+spending\s+(?:for\s+)?(?:the\s+)?last\s+'
        r'(\d+|' + _word_alt() + r')\s+months?',
        normalized,
    )
    if m:
        months = _parse_int_word(m.group(1))
        if months is not None:
            return RouteResult(
                tool_name='spending_timeseries',
                params={'months': months},
                matched_case=6,
            )

    # Case 4 — compare_purchases_by_vendor
    # "Compare purchases by supplier for the last six months."
    m = re.search(
        r'compare\s+purchases\s+by\s+' + _VENDOR_SUPPLIER + r'\s+'
        r'(?:for\s+)?(?:the\s+)?last\s+'
        r'(\d+|' + _word_alt() + r')\s+months?',
        normalized,
    )
    if m:
        months = _parse_int_word(m.group(1))
        if months is not None:
            return RouteResult(
                tool_name='compare_purchases_by_vendor',
                params={'months': months},
                matched_case=4,
            )

    # Case 5 — top_vendors_by_spending
    # "Show the five vendors with the highest spending."
    # Decision: highest spending without an explicit period → last 12 months
    # (recent historical), not only this_month. Documented product choice.
    m = re.search(
        r'(?:show\s+(?:me\s+|the\s+)?)?'
        r'(\d+|' + _word_alt() + r')\s+'
        + _VENDOR_SUPPLIER
        + r'\s+with\s+(?:the\s+)?highest\s+spending',
        normalized,
    )
    if m:
        limit = _parse_int_word(m.group(1))
        if limit is not None:
            months = _extract_last_n_months(normalized)
            params: dict[str, Any] = {'limit': limit}
            if months is not None:
                params['months'] = months
            else:
                # Default for "highest spending" without period: last 12 months.
                params['months'] = 12
            return RouteResult(
                tool_name='top_vendors_by_spending',
                params=params,
                matched_case=5,
            )

    # Case 3 — purchases_by_vendor
    # "Show purchases by vendor this month."
    if re.search(
        r'(?:show\s+(?:me\s+)?)?purchases\s+by\s+' + _VENDOR_SUPPLIER + r'\s+this\s+month',
        normalized,
    ):
        return RouteResult(
            tool_name='purchases_by_vendor',
            params={'period': 'this_month'},
            matched_case=3,
        )

    return RouteResult(clarification=UNSUPPORTED_CLARIFICATION)


def _word_alt() -> str:
    return '|'.join(sorted(_WORD_NUMBERS.keys(), key=len, reverse=True))


def _parse_int_word(token: str) -> int | None:
    token = (token or '').strip().lower()
    if token.isdigit():
        value = int(token)
        return value if value >= 1 else None
    return _WORD_NUMBERS.get(token)


def _parse_money(raw: str) -> Decimal | None:
    cleaned = (raw or '').replace(',', '').replace(' ', '').strip()
    if not cleaned:
        return None
    try:
        amount = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None
    if amount < 0:
        return None
    return amount.quantize(Decimal('0.01'))


def _clean_vendor(raw: str) -> str | None:
    """Normalize captured vendor phrase; preserve original casing via title-ish strip."""
    if not raw:
        return None
    # Caller passes lowercased text; restore reasonable display from capture.
    vendor = raw.strip(' .,;:!?\'"')
    # Drop leading filler words that regex may include.
    vendor = re.sub(
        r'^(?:me\s+|the\s+|our\s+|a\s+|an\s+)',
        '',
        vendor,
        flags=re.IGNORECASE,
    ).strip()
    if not vendor or vendor in ('vendor', 'vendors', 'supplier', 'suppliers'):
        return None
    # Input is lowercased; title-case for display. Vendor resolve is case-insensitive.
    return ' '.join(part.capitalize() for part in vendor.split())


def _extract_last_n_months(normalized: str) -> int | None:
    m = re.search(
        r'(?:for\s+|over\s+|in\s+)?(?:the\s+)?last\s+'
        r'(\d+|' + _word_alt() + r')\s+months?',
        normalized,
    )
    if not m:
        return None
    return _parse_int_word(m.group(1))
