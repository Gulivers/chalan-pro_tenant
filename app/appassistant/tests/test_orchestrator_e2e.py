"""
Orchestrator + query endpoint e2e (Increment C).

TenantTestCase fixtures mirror test_tools_spend (PINV spend only).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django_tenants.test.cases import TenantTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate

from appassistant.contracts.response import validate_response_payload
from appassistant.models import AssistantQueryLog
from appassistant.services.orchestrator import run_assistant_query
from appassistant.services.spend import SPEND_TYPE_CODE
from appassistant.tools.registry import reset_default_registry
from appassistant.views import AssistantQueryView
from apptransactions.models import Document, DocumentType
from ctrctsapp.models import Builder

User = get_user_model()


def _set_doc_date(doc: Document, d: date) -> None:
    Document.objects.filter(pk=doc.pk).update(date=d)
    doc.refresh_from_db()


@override_settings(TIME_ZONE='UTC', ASSISTANT_ENABLED=True)
class OrchestratorE2ETests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant Orchestrator E2E Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_orch_e2e'

    def setUp(self):
        super().setUp()
        reset_default_registry()
        self.factory = APIRequestFactory()
        self.view = AssistantQueryView.as_view()

        self.pinv, _ = DocumentType.objects.get_or_create(
            type_code=SPEND_TYPE_CODE,
            defaults={
                'description': 'Purchase Invoice',
                'is_purchase': True,
                'is_active': True,
            },
        )
        self.harbor = Builder.objects.create(name='Harbor Freight', supplier_rank=1)
        self.other = Builder.objects.create(name='Other Vendor', supplier_rank=1)

        self.user = User.objects.create_user(
            username='orch_user',
            email='orch@example.com',
            password='testpass123',
        )
        ct = ContentType.objects.get_for_model(Document)
        perm = Permission.objects.get(content_type=ct, codename='view_document')
        self.user.user_permissions.add(perm)
        self.user = User.objects.get(pk=self.user.pk)
        # appcore signal creates Token on user save; do not force-insert again.
        self.token, _ = Token.objects.get_or_create(user=self.user)

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

        old = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('300.00'),
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(old, date(2026, 6, 10))

    def _post(self, message: str, user=None):
        payload = {
            'schema_version': '1',
            'message': message,
            'context': {
                'view': 'transactions',
                'route_name': 'transactions',
                'entity_type': None,
                'entity_id': None,
            },
        }
        request = self.factory.post('/api/assistant/query/', payload, format='json')
        force_authenticate(request, user=user or self.user, token=self.token)
        return self.view(request)

    def _assert_valid(self, data):
        self.assertEqual(validate_response_payload(data), [])
        self.assertEqual(data['meta']['router'], 'deterministic')
        self.assertIn('PINV', data['context']['spend_definition'])

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case1_list_via_endpoint(self, _mock):
        response = self._post(
            'Show me Harbor Freight transactions over $1,500 this month.'
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        self._assert_valid(data)
        self.assertEqual(data['meta']['tools_executed'], ['list_purchase_transactions'])
        table = next(b for b in data['blocks'] if b['type'] == 'table')
        self.assertEqual(len(table['rows']), 1)
        self.assertEqual(table['rows'][0]['total_amount'], '2000.00')
        log = AssistantQueryLog.objects.latest('created_at')
        self.assertTrue(log.success)
        self.assertEqual(log.tool_name, 'list_purchase_transactions')
        self.assertEqual(log.params_safe.get('vendor'), 'Harbor Freight')
        self.assertEqual(log.params_safe.get('min_amount'), '1500.00')
        self.assertNotIn('message', log.params_safe)
        self.assertEqual(log.row_count, 1)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case2_sum_via_endpoint(self, _mock):
        response = self._post(
            'How much did we spend with Harbor Freight this month?'
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        self._assert_valid(data)
        self.assertEqual(data['meta']['tools_executed'], ['sum_purchase_spending'])
        kpi = next(b for b in data['blocks'] if b['type'] == 'kpi')
        self.assertEqual(kpi['value'], '2100.00')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case3_purchases_by_vendor(self, _mock):
        response = self._post('Show purchases by vendor this month.')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self._assert_valid(data)
        self.assertEqual(data['meta']['tools_executed'], ['purchases_by_vendor'])
        table = next(b for b in data['blocks'] if b['type'] == 'table')
        vendors = {r['vendor']: r['total_amount'] for r in table['rows']}
        self.assertEqual(vendors['Harbor Freight'], '2100.00')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case4_compare(self, _mock):
        response = self._post(
            'Compare purchases by supplier for the last six months.'
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        self._assert_valid(data)
        self.assertEqual(data['meta']['tools_executed'], ['compare_purchases_by_vendor'])
        types = {b['type'] for b in data['blocks']}
        self.assertIn('table', types)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case5_top_vendors(self, _mock):
        response = self._post('Show the five vendors with the highest spending.')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self._assert_valid(data)
        self.assertEqual(data['meta']['tools_executed'], ['top_vendors_by_spending'])
        log = AssistantQueryLog.objects.latest('created_at')
        self.assertEqual(log.params_safe.get('limit'), 5)
        self.assertEqual(log.params_safe.get('months'), 12)
        table = next(b for b in data['blocks'] if b['type'] == 'table')
        self.assertEqual(table['rows'][0]['vendor'], 'Harbor Freight')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case6_timeseries(self, _mock):
        response = self._post('Graph spending for the last three months.')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self._assert_valid(data)
        self.assertEqual(data['meta']['tools_executed'], ['spending_timeseries'])
        line = next(b for b in data['blocks'] if b['type'] == 'line_chart')
        self.assertEqual(len(line['labels']), 3)

    def test_unsupported_clarification(self):
        response = self._post('Tell me a joke about invoices.')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self._assert_valid(data)
        self.assertEqual(data['meta']['tools_executed'], [])
        self.assertTrue(any(b['type'] == 'text' for b in data['blocks']))
        self.assertIn('not supported', data['message'].lower())
        log = AssistantQueryLog.objects.latest('created_at')
        self.assertTrue(log.success)
        self.assertEqual(log.tool_name, '')
        self.assertNotIn('message', log.params_safe)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_tool_error_fail_closed_200(self, _mock):
        # Ambiguous vendor → tool error_code, still HTTP 200 with clarification.
        Builder.objects.create(name='Harbor Tools', supplier_rank=1)
        result = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor this month?',
            context={'view': 'transactions'},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, 'ambiguous_vendor')
        self.assertEqual(result.tool_name, 'sum_purchase_spending')
        self.assertEqual(validate_response_payload(result.payload), [])
        self.assertTrue(any(b['type'] == 'text' for b in result.payload['blocks']))

    @patch('appassistant.services.orchestrator.execute_tool', side_effect=RuntimeError('boom'))
    def test_unexpected_exception_fail_closed(self, _mock_exec):
        result = run_assistant_query(
            user=self.user,
            message='Show purchases by vendor this month.',
            context={'view': 'transactions'},
            request_id='22222222-2222-2222-2222-222222222222',
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, 'internal')
        self.assertEqual(result.row_count, 0)
        self.assertEqual(validate_response_payload(result.payload), [])
        self.assertTrue(any(b['type'] == 'text' for b in result.payload['blocks']))
        self.assertNotIn('boom', result.payload['message'])

    def test_permission_denied_403(self):
        naked = User.objects.create_user(username='noperm_orch', password='x')
        token, _ = Token.objects.get_or_create(user=naked)
        payload = {
            'schema_version': '1',
            'message': 'Show purchases by vendor this month.',
            'context': {},
        }
        request = self.factory.post('/api/assistant/query/', payload, format='json')
        force_authenticate(request, user=naked, token=token)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)
