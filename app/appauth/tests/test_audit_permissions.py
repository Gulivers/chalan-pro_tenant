# -*- coding: utf-8 -*-
"""Permission and media closures from the priority security audit."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from appauth.testing import authenticate_api_client
from appschedule.models import Event, EventNote
from crewsapp.models import Crew
from project.media_access import build_signed_media_url, sign_media_path
from tenants.services.onboarding_provision import OnboardingProvisionError
from tenants.throttles import LandingContactIPThrottle

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


class AuditPermissionTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Audit Permissions Tenant'
        tenant.email = 'audit-owner@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_audit_permissions'

    def setUp(self):
        super().setUp()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='audituser',
            email='audituser@example.com',
            password='ValidPass123!',
        )

    def test_products_options_requires_view_product(self):
        authenticate_api_client(self.client, self.user)
        denied = self.client.get('/api/products/options/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_product')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get('/api/products/options/')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    def test_purchase_cost_requires_view_product(self):
        from appinventory.models import Product, ProductCategory, UnitCategory, UnitOfMeasure

        unit_cat = UnitCategory.objects.create(name='Count')
        unit = UnitOfMeasure.objects.create(
            name='Each', code='EA', category=unit_cat, reference_unit=True
        )
        category = ProductCategory.objects.create(name='Cat')
        product = Product.objects.create(
            name='Widget', sku='W-1', category=category, unit_default=unit, is_active=True
        )

        authenticate_api_client(self.client, self.user)
        denied = self.client.get(f'/api/products/{product.id}/purchase-cost/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_product')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get(f'/api/products/{product.id}/purchase-cost/')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    def test_customers_export_requires_view_document(self):
        authenticate_api_client(self.client, self.user)
        denied = self.client.get('/api/export/customers-list/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_document')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get('/api/export/customers-list/')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertNotIn(b'Traceback', allowed.content)

    def test_document_pdf_requires_view_document(self):
        authenticate_api_client(self.client, self.user)
        denied = self.client.get('/api/documents/1/pdf/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_document')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get('/api/documents/1/pdf/')
        self.assertIn(
            allowed.status_code,
            (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
        )

    def test_contract_pdf_requires_view_contract(self):
        authenticate_api_client(self.client, self.user)
        denied = self.client.get('/api/contract-pdf/1/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_contract')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get('/api/contract-pdf/1/')
        self.assertIn(
            allowed.status_code,
            (status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
        )

    def test_event_note_requires_view_eventnote(self):
        crew = Crew.objects.create(name='Crew A')
        event = Event.objects.create(
            title='Job',
            crew=crew,
            date='2026-01-15',
            end_dt='2026-01-15',
            created_by=self.user,
        )
        EventNote.objects.create(event=event, notes='secret', work_account=None)

        authenticate_api_client(self.client, self.user)
        denied = self.client.get(f'/api/events/{event.id}/note/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_eventnote')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get(f'/api/events/{event.id}/note/')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    def test_event_chat_requires_view_eventchatmessage(self):
        crew = Crew.objects.create(name='Crew Chat')
        event = Event.objects.create(
            title='Chat Job',
            crew=crew,
            date='2026-01-16',
            end_dt='2026-01-16',
            created_by=self.user,
        )

        authenticate_api_client(self.client, self.user)
        denied = self.client.get(f'/api/events/{event.id}/chat/messages/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        reader = grant(self.user, 'view_eventchatmessage')
        authenticate_api_client(self.client, reader)
        allowed = self.client.get(f'/api/events/{event.id}/chat/messages/')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    def test_unsigned_media_is_not_served(self):
        rel = 'contract/audit_probe.txt'
        default_storage.save(rel, ContentFile(b'secret-bytes'))
        try:
            denied = self.client.get(f'/media/{rel}')
            self.assertEqual(denied.status_code, status.HTTP_404_NOT_FOUND)

            token = sign_media_path(rel)
            allowed = self.client.get(f'/media/s/{token}/')
            self.assertEqual(allowed.status_code, status.HTTP_200_OK)
            body = b''.join(allowed.streaming_content)
            self.assertEqual(body, b'secret-bytes')
            self.assertEqual(allowed.get('X-Content-Type-Options'), 'nosniff')
        finally:
            if default_storage.exists(rel):
                default_storage.delete(rel)

    def test_signed_url_helper_embeds_path(self):
        url = build_signed_media_url(None, 'event_images/work_account_1/x.png')
        self.assertTrue(url.startswith('/media/s/'))


LANDING_CONTACT_THROTTLE = {
    'REST_FRAMEWORK': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'appauth.authentication.TenantJWTAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'landing_contact_ip': '2/minute',
        },
    },
}


@override_settings(
    **LANDING_CONTACT_THROTTLE,
    DEBUG=True,
    TURNSTILE_SECRET_KEY='',
    EMAIL_HOST_PASSWORD='smtp-pass',
    LANDING_CONTACT_TO_EMAIL='ops@example.com',
    DEFAULT_FROM_EMAIL='noreply@example.com',
)
class LandingContactSecurityTests(APITestCase):
    def setUp(self):
        cache.clear()
        LandingContactIPThrottle.rate = '2/minute'
        self.client = APIClient()
        self.url = '/api/landing/contact/'
        self.payload = {
            'name': 'Ada',
            'email': 'ada@example.com',
            'phone': '(555) 123-4567',
            'subject': 'demo',
            'message': 'Hello from the field.',
            'locale': 'en',
        }

    def tearDown(self):
        LandingContactIPThrottle.rate = None
        cache.clear()

    @override_settings(DEBUG=False, TURNSTILE_SECRET_KEY='test-secret')
    def test_contact_without_turnstile_token_is_400(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success', True))

    def test_contact_throttle_returns_429(self):
        with patch('tenants.views.EmailMultiAlternatives') as mail_cls:
            mail_cls.return_value.send.return_value = 1
            first = self.client.post(self.url, self.payload, format='json')
            second = self.client.post(self.url, self.payload, format='json')
            third = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(third.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class OnboardingProvisionMessageTests(SimpleTestCase):
    def test_provision_error_exposes_fixed_message_only(self):
        err = OnboardingProvisionError(
            'Could not create tenant.',
            status_code=400,
            details='Traceback (most recent call last):\n  File secret.py',
        )
        self.assertEqual(str(err), 'Could not create tenant.')
        self.assertEqual(err.message, 'Could not create tenant.')
        self.assertIn('Traceback', err.details)


@override_settings(DEBUG=False)
class OnboardingVerifyLeakTests(APITestCase):
    def test_verify_view_omits_details_when_not_debug(self):
        err = OnboardingProvisionError(
            'Could not create domain.',
            status_code=500,
            details='INTERNAL_SCHEMA_TRACE',
        )
        with patch(
            'tenants.views.complete_pending_registration',
            side_effect=err,
        ):
            response = self.client.post(
                '/api/onboarding/verify/',
                {'token': '00000000-0000-0000-0000-000000000001'},
                format='json',
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['error'], 'Could not create domain.')
        self.assertNotIn('details', response.data)
        self.assertNotIn('INTERNAL_SCHEMA_TRACE', str(response.data))
