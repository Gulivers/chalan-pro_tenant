"""
Shift schedule + contract dates forward/backward for demo tenants.

Maps an anchor calendar day onto a target day (default: today) and applies
the same day offset to Event / EventDraft (and optionally Contract timestamps).

IMPORTANT — keep Mon–Fri weeks (schedule):
  Do NOT advance demos with --days 1 each calendar day.
  That moves Friday→Saturday and leaves the next Monday empty (weekend gap).
  Always move in full weeks: Monday→Monday (+7 days), same weekday.

Examples (ubuntu-house / docker-compose.dev.yml):

  # Dry-run: schedule + contracts (default)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 --days 7 --shift-timestamps

  # RECOMMENDED: advance one demo week (events + contracts)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 --days 7 --shift-timestamps --apply

  # Only contracts (e.g. catch-up after schedule was already shifted)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 --days 217 --contracts-only --apply

  # Only schedule
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 --days 7 --schedule-only --shift-timestamps --apply

  # Explicit Mondays (anchor = a Monday currently in the DB)
  docker compose -f docker-compose.dev.yml exec backend \\
    python manage.py shift_schedule_dates \\
      --schema division16 \\
      --anchor-date 2026-07-20 --target-date 2026-07-27 \\
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
from ctrctsapp.models import Contract


class Command(BaseCommand):
    help = (
        "Shift schedule Event/EventDraft dates and/or Contract date_created/"
        "last_updated by mapping --anchor-date onto --target-date (or by --days). "
        "Intended for demo tenants (e.g. division16)."
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
            help="Also shift Event/EventDraft created_at/updated_at by the same offset "
            "(UI cards show updated_at under the title). Contracts always shift "
            "date_created/last_updated when contracts are included.",
        )
        parser.add_argument(
            "--schedule-only",
            action="store_true",
            help="Only shift Event/EventDraft (skip contracts).",
        )
        parser.add_argument(
            "--contracts-only",
            action="store_true",
            help="Only shift Contract date_created/last_updated (skip schedule).",
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
        schedule_only = options["schedule_only"]
        contracts_only = options["contracts_only"]

        if schedule_only and contracts_only:
            raise CommandError("Use only one of --schedule-only / --contracts-only")

        do_schedule = not contracts_only
        do_contracts = not schedule_only

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
                    if not anchor and do_contracts:
                        # Infer from contracts if schedule empty / contracts-only
                        latest = (
                            Contract.objects.order_by("-date_created")
                            .values_list("date_created", flat=True)
                            .first()
                        )
                        anchor = latest.date() if latest else None
                    if not anchor:
                        raise CommandError(
                            "No events/contracts found; cannot infer --anchor-date"
                        )
                if options["target_date"]:
                    target = self._parse_date(options["target_date"], "target-date")
                else:
                    target = timezone.localdate()
                delta_days = (target - anchor).days

            delta = timedelta(days=delta_days)

            n_events = Event.objects.count() if do_schedule else 0
            n_drafts = EventDraft.objects.count() if do_schedule else 0
            n_contracts = Contract.objects.count() if do_contracts else 0

            self.stdout.write(self.style.NOTICE(f"Schema: {schema}"))
            self.stdout.write(
                f"Scope: schedule={'yes' if do_schedule else 'no'} | "
                f"contracts={'yes' if do_contracts else 'no'}"
            )
            if do_schedule:
                min_date = Event.objects.order_by("date").values_list("date", flat=True).first()
                max_date = Event.objects.order_by("-date").values_list("date", flat=True).first()
                self.stdout.write(f"Events: {n_events} | Drafts: {n_drafts}")
                self.stdout.write(f"Schedule range: {min_date} → {max_date}")
            if do_contracts:
                c_min = (
                    Contract.objects.order_by("date_created")
                    .values_list("date_created", flat=True)
                    .first()
                )
                c_max = (
                    Contract.objects.order_by("-date_created")
                    .values_list("date_created", flat=True)
                    .first()
                )
                self.stdout.write(f"Contracts: {n_contracts}")
                self.stdout.write(
                    f"Contract date_created range: "
                    f"{c_min.date() if c_min else None} → {c_max.date() if c_max else None}"
                )

            if anchor is not None and target is not None:
                self.stdout.write(
                    f"Mapping: {anchor.isoformat()} → {target.isoformat()} "
                    f"(offset {delta_days:+d} days)"
                )
            else:
                self.stdout.write(f"Offset: {delta_days:+d} days")
            self.stdout.write(f"Shift event timestamps: {shift_ts}")
            self.stdout.write(f"Mode: {'APPLY' if apply else 'DRY-RUN'}")

            if do_schedule:
                sample_before = list(
                    Event.objects.filter(
                        date__gte=date(2025, 12, 14), date__lte=date(2025, 12, 16)
                    )
                    .order_by("date", "id")
                    .values("id", "date", "end_dt", "title")[:5]
                )
                if not sample_before and target:
                    sample_before = list(
                        Event.objects.filter(
                            date__gte=target - timedelta(days=1),
                            date__lte=target + timedelta(days=1),
                        )
                        .order_by("date", "id")
                        .values("id", "date", "end_dt", "title")[:5]
                    )
                if sample_before:
                    self.stdout.write("Sample events (before):")
                    for row in sample_before:
                        self.stdout.write(
                            f"  #{row['id']} {row['date']}→{row['date'] + delta} "
                            f"| {row['title']}"
                        )

            if do_contracts:
                sample_c = list(
                    Contract.objects.order_by("-date_created").values(
                        "id", "date_created", "doc_type", "type", "lot"
                    )[:5]
                )
                if sample_c:
                    self.stdout.write("Sample contracts (before):")
                    for row in sample_c:
                        new_dt = row["date_created"] + delta
                        self.stdout.write(
                            f"  #{row['id']} {row['date_created'].date()}→{new_dt.date()} "
                            f"| {row['doc_type']}/{row['type']} lot={row['lot']}"
                        )

            if delta_days == 0:
                self.stdout.write(self.style.WARNING("Offset is 0; nothing to do."))
                return

            if not apply:
                self.stdout.write(
                    self.style.WARNING(
                        "Dry-run only. Re-run with --apply to persist."
                    )
                )
                return

            events_updated = drafts_updated = dups_fixed = contracts_updated = 0

            with transaction.atomic():
                with connection.cursor() as cur:
                    if do_schedule:
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

                    if do_contracts:
                        # Contracts: date_created / last_updated are the demo dates
                        cur.execute(
                            """
                            UPDATE ctrctsapp_contract
                            SET date_created = date_created + (%(d)s * INTERVAL '1 day'),
                                last_updated = last_updated + (%(d)s * INTERVAL '1 day')
                            """,
                            {"d": delta_days},
                        )
                        contracts_updated = cur.rowcount

            parts = []
            if do_schedule:
                parts.append(f"events={events_updated}")
                parts.append(f"drafts={drafts_updated}")
                if dups_fixed:
                    parts.append(f"resolved_dups={dups_fixed}")
                new_min = Event.objects.order_by("date").values_list("date", flat=True).first()
                new_max = Event.objects.order_by("-date").values_list("date", flat=True).first()
                parts.append(f"schedule_range={new_min}→{new_max}")
            if do_contracts:
                parts.append(f"contracts={contracts_updated}")
                c_min = (
                    Contract.objects.order_by("date_created")
                    .values_list("date_created", flat=True)
                    .first()
                )
                c_max = (
                    Contract.objects.order_by("-date_created")
                    .values_list("date_created", flat=True)
                    .first()
                )
                parts.append(
                    f"contract_range="
                    f"{c_min.date() if c_min else None}→{c_max.date() if c_max else None}"
                )

            self.stdout.write(self.style.SUCCESS("Updated " + ", ".join(parts)))
