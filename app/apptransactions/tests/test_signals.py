from django.test import TestCase
from django.contrib.auth import get_user_model
from apptransactions.models import Document, DocumentLine, DocumentType
from appinventory.models import Product, Warehouse, InventoryMovement, Stock
from decimal import Decimal

User = get_user_model()

class InventorySignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.warehouse = Warehouse.objects.create(name='Main Warehouse')
        self.product = Product.objects.create(name='Widget A')
        self.doc_type = DocumentType.objects.create(
            name='Entrada', stock_movement=1, description="Entrada de inventario")
        self.document = Document.objects.create(
            document_type=self.doc_type,
            created_by=self.user,
            warehouse=self.warehouse
        )

    def test_inventory_movement_created_on_documentline_save(self):
        line = DocumentLine.objects.create(
            document=self.document,
            product=self.product,
            quantity=10,
            unit=None,
            warehouse=self.warehouse
        )
        movement = InventoryMovement.objects.filter(line_id=line.id).first()
        self.assertIsNotNone(movement, "✅ InventoryMovement debe haberse creado por el signal")
        self.assertEqual(movement.quantity, Decimal('10'))

    def test_inventory_movement_updates_stock_correctly(self):
        line = DocumentLine.objects.create(
            document=self.document,
            product=self.product,
            quantity=10,
            unit=None,
            warehouse=self.warehouse
        )
        stock = Stock.objects.get(product=self.product, warehouse=self.warehouse)
        self.assertEqual(stock.quantity, Decimal('10'))

        # Cambiar la cantidad
        line.quantity = 5
        line.save()

        stock.refresh_from_db()
        self.assertEqual(stock.quantity, Decimal('5'))

    def test_inventory_movement_deleted_on_documentline_delete(self):
        line = DocumentLine.objects.create(
            document=self.document,
            product=self.product,
            quantity=10,
            unit=None,
            warehouse=self.warehouse
        )
        line.delete()

        movement = InventoryMovement.objects.filter(line_id=line.id).first()
        self.assertIsNone(movement, "🗑️ InventoryMovement debe eliminarse cuando se borra DocumentLine")

        stock = Stock.objects.get(product=self.product, warehouse=self.warehouse)
        self.assertEqual(stock.quantity, Decimal('0'))
