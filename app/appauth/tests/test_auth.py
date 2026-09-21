"""
Stage B authentication tests — tenant-bound Simple JWT + blacklist.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.cache import cache
from django.db import connection
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import schema_context
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch

from appauth.jwt_tokens import TenantRefreshToken
from appauth.services.password_reset import collect_password_validation_errors
from appauth.throttles import LoginIPThrottle, LoginUsernameThrottle
from ctrctsapp.models import Contract

User = get_user_model()


def tenant_api_client(tenant) -> APIClient:
    client = APIClient()
    domain = tenant.get_primary_domain().domain
    client.defaults['HTTP_HOST'] = domain
    return client


class AuthLoginJWTTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'JWT Login Tenant'
        tenant.email = 'owner@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_appauth_jwt_login'

    def setUp(self):
        super().setUp()
        cache.clear()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='jwtuser',
            email='jwtuser@example.com',
            password='ValidPass123!',
        )
        self.login_url = '/api/auth/login/'

    def test_login_returns_jwt_pair(self):
        with override_settings(DEBUG=True, AUTH_USE_REFRESH_COOKIE=False):
            response = self.client.post(
                self.login_url,
                {'username': 'jwtuser', 'password': 'ValidPass123!'},
                format='json',
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(response.data['refresh'])
        access = AccessToken(response.data['access'])
        self.assertEqual(access['schema_name'], self.get_test_schema_name())
        self.assertEqual(int(access['user_id']), self.user.pk)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'username': 'jwtuser', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get('code'), 'invalid_credentials')

    def test_login_inactive_tenant(self):
        self.tenant.is_active = False
        self.tenant.save(update_fields=['is_active'])
        response = self.client.post(
            self.login_url,
            {'username': 'jwtuser', 'password': 'ValidPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('code'), 'tenant_inactive')

    def test_login_throttled_by_ip(self):
        rates = {
            'auth_login_ip': '3/minute',
            'auth_login_username': '100/minute',
        }
        cache.clear()
        with (
            patch.object(LoginIPThrottle, 'THROTTLE_RATES', rates),
            patch.object(LoginUsernameThrottle, 'THROTTLE_RATES', rates),
        ):
            for _ in range(3):
                self.client.post(
                    self.login_url,
                    {'username': 'jwtuser', 'password': 'wrong'},
                    format='json',
                )
            response = self.client.post(
                self.login_url,
                {'username': 'jwtuser', 'password': 'wrong'},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_me_with_bearer(self):
        with override_settings(DEBUG=True, AUTH_USE_REFRESH_COOKIE=False):
            login = self.client.post(
                self.login_url,
                {'username': 'jwtuser', 'password': 'ValidPass123!'},
                format='json',
            )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'jwtuser')

    def test_refresh_rotates(self):
        with override_settings(DEBUG=True, AUTH_USE_REFRESH_COOKIE=False):
            login = self.client.post(
                self.login_url,
                {'username': 'jwtuser', 'password': 'ValidPass123!'},
                format='json',
            )
            old_refresh = login.data['refresh']
            response = self.client.post(
                '/api/auth/refresh/',
                {'refresh': old_refresh},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('access', response.data)
            self.assertTrue(response.data.get('refresh'))
            # Old refresh blacklisted
            again = self.client.post(
                '/api/auth/refresh/',
                {'refresh': old_refresh},
                format='json',
            )
            self.assertEqual(again.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh(self):
        with override_settings(DEBUG=True, AUTH_USE_REFRESH_COOKIE=False):
            login = self.client.post(
                self.login_url,
                {'username': 'jwtuser', 'password': 'ValidPass123!'},
                format='json',
            )
            refresh = login.data['refresh']
            response = self.client.post(
                '/api/auth/logout/',
                {'refresh': refresh},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            again = self.client.post(
                '/api/auth/refresh/',
                {'refresh': refresh},
                format='json',
            )
            self.assertEqual(again.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthIsolationJWTTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'JWT Isolation Tenant'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_appauth_jwt_isolation'

    def setUp(self):
        super().setUp()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='iso_user',
            email='iso@example.com',
            password='ValidPass123!',
        )

    def test_access_token_schema_mismatch_rejected(self):
        refresh = TenantRefreshToken.for_user(self.user)
        access = refresh.access_token
        # Tamper claim
        access['schema_name'] = 'other_schema_not_this_tenant'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(access)}')
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outstanding_registered_in_tenant_schema(self):
        refresh = TenantRefreshToken.for_user(self.user)
        jti = refresh['jti']
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

        self.assertTrue(OutstandingToken.objects.filter(jti=jti).exists())
        self.assertEqual(connection.schema_name, self.get_test_schema_name())


class AuthPasswordResetJWTTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'JWT Password Tenant'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_appauth_jwt_password'

    def setUp(self):
        super().setUp()
        cache.clear()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='resetjwt',
            email='resetjwt@example.com',
            password='OldPass123!',
        )

    def test_forgot_anti_enumeration(self):
        response = self.client.post(
            '/api/auth/password/forgot/',
            {'email': 'nobody@example.com'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('code'), 'reset_email_sent')

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                'NAME': (
                    'django.contrib.auth.password_validation.'
                    'MinimumLengthValidator'
                ),
                'OPTIONS': {'min_length': 8},
            },
        ],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEBUG=True,
        AUTH_USE_REFRESH_COOKIE=False,
    )
    def test_reset_invalidates_refresh(self):
        login = self.client.post(
            '/api/auth/login/',
            {'username': 'resetjwt', 'password': 'OldPass123!'},
            format='json',
        )
        refresh = login.data['refresh']
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        reset_token = default_token_generator.make_token(self.user)
        response = self.client.post(
            '/api/auth/password/reset/',
            {
                'uid': uid,
                'token': reset_token,
                'new_password': 'BrandNewPass99!',
                'confirm_password': 'BrandNewPass99!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        again = self.client.post(
            '/api/auth/refresh/',
            {'refresh': refresh},
            format='json',
        )
        self.assertEqual(again.status_code, status.HTTP_401_UNAUTHORIZED)
