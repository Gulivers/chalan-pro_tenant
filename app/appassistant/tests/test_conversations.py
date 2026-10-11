"""Conversation load / isolation tests (Increment C1)."""

from __future__ import annotations

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase

from appassistant.models import AssistantConversation
from appassistant.services.conversation_state import empty_state
from appassistant.services.conversations import (
    conversation_allows_inheritance,
    create_conversation_for_user,
    get_conversation_for_user,
    get_reusable_state,
)

User = get_user_model()


class ConversationIsolationTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant Conversation Test Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_conversation'

    def setUp(self):
        super().setUp()
        self.user_a = User.objects.create_user(username='conv_a', password='x')
        self.user_b = User.objects.create_user(username='conv_b', password='x')

    def test_cannot_load_other_users_conversation(self):
        conv = create_conversation_for_user(self.user_a)
        self.assertIsNotNone(get_conversation_for_user(self.user_a, conv.id))
        self.assertIsNone(get_conversation_for_user(self.user_b, conv.id))
        self.assertIsNone(get_conversation_for_user(self.user_a, uuid.uuid4()))

    def test_expired_state_not_reusable(self):
        conv = create_conversation_for_user(self.user_a)
        conv.state = empty_state()
        conv.state['filters'] = {
            'vendor_ids': [1],
            'vendors': [{'id': 1, 'name': 'X'}],
        }
        conv.last_activity_at = timezone.now() - timedelta(hours=25)
        conv.save()
        self.assertFalse(conversation_allows_inheritance(conv))
        state, expired = get_reusable_state(conv)
        self.assertTrue(expired)
        self.assertEqual(state['filters'], {})

    def test_create_sets_schema_and_empty_state(self):
        conv = create_conversation_for_user(self.user_a)
        self.assertTrue(AssistantConversation.objects.filter(pk=conv.pk).exists())
        self.assertEqual(conv.turn_count, 0)
        self.assertEqual(conv.state.get('filters'), {})
        self.assertTrue(conv.schema_name)
