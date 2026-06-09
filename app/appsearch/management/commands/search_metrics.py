from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_public_schema_name, schema_context

from appsearch.models import IndexOutbox
from appsearch.services.telemetry import summarize_telemetry
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Report search API telemetry (latency avg/p95) for tenant schema(s).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            dest='schemas',
            action='append',
            help='Tenant schema name (repeatable). Default: all active tenants.',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Lookback window in days (default: 7).',
        )
        parser.add_argument(
            '--operation',
            choices=['search', 'similar'],
            default=None,
            help='Filter by operation (default: all).',
        )

    def handle(self, *args, **options):
        schemas = options.get('schemas')
        public = get_public_schema_name()
        tenants = Tenant.objects.filter(is_active=True).exclude(schema_name=public).order_by('schema_name')
        if schemas:
            tenants = tenants.filter(schema_name__in=schemas)

        if not tenants.exists():
            raise CommandError('No matching active tenants found.')

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                summary = summarize_telemetry(
                    operation=options.get('operation'),
                    days=options['days'],
                )
                self.stdout.write(
                    f"{tenant.schema_name}: count={summary['count']} "
                    f"avg_ms={summary['latency_avg_ms']} p95_ms={summary['latency_p95_ms']}"
                )
