"""
Shift schedule event dates forward/backward for demo tenants.

Maps an anchor calendar day onto a target day (default: today) and applies
the same day offset to all Event / EventDraft dates (and optionally timestamps).

IMPORTANT — keep Mon–Fri weeks:
  Do NOT advance demos with --days 1 each calendar day.
  That moves Friday→Saturday and leaves the next Monday empty (weekend gap).
  Always move in full weeks: Monday→Monday (+7 days), same weekday.

Examples (ubuntu-house / docker-compose.dev.yml):

  # Dry-run first (no DB writes)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 --days 7 --shift-timestamps

  # RECOMMENDED: advance one demo week (Mon–Fri block stays Mon–Fri)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 --days 7 --shift-timestamps --apply

  # Same idea with explicit Mondays (anchor = a Monday currently in the DB)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 \\
      --anchor-date 2026-07-20 --target-date 2026-07-27 \\
      --shift-timestamps --apply

  # Initial load style: map an old Monday onto a target Monday
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 \\
      --anchor-date 2025-12-15 --target-date 2026-07-20 \\
      --shift-timestamps --apply

  # Fix weekday drift only (e.g. Tue–Sat → Mon–Fri)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 --days -1 --shift-timestamps --apply

Without Docker (inside the backend container / venv):
  python manage.py shift_schedule_dates --schema division16 --days 7 --shift-timestamps --apply
"""
from __future__ import annotations

from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from appschedule.models import Event, EventDraft


