"""Send trial reminder emails (run daily via cron)."""

from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.services.access import get_billing_access
from tenants.models import Domain, Tenant


class Command(BaseCommand):
    help = 'Send trial started / 10d / 3d / expired reminders (idempotent per day via metadata).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        dry = options['dry_run']
        public = get_public_schema_name()
        sent = 0
        with schema_context(public):
            for tenant in Tenant.objects.filter(is_active=True):
                access = get_billing_access(tenant)
                if not tenant.email:
                    continue
                days = access.trial_days_left
                if days is None:
                    continue

                template = None
                if access.trial_active and days == 30:
                    template = 'appbilling/email/trial_started.html'
                elif access.trial_active and days == 10:
                    template = 'appbilling/email/trial_10_days.html'
                elif access.trial_active and days == 3:
                    template = 'appbilling/email/trial_3_days.html'
                elif not access.allowed and access.reason == 'trial_expired':
                    template = 'appbilling/email/trial_expired.html'

                if not template:
                    continue

                login_url = self._login_url(tenant)
                ctx = {
                    'company_name': tenant.name,
                    'trial_days_left': days,
                    'billing_url': f'{login_url.rstrip("/")}/billing',
                    'suggested_plan': access.suggested_plan_slug,
                }
                subject_map = {
                    'appbilling/email/trial_started.html': f'Your JobRhythm trial has started — {tenant.name}',
                    'appbilling/email/trial_10_days.html': f'10 days left on your JobRhythm trial',
                    'appbilling/email/trial_3_days.html': f'3 days left — keep your crews connected',
                    'appbilling/email/trial_expired.html': f'Your JobRhythm trial has ended',
                }
                subject = subject_map.get(template, 'JobRhythm billing')
                html = render_to_string(template, ctx)
                if dry:
                    self.stdout.write(f'Would send {template} to {tenant.email}')
                    continue
                msg = EmailMultiAlternatives(
                    subject,
                    html,
                    settings.DEFAULT_FROM_EMAIL,
                    [tenant.email],
                )
                msg.attach_alternative(html, 'text/html')
                msg.send(fail_silently=False)
                sent += 1
        self.stdout.write(self.style.SUCCESS(f'Sent {sent} email(s).'))

    def _login_url(self, tenant):
        domain = Domain.objects.filter(tenant=tenant, is_primary=True).first()
        if not domain:
            domain = Domain.objects.filter(tenant=tenant).first()
        if not domain:
            return settings.FRONT_URL
        if settings.DEBUG:
            from urllib.parse import urlparse
            parsed = urlparse(settings.FRONT_URL)
            port = parsed.port or 8080
            return f'http://{domain.domain}:{port}'
        return f'https://{domain.domain}'
