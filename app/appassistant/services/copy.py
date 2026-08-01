"""
User-facing English copy helpers for Assistant Level-1 spend tools.

Metric in Level 1: Net invoiced spending (active PINV totals).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from appassistant.services.money import as_money_display
from appassistant.services.periods import resolve_period
from appassistant.services.spend import SPEND_METRIC_LABEL, SPEND_METRIC_SHORT


def format_money_display(value: Decimal | None) -> str:
    """Display money as $22,966.78 (Decimal-backed; never float math)."""
    return as_money_display(value)


def invoice_count_label(count: int) -> str:
    n = max(0, int(count))
    if n == 1:
        return '1 purchase invoice'
    return f'{n} purchase invoices'


def source_display(count: int) -> str:
    """Operational source line, e.g. 'Source: 3 purchase invoices'."""
    return f'Source: {invoice_count_label(count)}'


def period_phrase(date_from: date, date_to: date, *, months: int | None = None) -> str:
    """
    Prefer natural phrases when the range matches a known relative period.
    Falls back to an inclusive ISO date range.
    """
    try:
        this_from, this_to = resolve_period(period='this_month')
        if date_from == this_from and date_to == this_to:
            return 'this month'
    except Exception:
        pass

    if months is not None and months >= 1:
        try:
            last_from, last_to = resolve_period(months=months)
            if date_from == last_from and date_to == last_to:
                unit = 'month' if months == 1 else 'months'
                return f'the last {months} {unit}'
        except Exception:
            pass

    return f'{date_from.isoformat()} to {date_to.isoformat()}'


def net_spending_message(
    *,
    vendor_name: str | None,
    amount: Decimal,
    date_from: date,
    date_to: date,
    invoice_count: int,
    months: int | None = None,
) -> str:
    """
    Example:
      Net spending with Home Depot this month is $22,966.78, based on 3 purchase invoices.
    """
    period = period_phrase(date_from, date_to, months=months)
    money = format_money_display(amount)
    basis = invoice_count_label(invoice_count)
    if vendor_name:
        return (
            f'{SPEND_METRIC_SHORT} with {vendor_name} {period} is {money}, '
            f'based on {basis}.'
        )
    return (
        f'{SPEND_METRIC_SHORT} {period} is {money}, based on {basis}.'
    )


def list_invoices_message(
    *,
    vendor_name: str | None,
    invoice_count: int,
    date_from: date,
    date_to: date,
    months: int | None = None,
) -> str:
    period = period_phrase(date_from, date_to, months=months)
    basis = invoice_count_label(invoice_count)
    metric = SPEND_METRIC_LABEL
    if vendor_name:
        return (
            f'Found {basis} for {vendor_name} ({metric.lower()}) {period}.'
        )
    return f'Found {basis} ({metric.lower()}) {period}.'


def by_vendor_message(
    *,
    vendor_count: int,
    invoice_count: int,
    date_from: date,
    date_to: date,
    months: int | None = None,
) -> str:
    period = period_phrase(date_from, date_to, months=months)
    vlabel = 'vendor' if vendor_count == 1 else 'vendors'
    return (
        f'{SPEND_METRIC_LABEL} by vendor {period}: '
        f'{vendor_count} {vlabel}, based on {invoice_count_label(invoice_count)}.'
    )


def compare_vendors_message(*, vendor_count: int, months: int, invoice_count: int) -> str:
    unit = 'month' if months == 1 else 'months'
    vlabel = 'vendor' if vendor_count == 1 else 'vendors'
    return (
        f'{SPEND_METRIC_LABEL} comparison for the last {months} {unit}: '
        f'top {vendor_count} {vlabel}, based on {invoice_count_label(invoice_count)}.'
    )


def top_vendors_message(
    *,
    vendor_count: int,
    date_from: date,
    date_to: date,
    invoice_count: int,
    months: int | None = None,
) -> str:
    period = period_phrase(date_from, date_to, months=months)
    vlabel = 'vendor' if vendor_count == 1 else 'vendors'
    return (
        f'Top {vendor_count} {vlabel} by {SPEND_METRIC_LABEL.lower()} {period}, '
        f'based on {invoice_count_label(invoice_count)}.'
    )


def timeseries_message(
    *,
    vendor_name: str | None,
    months: int,
    invoice_count: int,
) -> str:
    unit = 'month' if months == 1 else 'months'
    scope = f' for {vendor_name}' if vendor_name else ''
    return (
        f'{SPEND_METRIC_LABEL}{scope} over the last {months} {unit}, '
        f'based on {invoice_count_label(invoice_count)}.'
    )