class Command(BaseCommand):
    help = (
        "Shift schedule Event/EventDraft dates by mapping --anchor-date onto "
        "--target-date (or by --days). Intended for demo tenants (e.g. division16)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            required=True,
            help="Tenant schema name (e.g. division16)",
        )
        parser.add_argument(
            "--anchor-date",
            type=str,
            default=None,
            help="Source calendar day that should become the target "
            "(YYYY-MM-DD). Default: max(Event.date) in the schema.",
        )
        parser.add_argument(
            "--target-date",
            type=str,
            default=None,
            help="Destination day for the anchor (YYYY-MM-DD). Default: today (local).",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Explicit day offset (positive = forward). Overrides anchor/target.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist changes (default is dry-run).",
        )
        parser.add_argument(
            "--shift-timestamps",
            action="store_true",
            help="Also shift created_at/updated_at by the same offset "
            "(UI cards show updated_at under the title).",
        )
    def _parse_date(self, value: str, label: str) -> date:
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise CommandError(f"Invalid {label}: {value!r} (use YYYY-MM-DD)") from exc

    def handle(self, *args, **options):
        schema = options["schema"].strip()
        apply = options["apply"]
        shift_ts = options["shift_timestamps"]

        # Validate schema exists
        with connection.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
                [schema],
            )
            if not cur.fetchone():
                raise CommandError(f"Schema not found: {schema}")

        with schema_context(schema):
            if options["days"] is not None:
                delta_days = options["days"]
                anchor = None
                target = None
            else:
                if options["anchor_date"]:
                    anchor = self._parse_date(options["anchor_date"], "anchor-date")
                else:
                    anchor = (
                        Event.objects.order_by("-date")
                        .values_list("date", flat=True)
                        .first()
                    )
                    if not anchor:
                        raise CommandError("No events found; cannot infer --anchor-date")
                if options["target_date"]:
                    target = self._parse_date(options["target_date"], "target-date")
                else:
                    target = timezone.localdate()
                delta_days = (target - anchor).days

            delta = timedelta(days=delta_days)

            qs_e = Event.objects.all()
            qs_d = EventDraft.objects.all()
            n_events = qs_e.count()
            n_drafts = qs_d.count()

            sample_before = list(
                qs_e.filter(date__gte=date(2025, 12, 14), date__lte=date(2025, 12, 16))
                .order_by("date", "id")
                .values("id", "date", "end_dt", "title")[:8]
            )
            # If already shifted, show samples around target week instead
            if not sample_before and target:
                sample_before = list(
                    qs_e.filter(
                        date__gte=target - timedelta(days=1),
                        date__lte=target + timedelta(days=1),
                    )
                    .order_by("date", "id")
                    .values("id", "date", "end_dt", "title")[:8]
                )

            min_date = qs_e.order_by("date").values_list("date", flat=True).first()
            max_date = qs_e.order_by("-date").values_list("date", flat=True).first()

            self.stdout.write(self.style.NOTICE(f"Schema: {schema}"))
            self.stdout.write(f"Events: {n_events} | Drafts: {n_drafts}")
            self.stdout.write(f"Current range: {min_date} → {max_date}")
            if anchor is not None and target is not None:
                self.stdout.write(
                    f"Mapping: {anchor.isoformat()} → {target.isoformat()} "
                    f"(offset {delta_days:+d} days)"
                )
            else:
                self.stdout.write(f"Offset: {delta_days:+d} days")
            self.stdout.write(f"Shift timestamps: {shift_ts}")
            self.stdout.write(f"Mode: {'APPLY' if apply else 'DRY-RUN'}")

            if sample_before:
                self.stdout.write("Sample (before):")
                for row in sample_before:
                    new_d = row["date"] + delta
                    new_e = row["end_dt"] + delta
                    self.stdout.write(
                        f"  #{row['id']} {row['date']}→{new_d} "
                        f"end {row['end_dt']}→{new_e} | {row['title']}"
                    )

            if delta_days == 0:
                self.stdout.write(self.style.WARNING("Offset is 0; nothing to do."))
                return

            if not apply:
                self.stdout.write(
                    self.style.WARNING(
                        "Dry-run only. Re-run with --apply to persist "
                        "(recommended: --shift-timestamps for demo cards)."
                    )
                )
                return

            with transaction.atomic():
                # Drop unique (crew,date,title) while shifting: soft-deleted rows and
                # consecutive absences (DAY OFF / VACATION) can collide on small offsets.
                with connection.cursor() as cur:
                    cur.execute(
                        """
                        ALTER TABLE appschedule_event
                        DROP CONSTRAINT IF EXISTS uniq_event_crew_date_title
                        """
                    )

                    if shift_ts:
                        cur.execute(
                            """
                            UPDATE appschedule_event
                            SET date = date + %(d)s,
                                end_dt = end_dt + %(d)s,
                                created_at = created_at + (%(d)s * INTERVAL '1 day'),
                                updated_at = updated_at + (%(d)s * INTERVAL '1 day')
                            """,
                            {"d": delta_days},
                        )
                    else:
                        cur.execute(
                            """
                            UPDATE appschedule_event
                            SET date = date + %(d)s,
                                end_dt = end_dt + %(d)s
                            """,
                            {"d": delta_days},
                        )
                    events_updated = cur.rowcount

                    if shift_ts:
                        cur.execute(
                            """
                            UPDATE appschedule_eventdraft
                            SET date = date + %(d)s,
                                end_dt = end_dt + %(d)s,
                                created_at = created_at + (%(d)s * INTERVAL '1 day'),
                                updated_at = updated_at + (%(d)s * INTERVAL '1 day')
                            """,
                            {"d": delta_days},
                        )
                    else:
                        cur.execute(
                            """
                            UPDATE appschedule_eventdraft
                            SET date = date + %(d)s,
                                end_dt = end_dt + %(d)s
                            """,
                            {"d": delta_days},
                        )
                    drafts_updated = cur.rowcount

                    cur.execute(
                        """
                        WITH dups AS (
                          SELECT id,
                                 row_number() OVER (
                                   PARTITION BY crew_id, date, title
                                   ORDER BY deleted ASC, id ASC
                                 ) AS rn
                          FROM appschedule_event
                        )
                        UPDATE appschedule_event e
                        SET deleted = true,
                            title = left(e.title || ' [DUP-' || e.id || ']', 255)
                        FROM dups d
                        WHERE e.id = d.id AND d.rn > 1
                        """
                    )
                    dups_fixed = cur.rowcount

                    cur.execute(
                        """
                        ALTER TABLE appschedule_event
                        ADD CONSTRAINT uniq_event_crew_date_title
                        UNIQUE (crew_id, date, title)
                        """
                    )

            new_min = Event.objects.order_by("date").values_list("date", flat=True).first()
            new_max = Event.objects.order_by("-date").values_list("date", flat=True).first()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated events={events_updated}, drafts={drafts_updated}"
                    f"{f', resolved_dups={dups_fixed}' if dups_fixed else ''}. "
                    f"New range: {new_min} → {new_max}"
                )
            )
