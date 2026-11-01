# -*- coding: utf-8 -*-
"""
Genera apptransactions/fixtures/masters_document_type.json desde un tenant.

Incluye DocumentType + DocumentStatus. Excluye MR (y sus statuses): lo siembra
la migración 0008 / seed de sistema y no debe ir en el fixture de onboarding.

Fuente canónica: schema division16 (tenant_id=division16_llc_001).

Uso (ubuntu-house):
  docker compose -f docker-compose.dev.yml exec backend python manage.py \\
    generate_masters_document_type_fixture
"""
import json
import os

from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django_tenants.utils import schema_context

from apptransactions.models import DocumentStatus, DocumentType

DEFAULT_SCHEMA = 'division16'
# MR es protegido / sembrado por migración; no versionar en masters.
EXCLUDED_TYPE_CODES = frozenset({'MR'})


class Command(BaseCommand):
    help = (
        'Genera masters_document_type.json (DocumentType + DocumentStatus, sin MR) '
        f'desde el tenant canónico. Default schema: {DEFAULT_SCHEMA}.'
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
            help='Ruta de salida (default: apptransactions/fixtures/masters_document_type.json)',
        )

    def handle(self, *args, **options):
        schema = options['schema'] or DEFAULT_SCHEMA
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        output_path = options['output'] or os.path.join(
            base_dir, 'apptransactions', 'fixtures', 'masters_document_type.json'
        )

        with schema_context(schema):
            doc_types = (
                DocumentType.objects.exclude(type_code__in=EXCLUDED_TYPE_CODES)
                .order_by('pk')
            )
            type_ids = list(doc_types.values_list('pk', flat=True))
            statuses = (
                DocumentStatus.objects.filter(document_type_id__in=type_ids)
                .order_by('document_type_id', 'sequence', 'pk')
            )
            types_json = json.loads(serialize('json', doc_types, indent=2))
            statuses_json = json.loads(serialize('json', statuses, indent=2))
            combined = types_json + statuses_json

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
            f.write('\n')

        self.stdout.write(
            self.style.SUCCESS(
                f'masters_document_type.json generado desde schema "{schema}" → '
                f'{output_path} '
                f'({len(types_json)} DocumentType, {len(statuses_json)} DocumentStatus; '
                f'excluido: {", ".join(sorted(EXCLUDED_TYPE_CODES))})'
            )
        )
