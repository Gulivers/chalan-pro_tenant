from django.core.management.base import BaseCommand
from appschedule.models import Event
from django.db.models import Count, Q

class Command(BaseCommand):
    help = "Check for duplicate Events by (crew.category, job, lot) or (crew.category, job, address)"

    def handle(self, *args, **kwargs):
        print("\n🔍 Checking for duplicate Events by crew category + job + lot...")

        duplicates_lot = (
            Event.objects
            .filter(lot__isnull=False, lot__gt="", deleted=False)
            .values('crew__category', 'job', 'lot')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        if duplicates_lot:
            self.stdout.write(self.style.ERROR("\n🚨 Duplicates found for (crew.category, job, lot):"))
            for dup in duplicates_lot:
                self.stdout.write(f" - {dup}")
        else:
            self.stdout.write(self.style.SUCCESS("✅ No duplicates found for (crew.category, job, lot)"))

        print("\n🔍 Checking for duplicate Events by crew category + job + address...")

        duplicates_address = (
            Event.objects
            .filter(address__isnull=False, address__gt="", lot__isnull=True, deleted=False)
            .values('crew__category', 'job', 'address')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        if duplicates_address:
            self.stdout.write(self.style.ERROR("\n🚨 Duplicates found for (crew.category, job, address):"))
            for dup in duplicates_address:
                self.stdout.write(f" - {dup}")
        else:
            self.stdout.write(self.style.SUCCESS("✅ No duplicates found for (crew.category, job, address)"))

        print("\n🧹 Done!")
