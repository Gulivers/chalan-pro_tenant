"""
compare_purchases_by_vendor — top vendors across a period.

Accepts months (classic last-N), period labels, or explicit date_from/date_to.
For short spans (< ~45 days) returns totals-by-vendor (no monthly TruncMonth
columns); longer ranges keep the monthly breakdown when months is set or the
span is wide enough.

Spend = PINV + is_active only; NOT document_type__is_purchase.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from appassistant.services.blocks import bar_chart_block, table_block
from appassistant.services.copy import compare_vendors_message, period_phrase
from appassistant.services.money import as_money_str, coerce_money, zero_money
from appassistant.services.periods import (
    PeriodValidationError,
    days_in_range,
    iter_month_labels,
    resolve_period,
)
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL
from appassistant.tools._common import (
    filtered_spend_qs,
    optional_str,
    parse_bool,
    parse_limit,
    parse_months,
    parse_period_bounds,
    require_view_document,
    tool_result,
)
from appassistant.tools.base import AssistantTool
from appassistant.tools.errors import validation_error

# Below this inclusive span, monthly TruncMonth columns are not useful;
# return ranking / totals by vendor for the range instead.
MONTHLY_BREAKDOWN_MIN_DAYS = 45


class ComparePurchasesByVendorTool(AssistantTool):
    name = 'compare_purchases_by_vendor'
    description = (
        'Compare top vendors by Net invoiced spending (active PINV) over a period. '
        'Accepts months (1..12), period labels, or date_from/date_to (ISO). '
        'Short ranges return totals by vendor; longer ranges include a monthly breakdown. '
        f'Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        months = parse_months(params, required=False)
        period = optional_str(params, 'period', max_len=64)
        has_explicit_range = bool(params.get('date_from') or params.get('date_to'))

        try:
            if months is not None and not period and not has_explicit_range:
                date_from, date_to = resolve_period(months=months)
            elif period or has_explicit_range or months is not None:
                date_from, date_to = parse_period_bounds(params)
            else:
                raise validation_error(
                    'Provide months (1..12), a period label, or date_from/date_to '
                    'for the comparison range.'
                )
        except PeriodValidationError as exc:
            raise validation_error(str(exc)) from exc

        span_days = days_in_range(date_from, date_to)
        if has_explicit_range:
            # Explicit ISO bounds are authority: ignore residual months from the LLM
            # so short week-based spans always degrade to totals-by-vendor.
            months = None
            monthly_breakdown = span_days >= MONTHLY_BREAKDOWN_MIN_DAYS
        else:
            # Classic months=N (or long period labels) keep monthly columns.
            monthly_breakdown = months is not None or span_days >= MONTHLY_BREAKDOWN_MIN_DAYS

        return {
            'months': months,
            'date_from': date_from,
            'date_to': date_to,
            'top_n': parse_limit(params, default=10, maximum=20, key='top_n'),
            'include_chart': parse_bool(params, 'include_chart', default=True),
            'include_table': parse_bool(params, 'include_table', default=True),
            'monthly_breakdown': monthly_breakdown,
        }

    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        require_view_document(user)
        p = self.validate_params(params)
        qs = filtered_spend_qs(date_from=p['date_from'], date_to=p['date_to'])
        invoice_count = qs.count()
        top = list(
            qs.values('builder_id', 'builder__name')
            .annotate(total=Sum('total_amount'))
            .order_by('-total', 'builder__name', 'builder_id')[: p['top_n']]
        )

        phrase = period_phrase(p['date_from'], p['date_to'], months=p['months'])
        title = f'{SPEND_METRIC_LABEL} by vendor ({phrase})'

        if p['monthly_breakdown']:
            columns, rows, chart_labels, chart_values = self._monthly_rows(
                qs=qs,
                top=top,
                date_from=p['date_from'],
                date_to=p['date_to'],
            )
        else:
            columns, rows, chart_labels, chart_values = self._totals_rows(top)

        blocks: list[dict] = []
        if p['include_table']:
            blocks.append(
                table_block(
                    block_id='compare-purchases-by-vendor',
                    title=title,
                    columns=columns,
                    rows=rows,
                ),
            )
        if p['include_chart'] and chart_labels:
            blocks.append(
                bar_chart_block(
                    block_id='compare-purchases-by-vendor-chart',
                    title=f'{SPEND_METRIC_LABEL} by vendor',
                    labels=chart_labels,
                    values=chart_values,
                    series_name=SPEND_METRIC_LABEL,
                )
            )
        if not blocks:
            blocks.append(
                table_block(
                    block_id='compare-purchases-by-vendor',
                    title=title,
                    columns=columns,
                    rows=rows,
                )
            )

        message = compare_vendors_message(
            vendor_count=len(rows),
            invoice_count=invoice_count,
            months=p['months'],
            date_from=p['date_from'],
            date_to=p['date_to'],
        )
        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=len(rows),
            invoice_count=invoice_count,
            partial=False,
        )

    def _totals_rows(
        self,
        top: list[dict[str, Any]],
    ) -> tuple[list[dict], list[dict], list[str], list[str]]:
        columns = [
            {'key': 'vendor', 'label': 'Vendor'},
            {'key': 'total', 'label': 'Total', 'format': 'currency'},
        ]
        rows: list[dict[str, Any]] = []
        chart_labels: list[str] = []
        chart_values: list[str] = []
        for row in top:
            vendor_id = row['builder_id']
            name = row['builder__name'] or f'Builder #{vendor_id or "none"}'
            total = coerce_money(row['total']) if row['total'] is not None else zero_money()
            rows.append({
                'vendor_id': vendor_id,
                'vendor': name,
                'total': as_money_str(total),
            })
            chart_labels.append(name)
            chart_values.append(as_money_str(total))
        return columns, rows, chart_labels, chart_values

    def _monthly_rows(
        self,
        *,
        qs,
        top: list[dict[str, Any]],
        date_from,
        date_to,
    ) -> tuple[list[dict], list[dict], list[str], list[str]]:
        month_meta = iter_month_labels(date_from, date_to)
        month_labels = [m[0] for m in month_meta]
        concrete_ids = [row['builder_id'] for row in top if row['builder_id'] is not None]
        include_null_builder = any(row['builder_id'] is None for row in top)

        monthly_map: dict[Any, dict[str, Decimal]] = defaultdict(dict)
        if concrete_ids:
            monthly_rows = (
                qs.filter(builder_id__in=concrete_ids)
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
        if include_null_builder:
            monthly_rows_null = (
                qs.filter(builder_id__isnull=True)
                .annotate(month=TruncMonth('date'))
                .values('month')
                .annotate(total=Sum('total_amount'))
            )
            for row in monthly_rows_null:
                if not row['month']:
                    continue
                label = row['month'].strftime('%Y-%m')
                monthly_map[None][label] = (
                    coerce_money(row['total']) if row['total'] is not None else zero_money()
                )

        columns = [
            {'key': 'vendor', 'label': 'Vendor'},
            *[{'key': label, 'label': label, 'format': 'currency'} for label in month_labels],
            {'key': 'total', 'label': 'Total', 'format': 'currency'},
        ]
        rows: list[dict[str, Any]] = []
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
            vendor_months = monthly_map.get(vendor_id, {})
            for label in month_labels:
                amount = vendor_months.get(label, zero_money())
                entry[label] = as_money_str(amount)
            rows.append(entry)
            chart_labels.append(name)
            chart_values.append(as_money_str(total))
        return columns, rows, chart_labels, chart_values
