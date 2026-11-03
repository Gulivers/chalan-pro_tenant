# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django_tenants.test.cases import TenantTestCase

from project.media_access import (
    build_signed_media_url,
    sign_media_path,
    unsign_media_token,
    validate_upload_file,
)


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
