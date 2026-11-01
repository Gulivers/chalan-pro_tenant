"""
Sembrar DocumentStatus workflows por defecto (PO/PK/PR/GRN/…).

No activa uses_status_tracking. Idempotente: si el tipo ya tiene statuses, no toca.

Ejemplos:
  python manage.py seed_document_status_workflows --schema division16
  python manage.py seed_document_status_workflows
"""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_public_schema_name, get_tenant_model, schema_context

from apptransactions.services.document_status import seed_default_document_statuses


class Command(BaseCommand):
    help = (
        "Seed default DocumentStatus workflows for master document types "
        "(tracking stays OFF)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            dest="schema",
            default=None,
            help="Only seed this tenant schema (default: all non-public tenants).",
        )

    def handle(self, *args, **options):
        Tenant = get_tenant_model()
        public = get_public_schema_name()
        schema = options.get("schema")
        if schema:
            if schema == public:
                raise CommandError("Cannot seed document statuses on the public schema.")
            if not Tenant.objects.filter(schema_name=schema).exists():
                raise CommandError(f"Tenant schema not found: {schema}")
            schemas = [schema]
        else:
            schemas = list(
                Tenant.objects.exclude(schema_name=public)
                .order_by("schema_name")
                .values_list("schema_name", flat=True)
            )

        total = 0
        for schema_name in schemas:
            with schema_context(schema_name):
                created = seed_default_document_statuses()
                total += created
                self.stdout.write(
                    self.style.SUCCESS(f"{schema_name}: created {created} status row(s)")
                )
        self.stdout.write(self.style.SUCCESS(f"Done. Total created: {total}"))
