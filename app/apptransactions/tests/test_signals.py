from decimal import Decimal

from django.contrib.auth import get_user_model
from django_tenants.test.cases import TenantTestCase

from appinventory.models import InventoryMovement, Product, Stock, Warehouse
from apptransactions.models import Document, DocumentLine, DocumentType

User = get_user_model()


class InventorySignalTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Inventory Signal Tenant'
        tenant.email = 'signals@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_inventory_signals'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='signaluser',
            email='signaluser@example.com',
            password='ValidPass123!',
        )
        self.warehouse = Warehouse.objects.create(name='Main Warehouse')
        self.product = Product.objects.create(name='Widget A', sku='W-SIGNAL-1', is_active=True)
        self.doc_type = DocumentType.objects.create(
            type_code='IN',
            description='Entrada de inventario',
            stock_movement=1,
            warehouse_required=True,
            prices_required=False,
        )
        self.document = Document.objects.create(
            document_type=self.doc_type,
            created_by=self.user,
        )

    def _make_line(self, quantity=10):
        with self.captureOnCommitCallbacks(execute=True):
            return DocumentLine.objects.create(
                document=self.document,
                product=self.product,
                quantity=quantity,
                unit_price=Decimal('1.00'),
                warehouse=self.warehouse,
            )

    def test_inventory_movement_created_on_documentline_save(self):
        line = self._make_line()
        movement = InventoryMovement.objects.filter(line_id=line.id).first()
        self.assertIsNotNone(movement)
        self.assertEqual(movement.quantity, Decimal('10'))

    def test_inventory_movement_updates_stock_correctly(self):
        line = self._make_line()
        stock = Stock.objects.get(product=self.product, warehouse=self.warehouse)
        self.assertEqual(stock.quantity, Decimal('10'))

        with self.captureOnCommitCallbacks(execute=True):
            line.quantity = 5
            line.save()

        stock.refresh_from_db()
        self.assertEqual(stock.quantity, Decimal('5'))

    def test_inventory_movement_deleted_on_documentline_delete(self):
        line = self._make_line()
        line_id = line.id
        with self.captureOnCommitCallbacks(execute=True):
            line.delete()

        self.assertFalse(
            InventoryMovement.objects.filter(line_id=line_id).exists()
        )
