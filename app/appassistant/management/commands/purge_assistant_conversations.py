"""
Purge expired JobRhythm Assistant conversations (and optionally old query logs).

Retention policy (D2):
  - Conversational state is reusable for 24h of inactivity (enforced in app code).
  - Hard-delete conversations whose last_activity_at is older than 14 days.
  - Related AssistantQueryLog.conversation is SET_NULL; logs may be purged too.

Ops / cron (no Celery in this stage):
  Schedule periodically on each environment, for every tenant schema, e.g.:

    # Example daily cron on ubuntu-house / VPS (adjust paths and tenant loop):
    # 15 3 * * * cd /path/to/chalanpro && docker compose -f docker-compose.dev.yml \\
    #   exec -T backend python manage.py purge_assistant_conversations --days=14

  For django-tenants, run with a tenant schema context (tenant_command or
  iterate tenants). Example with django_tenants:

    python manage.py tenant_command purge_assistant_conversations --schema=demo

Dry-run is the default when --commit is omitted? No: default is commit=False
via --dry-run flag for safety.
"""

from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from appassistant.models import AssistantConversation, AssistantQueryLog
from appassistant.services.conversation_state import CONVERSATION_RETENTION


class Command(BaseCommand):
    help = (
        'Delete AssistantConversation rows older than the retention window. '
        'Documented for cron/ops; Celery is not required for Level-1 continuity.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=CONVERSATION_RETENTION.days,
            help=f'Retention days (default {CONVERSATION_RETENTION.days}).',
        )
        parser.add_argument(
            '--purge-logs',
            action='store_true',
            help='Also delete AssistantQueryLog rows older than --days.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print counts without deleting.',
        )

    def handle(self, *args, **options):
        days = options['days']
        if days < 1:
            self.stderr.write('--days must be >= 1')
            return

        cutoff = timezone.now() - timedelta(days=days)
        conv_qs = AssistantConversation.objects.filter(last_activity_at__lt=cutoff)
        conv_count = conv_qs.count()

        log_count = 0
        log_qs = None
        if options['purge_logs']:
            log_qs = AssistantQueryLog.objects.filter(created_at__lt=cutoff)
            log_count = log_qs.count()

        if options['dry_run']:
            self.stdout.write(
                f'[dry-run] would delete {conv_count} conversation(s) '
                f'and {log_count} query log(s) older than {days} day(s) '
                f'(cutoff={cutoff.isoformat()}).'
            )
            return

        deleted_conv, _ = conv_qs.delete()
        deleted_logs = 0
        if log_qs is not None:
            deleted_logs, _ = log_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Purged conversations={deleted_conv}, query_logs={deleted_logs} '
                f'(retention_days={days}).'
            )
        )
