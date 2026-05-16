import json
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from appcore.services.password_reset import (
    apply_password_reset,
    collect_password_validation_errors,
    send_password_reset_email,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def _parse_json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return None


@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    data = _parse_json_body(request)
    if data is None:
        return JsonResponse(
            {"non_field_errors": ["Invalid request body."]},
            status=400,
        )

    email = (data.get("email") or "").strip()
    if not email:
        return JsonResponse(
            {"email": ["This field is required."]},
            status=400,
        )

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse(
            {"non_field_errors": ["Unable to process password reset for this email."]},
            status=404,
        )

    try:
        send_password_reset_email(request, user, email)
    except Exception:
        logger.exception("Failed to send password reset email for user pk=%s", user.pk)
        return JsonResponse(
            {
                "non_field_errors": [
                    "Could not send the reset email. Please try again later."
                ]
            },
            status=500,
        )

    return JsonResponse({"message": "Email sent"}, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request, uidb64, token):
    data = _parse_json_body(request)
    if data is None:
        return JsonResponse(
            {"non_field_errors": ["Invalid request body."]},
            status=400,
        )

    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, UnicodeDecodeError, OverflowError):
        return JsonResponse(
            {
                "non_field_errors": [
                    "Invalid or expired reset link. Please request a new one."
                ]
            },
            status=400,
        )

    if not default_token_generator.check_token(user, token):
        return JsonResponse(
            {
                "non_field_errors": [
                    "Invalid or expired reset link. Please request a new one."
                ]
            },
            status=400,
        )

    field_errors = collect_password_validation_errors(
        user, new_password, confirm_password
    )
    if field_errors:
        return JsonResponse(field_errors, status=400)

    try:
        apply_password_reset(user, new_password)
    except Exception:
        logger.exception("Failed to reset password for user pk=%s", user.pk)
        return JsonResponse(
            {
                "non_field_errors": [
                    "Could not update your password. Please try again."
                ]
            },
            status=500,
        )

    return JsonResponse({"message": "Password reset successfully"}, status=200)
