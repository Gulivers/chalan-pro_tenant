"""
Endpoint tests for POST /api/assistant/query/.

Uses APIRequestFactory + the view directly so we do not depend on
PUBLIC_SCHEMA_URLCONF (assistant is tenant-only via project.urls).

TenantTestCase is required because AssistantQueryLog lives in TENANT_APPS.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import override_settings
from django_tenants.test.cases import TenantTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate

from appassistant.models import AssistantQueryLog
from appassistant.views import AssistantQueryView
from apptransactions.models import Document

User = get_user_model()


class AssistantQueryEndpointTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant Query Endpoint Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_query_ep'

    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.view = AssistantQueryView.as_view()
        self.user = User.objects.create_user(
            username='assistant_user',
            email='assistant@example.com',
            password='testpass123',
        )
        # appcore signal creates Token on user save; do not force-insert again.
        self.token, _ = Token.objects.get_or_create(user=self.user)
        # Unsupported message avoids Document spend queries in this gate suite.
        self.payload = {
            'schema_version': '1',
            'message': 'Tell me something unsupported about spend.',
            'context': {
                'view': 'transactions',
                'route_name': 'transactions',
                'entity_type': None,
                'entity_id': None,
            },
        }
        self.schema_name = getattr(connection, 'schema_name', None) or 'public'

    def _grant_view_document(self, user):
        ct = ContentType.objects.get_for_model(Document)
        perm = Permission.objects.get(content_type=ct, codename='view_document')
        user.user_permissions.add(perm)
        return User.objects.get(pk=user.pk)

    def _post(self, payload, user=None):
        request = self.factory.post('/api/assistant/query/', payload, format='json')
        if user is None:
            force_authenticate(request, user=AnonymousUser())
        else:
            force_authenticate(request, user=user, token=getattr(user, 'auth_token', None))
        return self.view(request)

    def test_unauthenticated_returns_401(self):
        request = self.factory.post('/api/assistant/query/', self.payload, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, 401)

    def test_authenticated_without_permission_returns_403(self):
        response = self._post(self.payload, user=self.user)
        self.assertEqual(response.status_code, 403)

    @override_settings(ASSISTANT_ENABLED=True)
    def test_authenticated_with_permission_returns_200(self):
        self.user = self._grant_view_document(self.user)
        response = self._post(self.payload, user=self.user)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['schema_version'], '1')
        self.assertEqual(data['meta']['router'], 'deterministic')
        self.assertEqual(data['meta']['tools_executed'], [])
        self.assertTrue(data['meta']['request_id'])
        self.assertIn('PINV', data['context']['spend_definition'])
        self.assertTrue(any(b.get('type') == 'text' for b in data['blocks']))
        self.assertIn('not supported', data['message'].lower())
        self.assertEqual(AssistantQueryLog.objects.count(), 1)
        log = AssistantQueryLog.objects.get()
        self.assertTrue(log.success)
        self.assertEqual(log.tool_name, '')
        self.assertEqual(log.params_safe.get('view'), 'transactions')
        self.assertEqual(log.params_safe.get('message_len'), len(self.payload['message']))
        self.assertNotIn('message', log.params_safe)

    @override_settings(ASSISTANT_ENABLED=True)
    def test_invalid_payload_returns_400(self):
        self.user = self._grant_view_document(self.user)
        response = self._post({'schema_version': '1', 'message': ''}, user=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(AssistantQueryLog.objects.filter(success=False).count(), 1)

    @override_settings(ASSISTANT_ENABLED=True)
    def test_ignores_tenant_id_in_body(self):
        self.user = self._grant_view_document(self.user)
        payload = {
            **self.payload,
            'context': {
                **self.payload['context'],
                'tenant_id': 'should-be-ignored',
                'user_id': 99999,
            },
        }
        response = self._post(payload, user=self.user)
        self.assertEqual(response.status_code, 200)
        ctx = response.data['context']
        self.assertNotIn('tenant_id', ctx)
        self.assertNotIn('user_id', ctx)

    @override_settings(ASSISTANT_ENABLED=False)
    def test_disabled_returns_503(self):
        self.user = self._grant_view_document(self.user)
        response = self._post(self.payload, user=self.user)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data.get('code'), 'assistant_disabled')
        self.assertEqual(
            AssistantQueryLog.objects.filter(error_code='assistant_disabled').count(),
            1,
        )
