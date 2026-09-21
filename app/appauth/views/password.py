import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from appauth.errors import (
    PASSWORD_INVALID,
    PASSWORD_UPDATED,
    RESET_LINK_INVALID,
    THROTTLED,
    error_payload,
)
from appauth.services.password_reset import (
    GENERIC_FORGOT_MESSAGE,
    apply_password_reset,
    collect_password_validation_errors,
    send_password_reset_email,
)
from appauth.throttles import (
    PasswordForgotEmailThrottle,
    PasswordForgotIPThrottle,
    PasswordResetIPThrottle,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class PasswordForgotView(APIView):
    """
    POST /api/auth/password/forgot/

    Always returns the same success message whether or not the email exists
    (anti-enumeration). Runs in the current tenant schema.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [PasswordForgotIPThrottle, PasswordForgotEmailThrottle]

    def throttled(self, request, wait):
        raise Throttled(
            wait=wait,
            detail='Too many password reset requests. Please try again later.',
            code=THROTTLED,
        )

    def post(self, request):
        email = (request.data.get('email') or '').strip()
        if not email:
            return Response(
                {'email': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=email).first()
        if user is not None and user.is_active:
            try:
                send_password_reset_email(request, user, email)
            except Exception:
                logger.exception(
                    'Failed to send password reset email for user pk=%s', user.pk
                )
                # Still return generic 200 to avoid leaking deliverability / existence.

        return Response(
            {'code': 'reset_email_sent', 'detail': GENERIC_FORGOT_MESSAGE},
            status=status.HTTP_200_OK,
        )


class PasswordResetView(APIView):
    """
    POST /api/auth/password/reset/

    Body: uid, token, new_password, confirm_password.
    On success, invalidates all DRF tokens for the user.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [PasswordResetIPThrottle]

    def throttled(self, request, wait):
        raise Throttled(
            wait=wait,
            detail='Too many password reset attempts. Please try again later.',
            code=THROTTLED,
        )

    def post(self, request):
        uidb64 = (request.data.get('uid') or request.data.get('uidb64') or '').strip()
        token = (request.data.get('token') or '').strip()
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not uidb64 or not token:
            return Response(
                error_payload(
                    RESET_LINK_INVALID,
                    'Invalid or expired reset link. Please request a new one.',
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            UnicodeDecodeError,
            OverflowError,
            User.DoesNotExist,
        ):
            return Response(
                error_payload(
                    RESET_LINK_INVALID,
                    'Invalid or expired reset link. Please request a new one.',
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                error_payload(
                    RESET_LINK_INVALID,
                    'Invalid or expired reset link. Please request a new one.',
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        field_errors = collect_password_validation_errors(
            user, new_password, confirm_password
        )
        if field_errors:
            payload = dict(field_errors)
            payload['code'] = PASSWORD_INVALID
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        try:
            apply_password_reset(user, new_password)
        except Exception:
            logger.exception('Failed to reset password for user pk=%s', user.pk)
            return Response(
                error_payload(
                    PASSWORD_INVALID,
                    'Could not update your password. Please try again.',
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                'code': PASSWORD_UPDATED,
                'detail': 'Password reset successfully.',
            },
            status=status.HTTP_200_OK,
        )
