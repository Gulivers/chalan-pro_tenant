"""
purchases_by_vendor — Net invoiced spending by vendor for a period.

Metric: active PINV Document.total_amount only.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Sum

from appassistant.services.blocks import bar_chart_block, table_block
from appassistant.services.copy import by_vendor_message
from appassistant.services.money import as_money_str, coerce_money, zero_money
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL
from appassistant.tools._common import (
    filtered_spend_qs,
    parse_bool,
    parse_limit,
    parse_period_bounds,
    require_view_document,
    tool_result,
)
from appassistant.tools.base import AssistantTool


class PurchasesByVendorTool(AssistantTool):
    name = 'purchases_by_vendor'
    description = (
        'Aggregate Net invoiced spending (active PINV) by vendor for a period. '
        f'Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        date_from, date_to = parse_period_bounds(params)
        return {
            'date_from': date_from,
            'date_to': date_to,
            'limit': parse_limit(params, default=20, maximum=50),
            'include_chart': parse_bool(params, 'include_chart', default=True),
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
            {'key': 'vendor', 'label': 'Vendor'},
            {'key': 'doc_count', 'label': 'Invoices'},
            {'key': 'total_amount', 'label': 'Net spending', 'format': 'currency'},
        ]
        rows = []
        labels: list[str] = []
        values: list[str] = []
        for row in page:
            amount = coerce_money(row['total']) if row['total'] is not None else zero_money()
            name = row['builder__name'] or f"Builder #{row['builder_id'] or 'none'}"
            rows.append({
                'vendor_id': row['builder_id'],
                'vendor': name,
                'doc_count': row['doc_count'],
                'total_amount': as_money_str(amount),
            })
            labels.append(name)
            values.append(as_money_str(amount))

        blocks: list[dict] = [
            table_block(
                block_id='purchases-by-vendor',
                title=f'{SPEND_METRIC_LABEL} by vendor',
                columns=columns,
                rows=rows,
                pagination={
                    'limit': p['limit'],
                    'offset': 0,
                    'total': total_vendors,
                },
            ),
        ]
        if p['include_chart'] and labels:
            blocks.append(
                bar_chart_block(
                    block_id='purchases-by-vendor-chart',
                    title=f'{SPEND_METRIC_LABEL} by vendor',
                    labels=labels,
                    values=values,
                    series_name=SPEND_METRIC_LABEL,
                )
            )

        message = by_vendor_message(
            vendor_count=total_vendors,
            invoice_count=invoice_count,
            date_from=p['date_from'],
            date_to=p['date_to'],
        )
        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=total_vendors,
            invoice_count=invoice_count,
            partial=partial,
        )
