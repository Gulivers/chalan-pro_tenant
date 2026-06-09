"""Process IndexOutbox for every active tenant (cron entry point)."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_public_schema_name, schema_context

from appsearch.services.embeddings import EmbeddingServiceError
from appsearch.services.indexer import process_pending_outbox
from tenants.models import Tenant


class Command(BaseCommand):
    help = (
        'Process pending SearchIndex outbox entries for all active tenant schemas. '
        'Intended for host cron (see scripts/process_search_outbox_cron.sh).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Maximum pending outbox entries per tenant schema (default: 200).',
        )
        parser.add_argument(
            '--no-embed',
            action='store_true',
            help='Update chunk text and FTS only; skip OpenAI embeddings.',
        )
        parser.add_argument(
            '--fail-fast',
            action='store_true',
            help='Stop on the first tenant or embedding error (default: continue).',
        )

    def handle(self, *args, **options):
        if not getattr(settings, 'SEARCH_INDEXING_ENABLED', True):
            self.stdout.write(self.style.WARNING('SEARCH_INDEXING_ENABLED is False; skipping.'))
            return

        public_schema = get_public_schema_name()
        tenants = (
            Tenant.objects.filter(is_active=True)
            .exclude(schema_name=public_schema)
            .order_by('schema_name')
        )
        if not tenants.exists():
            raise CommandError('No active tenant schemas found.')

        embed = not options['no_embed']
        limit = options['limit']
        fail_fast = options['fail_fast']

        totals = {'tenants': 0, 'processed': 0, 'failed': 0, 'dead_letter': 0, 'errors': 0}

        for tenant in tenants:
            totals['tenants'] += 1
            self.stdout.write(
                self.style.NOTICE(f'Processing outbox for schema: {tenant.schema_name} ({tenant.name})')
            )
            with schema_context(tenant.schema_name):
                try:
                    stats = process_pending_outbox(limit=limit, embed=embed)
                except (RuntimeError, EmbeddingServiceError) as exc:
                    totals['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'  error: {exc}'))
                    if fail_fast:
                        raise CommandError(str(exc)) from exc
                    continue
                except Exception as exc:
                    totals['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'  unexpected error: {exc}'))
                    if fail_fast:
                        raise CommandError(str(exc)) from exc
                    continue

            totals['processed'] += stats['processed']
            totals['failed'] += stats['failed']
            totals['dead_letter'] += stats.get('dead_letter', 0)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  processed={stats['processed']} failed={stats['failed']} "
                    f"dead_letter={stats.get('dead_letter', 0)}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Summary: '
                f"tenants={totals['tenants']} "
                f"processed={totals['processed']} "
                f"failed={totals['failed']} "
                f"dead_letter={totals['dead_letter']} "
                f"tenant_errors={totals['errors']}"
            )
        )

        if totals['failed'] or totals['errors']:
            raise CommandError(
                'Outbox processing finished with failures '
                f"(failed_entries={totals['failed']}, tenant_errors={totals['errors']})."
            )
