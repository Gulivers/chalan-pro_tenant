import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from appsearch.models import BuilderAlias
from ctrctsapp.models import Builder

DEFAULT_ALIASES_FILE = (
    Path(settings.BASE_DIR) / 'appsearch' / 'eval' / 'builder_aliases.recommended.json'
)


class Command(BaseCommand):
    help = (
        'Create or update BuilderAlias rows from a JSON file (idempotent). '
        'Default file: app/appsearch/eval/builder_aliases.recommended.json'
    )

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Tenant schema name.')
        parser.add_argument(
            '--file',
            dest='aliases_file',
            default=str(DEFAULT_ALIASES_FILE),
            help='Path to JSON array: [{"alias":"...", "builder_name":"..."}]',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show actions without writing to the database.',
        )

    def handle(self, *args, **options):
        aliases_path = Path(options['aliases_file'])
        try:
            with aliases_path.open(encoding='utf-8') as handle:
                rows = json.load(handle)
        except OSError as exc:
            raise CommandError(f'Cannot read aliases file: {exc}') from exc
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON in aliases file: {exc}') from exc

        if not isinstance(rows, list):
            raise CommandError('Aliases file must contain a JSON array.')

        created = updated = skipped = 0
        dry_run = options['dry_run']

        with schema_context(options['schema']):
            for index, row in enumerate(rows, start=1):
                alias = (row.get('alias') or '').strip()
                builder_name = (row.get('builder_name') or '').strip()
                if not alias or not builder_name:
                    self.stdout.write(self.style.WARNING(f'Row {index}: missing alias or builder_name, skipped'))
                    skipped += 1
                    continue

                builder = Builder.objects.filter(name__iexact=builder_name, is_active=True).first()
                if builder is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Row {index}: builder {builder_name!r} not found in tenant, skipped'
                        )
                    )
                    skipped += 1
                    continue

                existing = BuilderAlias.objects.filter(alias__iexact=alias).first()
                if existing and existing.builder_id == builder.id:
                    self.stdout.write(f'  OK {alias!r} → {builder.name}')
                    continue

                if dry_run:
                    action = 'update' if existing else 'create'
                    self.stdout.write(f'  [dry-run] would {action} {alias!r} → {builder.name}')
                    continue

                alias_row, was_created = BuilderAlias.objects.update_or_create(
                    alias=alias,
                    defaults={'builder': builder, 'is_active': True},
                )
                if was_created:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f'  Created {alias!r} → {builder.name}'))
                else:
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f'  Updated {alias!r} → {builder.name}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Done: created={created} updated={updated} skipped={skipped} dry_run={dry_run}'
            )
        )
