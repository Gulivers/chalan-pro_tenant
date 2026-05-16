"""
Password reset helpers (system-level account management).
Uses Django's AUTH_PASSWORD_VALIDATORS via validate_password.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import connection
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_tenants.utils import get_public_schema_name

User = get_user_model()

PASSWORD_RESET_EMAIL_TEMPLATE = "account/forgot_password_instructions.html"


def frontend_base_url_for_password_reset(request):
    """
    Base URL for password-reset links: the same origin the user used (tenant host),
    not settings.FRONT_URL. If the request hits api.<TENANT_BASE_DOMAIN>, use the
    tenant's primary domain from tenants_domain.
    """
    meta = request.META
    proto = (meta.get("HTTP_X_FORWARDED_PROTO") or "").split(",")[0].strip().lower()
    if not proto:
        proto = "https" if request.is_secure() else "http"

    forwarded_host = (meta.get("HTTP_X_FORWARDED_HOST") or "").split(",")[0].strip()
    try:
        host = forwarded_host or request.get_host()
    except Exception:
        host = forwarded_host

    if not host:
        return settings.FRONT_URL.rstrip("/")

    tenant_base = (getattr(settings, "TENANT_BASE_DOMAIN", "") or "").lower()
    host_lc = host.lower()
    if ":" in host_lc:
        host_lc = host_lc.split(":")[0]

    api_hosts = {f"api.{tenant_base}", f"www.api.{tenant_base}"} if tenant_base else set()
    if tenant_base and host_lc in api_hosts:
        tenant = getattr(connection, "tenant", None)
        if tenant is not None and getattr(tenant, "schema_name", None) != get_public_schema_name():
            from tenants.models import Domain

            dom = (
                Domain.objects.filter(tenant=tenant, is_primary=True).first()
                or Domain.objects.filter(tenant=tenant).first()
            )
            if dom:
                return f"{proto}://{dom.domain}".rstrip("/")

    return f"{proto}://{host}".rstrip("/")


def build_password_reset_url(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    base = frontend_base_url_for_password_reset(request)
    return f"{base}/reset-password-confirm?uid={uid}&token={token}", uid, token


def send_password_reset_email(request, user, email):
    reset_url, _uid, _token = build_password_reset_url(request, user)
    text = (
        f"Hello {user.username}!\n\n\n"
        "Someone requested a link to change your password. "
        f"Click the link below to proceed.\n\n\n{reset_url}"
    )
    html_content = render_to_string(
        PASSWORD_RESET_EMAIL_TEMPLATE,
        context={"username": user.username, "reset_url": reset_url},
    )
    msg = EmailMultiAlternatives(
        "Reset password instructions",
        text,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def collect_password_validation_errors(user, new_password, confirm_password):
    """
    Run Django password validators and confirm-password check.
    Returns dict[field_name, list[str]] suitable for JSON 400 responses.
    """
    errors = {}

    if new_password is None or new_password == "":
        errors.setdefault("new_password", []).append("This field is required.")
    if confirm_password is None or confirm_password == "":
        errors.setdefault("confirm_password", []).append("This field is required.")

    if new_password and confirm_password is not None and new_password != confirm_password:
        errors.setdefault("confirm_password", []).append(
            "Password confirmation does not match."
        )

    if new_password:
        try:
            validate_password(new_password, user=user)
        except ValidationError as exc:
            errors.setdefault("new_password", []).extend(list(exc.messages))

    return errors


def apply_password_reset(user, new_password):
    """Validate and persist a new password (caller must verify token first)."""
    user.set_password(new_password)
    user.save(update_fields=["password"])
