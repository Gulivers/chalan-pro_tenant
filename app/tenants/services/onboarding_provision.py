"""Create tenant workspace after email verification."""
from __future__ import annotations

import logging
import os
import secrets
import string
from typing import Any, Optional

from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

from tenants.models import Domain, Tenant
from tenants.services.onboarding_parse import OnboardingFormData

logger = logging.getLogger(__name__)
User = get_user_model()


class OnboardingProvisionError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def _send_onboarding_welcome_email(
    *,
    recipient_email: str,
    company_name: str,
    login_url: str,
    username: str,
    temp_password: str,
    user_chose_strong_password: bool,
    admin_name: Optional[str],
) -> None:
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string

    admin_display = (admin_name or '').strip() or None
    context = {
        'company_name': company_name,
        'login_url': login_url,
        'username': username,
        'temp_password': temp_password,
        'user_chose_strong_password': user_chose_strong_password,
        'admin_display_name': admin_display,
    }
    text_body = (
        f"Your JobRhythm workspace is ready.\n\n"
        f"Company: {company_name}\n"
        f"Username: {username}\n"
        f"Sign-in link: {login_url}\n\n"
    )
    if user_chose_strong_password:
        text_body += 'Use the password you set during signup.\n'
    else:
        text_body += f'Temporary password: {temp_password}\n'
    html_body = render_to_string('onboarding_welcome_email.html', context)
    msg = EmailMultiAlternatives(
        'Your JobRhythm workspace is ready',
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
    )
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=False)


