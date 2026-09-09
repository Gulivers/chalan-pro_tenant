"""
Tests for ProductListSerializer list contracts (thumbnail image and on-hand stock).
"""

from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django_tenants.test.cases import TenantTestCase

from appinventory.models import (
    Product,
    ProductBrand,
    ProductBrandAssignment,
    ProductCategory,
    ProductImage,
    Stock,
    UnitCategory,
    UnitOfMeasure,
    Warehouse,
)
from appinventory.serializers import ProductListSerializer
from appinventory.views import product_on_hand_annotation


def _tiny_png(name='test.png'):
    # 1x1 PNG
    content = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx'
        b'\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return SimpleUploadedFile(name, content, content_type='image/png')


class ProductListSerializerImageTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Product List Serializer Image Tests'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_product_list_serializer'

    def setUp(self):
        super().setUp()
        unit_category = UnitCategory.objects.create(name='Count')
        self.unit = UnitOfMeasure.objects.create(
            name='Each',
            code='EA',
            category=unit_category,
            reference_unit=True,
        )
        self.category = ProductCategory.objects.create(name='Electrical')

        self.brand_default = ProductBrand.objects.create(
            name='Default Brand Test',
            is_default=True,
        )
        self.brand_other = ProductBrand.objects.create(name='Other Brand Test')

    def _create_product(self, sku):
        product = Product.objects.create(
            name=f'Product {sku}',
            sku=sku,
            category=self.category,
            unit_default=self.unit,
        )
        product.brands.add(self.brand_default, self.brand_other)
        return product

    def _assignment(self, product, brand):
        return ProductBrandAssignment.objects.get(product=product, brand=brand)

    def _create_image(self, product, brand, *, is_primary=False, filename='img.png'):
        assignment = self._assignment(product, brand)
        return ProductImage.objects.create(
            product=product,
            assignment=assignment,
            image=_tiny_png(filename),
            is_primary=is_primary,
        )

    def _serialized_image(self, product):
        return ProductListSerializer(product).data['image']

    def test_no_images_returns_none(self):
        product = self._create_product('NO-IMG-001')
        self.assertIsNone(self._serialized_image(product))

    def test_prefers_primary_image_of_default_brand(self):
        product = self._create_product('IMG-DEFAULT-001')
        self._create_image(product, self.brand_other, is_primary=True, filename='other.png')
        default_img = self._create_image(
            product,
            self.brand_default,
            is_primary=True,
            filename='default-primary.png',
        )

        self.assertEqual(self._serialized_image(product), default_img.image.url)

    def test_uses_default_brand_image_when_other_brand_has_primary_only(self):
        product = self._create_product('IMG-DEFAULT-002')
        self._create_image(product, self.brand_other, is_primary=True, filename='other-only.png')
        default_img = self._create_image(
            product,
            self.brand_default,
            is_primary=False,
            filename='default-secondary.png',
        )

        self.assertEqual(self._serialized_image(product), default_img.image.url)

    def test_falls_back_to_any_product_image_when_default_brand_has_none(self):
        product = self._create_product('IMG-FALLBACK-001')
        other_img = self._create_image(
            product,
            self.brand_other,
            is_primary=False,
            filename='fallback.png',
        )

        self.assertEqual(self._serialized_image(product), other_img.image.url)


class ProductListSerializerStockTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Product List Serializer Stock Tests'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_product_list_stock'

    def setUp(self):
        super().setUp()
        unit_category = UnitCategory.objects.create(name='Count Stock')
        self.unit = UnitOfMeasure.objects.create(
            name='Each',
            code='EA',
            category=unit_category,
            reference_unit=True,
        )
        self.category = ProductCategory.objects.create(name='Electrical Stock')

    def _create_product(self, sku):
        return Product.objects.create(
            name=f'Product {sku}',
            sku=sku,
            category=self.category,
            unit_default=self.unit,
            reorder_level=Decimal('10'),
        )

    def _annotated(self, product):
        return Product.objects.filter(pk=product.pk).annotate(
            total_stock=product_on_hand_annotation()
        ).get()

    def test_total_stock_none_without_annotation(self):
        product = self._create_product('STK-NONE-001')
        self.assertIsNone(ProductListSerializer(product).data['total_stock'])

    def test_total_stock_zero_when_annotated_without_rows(self):
        product = self._create_product('STK-ZERO-001')
        self.assertEqual(
            ProductListSerializer(self._annotated(product)).data['total_stock'],
            0.0,
        )

    def test_total_stock_sums_warehouses_when_annotated(self):
        product = self._create_product('STK-SUM-001')
        warehouse_a = Warehouse.objects.create(name='Warehouse A Stock Test')
        warehouse_b = Warehouse.objects.create(name='Warehouse B Stock Test')
        Stock.objects.create(
            product=product,
            warehouse=warehouse_a,
            quantity=Decimal('10.50'),
        )
        Stock.objects.create(
            product=product,
            warehouse=warehouse_b,
            quantity=Decimal('4.50'),
        )
        self.assertEqual(
            ProductListSerializer(self._annotated(product)).data['total_stock'],
            15.0,
        )
