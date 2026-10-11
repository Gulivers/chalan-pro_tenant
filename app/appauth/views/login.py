import logging

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from appauth.cookies import set_refresh_cookie, use_refresh_cookie
from appauth.errors import INVALID_CREDENTIALS, TENANT_INACTIVE, THROTTLED, error_payload
from appauth.jwt_tokens import issue_tokens_for_user
from appauth.services.tenant import resolve_request_tenant
from appauth.throttles import LoginIPThrottle, LoginUsernameThrottle
from tenants.services.access import assert_login_allowed

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    POST /api/auth/login/

    Authenticate against the current tenant schema and issue tenant-bound JWTs.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [LoginIPThrottle, LoginUsernameThrottle]

    def throttled(self, request, wait):
        raise Throttled(
            wait=wait,
            detail='Too many login attempts. Please try again later.',
            code=THROTTLED,
        )

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''

        if not username or not password:
            return Response(
                error_payload(
                    INVALID_CREDENTIALS,
                    'Invalid username or password.',
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            return Response(
                error_payload(
                    INVALID_CREDENTIALS,
                    'Invalid username or password.',
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tenant = resolve_request_tenant(request)
        ok, msg = assert_login_allowed(tenant)
        if not ok:
            return Response(
                error_payload(
                    TENANT_INACTIVE,
                    msg or 'This workspace has been deactivated. Contact support.',
                ),
                status=status.HTTP_403_FORBIDDEN,
            )

        access, refresh = issue_tokens_for_user(user)
        permissions = list(user.get_all_permissions())
        cookie_mode = use_refresh_cookie()
        payload = {
            'access': access,
            'refresh': None if cookie_mode else refresh,
            'permissions': permissions,
            'user': {
                'id': user.pk,
                'username': user.get_username(),
            },
        }
        response = Response(payload, status=status.HTTP_200_OK)
        if cookie_mode:
            set_refresh_cookie(response, refresh)
        return response