def provision_tenant_workspace(data: OnboardingFormData, logo=None) -> dict[str, Any]:
    company_name = data.company_name
    email = data.email
    client_type = data.client_type
    address = data.address
    preferences = data.preferences
    monthly_operations = data.monthly_operations
    crew_count = data.crew_count
    recommended_plan = data.recommended_plan
    landing_selected_plan = data.landing_selected_plan
    admin_name = data.admin_name
    admin_password = data.admin_password

    if Tenant.objects.filter(email=email).exists():
        raise OnboardingProvisionError(
            'This email is already registered. Please use a different email.'
        )
    if Tenant.objects.filter(name__iexact=company_name).exists():
        raise OnboardingProvisionError(
            'This company name is already registered. Please choose a different name.'
        )

    logger.info('Iniciando creación de tenant: %s', company_name)
    temp_tenant = Tenant(name=company_name, email=email, client_type=client_type)
    schema_name = temp_tenant._generate_schema_name()
    tenant_id = temp_tenant._generate_tenant_id()

    tenant = Tenant(
        name=company_name,
        email=email,
        client_type=client_type,
        logo=logo,
        address=address,
        preferences=preferences,
        monthly_operations=monthly_operations,
        crew_count=crew_count,
        recommended_plan=recommended_plan,
        landing_selected_plan=landing_selected_plan,
        schema_name=schema_name,
        tenant_id=tenant_id,
        on_trial=True,
        is_active=True,
    )
    from appbilling.services.trial import start_trial_for_tenant

    start_trial_for_tenant(tenant)

    try:
        tenant.full_clean()
        tenant.save()
        logger.info('Tenant guardado: %s (%s)', tenant.name, tenant.schema_name)
    except Exception as exc:
        logger.error('Error al crear tenant: %s', exc, exc_info=True)
        import traceback

        details = traceback.format_exc() if settings.DEBUG else str(exc)
        raise OnboardingProvisionError(
            f'Could not create tenant: {exc}',
            status_code=400,
            details=details,
        ) from exc

    base_domain = getattr(settings, 'TENANT_BASE_DOMAIN', 'jobrhythm.net')
    subdomain = tenant.schema_to_subdomain()
    domain_name = f'{subdomain}.{base_domain}'

    if Domain.objects.filter(domain=domain_name).exists():
        counter = 1
        while Domain.objects.filter(domain=f'{subdomain}{counter}.{base_domain}').exists():
            counter += 1
        domain_name = f'{subdomain}{counter}.{base_domain}'

    try:
        Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)
    except Exception as exc:
        logger.error('Error al crear dominio: %s', exc, exc_info=True)
        try:
            tenant.delete()
        except Exception:
            pass
        raise OnboardingProvisionError(
            f'Could not create domain: {exc}',
            status_code=500,
        ) from exc

    try:
        from project.middleware.dynamic_hosts_utils import refresh_dynamic_domains

        refresh_dynamic_domains()
    except Exception as exc:
        logger.warning('No se pudo actualizar dominios dinámicos: %s', exc)

    try:
        from django.db import connection

        connection.ensure_connection()
        if hasattr(connection, 'commit'):
            connection.commit()
    except Exception as exc:
        logger.debug('Commit explícito (opcional): %s', exc)

    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.schemata
                    WHERE schema_name = %s
                )
                """,
                [tenant.schema_name],
            )
            schema_exists = cursor.fetchone()[0]
        if not schema_exists:
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{tenant.schema_name}"')
    except Exception as exc:
        raise OnboardingProvisionError(
            f'Could not verify tenant schema: {exc}',
            status_code=500,
        ) from exc

    try:
        try:
            call_command('migrate_schemas', schema=tenant.schema_name, verbosity=1)
        except Exception as e1:
            try:
                with schema_context(tenant.schema_name):
                    call_command('migrate', verbosity=1, interactive=False)
            except Exception as e2:
                try:
                    if hasattr(tenant, 'create_schema'):
                        tenant.create_schema(check_if_exists=True)
                        with schema_context(tenant.schema_name):
                            call_command('migrate', verbosity=1, interactive=False)
                    else:
                        raise Exception('create_schema not available') from e2
                except Exception as e3:
                    try:
                        tenant.delete()
                    except Exception:
                        pass
                    raise OnboardingProvisionError(
                        'Could not run migrations for the new tenant.',
                        status_code=500,
                        details=f'migrate_schemas ({e1}); schema_context ({e2}); create_schema ({e3})',
                    ) from e3
    except OnboardingProvisionError:
        raise
    except Exception as exc:
        raise OnboardingProvisionError(
            f'Unexpected error while running migrations: {exc}',
            status_code=500,
        ) from exc

    username = email.split('@')[0]
    if admin_name:
        name_parts = admin_name.split()
        if name_parts:
            username = name_parts[0]

    counter = 1
    original_username = username
    temp_password = ''
    user_chose_strong_password = False
    expose_generated_password = False
    email_sent = False

    with schema_context(tenant.schema_name):
        fixture_doc_types = os.path.join(
            settings.BASE_DIR,
            'apptransactions',
            'fixtures',
            'masters_document_type.json',
        )
        if os.path.exists(fixture_doc_types):
            try:
                call_command('loaddata', fixture_doc_types, verbosity=0)
            except Exception as exc:
                logger.error('Error al cargar masters_document_type.json: %s', exc, exc_info=True)

        while User.objects.filter(username=username).exists():
            username = f'{original_username}{counter}'
            counter += 1

        alphabet = string.ascii_letters + string.digits + '!@#$%'
        if admin_password and len(admin_password) >= 8:
            temp_password = admin_password
            user_chose_strong_password = True
        elif admin_password:
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        else:
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        user_kwargs = {
            'username': username,
            'email': email,
            'password': temp_password,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
        if admin_name:
            name_parts = admin_name.split(maxsplit=1)
            user_kwargs['first_name'] = name_parts[0]
            if len(name_parts) > 1:
                user_kwargs['last_name'] = name_parts[1]

        user = User.objects.create_user(**user_kwargs)

        if settings.DEBUG:
            from urllib.parse import urlparse

            front_url_parsed = urlparse(settings.FRONT_URL)
            frontend_port = front_url_parsed.port if front_url_parsed.port else 8080
            redirect_url = f'http://{domain_name}:{frontend_port}/login/'
        else:
            redirect_url = f'https://{domain_name}/login/'

        if getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
            try:
                _send_onboarding_welcome_email(
                    recipient_email=email,
                    company_name=company_name,
                    login_url=redirect_url,
                    username=username,
                    temp_password=temp_password,
                    user_chose_strong_password=user_chose_strong_password,
                    admin_name=admin_name,
                )
                email_sent = True
            except Exception as exc:
                logger.exception('No se pudo enviar el correo de onboarding: %s', exc)

        expose_generated_password = (
            not user_chose_strong_password and (settings.DEBUG or not email_sent)
        )

    cred_message = (
        'Check your email to continue.'
        if email_sent
        else (
            'Save these credentials; we could not send the confirmation email.'
            if not user_chose_strong_password
            else 'Your password was set successfully.'
        )
    )

    return {
        'success': True,
        'message': 'Your account was created successfully. Redirecting to your workspace…',
        'url': redirect_url,
        'email_sent': email_sent,
        'tenant': {
            'name': tenant.name,
            'schema_name': tenant.schema_name,
            'domain': domain_name,
            'username': username,
            'email': email,
            'admin_name': admin_name or user.get_full_name() or username,
            'preferences': preferences,
            'monthly_operations': tenant.monthly_operations,
            'crew_count': tenant.crew_count,
            'recommended_plan': tenant.recommended_plan,
            'landing_selected_plan': tenant.landing_selected_plan,
            'temp_password': temp_password if expose_generated_password else None,
        },
        'credentials': {
            'username': username,
            'password': temp_password if expose_generated_password else None,
            'password_provided': bool(admin_password),
            'message': cred_message,
        },
    }
