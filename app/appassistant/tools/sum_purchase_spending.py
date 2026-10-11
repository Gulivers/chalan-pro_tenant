"""
sum_purchase_spending — Net invoiced spending for vendor(s) and period.

Metric: active PINV Document.total_amount only (not gross, PRN, or PO).
"""

from __future__ import annotations

from typing import Any

from appassistant.services.blocks import kpi_currency
from appassistant.services.copy import net_spending_message, period_phrase
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL, SPEND_METRIC_SHORT
from appassistant.tools._common import (
    filtered_spend_qs,
    optional_int,
    optional_str,
    parse_period_bounds,
    parse_vendor_ids,
    require_view_document,
    resolve_vendors_or_raise,
    sum_amount,
    tool_result,
)
from appassistant.tools.base import AssistantTool


class SumPurchaseSpendingTool(AssistantTool):
    name = 'sum_purchase_spending'
    description = (
        'Sum Net invoiced spending (active PINV total_amount) for a period. '
        'Vendor(s) optional — omit for all vendors. '
        f'Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        date_from, date_to = parse_period_bounds(params)
        return {
            'vendor': optional_str(params, 'vendor'),
            'vendor_id': optional_int(params, 'vendor_id', min_v=1),
            'vendor_ids': parse_vendor_ids(params),
            'date_from': date_from,
            'date_to': date_to,
        }

    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        require_view_document(user)
        p = self.validate_params(params)
        builders = resolve_vendors_or_raise(
            vendor=p['vendor'],
            vendor_id=p['vendor_id'],
            vendor_ids=p['vendor_ids'],
            required=False,
        )
        qs = filtered_spend_qs(
            date_from=p['date_from'],
            date_to=p['date_to'],
            builders=builders,
        )
        total = sum_amount(qs)
        count = qs.count()
        period = period_phrase(p['date_from'], p['date_to'])
        if not builders:
            vendor_label = None
            title = SPEND_METRIC_SHORT
        elif len(builders) == 1:
            vendor_label = builders[0].name
            title = f'{SPEND_METRIC_SHORT} with {vendor_label}'
        else:
            vendor_label = ', '.join(b.name for b in builders)
            title = f'{SPEND_METRIC_SHORT} with selected vendors'
        blocks = [
            kpi_currency(
                block_id='total-spending',
                title=title,
                amount=total,
                subtitle=f'{SPEND_METRIC_LABEL} · {period} · {count} invoice(s)',
            ),
        ]
        message = net_spending_message(
            vendor_name=vendor_label,
            amount=total,
            date_from=p['date_from'],
            date_to=p['date_to'],
            invoice_count=count,
        )
        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=count,
            invoice_count=count,
            partial=False,
        )
