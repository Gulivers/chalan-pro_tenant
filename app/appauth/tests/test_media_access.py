# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import get_public_schema_name, schema_context
from rest_framework.test import APIClient

from project.media_access import (
    build_signed_media_url,
    sign_media_path,
    unsign_media_token,
    validate_upload_file,
)
from tenants.models import Tenant


class ValidateUploadFileTests(SimpleTestCase):
    def test_rejects_html(self):
        f = SimpleUploadedFile('x.html', b'<html></html>', content_type='text/html')
        with self.assertRaises(ValidationError):
            validate_upload_file(f, images_only=False)

    def test_rejects_svg(self):
        f = SimpleUploadedFile(
            'x.svg',
            b'<svg xmlns="http://www.w3.org/2000/svg"></svg>',
            content_type='image/svg+xml',
        )
        with self.assertRaises(ValidationError):
            validate_upload_file(f, images_only=True)


class SignedMediaUrlTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Signed Media Tenant'
        tenant.email = 'signed-media@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_signed_media_access'

    def test_roundtrip_token_bound_to_schema(self):
        token = sign_media_path('event_images/work_account_1/old.png')
        schema, path = unsign_media_token(token)
        self.assertEqual(schema, self.get_test_schema_name())
        self.assertEqual(path, 'event_images/work_account_1/old.png')
        url = build_signed_media_url(None, 'event_images/work_account_1/old.png')
        self.assertTrue(url.startswith('/media/s/'))

    def _attach_logo(self) -> Tenant:
        public = get_public_schema_name()
        with schema_context(public):
            tenant = Tenant.objects.get(schema_name=self.get_test_schema_name())
            tenant.logo.save(
                'signed_media_logo.png',
                ContentFile(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
                    b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
                    b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
                ),
                save=True,
            )
            return tenant

    def test_tenant_logo_url_signed_for_active_tenant_schema(self):
        """SPA on tenant host: token schema must match connection schema."""
        tenant = self._attach_logo()
        try:
            url = tenant.get_logo_url()
            self.assertIsNotNone(url)
            token = url.rstrip('/').rsplit('/', 1)[-1]
            schema, path = unsign_media_token(token)
            self.assertEqual(schema, self.get_test_schema_name())
            self.assertTrue(path.startswith('tenant_logos/'))

            client = APIClient()
            domain = tenant.get_primary_domain().domain
            client.defaults['HTTP_HOST'] = domain
            response = client.get(f'/media/s/{token}/')
            self.assertEqual(response.status_code, 200)
        finally:
            if tenant.logo:
                tenant.logo.delete(save=False)

    def test_tenant_logo_url_signed_for_public_admin_preview(self):
        """Django Admin (public schema) keeps a public-scoped signed preview."""
        tenant = self._attach_logo()
        public = get_public_schema_name()
        try:
            with schema_context(public):
                url = tenant.get_logo_url()
                self.assertIsNotNone(url)
                token = url.rstrip('/').rsplit('/', 1)[-1]
                schema, path = unsign_media_token(token)
                self.assertEqual(schema, public)
                self.assertTrue(path.startswith('tenant_logos/'))
        finally:
            if tenant.logo:
                with schema_context(public):
                    tenant.logo.delete(save=False)

    def test_public_signed_logo_rejected_on_tenant_host(self):
        """Regression: always signing with public breaks tenant SPA <img>."""
        tenant = self._attach_logo()
        public = get_public_schema_name()
        try:
            public_token = sign_media_path(tenant.logo.name, schema_name=public)
            client = APIClient()
            client.defaults['HTTP_HOST'] = tenant.get_primary_domain().domain
            denied = client.get(f'/media/s/{public_token}/')
            self.assertEqual(denied.status_code, 404)

            ok_token = sign_media_path(
                tenant.logo.name,
                schema_name=self.get_test_schema_name(),
            )
            allowed = client.get(f'/media/s/{ok_token}/')
            self.assertEqual(allowed.status_code, 200)
        finally:
            if tenant.logo:
                with schema_context(public):
                    tenant.logo.delete(save=False)
