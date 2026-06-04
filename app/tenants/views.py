"""
Vistas para el sistema de onboarding y gestión de tenants
"""
import logging
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .throttles import (
    OnboardingCreateEmailThrottle,
    OnboardingCreateIPThrottle,
    OnboardingVerifyIPThrottle,
    get_client_ip,
)
from .services.captcha import get_turnstile_site_key, verify_turnstile_token
from .services.onboarding_parse import OnboardingValidationError, parse_onboarding_request
from .services.onboarding_pending import (
    complete_pending_registration,
    create_pending_registration,
    send_verification_email,
)
from .services.onboarding_provision import OnboardingProvisionError

logger = logging.getLogger(__name__)
User = get_user_model()


def _get_turnstile_token(request) -> str:
    return (
        (request.data.get('cf_turnstile_response') or '')
        or (request.data.get('turnstile_token') or '')
    ).strip()


@api_view(['GET'])
@permission_classes([AllowAny])
def onboarding_public_config(request):
    """Public config needed by the onboarding SPA (Turnstile site key)."""
    return Response({
        'turnstile_site_key': get_turnstile_site_key(),
        'email_verification_required': True,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OnboardingCreateIPThrottle, OnboardingCreateEmailThrottle])
def create_tenant_onboarding(request):
    """
    Step 1: validate onboarding payload + CAPTCHA, store pending registration,
    and send email verification before any tenant schema is created.
    """
    try:
        ok, captcha_error = verify_turnstile_token(
            _get_turnstile_token(request),
            remote_ip=get_client_ip(request),
        )
        if not ok:
            return Response({'success': False, 'error': captcha_error}, status=status.HTTP_400_BAD_REQUEST)

        data = parse_onboarding_request(request)
        logo = request.FILES.get('logo', None)
        pending = create_pending_registration(
            data,
            logo=logo,
            client_ip=get_client_ip(request) or None,
        )
        email_sent = send_verification_email(pending)

        response_payload = {
            'success': True,
            'verification_required': True,
            'message': (
                'Check your email to confirm your address and create your workspace.'
                if email_sent
                else 'Email delivery is not configured. Use the verification link logged on the server (development only).'
            ),
            'email_sent': email_sent,
            'email': data.email,
        }
        if settings.DEBUG and not email_sent:
            from tenants.services.onboarding_pending import _build_verify_url

            response_payload['debug_verify_url'] = _build_verify_url(pending.token)

        return Response(response_payload, status=status.HTTP_202_ACCEPTED)
    except OnboardingValidationError as exc:
        return Response({'success': False, 'error': exc.message}, status=exc.status_code)
    except OnboardingProvisionError as exc:
        return Response({'success': False, 'error': exc.message}, status=exc.status_code)
    except Exception as exc:
        logger.error('Error inesperado en create_tenant_onboarding: %s', exc, exc_info=True)
        return Response(
            {'success': False, 'error': f'Unexpected error while creating account: {exc}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OnboardingVerifyIPThrottle])
def verify_onboarding_email(request):
    """Step 2: verify email token and provision tenant workspace."""
    token = (request.data.get('token') or '').strip()
    if not token:
        return Response({'success': False, 'error': 'Verification token is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from uuid import UUID

        result = complete_pending_registration(UUID(token))
        return Response(result, status=status.HTTP_201_CREATED)
    except ValueError:
        return Response({'success': False, 'error': 'Invalid verification token.'}, status=status.HTTP_400_BAD_REQUEST)
    except OnboardingProvisionError as exc:
        payload = {'success': False, 'error': exc.message}
        if settings.DEBUG and exc.details:
            payload['details'] = exc.details
        return Response(payload, status=exc.status_code)
    except Exception as exc:
        logger.error('Error inesperado en verify_onboarding_email: %s', exc, exc_info=True)
        return Response(
            {'success': False, 'error': 'Unexpected error while verifying your email.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def landing_contact(request):
    """
    Public landing contact form (getjobrhythm.com). Sends email to LANDING_CONTACT_TO_EMAIL.
    """
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError as DjangoValidationError

    if not getattr(settings, 'EMAIL_HOST_PASSWORD', None):
        logger.warning('landing_contact: SMTP not configured (EMAIL_HOST_PASSWORD empty)')
        return Response(
            {'success': False, 'error': 'Email delivery is not configured.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    data = request.data
    if not isinstance(data, dict):
        return Response({'success': False, 'error': 'Invalid JSON body.'}, status=status.HTTP_400_BAD_REQUEST)

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    subject_key = (data.get('subject') or 'demo').strip()
    team_size = (data.get('team_size') or '').strip()
    message = (data.get('message') or '').strip()
    locale = (data.get('locale') or 'en').strip().lower()

    if not name or len(name) > 200:
        return Response({'success': False, 'error': 'Please provide a valid name.'}, status=status.HTTP_400_BAD_REQUEST)
    if not message or len(message) > 8000:
        return Response({'success': False, 'error': 'Please provide a message.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_email(email)
    except DjangoValidationError:
        return Response({'success': False, 'error': 'Please provide a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)
    if not phone or len(phone) < 7 or len(phone) > 40:
        return Response(
            {'success': False, 'error': 'Please provide a valid phone number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not re.fullmatch(r'[\d\s+\-().]{7,40}', phone):
        return Response(
            {'success': False, 'error': 'Please provide a valid phone number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    allowed_subjects = {'demo', 'sales', 'support'}
    if subject_key not in allowed_subjects:
        subject_key = 'demo'

    subject_labels = {
        'demo': ('Product demo request', 'Solicitud de demo de producto'),
        'sales': ('Talk to sales', 'Hablar con ventas'),
        'support': ('Support', 'Soporte'),
    }
    subj_en, subj_es = subject_labels[subject_key]
    topic = subj_es if locale == 'es' else subj_en

    to_email = settings.LANDING_CONTACT_TO_EMAIL
    mail_subject = f"[JobRhythm Contact] {topic} — {name}"

    text_body = (
        f"New contact form submission (locale={locale})\n\n"
        f"Topic: {subject_key} ({topic})\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Team size: {team_size or '—'}\n\n"
        f"Message:\n{message}\n"
    )
    safe_name = escape(name)
    safe_email = escape(email)
    safe_phone = escape(phone)
    safe_message = escape(message)
    safe_team = escape(team_size) if team_size else '—'
    html_body = (
        "<h2>JobRhythm — contact form</h2>"
        f"<p><strong>Locale:</strong> {escape(locale)}</p>"
        f"<p><strong>Topic:</strong> {escape(topic)} ({escape(subject_key)})</p>"
        f"<p><strong>Name:</strong> {safe_name}</p>"
        f"<p><strong>Email:</strong> <a href=\"mailto:{safe_email}\">{safe_email}</a></p>"
        f"<p><strong>Phone:</strong> {safe_phone}</p>"
        f"<p><strong>Team size:</strong> {safe_team}</p>"
        f"<p><strong>Message:</strong></p><pre style=\"white-space:pre-wrap;font-family:inherit\">"
        f"{safe_message}</pre>"
    )

    msg = EmailMultiAlternatives(
        mail_subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        reply_to=[email],
    )
    msg.attach_alternative(html_body, 'text/html')
    try:
        msg.send(fail_silently=False)
        logger.info(
            'landing_contact: delivered to %s (from %s, topic=%s)',
            to_email,
            email,
            subject_key,
        )
    except Exception as exc:
        logger.exception('landing_contact: send failed to %s: %s', to_email, exc)
        return Response(
            {'success': False, 'error': 'Could not send your message. Please try again later.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({'success': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Endpoint raíz de la API para el schema public."""
    return Response({
        'message': 'JobRhythm API - Public Schema',
        'version': '1.0.0',
        'endpoints': {
            'onboarding': {
                'config': {
                    'url': '/api/onboarding/config/',
                    'method': 'GET',
                },
                'request_verification': {
                    'url': '/api/onboarding/',
                    'method': 'POST',
                    'description': 'Validate signup, CAPTCHA, and send email verification (no schema created yet)',
                },
                'verify_email': {
                    'url': '/api/onboarding/verify/',
                    'method': 'POST',
                    'description': 'Confirm email token and provision tenant workspace',
                },
            },
            'admin': {
                'url': '/admin/',
                'description': 'Global admin panel to manage tenants',
            },
        },
        'documentation': {
            'onboarding': 'Open /onboarding in the frontend to create your account',
            'api_docs': 'Tenant endpoints are available after you create your account',
        },
    })
