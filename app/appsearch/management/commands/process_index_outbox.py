from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from appsearch.services.embeddings import EmbeddingServiceError
from appsearch.services.indexer import process_pending_outbox
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Process pending SearchIndex outbox entries for one or all tenant schemas.'

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
            default=100,
            help='Maximum pending outbox entries per schema (default: 100).',
        )
        parser.add_argument(
            '--no-embed',
            action='store_true',
            help='Update chunk text and FTS only; skip OpenAI embeddings.',
        )

    def handle(self, *args, **options):
        schemas = options['schemas']
        tenants = self._get_tenants(schemas)
        embed = not options['no_embed']

        for tenant in tenants:
            self.stdout.write(self.style.NOTICE(f'Processing outbox for schema: {tenant.schema_name}'))
            with schema_context(tenant.schema_name):
                try:
                    stats = process_pending_outbox(limit=options['limit'], embed=embed)
                except RuntimeError as exc:
                    raise CommandError(str(exc)) from exc
                except EmbeddingServiceError as exc:
                    raise CommandError(str(exc)) from exc

            self.stdout.write(
                self.style.SUCCESS(
                    f"  processed={stats['processed']} failed={stats['failed']}"
                )
            )

    def _get_tenants(self, schemas):
        queryset = Tenant.objects.filter(is_active=True).order_by('schema_name')
        if schemas:
            queryset = queryset.filter(schema_name__in=schemas)
            missing = set(schemas) - set(queryset.values_list('schema_name', flat=True))
            if missing:
                raise CommandError(f'Unknown or inactive schema(s): {", ".join(sorted(missing))}')
        if not queryset.exists():
            raise CommandError('No active tenants found.')
        return queryset
