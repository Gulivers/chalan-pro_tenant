from django.core.management.base import BaseCommand
from apptransactions.models import DocumentLine
from appinventory.models import Stock
from django.db import transaction
from appinventory.helpers import convert_to_reference_unit

# python manage.py recalculate_stock

class Command(BaseCommand):
    help = 'Recalculate stock levels for all products and warehouses based on document lines.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("[INFO] Clearing current stock levels...")
        Stock.objects.all().delete()

        self.stdout.write("[INFO] Recalculating stock from document lines...")
        count = 0

        lines = DocumentLine.objects.select_related(
            'document', 'product', 'unit', 'warehouse', 'document__document_type'
        )

        for line in lines:
            stock_movement = line.document.document_type.stock_movement
            if not stock_movement:
                continue  # Neutral document type, skip

            warehouse = line.warehouse or line.document.warehouse
            if not warehouse:
                continue  # No warehouse defined

            converted_qty = convert_to_reference_unit(line.product, line.unit, line.quantity)

            stock, created = Stock.objects.get_or_create(
                product=line.product,
                warehouse=warehouse,
                defaults={'quantity': 0}
            )
            stock.quantity += converted_qty * stock_movement
            stock.save()
            count += 1

            self.stdout.write(
                f"[INFO] Product: {line.product.name} | Warehouse: {warehouse.name} | type: { stock_movement } | Qty: {converted_qty:.2f} -> Total: {stock.quantity:.2f}"
            )

        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Stock successfully recalculated from {count} document lines."))
