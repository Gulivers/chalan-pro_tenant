"""
Relative period helpers for Assistant tools.

All periods are timezone-aware via django.utils.timezone and settings.TIME_ZONE.
Returned bounds are inclusive calendar dates (date_from, date_to).
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from typing import Any

from django.conf import settings
from django.utils import timezone


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
    - period='this_month'
    - period='last_n_months' with months in [1..12]
    - months alone (treated as last_n_months)

    Uses settings.TIME_ZONE / active timezone (product default: UTC).
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

    if period_key == 'this_month':
        today = _today()
        return _month_start(today.year, today.month), _month_end(today.year, today.month)

    if period_key in ('last_n_months', 'last_months') or (
        period_key is None and months is not None
    ):
        if months is None:
            raise PeriodValidationError('months is required for last_n_months.')
        if not isinstance(months, int) or isinstance(months, bool):
            raise PeriodValidationError('months must be an integer in [1..12].')
        if months < 1 or months > 12:
            raise PeriodValidationError('months must be an integer in [1..12].')
        today = _today()
        start_year, start_month = _add_months(today.year, today.month, -(months - 1))
        return (
            _month_start(start_year, start_month),
            _month_end(today.year, today.month),
        )

    if period_key:
        raise PeriodValidationError(
            f'Unsupported period "{period}". Use this_month, last_n_months, or date_from/date_to.'
        )

    raise PeriodValidationError(
        'Provide period (this_month / last_n_months), months, or date_from/date_to.'
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
