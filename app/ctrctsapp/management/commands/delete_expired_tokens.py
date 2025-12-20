from django.core.management.base import BaseCommand
from datetime import timedelta, datetime
from rest_framework_expiring_authtoken.models import ExpiringToken

class Command(BaseCommand):
    help = 'Delete expired tokens from the database'

    def handle(self, *args, **kwargs):
        expiration_time = timedelta(hours=8)  # Set the expiration time here
        tokens_deleted = ExpiringToken.objects.filter(
            created__lt=datetime.now() - expiration_time
        ).delete()

        self.stdout.write(self.style.SUCCESS(f'{tokens_deleted[0]} expired tokens deleted'))
