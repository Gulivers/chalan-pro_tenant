# -*- coding: utf-8 -*-
"""
Genera appinventory/fixtures/masters_productimage.json desde un tenant.

Incluye todas las ProductImage del tenant con FK a product (sin assignment).
Fuente canónica: jobrhythm_products (tenant_id=jobrhythm_products_001).
"""
import json
import os
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from appinventory.models import ProductImage

DEFAULT_SCHEMA = 'jobrhythm_products'


class Command(BaseCommand):
    help = (
        'Genera masters_productimage.json desde un tenant. '
        'Incluye todas las imágenes vinculadas al producto.'
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
            help='Ruta de salida (default: appinventory/fixtures/masters_productimage.json)',
        )

    def handle(self, *args, **options):
        schema = options['schema'] or DEFAULT_SCHEMA
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        default_output = os.path.join(base_dir, 'appinventory', 'fixtures', 'masters_productimage.json')
        output_path = options['output'] or default_output

        with schema_context(schema):
            out = []
            for pi in ProductImage.objects.select_related('product').order_by('id'):
                if not pi.product_id or not pi.image:
                    continue
                image_path = pi.image.name
                if not image_path:
                    continue
                uploaded_at = pi.uploaded_at.isoformat() if pi.uploaded_at else None
                out.append({
                    'model': 'appinventory.productimage',
                    'pk': len(out) + 1,
                    'fields': {
                        'product': pi.product_id,
                        'image': image_path,
                        'is_primary': getattr(pi, 'is_primary', True),
                        'uploaded_at': uploaded_at,
                        'uploaded_by': None,
                        'description': (pi.description or '')[:255],
                    },
                })

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f'masters_productimage.json generado: {len(out)} entradas → {output_path}'
                )
            )
