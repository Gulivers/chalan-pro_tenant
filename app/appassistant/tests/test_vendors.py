"""
Vendor resolution tests (tenant schema via TenantTestCase).
"""

from django_tenants.test.cases import TenantTestCase

from appassistant.services.vendors import (
    AmbiguousVendorError,
    VendorNotFoundError,
    resolve_vendor,
)
from apptransactions.models import Party
from ctrctsapp.models import Builder


class VendorResolutionTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Assistant Vendor Test Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_assistant_vendors'

    def setUp(self):
        super().setUp()
        self.harbor = Builder.objects.create(name='Harbor Freight', supplier_rank=1)
        self.harbor_tools = Builder.objects.create(name='Harbor Tools', supplier_rank=1)
        party = Party.objects.create(name='Acme Supplies Inc', supplier_rank=1)
        self.acme_builder = Builder.objects.create(
            name='ACME LLC',
            party=party,
            supplier_rank=1,
        )

    def test_exact_name(self):
        builder = resolve_vendor(name='harbor freight')
        self.assertEqual(builder.pk, self.harbor.pk)

    def test_ambiguous_partial_name(self):
        with self.assertRaises(AmbiguousVendorError) as ctx:
            resolve_vendor(name='Harbor')
        ids = {c.id for c in ctx.exception.candidates}
        self.assertEqual(ids, {self.harbor.pk, self.harbor_tools.pk})

    def test_party_name_fallback(self):
        builder = resolve_vendor(name='Acme Supplies Inc')
        self.assertEqual(builder.pk, self.acme_builder.pk)

    def test_vendor_id(self):
        builder = resolve_vendor(vendor_id=self.harbor.pk)
        self.assertEqual(builder.pk, self.harbor.pk)

    def test_not_found(self):
        with self.assertRaises(VendorNotFoundError):
            resolve_vendor(name='No Such Vendor XYZ')
