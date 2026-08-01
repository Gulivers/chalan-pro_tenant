"""
top_vendors_by_spending — highest PINV spend vendors for a period.

Spend = PINV + is_active only; NOT document_type__is_purchase.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Sum

from appassistant.services.blocks import table_block
from appassistant.services.copy import top_vendors_message
from appassistant.services.money import as_money_str, coerce_money, zero_money
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL
from appassistant.tools._common import (
    filtered_spend_qs,
    parse_limit,
    parse_period_bounds,
    require_view_document,
    tool_result,
)
from appassistant.tools.base import AssistantTool


class TopVendorsBySpendingTool(AssistantTool):
    name = 'top_vendors_by_spending'
    description = (
        'Return the top vendors by Net invoiced spending (active PINV) for a period. '
        f'Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        date_from, date_to = parse_period_bounds(params)
        from appassistant.tools._common import parse_months
        return {
            'date_from': date_from,
            'date_to': date_to,
            'months': parse_months(params, required=False),
            'limit': parse_limit(params, default=5, maximum=20),
        }

    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        require_view_document(user)
        p = self.validate_params(params)
        qs = filtered_spend_qs(date_from=p['date_from'], date_to=p['date_to'])
        invoice_count = qs.count()
        grouped = (
            qs.values('builder_id', 'builder__name')
            .annotate(
                total=Sum('total_amount'),
                doc_count=Count('id'),
            )
            .order_by('-total', 'builder__name', 'builder_id')
        )
        total_vendors = grouped.count()
        page = list(grouped[: p['limit']])
        partial = total_vendors > p['limit']

        columns = [
            {'key': 'rank', 'label': 'Rank'},
            {'key': 'vendor', 'label': 'Vendor'},
            {'key': 'doc_count', 'label': 'Invoices'},
            {'key': 'total_amount', 'label': 'Net spending', 'format': 'currency'},
        ]
        rows = []
        for idx, row in enumerate(page, start=1):
            amount = coerce_money(row['total']) if row['total'] is not None else zero_money()
            name = row['builder__name'] or f"Builder #{row['builder_id'] or 'none'}"
            rows.append({
                'rank': idx,
                'vendor_id': row['builder_id'],
                'vendor': name,
                'doc_count': row['doc_count'],
                'total_amount': as_money_str(amount),
            })

        blocks = [
            table_block(
                block_id='top-vendors',
                title=f'Top {p["limit"]} vendors by {SPEND_METRIC_LABEL.lower()}',
                columns=columns,
                rows=rows,
            ),
        ]
        message = top_vendors_message(
            vendor_count=len(rows),
            date_from=p['date_from'],
            date_to=p['date_to'],
            invoice_count=invoice_count,
            months=p.get('months'),
        )
        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=len(rows),
            invoice_count=invoice_count,
            partial=partial,
        )
