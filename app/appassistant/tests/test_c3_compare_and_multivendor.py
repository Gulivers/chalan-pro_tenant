"""C3: period comparison, multi-vendor, presentation flags."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django_tenants.test.cases import TenantTestCase

from appassistant.services.orchestrator import run_assistant_query
from appassistant.services.spend import SPEND_TYPE_CODE
from appassistant.tools.executor import execute_tool_strict
from appassistant.tools.registry import reset_default_registry
from apptransactions.models import Document, DocumentType
from ctrctsapp.models import Builder

User = get_user_model()


def _set_doc_date(doc: Document, d: date) -> None:
    Document.objects.filter(pk=doc.pk).update(date=d)
    doc.refresh_from_db()


@override_settings(
    TIME_ZONE='UTC',
    ASSISTANT_ENABLED=True,
    ASSISTANT_LLM_PRIMARY=False,
)
class C3CompareAndMultiVendorTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant C3 Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_c3'

    def setUp(self):
        super().setUp()
        # TenantTestCase ignores class-level @override_settings for custom flags.
        self._llm_primary_ctx = self.settings(ASSISTANT_LLM_PRIMARY=False)
        self._llm_primary_ctx.enable()
        self.addCleanup(self._llm_primary_ctx.disable)
        reset_default_registry()
        self.pinv, _ = DocumentType.objects.get_or_create(
            type_code=SPEND_TYPE_CODE,
            defaults={
                'description': 'Purchase Invoice',
                'is_purchase': True,
                'is_active': True,
            },
        )
        self.harbor = Builder.objects.create(name='Harbor Freight', supplier_rank=1)
        self.lowes = Builder.objects.create(name="Lowe's", supplier_rank=1)
        self.user = User.objects.create_user(username='c3_user', password='x')
        ct = ContentType.objects.get_for_model(Document)
        perm = Permission.objects.get(content_type=ct, codename='view_document')
        self.user.user_permissions.add(perm)
        self.user = User.objects.get(pk=self.user.pk)

        self.today = date(2026, 7, 15)
        for amount, day, builder in (
            (Decimal('2000.00'), self.today, self.harbor),
            (Decimal('500.00'), date(2026, 6, 10), self.harbor),
            (Decimal('800.00'), self.today, self.lowes),
            (Decimal('100.00'), date(2026, 6, 5), self.lowes),
        ):
            doc = Document.objects.create(
                document_type=self.pinv,
                builder=builder,
                total_amount=amount,
                is_active=True,
                created_by=self.user,
            )
            _set_doc_date(doc, day)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case2_compare_with_last_month(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        second = run_assistant_query(
            user=self.user,
            message='Compare it with last month.',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertEqual(second.tool_name, 'compare_vendor_spending_periods')
        types = {b['type'] for b in second.payload['blocks']}
        self.assertIn('kpi', types)
        self.assertIn('table', types)
        primary = next(
            b for b in second.payload['blocks']
            if b.get('id') == 'primary-period-spending'
        )
        compared = next(
            b for b in second.payload['blocks']
            if b.get('id') == 'comparison-period-spending'
        )
        diff = next(
            b for b in second.payload['blocks']
            if b.get('id') == 'period-difference'
        )
        self.assertEqual(primary['value'], '2000.00')
        self.assertEqual(compared['value'], '500.00')
        self.assertEqual(diff['value'], '1500.00')
        # 1500/500*100 = 300.00
        self.assertIn('300.00%', diff['subtitle'])

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_compare_zero_base_percent_na(self, _mock):
        result = execute_tool_strict(
            'compare_vendor_spending_periods',
            user=self.user,
            params={
                'vendor_id': self.harbor.pk,
                'date_from': '2026-07-01',
                'date_to': '2026-07-15',
                'comparison_period': {
                    'period_label': 'empty',
                    'date_from': '2026-01-01',
                    'date_to': '2026-01-31',
                },
            },
        )
        diff = next(b for b in result['blocks'] if b.get('id') == 'period-difference')
        self.assertIn('n/a', diff['subtitle'].lower())
        self.assertTrue(any(b.get('id') == 'period-pct-note' for b in result['blocks']))

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case5_include_another_vendor(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='Show me Harbor Freight transactions over $100 this month.',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        second = run_assistant_query(
            user=self.user,
            message="Include Lowe's too.",
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        vendor_ids = second.payload['context']['active_filters']['filters']['vendor_ids']
        self.assertEqual(sorted(vendor_ids), sorted([self.harbor.pk, self.lowes.pk]))
        self.assertEqual(second.tool_name, 'list_purchase_transactions')
        self.assertGreaterEqual(second.row_count, 2)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case8_presentation_graph_then_table(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='Compare purchases by supplier for the last six months.',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        self.assertTrue(first.success)
        graph = run_assistant_query(
            user=self.user,
            message='Graph it.',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(graph.success)
        g_types = {b['type'] for b in graph.payload['blocks']}
        self.assertIn('bar_chart', g_types)
        self.assertNotIn('table', g_types)

        table = run_assistant_query(
            user=self.user,
            message='Show it as a table instead.',
            context={},
            request_id='33333333-3333-3333-3333-333333333333',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(table.success)
        t_types = {b['type'] for b in table.payload['blocks']}
        self.assertIn('table', t_types)
        self.assertNotIn('bar_chart', t_types)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_multi_vendor_sum(self, _mock):
        result = execute_tool_strict(
            'sum_purchase_spending',
            user=self.user,
            params={
                'vendor_ids': [self.harbor.pk, self.lowes.pk],
                'period': 'this_month',
            },
        )
        kpi = next(b for b in result['blocks'] if b['type'] == 'kpi')
        self.assertEqual(kpi['value'], '2800.00')
