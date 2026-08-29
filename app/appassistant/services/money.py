"""Decimal money helpers for Assistant tools. Never use float for money."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

MONEY_QUANTIZE = Decimal('0.01')


def zero_money() -> Decimal:
    return Decimal('0.00')


def coerce_money(value: Any) -> Decimal:
    """
    Coerce a value to Decimal money (2 decimal places).
    Rejects bool and float to avoid binary float artifacts.
    """
    if value is None:
        raise ValueError('Money value is required.')
    if isinstance(value, bool):
        raise ValueError('Money value must not be a boolean.')
    if isinstance(value, float):
        raise ValueError('Money value must not be a float; use Decimal or string.')
    if isinstance(value, Decimal):
        amount = value
    elif isinstance(value, int):
        amount = Decimal(value)
    elif isinstance(value, str):
        text = value.strip().replace(',', '')
        if not text:
            raise ValueError('Money value is empty.')
        try:
            amount = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(f'Invalid money value: {value!r}') from exc
    else:
        raise ValueError(f'Unsupported money type: {type(value).__name__}')
    return amount.quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)


def as_money_str(value: Decimal | None) -> str:
    """Serialize money as a fixed 2-decimal string (never float)."""
    if value is None:
        value = zero_money()
    if not isinstance(value, Decimal):
        value = coerce_money(value)
    return str(value.quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP))


def as_money_display(value: Decimal | None) -> str:
    """User-facing money for assistant messages, e.g. $22,966.78."""
    raw = as_money_str(value)
    sign = ''
    if raw.startswith('-'):
        sign = '-'
        raw = raw[1:]
    whole, _, frac = raw.partition('.')
    grouped = f'{int(whole):,}'
    return f'{sign}${grouped}.{frac or "00"}'
