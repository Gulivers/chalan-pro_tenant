# -*- coding: utf-8 -*-
"""
Exporta imágenes de productos desde MEDIA_ROOT hacia
appinventory/fixtures/media/ preservando la ruta relativa del ImageField
(p. ej. products/{product_id}/{brand_id}/{file}.jpg) para Inventory Master Data Setup.

Fuente canónica actual: tenant jobrhythm_products (tenant_id=jobrhythm_products_001).
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django_tenants.utils import schema_context

from appinventory.models import ProductImage

DEFAULT_SCHEMA = 'jobrhythm_products'


class Command(BaseCommand):
    help = (
        'Exporta imágenes de productos del tenant a fixtures/media/ '
        '(preserva ruta relativa) para Inventory Master Data Setup.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            default=DEFAULT_SCHEMA,
            help=f'Schema del tenant fuente (default: {DEFAULT_SCHEMA}).',
        )

    def handle(self, *args, **options):
        schema = options['schema'] or DEFAULT_SCHEMA
        base_dir = getattr(settings, 'BASE_DIR', None)
        if not base_dir:
            self.stdout.write(self.style.ERROR('BASE_DIR no encontrado.'))
            return
        fixtures_media = os.path.join(base_dir, 'appinventory', 'fixtures', 'media')
        os.makedirs(fixtures_media, exist_ok=True)

        def run():
            media_root = getattr(settings, 'MEDIA_ROOT', None) or os.path.join(base_dir, 'media')
            qs = ProductImage.objects.select_related('product').all()
            exported = 0
            missing = 0
            for pi in qs:
                if not pi.product_id or not pi.image:
                    continue
                rel_path = pi.image.name if hasattr(pi.image, 'name') else str(pi.image)
                if not rel_path:
                    continue
                # Normalizar: quitar leading slash
                rel_path = rel_path.lstrip('/')
                src = os.path.join(media_root, rel_path)
                if not os.path.isfile(src):
                    missing += 1
                    continue
                dest = os.path.join(fixtures_media, rel_path)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                exported += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Exportadas {exported} imágenes a {fixtures_media}'
                    + (f' (faltan en disco: {missing})' if missing else '')
                )
            )

        with schema_context(schema):
            self.stdout.write(self.style.SUCCESS(f'Ejecutando en schema: {schema}'))
            run()
