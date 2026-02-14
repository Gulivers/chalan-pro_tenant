# -*- coding: utf-8 -*-
"""
Exporta imágenes de productos desde el tenant actual (MEDIA_ROOT) hacia
appinventory/fixtures/media/products/{product_id}/{brand_id}/ para que
se incluyan en el Inventory Master Data Setup al importar maestros.
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django_tenants.utils import schema_context

from appinventory.models import ProductImage


class Command(BaseCommand):
    help = (
        'Exporta imágenes de productos del tenant a fixtures/media/products/{product_id}/{brand_id}/ '
        'para que se importen al hacer Inventory Master Data Setup.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            default=None,
            help='Schema del tenant (ej: test_dominio_local). Si no se indica, usa el schema actual.',
        )

    def handle(self, *args, **options):
        schema = options['schema']
        base_dir = getattr(settings, 'BASE_DIR', None)
        if not base_dir:
            self.stdout.write(self.style.ERROR('BASE_DIR no encontrado.'))
            return
        fixtures_media = os.path.join(base_dir, 'appinventory', 'fixtures', 'media', 'products')
        os.makedirs(fixtures_media, exist_ok=True)

        def run():
            media_root = getattr(settings, 'MEDIA_ROOT', None) or os.path.join(base_dir, 'media')
            qs = ProductImage.objects.select_related('assignment__product', 'assignment__brand').all()
            exported = 0
            for pi in qs:
                if not pi.assignment or not pi.image:
                    continue
                product_id = pi.assignment.product_id
                brand_id = pi.assignment.brand_id
                rel_path = pi.image.name if hasattr(pi.image, 'name') else str(pi.image)
                if not rel_path:
                    continue
                src = os.path.join(media_root, rel_path)
                if not os.path.isfile(src):
                    continue
                dest_dir = os.path.join(fixtures_media, str(product_id), str(brand_id))
                os.makedirs(dest_dir, exist_ok=True)
                filename = os.path.basename(rel_path)
                dest = os.path.join(dest_dir, filename)
                shutil.copy2(src, dest)
                exported += 1
            self.stdout.write(self.style.SUCCESS(f'Exportadas {exported} imágenes a {fixtures_media}'))

        if schema:
            with schema_context(schema):
                self.stdout.write(self.style.SUCCESS(f'Ejecutando en schema: {schema}'))
                run()
        else:
            run()
