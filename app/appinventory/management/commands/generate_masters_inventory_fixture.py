# -*- coding: utf-8 -*-
"""
Genera fixtures de inventario maestro desde un tenant canónico.

Incluye: UnitCategory, UnitOfMeasure, Warehouse, ProductCategory, ProductBrand,
PriceType, Product, ProductPrice (Product.brand FK). ProductImage se genera aparte.

Fuente canónica: schema jobrhythm_products (tenant_id=jobrhythm_products_001).

Uso (ubuntu-house):
  docker compose -f docker-compose.dev.yml exec backend python manage.py \\
    generate_masters_inventory_fixture

Opciones:
  --schema jobrhythm_products   (default)
  --skip-images                 no exportar media ni masters_productimage.json
  --skip-excel                  no regenerar masters_inventory.xlsx
"""
import os
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

DEFAULT_SCHEMA = 'jobrhythm_products'

MASTERS_INVENTORY_MODELS = [
    'appinventory.UnitCategory',
    'appinventory.UnitOfMeasure',
    'appinventory.Warehouse',
    'appinventory.ProductCategory',
    'appinventory.ProductBrand',
    'appinventory.PriceType',
    'appinventory.Product',
    'appinventory.ProductPrice',
]


class Command(BaseCommand):
    help = (
        'Genera masters_inventory.json (+ imágenes + Excel) desde el tenant canónico. '
        f'Default schema: {DEFAULT_SCHEMA}.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            default=DEFAULT_SCHEMA,
            help=f'Schema del tenant fuente (default: {DEFAULT_SCHEMA}).',
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Ruta de salida (default: appinventory/fixtures/masters_inventory.json)',
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='No exportar fixtures/media ni generar masters_productimage.json',
        )
        parser.add_argument(
            '--skip-excel',
            action='store_true',
            help='No regenerar masters_inventory.xlsx',
        )

    def handle(self, *args, **options):
        schema = options['schema'] or DEFAULT_SCHEMA
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        default_output = os.path.join(base_dir, 'appinventory', 'fixtures', 'masters_inventory.json')
        output_path = options['output'] or default_output

        with schema_context(schema):
            out = StringIO()
            call_command(
                'dumpdata',
                *MASTERS_INVENTORY_MODELS,
                indent=2,
                stdout=out,
            )
            json_str = out.getvalue()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

        self.stdout.write(
            self.style.SUCCESS(
                f'masters_inventory.json generado desde schema "{schema}" → {output_path}'
            )
        )

        if not options['skip_images']:
            self.stdout.write('Exportando imágenes a fixtures/media/...')
            call_command('export_fixture_product_images', schema=schema)
            self.stdout.write('Generando masters_productimage.json...')
            call_command('generate_masters_productimage_fixture', schema=schema)

        if not options['skip_excel']:
            self.stdout.write('Regenerando masters_inventory.xlsx...')
            call_command('generate_masters_inventory_excel')
