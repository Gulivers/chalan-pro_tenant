# -*- coding: utf-8 -*-
"""
Siembra / repara DocumentType + DocumentStatus desde masters_document_type.json.

Uso (local):
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py seed_masters_document_type --schema mi_tenant

Uso (producción):
  docker compose exec backend \\
    python manage.py seed_masters_document_type --schema mi_tenant
"""
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_public_schema_name, schema_context

from apptransactions.services.masters_document_type import (
    default_fixture_path,
    seed_tenant_document_masters,
)


class Command(BaseCommand):
    help = (
        'Carga masters_document_type.json en un tenant por type_code '
        '(seguro frente a colisión de PKs con MR).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            required=True,
            help='Schema del tenant destino (no public).',
        )
        parser.add_argument(
            '--fixture',
            type=str,
            default=None,
            help='Ruta alternativa al fixture JSON.',
        )

    def handle(self, *args, **options):
        schema = options['schema']
        if schema == get_public_schema_name():
            raise CommandError('No se puede sembrar masters en el schema public.')

        fixture = options['fixture'] or default_fixture_path()
        self.stdout.write(f'Sembrando masters desde {fixture} → schema "{schema}"...')
        with schema_context(schema):
            result = seed_tenant_document_masters(fixture_path=fixture)
        self.stdout.write(self.style.SUCCESS(f'✓ Listo: {result}'))
