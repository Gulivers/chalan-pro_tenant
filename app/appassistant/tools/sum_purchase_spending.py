"""
sum_purchase_spending — Net invoiced spending for a vendor and period.

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
    require_view_document,
    resolve_vendor_or_raise,
    sum_amount,
    tool_result,
)
from appassistant.tools.base import AssistantTool


class SumPurchaseSpendingTool(AssistantTool):
    name = 'sum_purchase_spending'
    description = (
        'Sum Net invoiced spending (active PINV total_amount) for a vendor and period. '
        f'Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        date_from, date_to = parse_period_bounds(params)
        vendor = optional_str(params, 'vendor')
        vendor_id = optional_int(params, 'vendor_id', min_v=1)
        if vendor is None and vendor_id is None:
            from appassistant.tools.errors import validation_error
            raise validation_error('vendor or vendor_id is required.')
        return {
            'vendor': vendor,
            'vendor_id': vendor_id,
            'date_from': date_from,
            'date_to': date_to,
        }

    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        require_view_document(user)
        p = self.validate_params(params)
        builder = resolve_vendor_or_raise(
            vendor=p['vendor'],
            vendor_id=p['vendor_id'],
            required=True,
        )
        qs = filtered_spend_qs(
            date_from=p['date_from'],
            date_to=p['date_to'],
            builder=builder,
        )
        total = sum_amount(qs)
        count = qs.count()
        period = period_phrase(p['date_from'], p['date_to'])
        blocks = [
            kpi_currency(
                block_id='total-spending',
                title=f'{SPEND_METRIC_SHORT} with {builder.name}',
                amount=total,
                subtitle=f'{SPEND_METRIC_LABEL} · {period} · {count} invoice(s)',
            ),
        ]
        message = net_spending_message(
            vendor_name=builder.name,
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
