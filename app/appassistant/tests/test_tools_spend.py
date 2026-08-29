"""
Spend tools unit tests (Increment B).

Spend = PINV + is_active only; NOT document_type__is_purchase.

Uses django-tenants TenantTestCase so Document/Builder tables exist in a
tenant schema. If shared migrate fails (e.g. historical appbilling.0003),
run the live-tenant smoke documented in the module docstring of
test_query_endpoint / coordinator notes.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, override_settings
from django_tenants.test.cases import TenantTestCase

from appassistant.contracts.response import validate_response_payload
from appassistant.services.money import as_money_str, coerce_money, zero_money
from appassistant.services.spend import SPEND_TYPE_CODE, spend_documents_qs
from appassistant.tools.errors import ToolError
from appassistant.tools.executor import execute_tool, execute_tool_strict
from appassistant.tools.registry import get_default_registry, reset_default_registry
from apptransactions.models import Document, DocumentType
from ctrctsapp.models import Builder

User = get_user_model()


def _set_doc_date(doc: Document, d: date) -> None:
    """Document.date uses auto_now_add; set explicitly for period tests."""
    Document.objects.filter(pk=doc.pk).update(date=d)
    doc.refresh_from_db()


class MoneyHelpersTests(SimpleTestCase):
    def test_as_money_str_never_float(self):
        s = as_money_str(Decimal('1500.5'))
        self.assertIsInstance(s, str)
        self.assertEqual(s, '1500.50')
        self.assertNotIsInstance(s, float)

    def test_coerce_rejects_float(self):
        with self.assertRaises(ValueError):
            coerce_money(1500.50)

    def test_zero_money(self):
        self.assertEqual(zero_money(), Decimal('0.00'))


@override_settings(TIME_ZONE='UTC')
class SpendToolsTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant Spend Test Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_spend'

    def setUp(self):
        super().setUp()
        reset_default_registry()
        self.pinv, _ = DocumentType.objects.get_or_create(
            type_code=SPEND_TYPE_CODE,
            defaults={
                'description': 'Purchase Invoice',
                'is_purchase': True,
                'is_active': True,
            },
        )
        # Purchase-flagged but NOT PINV — must never count as spend.
        self.grn, _ = DocumentType.objects.get_or_create(
            type_code='GRN_ASSIST_TEST',
            defaults={
                'description': 'Goods Receipt',
                'is_purchase': True,
                'is_active': True,
            },
        )
        self.harbor = Builder.objects.create(name='Harbor Freight', supplier_rank=1)
        self.other = Builder.objects.create(name='Other Vendor', supplier_rank=1)
        self.harbor2 = Builder.objects.create(name='Harbor Tools', supplier_rank=1)

        self.user = User.objects.create_user(
            username='spend_user',
            email='spend@example.com',
            password='testpass123',
        )
        ct = ContentType.objects.get_for_model(Document)
        perm = Permission.objects.get(content_type=ct, codename='view_document')
        self.user.user_permissions.add(perm)
        self.user = User.objects.get(pk=self.user.pk)

        self.today = date(2026, 7, 15)
        self.doc_harbor = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('2000.00'),
            notes='Harbor PINV',
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(self.doc_harbor, self.today)

        self.doc_small = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('100.00'),
            notes='Small',
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(self.doc_small, self.today)

        self.doc_other = Document.objects.create(
            document_type=self.pinv,
            builder=self.other,
            total_amount=Decimal('500.00'),
            notes='Other PINV',
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(self.doc_other, self.today)

        self.doc_grn = Document.objects.create(
            document_type=self.grn,
            builder=self.harbor,
            total_amount=Decimal('9999.00'),
            notes='GRN not spend',
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(self.doc_grn, self.today)

        self.doc_inactive = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('3000.00'),
            notes='Inactive',
            is_active=False,
            created_by=self.user,
        )
        _set_doc_date(self.doc_inactive, self.today)

    def _assert_no_floats(self, obj):
        if isinstance(obj, float):
            self.fail(f'Found float in payload: {obj}')
        if isinstance(obj, dict):
            for v in obj.values():
                self._assert_no_floats(v)
        elif isinstance(obj, list):
            for v in obj:
                self._assert_no_floats(v)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_spend_qs_only_pinv_active(self, _mock):
        ids = set(spend_documents_qs().values_list('id', flat=True))
        self.assertIn(self.doc_harbor.pk, ids)
        self.assertNotIn(self.doc_grn.pk, ids)
        self.assertNotIn(self.doc_inactive.pk, ids)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_list_purchase_transactions_min_amount(self, _mock):
        result = execute_tool_strict(
            'list_purchase_transactions',
            user=self.user,
            params={
                'vendor': 'Harbor Freight',
                'min_amount': '1500.00',
                'period': 'this_month',
                'limit': 20,
            },
        )
        self.assertEqual(result['row_count'], 1)
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        self.assertEqual(len(table['rows']), 1)
        self.assertEqual(table['rows'][0]['total_amount'], '2000.00')
        self.assertIsInstance(table['rows'][0]['total_amount'], str)
        links = [b for b in result['blocks'] if b['type'] == 'entity_link']
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['route_key'], 'transactions-form')
        self.assertEqual(
            links[0]['path'],
            f'/transactions/form?id={self.doc_harbor.pk}&mode=view',
        )
        self._assert_no_floats(result)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_sum_purchase_spending(self, _mock):
        result = execute_tool_strict(
            'sum_purchase_spending',
            user=self.user,
            params={'vendor': 'Harbor Freight', 'period': 'this_month'},
        )
        kpi = next(b for b in result['blocks'] if b['type'] == 'kpi')
        self.assertEqual(kpi['value'], '2100.00')
        self.assertEqual(kpi['format'], 'currency')
        self.assertIsInstance(kpi['value'], str)
        self._assert_no_floats(result)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_sum_purchase_spending_all_vendors(self, _mock):
        result = execute_tool_strict(
            'sum_purchase_spending',
            user=self.user,
            params={'period': 'this_month'},
        )
        kpi = next(b for b in result['blocks'] if b['type'] == 'kpi')
        # Harbor 2100 + Other Vendor 500
        self.assertEqual(kpi['value'], '2600.00')
        self.assertIn('this month', result['message'].lower())
        self.assertNotIn(' with ', result['message'])

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_purchases_by_vendor(self, _mock):
        result = execute_tool_strict(
            'purchases_by_vendor',
            user=self.user,
            params={'period': 'this_month', 'limit': 50},
        )
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        vendors = {r['vendor']: r['total_amount'] for r in table['rows']}
        self.assertEqual(vendors['Harbor Freight'], '2100.00')
        self.assertEqual(vendors['Other Vendor'], '500.00')
        chart = next(b for b in result['blocks'] if b['type'] == 'bar_chart')
        self.assertEqual(len(chart['labels']), len(chart['values']))

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_top_vendors_default_limit(self, _mock):
        result = execute_tool_strict(
            'top_vendors_by_spending',
            user=self.user,
            params={'period': 'this_month'},
        )
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        self.assertEqual(table['rows'][0]['vendor'], 'Harbor Freight')
        self.assertEqual(table['rows'][0]['total_amount'], '2100.00')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_spending_timeseries(self, _mock):
        old = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('300.00'),
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(old, date(2026, 6, 10))

        result = execute_tool_strict(
            'spending_timeseries',
            user=self.user,
            params={'months': 3, 'vendor': 'Harbor Freight'},
        )
        line = next(b for b in result['blocks'] if b['type'] == 'line_chart')
        self.assertEqual(len(line['labels']), 3)
        self.assertEqual(len(line['values']), 3)
        by_month = dict(zip(line['labels'], line['values']))
        self.assertEqual(by_month['2026-06'], '300.00')
        self.assertEqual(by_month['2026-07'], '2100.00')
        self._assert_no_floats(result)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_compare_purchases_by_vendor(self, _mock):
        result = execute_tool_strict(
            'compare_purchases_by_vendor',
            user=self.user,
            params={'months': 3, 'top_n': 5},
        )
        types = {b['type'] for b in result['blocks']}
        self.assertIn('table', types)
        self.assertIn('bar_chart', types)
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        # Classic months path keeps monthly breakdown columns.
        self.assertIn('2026-07', {c['key'] for c in table['columns']})

    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 2))
    def test_compare_purchases_by_vendor_explicit_short_range(self, _mock):
        """Last ~3 weeks via date_from/date_to: totals by vendor, no months required."""
        recent = Document.objects.create(
            document_type=self.pinv,
            builder=self.other,
            total_amount=Decimal('75.00'),
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(recent, date(2026, 7, 20))

        result = execute_tool_strict(
            'compare_purchases_by_vendor',
            user=self.user,
            params={
                'date_from': '2026-07-13',
                'date_to': '2026-08-02',
                'top_n': 10,
            },
        )
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        col_keys = {c['key'] for c in table['columns']}
        self.assertEqual(col_keys, {'vendor', 'total'})
        vendors = {r['vendor']: r['total'] for r in table['rows']}
        # Harbor 2000+100 on 2026-07-15; Other 500 (fixture) + 75 (recent).
        self.assertEqual(vendors['Harbor Freight'], '2100.00')
        self.assertEqual(vendors['Other Vendor'], '575.00')
        self.assertNotIn('months is required', result.get('message', '').lower())
        self.assertIn('2026-07-13', result['message'])
        self._assert_no_floats(result)

    def test_compare_purchases_by_vendor_requires_period_or_range(self):
        with self.assertRaises(ToolError) as ctx:
            execute_tool_strict(
                'compare_purchases_by_vendor',
                user=self.user,
                params={'top_n': 5},
            )
        self.assertEqual(ctx.exception.code, 'validation')
        self.assertIn('date_from', ctx.exception.message.lower())

    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 2))
    def test_compare_explicit_short_range_ignores_residual_months(self, _mock):
        """LLM may send months=1 with week-span dates; bounds win → totals only."""
        result = execute_tool_strict(
            'compare_purchases_by_vendor',
            user=self.user,
            params={
                'months': 1,
                'date_from': '2026-07-13',
                'date_to': '2026-08-02',
                'top_n': 10,
            },
        )
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        self.assertEqual({c['key'] for c in table['columns']}, {'vendor', 'total'})

    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 2))
    def test_compare_explicit_long_range_monthly_breakdown(self, _mock):
        """Explicit range ≥45 days without months still gets monthly columns."""
        result = execute_tool_strict(
            'compare_purchases_by_vendor',
            user=self.user,
            params={
                'date_from': '2026-05-01',
                'date_to': '2026-08-02',
                'top_n': 5,
            },
        )
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        col_keys = {c['key'] for c in table['columns']}
        self.assertIn('2026-07', col_keys)
        self.assertIn('total', col_keys)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_compare_null_builder_monthly_totals(self, _mock):
        """Unassigned builder rows must populate month columns, not only Total."""
        doc_null = Document.objects.create(
            document_type=self.pinv,
            builder=None,
            total_amount=Decimal('450.00'),
            notes='Unassigned PINV',
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(doc_null, self.today)

        result = execute_tool_strict(
            'compare_purchases_by_vendor',
            user=self.user,
            params={'months': 3, 'top_n': 10},
        )
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        null_rows = [r for r in table['rows'] if r.get('vendor_id') is None]
        self.assertEqual(len(null_rows), 1)
        self.assertEqual(null_rows[0]['total'], '450.00')
        self.assertEqual(null_rows[0]['2026-07'], '450.00')
        self._assert_no_floats(result)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_ambiguous_vendor(self, _mock):
        result = execute_tool(
            'sum_purchase_spending',
            user=self.user,
            params={'vendor': 'Harbor', 'period': 'this_month'},
        )
        self.assertEqual(result.get('error_code'), 'ambiguous_vendor')
        self.assertEqual(result['row_count'], 0)
        self.assertTrue(any(b['type'] == 'text' for b in result['blocks']))

    def test_limit_exceeded(self):
        with self.assertRaises(ToolError) as ctx:
            execute_tool_strict(
                'list_purchase_transactions',
                user=self.user,
                params={
                    'period': 'this_month',
                    'limit': 51,
                    'date_from': '2026-07-01',
                    'date_to': '2026-07-31',
                },
            )
        self.assertEqual(ctx.exception.code, 'validation')

    def test_empty_result(self):
        result = execute_tool_strict(
            'list_purchase_transactions',
            user=self.user,
            params={
                'vendor': 'Harbor Freight',
                'min_amount': '999999.00',
                'date_from': '2026-07-01',
                'date_to': '2026-07-31',
            },
        )
        self.assertEqual(result['row_count'], 0)
        table = next(b for b in result['blocks'] if b['type'] == 'table')
        self.assertEqual(table['rows'], [])

    def test_permission_denied(self):
        naked = User.objects.create_user(username='noperm', password='x')
        with self.assertRaises(ToolError) as ctx:
            execute_tool_strict(
                'list_purchase_transactions',
                user=naked,
                params={
                    'date_from': '2026-07-01',
                    'date_to': '2026-07-31',
                },
            )
        self.assertEqual(ctx.exception.code, 'permission')

    def test_registry_has_spend_tools(self):
        names = get_default_registry().names()
        self.assertEqual(
            names,
            [
                'compare_purchases_by_vendor',
                'compare_vendor_spending_periods',
                'list_purchase_transactions',
                'purchases_by_vendor',
                'spending_timeseries',
                'sum_purchase_spending',
                'top_vendors_by_spending',
            ],
        )

    def test_tool_result_wraps_into_valid_response_blocks(self):
        result = execute_tool_strict(
            'sum_purchase_spending',
            user=self.user,
            params={
                'vendor_id': self.harbor.pk,
                'date_from': '2026-07-01',
                'date_to': '2026-07-31',
            },
        )
        payload = {
            'schema_version': '1',
            'message': result['message'],
            'blocks': result['blocks'],
            'sources': result['sources'],
            'context': {},
            'meta': {'request_id': 'test-req', 'partial': result['partial']},
        }
        self.assertEqual(validate_response_payload(payload), [])
