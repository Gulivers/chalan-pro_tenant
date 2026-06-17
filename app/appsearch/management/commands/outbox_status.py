from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_public_schema_name, schema_context

from appsearch.models import IndexOutbox
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Show pending and dead-letter IndexOutbox counts per tenant schema.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            dest='schemas',
            action='append',
            help='Tenant schema name (repeatable). Default: all active tenants.',
        )

    def handle(self, *args, **options):
        schemas = options.get('schemas')
        public = get_public_schema_name()
        tenants = Tenant.objects.filter(is_active=True).exclude(schema_name=public).order_by('schema_name')
        if schemas:
            tenants = tenants.filter(schema_name__in=schemas)

        if not tenants.exists():
            raise CommandError('No matching active tenants found.')

        total_pending = 0
        total_dead = 0

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                pending = IndexOutbox.objects.filter(
                    processed_at__isnull=True,
                    dead_letter_at__isnull=True,
                ).count()
                dead = IndexOutbox.objects.filter(dead_letter_at__isnull=False).count()
                total_pending += pending
                total_dead += dead
                self.stdout.write(
                    f'{tenant.schema_name}: pending={pending} dead_letter={dead}'
                )

        self.stdout.write(self.style.SUCCESS(
            f'Summary: pending={total_pending} dead_letter={total_dead}'
        ))
