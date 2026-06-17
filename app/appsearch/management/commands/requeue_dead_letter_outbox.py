from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_public_schema_name, schema_context

from appsearch.models import IndexOutbox
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Requeue dead-letter IndexOutbox entries for retry (resets attempts).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            dest='schemas',
            action='append',
            help='Tenant schema name (repeatable). Default: all active tenants.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Maximum dead-letter entries to requeue per tenant (default: 200).',
        )

    def handle(self, *args, **options):
        schemas = options.get('schemas')
        limit = options['limit']
        public = get_public_schema_name()
        tenants = Tenant.objects.filter(is_active=True).exclude(schema_name=public).order_by('schema_name')
        if schemas:
            tenants = tenants.filter(schema_name__in=schemas)

        if not tenants.exists():
            raise CommandError('No matching active tenants found.')

        total = 0
        for tenant in tenants:
            with schema_context(tenant.schema_name):
                dead = list(
                    IndexOutbox.objects.filter(dead_letter_at__isnull=False, processed_at__isnull=True)
                    .order_by('dead_letter_at')[:limit]
                )
                for entry in dead:
                    entry.attempts = 0
                    entry.dead_letter_at = None
                    entry.last_error = ''
                    entry.save(update_fields=['attempts', 'dead_letter_at', 'last_error'])
                total += len(dead)
                self.stdout.write(f'{tenant.schema_name}: requeued={len(dead)}')

        self.stdout.write(self.style.SUCCESS(f'Summary: requeued={total}'))
