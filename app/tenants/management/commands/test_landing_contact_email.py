"""
Envía un correo de prueba al buzón del formulario de contacto (LANDING_CONTACT_TO_EMAIL).

Uso:
  python manage.py test_landing_contact_email
  python manage.py test_landing_contact_email --to team@jobrhythm.net
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Prueba SMTP y destino LANDING_CONTACT_TO_EMAIL (formulario landing).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            default='',
            help='Sobrescribe LANDING_CONTACT_TO_EMAIL para esta prueba',
        )

    def handle(self, *args, **options):
        if not getattr(settings, 'EMAIL_HOST_PASSWORD', None):
            self.stderr.write(
                self.style.ERROR('EMAIL_HOST_PASSWORD no está configurado.')
            )
            return

        to_email = (options['to'] or '').strip() or settings.LANDING_CONTACT_TO_EMAIL
        subject = '[JobRhythm] Test landing contact form'
        body = (
            'This is a test message from manage.py test_landing_contact_email.\n'
            f'Configured recipient: {settings.LANDING_CONTACT_TO_EMAIL}\n'
            f'From: {settings.DEFAULT_FROM_EMAIL}\n'
            f'SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}\n'
        )

        msg = EmailMultiAlternatives(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
        )
        msg.send(fail_silently=False)
        self.stdout.write(
            self.style.SUCCESS(f'Correo de prueba enviado a {to_email}')
        )
