# -*- coding: utf-8 -*-
"""
Genera app/appinventory/fixtures/masters_inventory.json desde un tenant.

Incluye los modelos de datos maestros de inventario (categorías, unidades, marcas,
productos, precios, etc.) en el orden correcto para loaddata. No incluye
ProductImage ni ProductBrandAssignment; Product se serializa con el campo M2M
"brands" para que al cargar se creen las asignaciones producto-marca.

Uso (desde el host, con Docker):
  docker compose exec backend python manage.py generate_masters_inventory_fixture \\
    --schema test_dominio_local

Con salida en ruta distinta:
  docker compose exec backend python manage.py generate_masters_inventory_fixture \\
    --schema test_dominio_local \\
    --output /app/appinventory/fixtures/masters_inventory.json

Tras generar masters_inventory.json, este comando ejecuta automáticamente:
- generate_masters_productimage_fixture → masters_productimage.json
- dumpdata de ProductBrandAssignment → productbrandassignment.json
(ambos desde el mismo tenant para mantener coherencia de IDs.)
"""
import os
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context


# Orden de modelos por dependencias (FK); Product incluye "brands" (M2M) en la serialización
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
        'Genera masters_inventory.json desde un tenant (datos maestros de inventario). '
        'Uso: python manage.py generate_masters_inventory_fixture --schema <schema> [--output <ruta>]'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            required=True,
            help='Schema del tenant fuente (ej: test_dominio_local)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Ruta de salida (default: appinventory/fixtures/masters_inventory.json)',
        )

    def handle(self, *args, **options):
        schema = options['schema']
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

        # Regenerar masters_productimage.json para que assignment_id coincida con el orden del fixture
        self.stdout.write('Ejecutando generate_masters_productimage_fixture...')
        call_command('generate_masters_productimage_fixture', schema=schema)

        # Regenerar productbrandassignment.json desde el mismo tenant (IDs coherentes con los anteriores)
        assignment_output = os.path.join(base_dir, 'appinventory', 'fixtures', 'productbrandassignment.json')
        self.stdout.write('Generando productbrandassignment.json...')
        with schema_context(schema):
            out_assign = StringIO()
            call_command(
                'dumpdata',
                'appinventory.ProductBrandAssignment',
                indent=2,
                stdout=out_assign,
            )
            with open(assignment_output, 'w', encoding='utf-8') as f:
                f.write(out_assign.getvalue())
        self.stdout.write(
            self.style.SUCCESS(f'productbrandassignment.json generado → {assignment_output}')
        )
