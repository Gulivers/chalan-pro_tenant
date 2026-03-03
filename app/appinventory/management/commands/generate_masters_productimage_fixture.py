# -*- coding: utf-8 -*-
"""
Genera appinventory/fixtures/masters_productimage.json desde un tenant.

Usa los assignment_id reales del tenant para que coincidan con
productbrandassignment.json (que se carga antes en la importación). Incluye
todas las ProductImage del tenant, no solo las de una marca.
"""
import json
import os
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from appinventory.models import ProductImage, ProductBrandAssignment


class Command(BaseCommand):
    help = (
        'Genera masters_productimage.json desde un tenant. Incluye todas las imágenes; '
        'los assignment_id coinciden con productbrandassignment.json (cargar ese fixture antes).'
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

        # Mapa (product_id, brand_id) -> assignment_id del tenant. Usamos los IDs reales del
        # tenant para que masters_productimage.json coincida con productbrandassignment.json
        # (que se carga antes en la importación). Así se incluyen TODAS las imágenes, no solo
        # las de la "primera marca", ya que dumpdata de Product no serializa "brands" (M2M con through).
        with schema_context(schema):
            pair_to_assignment_id = {}
            for a in ProductBrandAssignment.objects.order_by('id').values_list('id', 'product_id', 'brand_id'):
                aid, pid, bid = a[0], int(a[1]), int(a[2])
                pair_to_assignment_id[(pid, bid)] = aid

        with schema_context(schema):
            out = []
            for pi in ProductImage.objects.select_related('assignment').all():
                if not pi.assignment:
                    continue
                product_id = pi.assignment.product_id
                brand_id = pi.assignment.brand_id
                assignment_id = pair_to_assignment_id.get((product_id, brand_id))
                if assignment_id is None:
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
                        'assignment': assignment_id,
                        'image': image_path,
                        'is_primary': getattr(pi, 'is_primary', True),
                        'uploaded_at': uploaded_at,
                        # uploaded_by se deja siempre en null en el fixture maestro para evitar
                        # errores de FK (auth_user) en tenants donde no existen esos usuarios.
                        # Es un dato puramente informativo y no afecta al funcionamiento.
                        'uploaded_by': None,
                        'description': (pi.description or '')[:255],
                    },
                })

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f'masters_productimage.json generado: {len(out)} entradas → {output_path}'))
