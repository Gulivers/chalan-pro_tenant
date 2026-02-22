from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import schema_context
from apptransactions.models import DocumentLine
from appinventory.models import Stock
from appinventory.helpers import convert_to_reference_unit
from tenants.models import Tenant

# python manage.py recalculate_stock --schema=phoenix
# python manage.py recalculate_stock --all
#Uso en local:
# Todos los tenants
#docker compose -f docker-compose.dev.yml exec backend python manage.py recalculate_stock --all
# Un tenant concreto
#docker compose -f docker-compose.dev.yml exec backend python manage.py recalculate_stock --schema=test_dominio_local


class Command(BaseCommand):
    help = 'Recalculate stock levels for all products and warehouses based on document lines.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            help='Schema del tenant (ej: phoenix). Si no se indica, se usa el schema actual.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Ejecutar en todos los tenants (excluye public).',
        )

    def run(self):
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
                f"[INFO] Product: {line.product.name} | Warehouse: {warehouse.name} | type: {stock_movement} | Qty: {converted_qty:.2f} -> Total: {stock.quantity:.2f}"
            )

        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Stock recalculated from {count} document lines."))

    def handle(self, *args, **options):
        schema = options.get('schema')
        run_all = options.get('all')

        if run_all:
            tenants = Tenant.objects.exclude(schema_name='public').filter(is_active=True)
            for tenant in tenants:
                self.stdout.write(self.style.SUCCESS(f'\n--- Schema: {tenant.schema_name} ({tenant.name}) ---'))
                with schema_context(tenant.schema_name):
                    with transaction.atomic():
                        self.run()
        elif schema:
            self.stdout.write(self.style.SUCCESS(f'Ejecutando en schema: {schema}'))
            with schema_context(schema):
                with transaction.atomic():
                    self.run()
        else:
            self.stdout.write(self.style.WARNING('Ejecutando en el schema actual (usa --schema o --all para tenants).'))
            with transaction.atomic():
                self.run()
