"""
list_purchase_transactions — list Net invoiced spending documents (PINV).

Metric: active PINV only (not gross, PRN, or PO).
"""

from __future__ import annotations

from typing import Any

from appassistant.services.blocks import document_entity_link, kpi_block, table_block
from appassistant.services.copy import list_invoices_message
from appassistant.services.money import as_money_str
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL
from appassistant.tools._common import (
    filtered_spend_qs,
    optional_int,
    optional_str,
    parse_limit,
    parse_min_amount,
    parse_offset,
    parse_period_bounds,
    parse_vendor_ids,
    require_view_document,
    resolve_vendors_or_raise,
    tool_result,
)
from appassistant.tools.base import AssistantTool


class ListPurchaseTransactionsTool(AssistantTool):
    name = 'list_purchase_transactions'
    description = (
        'List active PINV documents (Net invoiced spending) filtered by vendor(s), '
        f'min amount, and period. Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        date_from, date_to = parse_period_bounds(params)
        return {
            'vendor': optional_str(params, 'vendor'),
            'vendor_id': optional_int(params, 'vendor_id', min_v=1),
            'vendor_ids': parse_vendor_ids(params),
            'min_amount': parse_min_amount(params),
            'date_from': date_from,
            'date_to': date_to,
            'limit': parse_limit(params, default=20, maximum=50),
            'offset': parse_offset(params),
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
            min_amount=p['min_amount'],
        ).order_by('-date', '-id')

        total = qs.count()
        page = list(qs[p['offset']: p['offset'] + p['limit']])
        partial = (p['offset'] + len(page)) < total

        columns = [
            {'key': 'id', 'label': 'ID'},
            {'key': 'date', 'label': 'Date'},
            {'key': 'vendor', 'label': 'Vendor'},
            {'key': 'total_amount', 'label': 'Net amount', 'format': 'currency'},
            {'key': 'notes', 'label': 'Notes'},
        ]
        rows = []
        links = []
        for doc in page:
            vendor_name = ''
            if doc.builder_id:
                vendor_name = doc.builder.name or ''
            rows.append({
                'id': doc.pk,
                'date': doc.date.isoformat() if doc.date else '',
                'vendor': vendor_name,
                'vendor_id': doc.builder_id,
                'total_amount': as_money_str(doc.total_amount),
                'notes': (doc.notes or '')[:120],
            })
            links.append(
                document_entity_link(
                    document_id=doc.pk,
                    label=f'PINV #{doc.pk}',
                )
            )

        vendor_label = None
        if len(builders) == 1:
            vendor_label = builders[0].name
        elif len(builders) > 1:
            vendor_label = ', '.join(b.name for b in builders)

        blocks = [
            kpi_block(
                block_id='purchase-count',
                title='Matching purchase invoices',
                value=str(total),
                format='number',
            ),
            table_block(
                block_id='purchase-transactions',
                title=f'{SPEND_METRIC_LABEL} — purchase invoices',
                columns=columns,
                rows=rows,
                pagination={
                    'limit': p['limit'],
                    'offset': p['offset'],
                    'total': total,
                },
            ),
            *links,
        ]
        message = list_invoices_message(
            vendor_name=vendor_label,
            invoice_count=total,
            date_from=p['date_from'],
            date_to=p['date_to'],
        )
        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=total,
            invoice_count=total,
            partial=partial,
        )
