# -*- coding: utf-8 -*-
"""
Genera appinventory/fixtures/masters_productimage.json desde un tenant.
Reasigna assignment_id a 1, 2, 3... según el orden (product_id, brand_id) que
tendrán las asignaciones al cargar masters_inventory.json, para que loaddata
no viole la FK en un tenant nuevo.
"""
import json
import os
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from appinventory.models import ProductImage, ProductBrandAssignment


class Command(BaseCommand):
    help = (
        'Genera masters_productimage.json desde un tenant con assignment_id 1,2,3... '
        'para inyectar tras masters_inventory.json en el import de maestros.'
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
            help='Ruta de salida (default: appinventory/fixtures/masters_productimage.json)',
        )

    def handle(self, *args, **options):
        schema = options['schema']
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        default_output = os.path.join(base_dir, 'appinventory', 'fixtures', 'masters_productimage.json')
        output_path = options['output'] or default_output
        fixture_path = os.path.join(base_dir, 'appinventory', 'fixtures', 'masters_inventory.json')

        # Orden (product_id, brand_id) al cargar masters_inventory.json: desde fixture o tenant
        ordered_pairs = []
        if os.path.isfile(fixture_path):
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            products = [x for x in data if x.get('model') == 'appinventory.product']
            products.sort(key=lambda x: x.get('pk', 0))
            for p in products:
                for b in p.get('fields', {}).get('brands', []):
                    ordered_pairs.append((p['pk'], b))
        if not ordered_pairs:
            with schema_context(schema):
                assignments = ProductBrandAssignment.objects.order_by('product_id', 'brand_id').values_list(
                    'product_id', 'brand_id'
                )
                ordered_pairs = [(int(p), int(b)) for p, b in assignments]
        pair_to_new_id = {pair: (i + 1) for i, pair in enumerate(ordered_pairs)}

        with schema_context(schema):
            out = []
            for pi in ProductImage.objects.select_related('assignment').all():
                if not pi.assignment:
                    continue
                product_id = pi.assignment.product_id
                brand_id = pi.assignment.brand_id
                new_assignment_id = pair_to_new_id.get((product_id, brand_id))
                if new_assignment_id is None:
                    continue
                image_path = pi.image.name if pi.image else ''
                if not image_path:
                    continue
                uploaded_at = pi.uploaded_at.isoformat() if pi.uploaded_at else None
                out.append({
                    'model': 'appinventory.productimage',
                    'pk': len(out) + 1,
                    'fields': {
                        'product': product_id,
                        'assignment': new_assignment_id,
                        'image': image_path,
                        'is_primary': getattr(pi, 'is_primary', True),
                        'uploaded_at': uploaded_at,
                        'uploaded_by': pi.uploaded_by_id,
                        'description': (pi.description or '')[:255],
                    },
                })

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f'masters_productimage.json generado: {len(out)} entradas → {output_path}'))
