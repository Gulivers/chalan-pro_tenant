# -*- coding: utf-8 -*-
"""Seed de masters_document_type sin colisión de PKs con MR."""

from django_tenants.test.cases import TenantTestCase

from apptransactions.models import DocumentStatus, DocumentType
from apptransactions.services.masters_document_type import seed_tenant_document_masters


class MastersDocumentTypeSeedTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Masters DocType Seed Tenant'
        tenant.email = 'masters-seed@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_masters_document_type_seed'

    def test_post_schema_sync_leaves_more_than_mr(self):
        # TenantTestCase crea el schema → post_schema_sync debe sembrar el fixture.
        codes = set(DocumentType.objects.values_list('type_code', flat=True))
        self.assertIn('MR', codes)
        self.assertIn('PO', codes)
        self.assertIn('PK', codes)
        self.assertGreaterEqual(DocumentType.objects.count(), 11)
        self.assertGreater(DocumentStatus.objects.count(), 5)

    def test_seed_is_idempotent_and_survives_mr_pk_collision(self):
        mr = DocumentType.objects.filter(type_code='MR').first()
        self.assertIsNotNone(mr)

        DocumentStatus.objects.exclude(document_type=mr).delete()
        DocumentType.objects.exclude(type_code='MR').delete()
        self.assertEqual(DocumentType.objects.count(), 1)

        first = seed_tenant_document_masters()
        self.assertGreaterEqual(first['types_created'], 10)
        self.assertTrue(DocumentType.objects.filter(type_code='PO').exists())
        self.assertEqual(DocumentType.objects.filter(type_code='MR').count(), 1)

        second = seed_tenant_document_masters()
        self.assertEqual(second['types_created'], 0)
        self.assertGreaterEqual(second['statuses_created'], 0)
