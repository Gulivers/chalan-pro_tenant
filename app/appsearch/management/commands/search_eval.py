import json
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from appsearch.services.search import search_transactions

EVAL_DIR = Path(settings.BASE_DIR) / 'appsearch' / 'eval'


def default_queries_file(schema: str) -> Path:
    tenant_specific = EVAL_DIR / f'golden_queries.{schema}.json'
    if tenant_specific.is_file():
        return tenant_specific
    generic = EVAL_DIR / 'golden_queries.json'
    if generic.is_file():
        return generic
    return tenant_specific


def _load_eval_document(raw) -> tuple[dict | None, list]:
    """Accept legacy array or `{ "_meta": {...}, "cases": [...] }`."""
    if isinstance(raw, list):
        if not raw:
            raise CommandError('queries-file must contain a non-empty JSON array.')
        return None, raw
    if isinstance(raw, dict) and isinstance(raw.get('cases'), list):
        cases = raw['cases']
        if not cases:
            raise CommandError('queries-file cases array must not be empty.')
        meta = raw.get('_meta')
        return (meta if isinstance(meta, dict) else None), cases
    raise CommandError(
        'queries-file must be a JSON array or an object with a "cases" array '
        '(optional "_meta" documents file purpose).'
    )


def _write_eval_document(path: Path, *, meta: dict | None, cases: list) -> None:
    payload = {'_meta': meta, 'cases': cases} if meta else cases
    with path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write('\n')


class Command(BaseCommand):
    help = (
        'Evaluate semantic search against golden queries (recall@k, min_count, forbidden ids). '
        'Default queries file: app/appsearch/eval/golden_queries.<schema>.json'
    )

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Tenant schema name.')
        parser.add_argument(
            '--queries-file',
            default=None,
            help='Path to JSON eval set (default: appsearch/eval/golden_queries.<schema>.json).',
        )
        parser.add_argument('--k', type=int, default=10, help='Recall@k (default: 10).')
        parser.add_argument('--limit', type=int, default=50, help='Search limit per query.')
        parser.add_argument(
            '--fail-under',
            type=float,
            default=None,
            help='Exit with code 1 if average recall@k is below this value (e.g. 0.95).',
        )
        parser.add_argument(
            '--update-baseline',
            action='store_true',
            help='Rewrite expected_document_ids/min_count from current search results (refresh golden file).',
        )

    def handle(self, *args, **options):
        schema = options['schema']
        queries_file = Path(options['queries_file']) if options['queries_file'] else default_queries_file(schema)
        k = options['k']
        limit = options['limit']
        update_baseline = options['update_baseline']

        if not queries_file.is_file():
            raise CommandError(
                f'Queries file not found: {queries_file}. '
                f'Copy app/appsearch/eval/golden_queries.test_dominio_local.json as a template.'
            )

        try:
            with queries_file.open(encoding='utf-8') as handle:
                file_meta, cases = _load_eval_document(json.load(handle))
        except OSError as exc:
            raise CommandError(f'Cannot read queries file: {exc}') from exc
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON in queries file: {exc}') from exc

        recalls = []
        failures = []
        updated_cases = []

        with schema_context(schema):
            for index, case in enumerate(cases, start=1):
                query = (case.get('query') or '').strip()
                case_id = case.get('id') or f'case_{index}'
                if not query:
                    self.stdout.write(self.style.WARNING(f'{case_id}: empty query, skipped'))
                    continue

                payload = search_transactions(query, limit=limit)
                got_list = payload.get('document_ids') or []
                got = set(got_list[:k])
                expected = case.get('expected_document_ids') or []
                expected_set = set(expected)
                forbidden = set(case.get('forbidden_document_ids') or [])
                min_count = case.get('min_count')
                expect_notice = bool(case.get('expect_notice'))
                notice = (payload.get('notice') or '').strip()

                if update_baseline:
                    case = dict(case)
                    case['expected_document_ids'] = got_list
                    case['min_count'] = payload.get('count', 0)
                    updated_cases.append(case)
                    continue

                case_failures = []

                if expect_notice and not notice:
                    case_failures.append('expected notice but got none')

                if min_count is not None and payload.get('count', 0) < min_count:
                    case_failures.append(
                        f'count {payload.get("count")} < min_count {min_count}'
                    )

                forbidden_hits = sorted(forbidden & set(got_list))
                if forbidden_hits:
                    case_failures.append(f'forbidden ids present: {forbidden_hits}')

                if expected_set:
                    hit = len(expected_set & got) / len(expected_set)
                    recalls.append(hit)
                    if hit < 1.0:
                        missing = sorted(expected_set - got)
                        case_failures.append(f'recall@{k}={hit:.2f} missing={missing}')
                elif min_count == 0 and payload.get('count', 0) > 0:
                    case_failures.append(f'expected empty but got {payload.get("count")} results')

                status = self.style.SUCCESS('PASS') if not case_failures else self.style.ERROR('FAIL')
                self.stdout.write(
                    f'{status} {case_id}: query={query!r} count={payload.get("count")} '
                    f'got={got_list[:k]}'
                )
                for detail in case_failures:
                    self.stdout.write(f'       - {detail}')
                    failures.append(f'{case_id}: {detail}')

        if update_baseline:
            _write_eval_document(
                queries_file,
                meta=file_meta,
                cases=updated_cases or cases,
            )
            self.stdout.write(self.style.SUCCESS(f'Baseline updated: {queries_file}'))
            return

        if not recalls and not any(c.get('min_count') == 0 for c in cases):
            raise CommandError('No evaluable cases with expected_document_ids found.')

        if recalls:
            avg_recall = sum(recalls) / len(recalls)
            self.stdout.write(self.style.SUCCESS(
                f'Average recall@{k} over {len(recalls)} cases: {avg_recall:.3f}'
            ))
            fail_under = options['fail_under']
            if fail_under is not None and avg_recall < fail_under:
                failures.append(f'average recall@{k} {avg_recall:.3f} < {fail_under}')

        if failures:
            self.stdout.write(self.style.ERROR(f'{len(failures)} failure(s)'))
            for item in failures:
                self.stdout.write(f'  - {item}')
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS('All golden queries passed.'))
