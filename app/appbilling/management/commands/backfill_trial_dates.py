"""Backfill trial_start/trial_end for existing tenants."""

from datetime import datetime, time as dt_time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.services.trial import TRIAL_DAYS, start_trial_for_tenant
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Set trial_start and trial_end on tenants missing them (30 days from created_on or now).'

    def handle(self, *args, **options):
        public = get_public_schema_name()
        updated = 0
        with schema_context(public):
            for tenant in Tenant.objects.all():
                if tenant.trial_end:
                    continue
                if tenant.created_on:
                    start = timezone.make_aware(
                        datetime.combine(tenant.created_on, dt_time.min)
                    )
                    tenant.trial_start = start
                    tenant.trial_end = start + timedelta(days=TRIAL_DAYS)
                else:
                    start_trial_for_tenant(tenant)
                tenant.on_trial = timezone.now() < tenant.trial_end
                tenant.save(update_fields=['trial_start', 'trial_end', 'on_trial'])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Backfilled {updated} tenant(s).'))
