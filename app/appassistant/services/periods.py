"""
Relative period helpers for Assistant tools.

All periods are timezone-aware via django.utils.timezone and settings.TIME_ZONE.
Returned bounds are inclusive calendar dates (date_from, date_to).
"""

from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone

_WORD_MONTH_COUNTS = {
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


class PeriodValidationError(ValueError):
    """Invalid period parameters."""


# Explicit date ranges cannot exceed this inclusive span (DoS / cost guard).
MAX_PERIOD_SPAN_DAYS = 366


def now_tz():
    """Timezone-aware 'now' for Assistant period calculations."""
    return timezone.now()


def _today() -> date:
    return timezone.localdate()


def _parse_date(value: Any, field: str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            return timezone.localtime(value).date()
        return value.date()
    if isinstance(value, str):
        text = value.strip()
        try:
            return date.fromisoformat(text)
        except ValueError as exc:
            raise PeriodValidationError(
                f'{field} must be an ISO date (YYYY-MM-DD).'
            ) from exc
    raise PeriodValidationError(f'{field} must be a date or ISO date string.')


def _month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def _month_end(year: int, month: int) -> date:
    return date(year, month, monthrange(year, month)[1])


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    idx = year * 12 + (month - 1) + delta
    return idx // 12, (idx % 12) + 1


def _quarter_of(day: date) -> int:
    return (day.month - 1) // 3 + 1


def _quarter_bounds(year: int, quarter: int) -> tuple[date, date]:
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    return _month_start(year, start_month), _month_end(year, end_month)


def _week_start_monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def previous_calendar_months(n: int = 1) -> tuple[date, date]:
    """
    Inclusive span of the N full calendar months immediately before the
    current month (current month is excluded).

    Example (today = 2026-08-01):
      n=1 → 2026-07-01 .. 2026-07-31
      n=2 → 2026-06-01 .. 2026-07-31
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1 or n > 12:
        raise PeriodValidationError('previous calendar months must be an integer in [1..12].')
    today = _today()
    end_year, end_month = _add_months(today.year, today.month, -1)
    start_year, start_month = _add_months(today.year, today.month, -n)
    return (
        _month_start(start_year, start_month),
        _month_end(end_year, end_month),
    )


def re_match_previous_months(period_key: str) -> int | None:
    """
    Parse labels like previous_2_calendar_months / last_2_calendar_months.
    """
    m = re.fullmatch(
        r'(?:previous|last)_(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)'
        r'_calendar_months?',
        (period_key or '').strip().lower(),
    )
    if not m:
        return None
    token = m.group(1)
    if token.isdigit():
        value = int(token)
    else:
        value = _WORD_MONTH_COUNTS.get(token)
    if value is None or value < 1 or value > 12:
        return None
    return value


def resolve_period(
    *,
    period: str | None = None,
    date_from: Any = None,
    date_to: Any = None,
    months: int | None = None,
) -> tuple[date, date]:
    """
    Resolve inclusive (date_from, date_to) for spend filters.

    Supported:
    - explicit date_from / date_to
    - period='this_month' / 'month_to_date' → month-to-date (no future days)
    - period='calendar_month' → full current calendar month
    - period='last_month'
    - period='this_year' / 'year_to_date'
    - period='last_n_months' with months in [1..12]
    - months alone (treated as last_n_months)

    Uses settings.TIME_ZONE / active timezone (product default: UTC).
    Relative ranges that include the current month end at local today (D4).
    """
    # Ensure Django TZ context matches product settings when possible.
    _ = getattr(settings, 'TIME_ZONE', 'UTC')

    has_from = date_from is not None and date_from != ''
    has_to = date_to is not None and date_to != ''
    period_key = (period or '').strip().lower() or None

    if has_from or has_to:
        if not has_from or not has_to:
            raise PeriodValidationError(
                'Both date_from and date_to are required when using an explicit range.'
            )
        start = _parse_date(date_from, 'date_from')
        end = _parse_date(date_to, 'date_to')
        if start > end:
            raise PeriodValidationError('date_from must be on or before date_to.')
        span_days = (end - start).days + 1
        if span_days > MAX_PERIOD_SPAN_DAYS:
            raise PeriodValidationError(
                f'Date range must be at most {MAX_PERIOD_SPAN_DAYS} days '
                f'(got {span_days}).'
            )
        return start, end

    today = _today()

    if period_key == 'today':
        return today, today

    if period_key == 'yesterday':
        day = today - timedelta(days=1)
        return day, day

    if period_key == 'this_week':
        start = _week_start_monday(today)
        return start, today

    if period_key == 'last_week':
        this_week_start = _week_start_monday(today)
        end = this_week_start - timedelta(days=1)
        start = end - timedelta(days=6)
        return start, end

    if period_key in ('this_month', 'month_to_date', 'mtd'):
        # D4: spend "this month" = month-to-date (exclude future calendar days).
        return _month_start(today.year, today.month), today

    if period_key == 'calendar_month':
        return _month_start(today.year, today.month), _month_end(today.year, today.month)

    if period_key in ('last_month', 'previous_month', 'previous_calendar_month'):
        return previous_calendar_months(1)

    m_prev = None
    if period_key:
        m_prev = re_match_previous_months(period_key)
    if m_prev is not None:
        return previous_calendar_months(m_prev)

    if period_key in ('this_quarter', 'quarter_to_date'):
        q = _quarter_of(today)
        start, _ = _quarter_bounds(today.year, q)
        return start, today

    if period_key == 'last_quarter':
        q = _quarter_of(today) - 1
        year = today.year
        if q < 1:
            q = 4
            year -= 1
        return _quarter_bounds(year, q)

    if period_key in ('this_year', 'year_to_date', 'ytd'):
        return date(today.year, 1, 1), today

    if period_key in ('last_six_months', 'last_6_months'):
        months = 6

    # Alias: last_3_months / last_three_months → months=N rolling window.
    if period_key and months is None:
        m_last = re.fullmatch(
            r'last_(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)'
            r'_months?',
            period_key,
        )
        if m_last:
            token = m_last.group(1)
            months = int(token) if token.isdigit() else _WORD_MONTH_COUNTS.get(token)

    if period_key in ('last_n_months', 'last_months') or (
        period_key is None and months is not None
    ) or period_key in ('last_six_months', 'last_6_months') or (
        period_key
        and re.fullmatch(
            r'last_(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)'
            r'_months?',
            period_key,
        )
    ):
        if months is None:
            raise PeriodValidationError('months is required for last_n_months.')
        if not isinstance(months, int) or isinstance(months, bool):
            raise PeriodValidationError('months must be an integer in [1..12].')
        if months < 1 or months > 12:
            raise PeriodValidationError('months must be an integer in [1..12].')
        start_year, start_month = _add_months(today.year, today.month, -(months - 1))
        return (
            _month_start(start_year, start_month),
            today,
        )

    if period_key:
        raise PeriodValidationError(
            f'Unsupported period "{period}". '
            'Use today, yesterday, this_week, last_week, this_month, '
            'month_to_date, calendar_month, last_month, this_quarter, '
            'last_quarter, this_year, last_n_months, or date_from/date_to.'
        )

    raise PeriodValidationError(
        'Provide period (this_month / last_month / last_n_months), months, '
        'or date_from/date_to.'
    )


def iter_month_labels(date_from: date, date_to: date) -> list[tuple[str, date, date]]:
    """
    Yield (label YYYY-MM, month_start, month_end) for each month overlapping the range.
    Labels are stable and timezone-independent (calendar months).
    """
    if date_from > date_to:
        return []
    year, month = date_from.year, date_from.month
    end_y, end_m = date_to.year, date_to.month
    out: list[tuple[str, date, date]] = []
    while (year, month) <= (end_y, end_m):
        start = _month_start(year, month)
        end = _month_end(year, month)
        # Clip to requested range
        clipped_start = max(start, date_from)
        clipped_end = min(end, date_to)
        label = f'{year:04d}-{month:02d}'
        out.append((label, clipped_start, clipped_end))
        year, month = _add_months(year, month, 1)
    return out


def days_in_range(date_from: date, date_to: date) -> int:
    return (date_to - date_from).days + 1
