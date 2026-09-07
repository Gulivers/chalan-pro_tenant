"""
Level-1 Assistant document-type intentions.

Tenants configure DocumentType freely (type_code, description, stock flags).
These booleans map types to analytics meanings without hard-coding PINV/PO-INV.
"""

from __future__ import annotations

from typing import Any


INTENTION_NET_INVOICED_SPEND = 'net_invoiced_spend'
INTENTION_JOB_MATERIAL_ISSUE = 'job_material_issue'
INTENTION_PURCHASE_RETURN = 'purchase_return'

INTENTION_FIELD_MAP = {
    INTENTION_NET_INVOICED_SPEND: 'counts_as_net_invoiced_spend',
    INTENTION_JOB_MATERIAL_ISSUE: 'counts_as_job_material_issue',
    INTENTION_PURCHASE_RETURN: 'counts_as_purchase_return',
}


def suggest_intentions_from_flags(
    *,
    is_purchase: bool = False,
    is_sales: bool = False,
    is_operational: bool = False,
    affects_physical: bool = False,
    stock_movement: int = 0,
    type_code: str = '',
) -> dict[str, bool]:
    """
    Heuristic suggestions for the Document Type form.
    Never auto-applies; UI/API may pre-check for new types only.
    Excludes initial-inventory-like codes from spend suggestion.
    """
    code = (type_code or '').strip().upper().replace(' ', '')
    code_compact = code.replace('-', '').replace('_', '')

    suggest_spend = False
    suggest_job = False
    suggest_return = False

    if code_compact in {'PINV', 'POINV'} or code in {'PO-INV', 'PO_INV'}:
        suggest_spend = True
    elif code_compact in {'PK', 'PICK', 'PICKING'}:
        suggest_job = True
    elif code_compact in {'PRN', 'PRET', 'PURRET'}:
        suggest_return = True
    elif code_compact in {'INIINV', 'INITINV', 'INVENTORYINIT'}:
        pass
    else:
        if (
            is_purchase
            and not is_sales
            and not is_operational
            and affects_physical
            and stock_movement == 1
        ):
            # Ambiguous vs initial inventory — only suggest, never force.
            suggest_spend = True
        if is_operational and stock_movement == -1:
            suggest_job = True
        if is_purchase and not is_sales and affects_physical and stock_movement == -1:
            suggest_return = True

    if suggest_spend and suggest_return:
        suggest_return = False

    return {
        INTENTION_NET_INVOICED_SPEND: suggest_spend,
        INTENTION_JOB_MATERIAL_ISSUE: suggest_job,
        INTENTION_PURCHASE_RETURN: suggest_return,
    }


def intentions_payload_for_type(document_type) -> dict[str, Any]:
    return {
        INTENTION_NET_INVOICED_SPEND: bool(
            getattr(document_type, 'counts_as_net_invoiced_spend', False)
        ),
        INTENTION_JOB_MATERIAL_ISSUE: bool(
            getattr(document_type, 'counts_as_job_material_issue', False)
        ),
        INTENTION_PURCHASE_RETURN: bool(
            getattr(document_type, 'counts_as_purchase_return', False)
        ),
    }
