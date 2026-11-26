"""
Reset PostgreSQL id sequences for ctrctsapp tables (after imports/restores).

Symptom
-------
API/UI: "Could not save this record. The database ID sequence is out of sync.
Run fix_builder_sequences and try again." (code: sequence_out_of_sync)

Usage (VPS / Docker)
--------------------
  cd /opt/chalanpro

  # All known ctrctsapp tables, all non-public tenant schemas
  docker compose exec backend python manage.py fix_builder_sequences

  # One tenant only (e.g. schema "test")
  docker compose exec backend python manage.py fix_builder_sequences --schema=test

  # One table in one tenant
  docker compose exec backend python manage.py fix_builder_sequences \\
      --schema=test --table=ctrctsapp_housemodel_jobs

Local (ubuntu-house, compose dev)
---------------------------------
  docker compose -f docker-compose.dev.yml exec backend \\
      python manage.py fix_builder_sequences --schema=<tenant>

Notes
-----
- Safe to re-run: setval(MAX(id), true) so the next insert uses MAX(id)+1.
- Does not migrate or change row data; only sequence counters.
- Known --table values: see TABLES below.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import get_tenant_model, schema_context


# Tables whose id sequences often lag after imports/restores.
TABLES = (
    "ctrctsapp_builder",
    "ctrctsapp_job",
    "ctrctsapp_housemodel",
    "ctrctsapp_housemodel_jobs",
    "ctrctsapp_workprice",
    "ctrctsapp_contract",
    "ctrctsapp_contractdetails",
)


class Command(BaseCommand):
    help = (
        "Reset PostgreSQL id sequences for ctrctsapp tables in tenant schemas "
        "(builder, job, housemodel, housemodel_jobs, …). "
        "Use after manual imports or restores that leave sequences behind max(id)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            dest="schema",
            default=None,
            help="Only fix this tenant schema (default: all non-public tenants).",
        )
        parser.add_argument(
            "--table",
            dest="table",
            default=None,
            help="Only fix this table name (must be in the known list).",
        )

    def handle(self, *args, **options):
        Tenant = get_tenant_model()
        if options["schema"]:
            schemas = [options["schema"]]
        else:
            schemas = list(
                Tenant.objects.exclude(schema_name="public").values_list(
                    "schema_name", flat=True
                )
            )

        if options["table"]:
            if options["table"] not in TABLES:
                self.stderr.write(
                    self.style.ERROR(
                        f"Unknown table {options['table']}. Known: {', '.join(TABLES)}"
                    )
                )
                return
            tables = (options["table"],)
        else:
            tables = TABLES

        for schema_name in schemas:
            with schema_context(schema_name):
                for table in tables:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT pg_get_serial_sequence(%s, 'id')",
                                [table],
                            )
                            seq = cursor.fetchone()[0]
                            if not seq:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"{schema_name}: {table} has no id sequence"
                                    )
                                )
                                continue
                            cursor.execute(
                                f'SELECT COALESCE(MAX(id), 1) FROM "{table}"'
                            )
                            max_id = int(cursor.fetchone()[0] or 1)
                            cursor.execute(
                                "SELECT setval(%s, %s, true)",
                                [seq, max(max_id, 1)],
                            )
                            last_value = cursor.fetchone()[0]
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"{schema_name}: {table} → seq={last_value}"
                            )
                        )
                    except Exception as exc:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{schema_name}: {table} skipped ({exc})"
                            )
                        )
