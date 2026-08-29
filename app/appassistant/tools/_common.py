"""Shared param validation and queryset filtering for spend tools."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from django.db.models import QuerySet, Sum

from appassistant.services.money import coerce_money, zero_money
from appassistant.services.periods import PeriodValidationError, resolve_period
from appassistant.services.spend import spend_documents_qs
from appassistant.services.vendors import (
    AmbiguousVendorError,
    VendorNotFoundError,
    resolve_vendor,
)
from appassistant.tools.errors import (
    ToolError,
    ambiguous_vendor_error,
    not_found_error,
    permission_error,
    validation_error,
)


def require_view_document(user) -> None:
    if not user or not getattr(user, 'is_authenticated', False):
        raise permission_error('Authentication required.')
    if not user.has_perm('apptransactions.view_document'):
        raise permission_error()


def optional_int(params: dict, key: str, *, min_v: int | None = None, max_v: int | None = None) -> int | None:
    if key not in params or params[key] is None or params[key] == '':
        return None
    value = params[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise validation_error(f'{key} must be an integer.')
    if min_v is not None and value < min_v:
        raise validation_error(f'{key} must be >= {min_v}.')
    if max_v is not None and value > max_v:
        raise validation_error(f'{key} must be <= {max_v}.')
    return value


def optional_str(params: dict, key: str, *, max_len: int = 255) -> str | None:
    if key not in params or params[key] is None or params[key] == '':
        return None
    value = params[key]
    if not isinstance(value, str):
        raise validation_error(f'{key} must be a string.')
    value = value.strip()
    if not value:
        return None
    if len(value) > max_len:
        raise validation_error(f'{key} must be at most {max_len} characters.')
    return value


def parse_limit(
    params: dict,
    *,
    default: int,
    maximum: int,
    key: str = 'limit',
) -> int:
    value = optional_int(params, key, min_v=1, max_v=maximum)
    if value is None:
        return default
    return value


MAX_OFFSET = 10_000


def parse_offset(params: dict, *, key: str = 'offset', maximum: int = MAX_OFFSET) -> int:
    value = optional_int(params, key, min_v=0, max_v=maximum)
    if value is None:
        return 0
    return value


def parse_bool(params: dict, key: str, *, default: bool = False) -> bool:
    if key not in params or params[key] is None or params[key] == '':
        return default
    value = params[key]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ('true', '1', 'yes'):
            return True
        if lowered in ('false', '0', 'no'):
            return False
    raise validation_error(f'{key} must be a boolean.')


def parse_months(params: dict, *, required: bool = False, key: str = 'months') -> int | None:
    value = optional_int(params, key, min_v=1, max_v=12)
    if value is None and required:
        raise validation_error(f'{key} is required and must be in [1..12].')
    return value

def parse_min_amount(params: dict) -> Decimal | None:
    if 'min_amount' not in params or params['min_amount'] is None or params['min_amount'] == '':
        return None
    try:
        return coerce_money(params['min_amount'])
    except ValueError as exc:
        raise validation_error(str(exc), details={'field': 'min_amount'}) from exc


def parse_period_bounds(params: dict) -> tuple[date, date]:
    try:
        return resolve_period(
            period=optional_str(params, 'period', max_len=64),
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
            months=parse_months(params, required=False),
        )
    except PeriodValidationError as exc:
        raise validation_error(str(exc)) from exc
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise validation_error(str(exc)) from exc


def resolve_vendor_or_raise(
    *,
    vendor: str | None = None,
    vendor_id: int | None = None,
    required: bool = False,
):
    if vendor_id is None and not vendor:
        if required:
            raise validation_error('vendor or vendor_id is required.')
        return None
    try:
        return resolve_vendor(name=vendor, vendor_id=vendor_id)
    except AmbiguousVendorError as exc:
        raise ambiguous_vendor_error(
            exc.message,
            [{'id': c.id, 'name': c.name} for c in exc.candidates],
        ) from exc
    except VendorNotFoundError as exc:
        raise not_found_error(exc.message) from exc


def parse_vendor_ids(params: dict, *, key: str = 'vendor_ids', maximum: int = 10) -> list[int]:
    """Optional list of positive builder IDs (already resolved by Django)."""
    if key not in params or params[key] is None or params[key] == '':
        return []
    value = params[key]
    if not isinstance(value, list):
        raise validation_error(f'{key} must be a list of positive integers.')
    if len(value) > maximum:
        raise validation_error(f'{key} must have at most {maximum} entries.')
    out: list[int] = []
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool) or item < 1:
            raise validation_error(f'{key} entries must be positive integers.')
        if item not in out:
            out.append(item)
    return out


def resolve_vendors_or_raise(
    *,
    vendor: str | None = None,
    vendor_id: int | None = None,
    vendor_ids: list[int] | None = None,
    required: bool = False,
) -> list:
    """
    Resolve one or more vendors in the current tenant schema.

    Returns a list of Builder instances (possibly empty when not required).
    """
    ids = list(vendor_ids or [])
    if vendor_id is not None and vendor_id not in ids:
        ids.append(vendor_id)

    builders = []
    if ids:
        for vid in ids:
            builders.append(resolve_vendor_or_raise(vendor_id=vid, required=True))
        return builders

    if vendor:
        return [resolve_vendor_or_raise(vendor=vendor, required=True)]

    if required:
        raise validation_error('vendor, vendor_id, or vendor_ids is required.')
    return []


def filtered_spend_qs(
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    builder=None,
    builders: list | None = None,
    builder_ids: list[int] | None = None,
    min_amount: Decimal | None = None,
) -> QuerySet:
    """
    Spend documents after authorize-then-filter.

    Spend = PINV + is_active only (see services.spend). Never is_purchase.
    """
    qs = spend_documents_qs()
    if date_from is not None:
        qs = qs.filter(date__gte=date_from)
    if date_to is not None:
        qs = qs.filter(date__lte=date_to)

    ids: list[int] = []
    if builder is not None:
        ids.append(builder.pk)
    if builders:
        for item in builders:
            pk = getattr(item, 'pk', item)
            if isinstance(pk, int) and pk not in ids:
                ids.append(pk)
    if builder_ids:
        for pk in builder_ids:
            if isinstance(pk, int) and pk not in ids:
                ids.append(pk)
    if len(ids) == 1:
        qs = qs.filter(builder_id=ids[0])
    elif len(ids) > 1:
        qs = qs.filter(builder_id__in=ids)

    if min_amount is not None:
        # Inclusive lower bound on total_amount.
        qs = qs.filter(total_amount__gte=min_amount)
    return qs


def sum_amount(qs: QuerySet) -> Decimal:
    total = qs.aggregate(total=Sum('total_amount'))['total']
    if total is None:
        return zero_money()
    return coerce_money(total)


def tool_result(
    *,
    tool_name: str,
    message: str,
    blocks: list[dict],
    row_count: int,
    partial: bool = False,
    invoice_count: int | None = None,
) -> dict[str, Any]:
    """
    Build a tool contract payload.

    sources are user-facing for Level 1, e.g.:
      {"type": "source", "label": "3 purchase invoices", "row_count": 3, ...}
    tool_name is kept for audit/debug; UI prefers label.
    """
    from appassistant.services.copy import invoice_count_label, source_display

    inv = int(invoice_count) if invoice_count is not None else int(row_count)
    label = invoice_count_label(inv)
    return {
        'message': message,
        'blocks': blocks,
        'sources': [
            {
                'type': 'source',
                'tool_name': tool_name,
                'label': label,
                'display': source_display(inv),
                'row_count': inv,
            }
        ],
        'row_count': row_count,
        'partial': partial,
    }
