"""C2 conversation continuity: inherit filters, start over, isolation."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase

from appassistant.contracts.response import validate_response_payload
from appassistant.models import AssistantConversation, AssistantQueryLog
from appassistant.services.orchestrator import run_assistant_query
from appassistant.services.spend import SPEND_TYPE_CODE
from appassistant.tools.registry import reset_default_registry
from apptransactions.models import Document, DocumentType
from ctrctsapp.models import Builder

User = get_user_model()


def _set_doc_date(doc: Document, d: date) -> None:
    Document.objects.filter(pk=doc.pk).update(date=d)
    doc.refresh_from_db()


@override_settings(TIME_ZONE='UTC', ASSISTANT_ENABLED=True)
class ConversationContinuityTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant Continuity Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_continuity'

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
        self.lowes = Builder.objects.create(name="Lowe's", supplier_rank=1)
        self.user = User.objects.create_user(username='cont_user', password='x')
        self.user_b = User.objects.create_user(username='cont_user_b', password='x')
        ct = ContentType.objects.get_for_model(Document)
        perm = Permission.objects.get(content_type=ct, codename='view_document')
        self.user.user_permissions.add(perm)
        self.user_b.user_permissions.add(perm)
        self.user = User.objects.get(pk=self.user.pk)
        self.user_b = User.objects.get(pk=self.user_b.pk)

        self.today = date(2026, 7, 15)
        doc = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('2000.00'),
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(doc, self.today)
        doc_june = Document.objects.create(
            document_type=self.pinv,
            builder=self.harbor,
            total_amount=Decimal('500.00'),
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(doc_june, date(2026, 6, 10))
        doc_lowes = Document.objects.create(
            document_type=self.pinv,
            builder=self.lowes,
            total_amount=Decimal('800.00'),
            is_active=True,
            created_by=self.user,
        )
        _set_doc_date(doc_lowes, self.today)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_response_includes_conversation_and_active_filters(self, _mock):
        result = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        self.assertTrue(result.success)
        self.assertTrue(result.conversation_id)
        self.assertEqual(validate_response_payload(result.payload), [])
        self.assertEqual(
            result.payload['meta']['conversation_id'],
            result.conversation_id,
        )
        chips = result.payload['context']['active_filters']['chips']
        labels = ' '.join(c['label'] for c in chips)
        self.assertIn('Harbor Freight', labels)
        self.assertIn('2026-07-01', labels)
        self.assertIn('2026-07-15', labels)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case1_inherit_vendor_replace_period(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        second = run_assistant_query(
            user=self.user,
            message='What about last month?',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertEqual(second.payload['meta']['router'], 'continuity')
        filters = second.payload['context']['active_filters']['filters']
        self.assertEqual(filters['vendor_ids'], [self.harbor.pk])
        self.assertEqual(filters['date_from'], '2026-06-01')
        self.assertEqual(filters['date_to'], '2026-06-30')
        kpi = next(b for b in second.payload['blocks'] if b['type'] == 'kpi')
        self.assertEqual(kpi['value'], '500.00')

    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 1))
    def test_paraphrase_previous_calendar_month(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='Show purchases by vendor this month.',
            context={},
            request_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        )
        second = run_assistant_query(
            user=self.user,
            message='and for the previous calendar month please?',
            context={},
            request_id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertIn(second.payload['meta']['router'], ('continuity', 'llm'))
        filters = second.payload['context']['active_filters']['filters']
        self.assertEqual(filters['date_from'], '2026-07-01')
        self.assertEqual(filters['date_to'], '2026-07-31')

        third = run_assistant_query(
            user=self.user,
            message='and for the two previous calendar months please?',
            context={},
            request_id='cccccccc-cccc-cccc-cccc-cccccccccccc',
            conversation_id=second.conversation_id,
        )
        self.assertTrue(third.success)
        filters3 = third.payload['context']['active_filters']['filters']
        self.assertEqual(filters3['date_from'], '2026-06-01')
        self.assertEqual(filters3['date_to'], '2026-07-31')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_chip_remove_vendor_follow_up(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='Show me Harbor Freight transactions over $100 this month.',
            context={},
            request_id='dddddddd-dddd-dddd-dddd-dddddddddddd',
        )
        self.assertTrue(first.success)
        second = run_assistant_query(
            user=self.user,
            message='Remove vendor Harbor Freight.',
            context={},
            request_id='eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        filters = second.payload['context']['active_filters']['filters']
        self.assertNotIn('vendor_ids', filters)
        self.assertEqual(filters.get('min_amount'), '100.00')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case3_add_min_amount_follow_up(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='Show me Harbor Freight transactions over $100 this month.',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        second = run_assistant_query(
            user=self.user,
            message='Only those over $1,500.',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertEqual(
            second.payload['context']['active_filters']['filters']['min_amount'],
            '1500.00',
        )
        self.assertEqual(second.tool_name, 'list_purchase_transactions')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case7_show_documents_keeps_filters(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        second = run_assistant_query(
            user=self.user,
            message='Show the documents.',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertEqual(second.tool_name, 'list_purchase_transactions')
        filters = second.payload['context']['active_filters']['filters']
        self.assertEqual(filters['vendor_ids'], [self.harbor.pk])
        self.assertEqual(filters['date_from'], '2026-07-01')
        self.assertEqual(filters['date_to'], '2026-07-15')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case13_start_over_clears_filters(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        reset = run_assistant_query(
            user=self.user,
            message='Start over.',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertNotEqual(reset.conversation_id, first.conversation_id)
        third = run_assistant_query(
            user=self.user,
            message='Show purchases by vendor this month.',
            context={},
            request_id='33333333-3333-3333-3333-333333333333',
            conversation_id=reset.conversation_id,
        )
        filters = third.payload['context']['active_filters']['filters']
        self.assertNotIn('vendor_ids', filters)

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_full_query_replaces_vendor_not_inherited(self, _mock):
        """Complete new list query is authoritative; do not keep prior vendor."""
        first = run_assistant_query(
            user=self.user,
            message='Show me Harbor Freight transactions over $100 this month.',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        self.assertTrue(first.success)
        self.assertEqual(
            first.payload['context']['active_filters']['filters']['vendor_ids'],
            [self.harbor.pk],
        )
        second = run_assistant_query(
            user=self.user,
            message="Show me Lowe's transactions over $100 this month.",
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        self.assertTrue(second.success)
        self.assertEqual(second.payload['meta']['router'], 'deterministic')
        filters = second.payload['context']['active_filters']['filters']
        self.assertEqual(filters['vendor_ids'], [self.lowes.pk])
        self.assertNotIn(self.harbor.pk, filters['vendor_ids'])

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_case11_user_isolation(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        other = run_assistant_query(
            user=self.user_b,
            message='What about last month?',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        # Other user must not inherit; treated as new conversation.
        self.assertNotEqual(other.conversation_id, first.conversation_id)
        self.assertNotEqual(other.payload['meta'].get('router'), 'continuity')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_expired_state_does_not_inherit(self, _mock):
        first = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        conv = AssistantConversation.objects.get(pk=first.conversation_id)
        conv.last_activity_at = timezone.now() - timedelta(hours=25)
        conv.save(update_fields=['last_activity_at'])
        second = run_assistant_query(
            user=self.user,
            message='What about last month?',
            context={},
            request_id='22222222-2222-2222-2222-222222222222',
            conversation_id=first.conversation_id,
        )
        # Follow-up without reusable state falls through to unsupported/new route.
        self.assertNotEqual(second.payload['meta'].get('router'), 'continuity')

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_rejects_client_supplied_state(self, _mock):
        from appassistant.contracts.request import AssistantRequestError, parse_assistant_request

        with self.assertRaises(AssistantRequestError):
            parse_assistant_request({
                'schema_version': '1',
                'message': 'Hello',
                'filters': {'vendor_ids': [1]},
            })

    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_audit_links_conversation(self, _mock):
        from appassistant.services.audit import log_assistant_query

        result = run_assistant_query(
            user=self.user,
            message='How much did we spend with Harbor Freight this month?',
            context={},
            request_id='11111111-1111-1111-1111-111111111111',
        )
        log_assistant_query(
            user=self.user,
            request_id=result.payload['meta']['request_id'],
            tool_name=result.tool_name,
            params_safe=result.params_safe,
            success=result.success,
            conversation=result.conversation_id,
            intent=result.intent,
            clarification=result.clarification,
        )
        log = AssistantQueryLog.objects.latest('created_at')
        self.assertEqual(str(log.conversation_id), result.conversation_id)
        self.assertTrue(log.intent)
