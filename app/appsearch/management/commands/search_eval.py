import json

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from appsearch.services.search import search_transactions


class Command(BaseCommand):
    help = (
        'Evaluate semantic search recall@k using a JSON file of golden queries. '
        'Example file: [{"query":"breakers","expected_document_ids":[1,2]}]'
    )

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Tenant schema name.')
        parser.add_argument('--queries-file', required=True, help='Path to JSON eval set.')
        parser.add_argument('--k', type=int, default=10, help='Recall@k (default: 10).')
        parser.add_argument('--limit', type=int, default=50, help='Search limit per query.')

    def handle(self, *args, **options):
        schema = options['schema']
        k = options['k']
        limit = options['limit']

        try:
            with open(options['queries_file'], encoding='utf-8') as handle:
                cases = json.load(handle)
        except OSError as exc:
            raise CommandError(f'Cannot read queries file: {exc}') from exc
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON in queries file: {exc}') from exc

        if not isinstance(cases, list) or not cases:
            raise CommandError('queries-file must contain a non-empty JSON array.')

        recalls = []
        with schema_context(schema):
            for index, case in enumerate(cases, start=1):
                query = (case.get('query') or '').strip()
                expected = case.get('expected_document_ids') or []
                if not query:
                    self.stdout.write(self.style.WARNING(f'Case {index}: empty query, skipped'))
                    continue

                payload = search_transactions(query, limit=limit)
                got = set(payload.get('document_ids') or [])[:k]
                expected_set = set(expected)
                if not expected_set:
                    self.stdout.write(self.style.WARNING(f'Case {index}: no expected ids, skipped'))
                    continue

                hit = len(expected_set & got) / len(expected_set)
                recalls.append(hit)
                self.stdout.write(
                    f'Case {index}: recall@{k}={hit:.2f} query={query!r} got={sorted(got)}'
                )

        if not recalls:
            raise CommandError('No evaluable cases found.')

        avg_recall = sum(recalls) / len(recalls)
        self.stdout.write(self.style.SUCCESS(
            f'Average recall@{k} over {len(recalls)} cases: {avg_recall:.3f}'
        ))
