"""
compare_purchases_by_vendor — top vendors across the last N months.

Spend = PINV + is_active only; NOT document_type__is_purchase.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from appassistant.services.blocks import bar_chart_block, table_block
from appassistant.services.money import as_money_str, coerce_money, zero_money
from appassistant.services.periods import (
    PeriodValidationError,
    iter_month_labels,
    resolve_period,
)
from appassistant.services.copy import compare_vendors_message
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL
from appassistant.tools._common import (
    filtered_spend_qs,
    parse_limit,
    parse_months,
    require_view_document,
    tool_result,
)
from appassistant.tools.base import AssistantTool
from appassistant.tools.errors import validation_error


class ComparePurchasesByVendorTool(AssistantTool):
    name = 'compare_purchases_by_vendor'
    description = (
        'Compare top vendors by Net invoiced spending (active PINV) over the last N months. '
        f'Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        months = parse_months(params, required=True)
        assert months is not None
        try:
            date_from, date_to = resolve_period(months=months)
        except PeriodValidationError as exc:
            raise validation_error(str(exc)) from exc
        top_n = parse_limit(params, default=10, maximum=20, key='top_n')
        return {
            'months': months,
            'date_from': date_from,
            'date_to': date_to,
            'top_n': top_n,
        }

    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        require_view_document(user)
        p = self.validate_params(params)
        month_meta = iter_month_labels(p['date_from'], p['date_to'])
        month_labels = [m[0] for m in month_meta]

        qs = filtered_spend_qs(date_from=p['date_from'], date_to=p['date_to'])
        invoice_count = qs.count()
        # Overall top vendors by total spend
        top = list(
            qs.values('builder_id', 'builder__name')
            .annotate(total=Sum('total_amount'))
            .order_by('-total', 'builder__name', 'builder_id')[: p['top_n']]
        )
        top_ids = [row['builder_id'] for row in top if row['builder_id'] is not None]

        # Monthly totals for those vendors
        monthly_map: dict[int, dict[str, Decimal]] = defaultdict(dict)
        if top_ids:
            monthly_rows = (
                qs.filter(builder_id__in=top_ids)
                .annotate(month=TruncMonth('date'))
                .values('builder_id', 'month')
                .annotate(total=Sum('total_amount'))
            )
            for row in monthly_rows:
                if not row['month']:
                    continue
                label = row['month'].strftime('%Y-%m')
                monthly_map[row['builder_id']][label] = (
                    coerce_money(row['total']) if row['total'] is not None else zero_money()
                )

        columns = [
            {'key': 'vendor', 'label': 'Vendor'},
            *[{'key': label, 'label': label, 'format': 'currency'} for label in month_labels],
            {'key': 'total', 'label': 'Total', 'format': 'currency'},
        ]
        rows = []
        chart_labels: list[str] = []
        chart_values: list[str] = []
        for row in top:
            vendor_id = row['builder_id']
            name = row['builder__name'] or f'Builder #{vendor_id or "none"}'
            total = coerce_money(row['total']) if row['total'] is not None else zero_money()
            entry: dict[str, Any] = {
                'vendor_id': vendor_id,
                'vendor': name,
                'total': as_money_str(total),
            }
            for label in month_labels:
                amount = monthly_map.get(vendor_id or -1, {}).get(label, zero_money())
                entry[label] = as_money_str(amount)
            rows.append(entry)
            chart_labels.append(name)
            chart_values.append(as_money_str(total))

        blocks: list[dict] = [
            table_block(
                block_id='compare-purchases-by-vendor',
                title=f'{SPEND_METRIC_LABEL} by vendor (last {p["months"]} months)',
                columns=columns,
                rows=rows,
            ),
        ]
        if chart_labels:
            blocks.append(
                bar_chart_block(
                    block_id='compare-purchases-by-vendor-chart',
                    title=f'{SPEND_METRIC_LABEL} by vendor',
                    labels=chart_labels,
                    values=chart_values,
                    series_name=SPEND_METRIC_LABEL,
                )
            )

        message = compare_vendors_message(
            vendor_count=len(rows),
            months=p['months'],
            invoice_count=invoice_count,
        )
        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=len(rows),
            invoice_count=invoice_count,
            partial=False,
        )
