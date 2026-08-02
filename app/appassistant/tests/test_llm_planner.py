"""C4 LLM planner: sanitize, ignore forged IDs, orchestrator wiring (mocked)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, override_settings
from django_tenants.test.cases import TenantTestCase

from appassistant.services.llm_planner import (
    _sanitize_plan,
    build_new_query_params_from_llm,
    llm_planner_enabled,
)
from appassistant.services.orchestrator import run_assistant_query
from appassistant.services.spend import SPEND_TYPE_CODE
from appassistant.tools.registry import reset_default_registry
from apptransactions.models import Document, DocumentType
from ctrctsapp.models import Builder

User = get_user_model()


def _set_doc_date(doc: Document, d: date) -> None:
    Document.objects.filter(pk=doc.pk).update(date=d)
    doc.refresh_from_db()


class LLMSanitizeTests(SimpleTestCase):
    def test_strips_vendor_id_from_params(self):
        plan = _sanitize_plan(
            {
                'intent': 'sum',
                'is_new_query': True,
                'tool': 'sum_purchase_spending',
                'params': {
                    'vendor': 'Home Depot',
                    'vendor_id': 99999,
                    'period': 'this_month',
                },
                'filter_operations': [],
            },
            model='gpt-4.1-mini',
        )
        self.assertTrue(plan.ok)
        self.assertEqual(plan.params.get('vendor'), 'Home Depot')
        self.assertNotIn('vendor_id', plan.params)
        self.assertEqual(plan.tool, 'sum_purchase_spending')

    def test_rejects_unknown_tool(self):
        plan = _sanitize_plan(
            {
                'intent': 'hack',
                'is_new_query': True,
                'tool': 'drop_database',
                'params': {},
            },
            model='gpt-4.1-mini',
        )
        self.assertTrue(plan.ok)
        self.assertIsNone(plan.tool)
        self.assertTrue(plan.needs_clarification)

    def test_period_label_normalized_in_operations(self):
        with patch(
            'appassistant.services.llm_planner.resolved_period_value',
            return_value={
                'period_label': 'last_month',
                'date_from': '2026-06-01',
                'date_to': '2026-06-30',
                'timezone': 'UTC',
            },
        ):
            plan = _sanitize_plan(
                {
                    'intent': 'replace_period',
                    'is_new_query': False,
                    'tool': 'sum_purchase_spending',
                    'filter_operations': [
                        {
                            'field': 'period',
                            'operation': 'replace_period',
                            'value': 'last_month',
                        }
                    ],
                },
                model='gpt-4.1-mini',
            )
        self.assertTrue(plan.ok)
        self.assertEqual(len(plan.operations), 1)
        self.assertEqual(plan.operations[0].value['date_from'], '2026-06-01')


@override_settings(
    TIME_ZONE='UTC',
    ASSISTANT_ENABLED=True,
    ASSISTANT_LLM_ENABLED=False,
)
class LLMDisabledFallbackTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant LLM Disabled Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_llm_off'

    def setUp(self):
        super().setUp()
        reset_default_registry()
        self.user = User.objects.create_user(username='llm_off', password='x')
        ct = ContentType.objects.get_for_model(Document)
        perm = Permission.objects.get(content_type=ct, codename='view_document')
        self.user.user_permissions.add(perm)
        self.user = User.objects.get(pk=self.user.pk)

    def test_llm_disabled_flag(self):
        with self.settings(ASSISTANT_LLM_ENABLED=False):
            self.assertFalse(llm_planner_enabled())

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_continuity_still_works_when_llm_off(self, _mock):
        # No fixtures needed for unsupported follow-up path after empty state.
        result = run_assistant_query(
            user=self.user,
            message='What about last month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        # Without prior state, continuity does not inherit; unsupported/clarify ok.
        self.assertTrue(result.conversation_id)


@override_settings(
    TIME_ZONE='UTC',
    ASSISTANT_ENABLED=True,
    ASSISTANT_LLM_ENABLED=True,
    OPENAI_API_KEY='sk-test-not-real',
    ASSISTANT_LLM_MODEL='gpt-4.1-mini',
)
class LLMOrchestratorTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant LLM On Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_llm_on'

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
        self.harbor = Builder.objects.create(name='Harbor Freight', supplier_rank=1)
        self.user = User.objects.create_user(username='llm_on', password='x')
        ct = ContentType.objects.get_for_model(Document)
        perm = Permission.objects.get(content_type=ct, codename='view_document')
        self.user.user_permissions.add(perm)
        self.user = User.objects.get(pk=self.user.pk)
        doc = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('900.00'),
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(doc, date(2026, 7, 10))

    def test_llm_enabled_with_key(self):
        from django.conf import settings as dj_settings

        self.assertTrue(dj_settings.ASSISTANT_LLM_ENABLED)
        self.assertTrue(bool(dj_settings.OPENAI_API_KEY))
        self.assertTrue(llm_planner_enabled())

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    @patch('appassistant.services.orchestrator.llm_planner_enabled', return_value=True)
    @patch('appassistant.services.orchestrator.plan_with_llm')
    def test_llm_follow_up_replace_period(self, mock_plan, _enabled, _mock_today):
        from appassistant.services.filter_merger import FilterOperation
        from appassistant.services.llm_planner import LLMPlan

        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        self.assertEqual(first.payload['meta']['router'], 'deterministic')

        mock_plan.return_value = LLMPlan(
            ok=True,
            intent='replace_period',
            is_new_query=False,
            tool='sum_purchase_spending',
            operations=[
                FilterOperation(
                    field='period',
                    operation='replace_period',
                    value={
                        'period_label': 'last_month',
                        'date_from': '2026-06-01',
                        'date_to': '2026-06-30',
                        'timezone': 'UTC',
                    },
                )
            ],
            model='gpt-4.1-mini',
            audit={'intent': 'replace_period'},
        )
        second = run_assistant_query(
            user=self.user,
            message='and for the previous calendar month please?',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertEqual(second.payload['meta']['router'], 'llm')
        self.assertEqual(
            second.payload['context']['active_filters']['filters']['date_from'],
            '2026-06-01',
        )
        self.assertEqual(
            second.payload['context']['active_filters']['filters']['vendor_ids'],
            [self.harbor.pk],
        )

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    @patch('appassistant.services.orchestrator.llm_planner_enabled', return_value=True)
    @patch('appassistant.services.orchestrator.plan_with_llm')
    def test_llm_failure_falls_back_to_continuity(self, mock_plan, _enabled, _mock_today):
        from appassistant.services.llm_planner import LLMPlan

        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        mock_plan.return_value = LLMPlan(ok=False, error='llm_call_failed')
        second = run_assistant_query(
            user=self.user,
            message='What about last month?',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertEqual(second.payload['meta']['router'], 'continuity')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_build_new_query_resolves_vendor_name(self, _mock):
        from appassistant.services.llm_planner import LLMPlan

        plan = LLMPlan(
            ok=True,
            is_new_query=True,
            tool='sum_purchase_spending',
            params={'vendor': 'Harbor Freight', 'period': 'this_month'},
        )
        params = build_new_query_params_from_llm(plan)
        self.assertEqual(params['vendor_id'], self.harbor.pk)
        self.assertEqual(params['period'], 'this_month')
