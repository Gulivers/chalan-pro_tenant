"""Closures from the JWT security review: anonymous reads, tickets, note HTML."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import signing
from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase, override_settings
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.test import APIClient

from appauth.services.password_reset import frontend_base_url_for_password_reset
from appauth.testing import authenticate_api_client
from appauth.ws_tickets import consume_ws_ticket, issue_ws_ticket
from appschedule.note_html import sanitize_note_html
from appschedule.ws_groups import tenant_ws_group

User = get_user_model()


def tenant_api_client(tenant) -> APIClient:
    client = APIClient()
    domain = tenant.get_primary_domain().domain
    client.defaults['HTTP_HOST'] = domain
    return client


def grant(user, *codenames):
    perms = Permission.objects.filter(codename__in=codenames)
    user.user_permissions.add(*perms)
    return User.objects.get(pk=user.pk)


class NoteHtmlTests(SimpleTestCase):
    def test_strips_script_and_handlers(self):
        raw = '<p onclick="alert(1)">ok</p><script>alert(1)</script><img src=x onerror="alert(1)">'
        clean = sanitize_note_html(raw)
        self.assertIn('<p>ok</p>', clean)
        self.assertNotIn('script', clean.lower())
        self.assertNotIn('onerror', clean.lower())
        self.assertNotIn('onclick', clean.lower())

    def test_drops_javascript_href(self):
        clean = sanitize_note_html('<a href="javascript:alert(1)">x</a>')
        self.assertNotIn('javascript:', clean.lower())
        self.assertIn('x', clean)


class SecurityHardeningTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Security Hardening Tenant'
        tenant.email = 'owner@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_security_hardening'

    def setUp(self):
        super().setUp()
        cache.clear()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='secuser',
            email='secuser@example.com',
            password='ValidPass123!',
        )

    def test_anonymous_reads_are_rejected(self):
        for url in (
            '/api/contract/contracts-provider/',
            '/api/builders/',
            '/api/house_models/1/jobs/',
            '/api/documents-provider/',
            '/api/crews/',
        ):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, url)

    def test_contracts_provider_requires_view_contract(self):
        authenticate_api_client(self.client, self.user)
        denied = self.client.get('/api/contract/contracts-provider/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_contract')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get('/api/contract/contracts-provider/?per_page=9999')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertIn('items', allowed.data)
        self.assertNotIn('Traceback', str(allowed.data))

    def test_builders_and_house_jobs_need_login_only(self):
        authenticate_api_client(self.client, self.user)
        builders = self.client.get('/api/builders/')
        self.assertEqual(builders.status_code, status.HTTP_200_OK)
        missing = self.client.get('/api/house_models/1/jobs/')
        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)

    def test_documents_provider_requires_view_document(self):
        authenticate_api_client(self.client, self.user)
        denied = self.client.get('/api/documents-provider/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_document')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get('/api/documents-provider/')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    def test_crew_reads_stay_open_and_writes_need_permission(self):
        authenticate_api_client(self.client, self.user)
        listing = self.client.get('/api/crews/')
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        created = self.client.post('/api/crews/', {'name': 'Night crew'}, format='json')
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)

    def test_ws_ticket_is_one_time_and_requires_jwt(self):
        anonymous = self.client.post('/api/auth/ws-ticket/')
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

        authenticate_api_client(self.client, self.user)
        issued = self.client.post('/api/auth/ws-ticket/')
        self.assertEqual(issued.status_code, status.HTTP_200_OK)
        ticket = issued.data['ticket']
        uid, schema = consume_ws_ticket(ticket)
        self.assertEqual(uid, self.user.pk)
        self.assertEqual(schema, self.get_test_schema_name())
        with self.assertRaises(signing.BadSignature):
            consume_ws_ticket(ticket)

    def test_issue_ws_ticket_round_trip(self):
        ticket = issue_ws_ticket(self.user)
        uid, schema = consume_ws_ticket(ticket)
        self.assertEqual(uid, self.user.pk)
        self.assertEqual(schema, self.get_test_schema_name())

    def test_public_tenant_context_hides_schema_name(self):
        response = self.client.get('/api/auth/tenant-context/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('schema_name', response.data)

    def test_ws_group_is_prefixed_with_schema(self):
        self.assertEqual(
            tenant_ws_group('calendar_updates'),
            f'{self.get_test_schema_name()}.calendar_updates',
        )

    def test_reset_link_ignores_forwarded_host(self):
        host = self.tenant.get_primary_domain().domain
        request = RequestFactory().get(
            '/',
            HTTP_HOST=host,
            HTTP_X_FORWARDED_HOST='evil.example',
        )
        url = frontend_base_url_for_password_reset(request)
        self.assertIn(host, url)
        self.assertNotIn('evil.example', url)

    def test_cookie_refresh_ignores_body_and_keeps_cookie_on_failure(self):
        with override_settings(AUTH_USE_REFRESH_COOKIE=True, DEBUG=True):
            login = self.client.post(
                '/api/auth/login/',
                {'username': 'secuser', 'password': 'ValidPass123!'},
                format='json',
                HTTP_SEC_FETCH_SITE='same-origin',
            )
            self.assertEqual(login.status_code, status.HTTP_200_OK)
            old_cookie = self.client.cookies['jr_refresh'].value

            rotated = self.client.post(
                '/api/auth/refresh/',
                {'refresh': 'ignore-this-body'},
                format='json',
                HTTP_SEC_FETCH_SITE='same-origin',
            )
            self.assertEqual(rotated.status_code, status.HTTP_200_OK)
            self.assertNotEqual(self.client.cookies['jr_refresh'].value, old_cookie)

            stale = tenant_api_client(self.tenant)
            stale.cookies['jr_refresh'] = old_cookie
            failed = stale.post(
                '/api/auth/refresh/',
                format='json',
                HTTP_SEC_FETCH_SITE='same-origin',
            )
            self.assertEqual(failed.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertNotIn('jr_refresh', failed.cookies)

            cross = tenant_api_client(self.tenant)
            cross.cookies['jr_refresh'] = self.client.cookies['jr_refresh'].value
            denied = cross.post(
                '/api/auth/refresh/',
                format='json',
                HTTP_ORIGIN='https://evil.example',
            )
            self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

            host = self.tenant.get_primary_domain().domain
            other_port = tenant_api_client(self.tenant)
            other_port.cookies['jr_refresh'] = self.client.cookies['jr_refresh'].value
            opened = other_port.post(
                '/api/auth/refresh/',
                format='json',
                HTTP_ORIGIN=f'http://{host}:8080',
            )
            self.assertNotEqual(opened.status_code, status.HTTP_403_FORBIDDEN)
