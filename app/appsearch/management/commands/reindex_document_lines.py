from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from appsearch.services.embeddings import EmbeddingServiceError
from appsearch.services.indexer import reindex_document_lines
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Rebuild SearchIndex entries for DocumentLine records in tenant schema(s).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            dest='schemas',
            action='append',
            help='Tenant schema name (repeatable). Default: all active tenants.',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=None,
            help='Embedding batch size (default: SEARCH_INDEX_BATCH_SIZE).',
        )
        parser.add_argument(
            '--no-embed',
            action='store_true',
            help='Build chunk text and FTS only; skip OpenAI embeddings.',
        )
        parser.add_argument(
            '--document-id',
            type=int,
            default=None,
            help='Reindex lines for a single document ID.',
        )

    def handle(self, *args, **options):
        tenants = self._get_tenants(options['schemas'])
        embed = not options['no_embed']

        for tenant in tenants:
            self.stdout.write(self.style.NOTICE(f'Reindexing document lines for schema: {tenant.schema_name}'))
            with schema_context(tenant.schema_name):
                line_ids = None
                if options['document_id'] is not None:
                    from apptransactions.models import DocumentLine

                    line_ids = list(
                        DocumentLine.objects.filter(document_id=options['document_id']).values_list('id', flat=True)
                    )
                    if not line_ids:
                        self.stdout.write(self.style.WARNING('  No document lines found for that document.'))
                        continue

                try:
                    stats = reindex_document_lines(
                        line_ids=line_ids,
                        batch_size=options['batch_size'],
                        embed=embed,
                    )
                except RuntimeError as exc:
                    raise CommandError(str(exc)) from exc
                except EmbeddingServiceError as exc:
                    raise CommandError(str(exc)) from exc

            self.stdout.write(
                self.style.SUCCESS(
                    '  '
                    f"indexed={stats['indexed']} deleted={stats['deleted']} "
                    f"skipped={stats['skipped']} failed={stats['failed']}"
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
