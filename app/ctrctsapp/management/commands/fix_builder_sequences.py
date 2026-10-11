from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import get_tenant_model, schema_context


class Command(BaseCommand):
    help = (
        "Reset PostgreSQL sequences for ctrctsapp_builder.id in tenant schemas. "
        "Use after manual imports or restores that leave sequences behind max(id)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            dest="schema",
            default=None,
            help="Only fix this tenant schema (default: all non-public tenants).",
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

        for schema_name in schemas:
            with schema_context(schema_name):
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT setval(
                                pg_get_serial_sequence('ctrctsapp_builder', 'id'),
                                COALESCE((SELECT MAX(id) FROM ctrctsapp_builder), 1),
                                true
                            )
                            """
                        )
                        cursor.execute(
                            "SELECT last_value FROM ctrctsapp_builder_id_seq"
                        )
                        last_value = cursor.fetchone()[0]
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{schema_name}: ctrctsapp_builder_id_seq → {last_value}"
                        )
                    )
                except Exception as exc:
                    self.stdout.write(
                        self.style.WARNING(f"{schema_name}: skipped ({exc})")
                    )
