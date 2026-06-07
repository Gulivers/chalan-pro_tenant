import re
from calendar import monthrange
from datetime import date, datetime

from django.utils import timezone

MONTH_NAMES = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12,
}

AMOUNT_PATTERN = re.compile(
    r'(?:(?:over|above|greater\s+than|more\s+than|>=?)\s*)'
    r'(?:\$|\u0024)?\s*([\d,]+(?:\.\d{1,2})?)',
    re.IGNORECASE,
)

THIS_MONTH_PATTERN = re.compile(r'\bthis\s+month\b', re.IGNORECASE)
MONTH_PATTERN = re.compile(
    r'\b(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|'
    r'august|aug|september|sep|sept|october|oct|november|nov|december|dec)'
    r'(?:\s+(20\d{2}))?\b',
    re.IGNORECASE,
)
PURCHASE_PATTERN = re.compile(r'\b(purchases?|compras?)\b', re.IGNORECASE)
SALES_PATTERN = re.compile(r'\b(sales?|ventas?)\b', re.IGNORECASE)


def _parse_amount(value: str) -> float | None:
    try:
        return float(value.replace(',', ''))
    except (TypeError, ValueError):
        return None


def _month_date_range(month: int, year: int) -> tuple[str, str]:
    last_day = monthrange(year, month)[1]
    start = date(year, month, 1)
    end = date(year, month, last_day)
    return start.isoformat(), end.isoformat()


def parse_search_intent(query: str, *, today: date | None = None) -> tuple[dict, str]:
    """
    Extract structured filters from natural language and return the remaining
    semantic text for embedding / FTS.
    """
    today = today or timezone.localdate()
    filters: dict = {}
    remaining = query.strip()

    amount_match = AMOUNT_PATTERN.search(remaining)
    if amount_match:
        amount = _parse_amount(amount_match.group(1))
        if amount is not None:
            filters['final_price_gte'] = amount
        remaining = remaining[:amount_match.start()] + remaining[amount_match.end():]

    if THIS_MONTH_PATTERN.search(remaining):
        filters['date_from'] = today.replace(day=1).isoformat()
        filters['date_to'] = today.isoformat()
        remaining = THIS_MONTH_PATTERN.sub(' ', remaining)

    month_match = MONTH_PATTERN.search(remaining)
    if month_match and 'date_from' not in filters:
        month = MONTH_NAMES[month_match.group(1).lower()]
        year = int(month_match.group(2)) if month_match.group(2) else today.year
        date_from, date_to = _month_date_range(month, year)
        filters['date_from'] = date_from
        filters['date_to'] = date_to
        remaining = remaining[:month_match.start()] + remaining[month_match.end():]

    if PURCHASE_PATTERN.search(remaining):
        filters['is_purchase'] = True
        remaining = PURCHASE_PATTERN.sub(' ', remaining)

    if SALES_PATTERN.search(remaining):
        filters['is_sales'] = True
        remaining = SALES_PATTERN.sub(' ', remaining)

    remaining = re.sub(r'\s+', ' ', remaining).strip()
    return filters, remaining
