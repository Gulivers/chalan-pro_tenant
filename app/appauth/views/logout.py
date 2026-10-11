from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from appauth.cookies import (
    clear_refresh_cookie,
    read_refresh_from_request,
    set_refresh_cookie,
    use_refresh_cookie,
)
from appauth.errors import LOGOUT_OK, NO_TOKEN, SESSION_EXPIRED, error_payload
from appauth.jwt_tokens import TenantRefreshToken
from appauth.services.tokens import invalidate_user_auth_tokens
from django.db import connection


def _assert_refresh_schema(refresh: RefreshToken) -> None:
    claim = refresh.get('schema_name')
    active = getattr(connection, 'schema_name', None)
    if not claim or claim != active:
        raise TokenError('Token tenant does not match this workspace.')


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    POST /api/auth/logout/

    Blacklist the refresh token (body/cookie) and clear the refresh cookie.
    """
    refresh_str = read_refresh_from_request(request)
    blacklisted = False

    if refresh_str:
        try:
            refresh = TenantRefreshToken(refresh_str)
            _assert_refresh_schema(refresh)
            refresh.blacklist()
            blacklisted = True
        except TokenError:
            pass
        except Exception:
            pass

    if request.user and request.user.is_authenticated:
        invalidate_user_auth_tokens(request.user)
        blacklisted = True

    response = Response(
        {
            'code': LOGOUT_OK if blacklisted or refresh_str else NO_TOKEN,
            'detail': (
                'Session closed successfully.'
                if blacklisted or refresh_str
                else 'No active token found.'
            ),
        },
        status=status.HTTP_200_OK if (blacklisted or refresh_str) else status.HTTP_400_BAD_REQUEST,
    )
    clear_refresh_cookie(response)
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_view(request):
    """
    POST /api/auth/refresh/

    Rotate refresh token (blacklist old) and return a new access token.
    Dev: refresh in JSON body. Prod: refresh cookie.
    """
    refresh_str = read_refresh_from_request(request)
    if not refresh_str:
        return Response(
            error_payload(SESSION_EXPIRED, 'Session expired. Please sign in again.'),
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        old_refresh = TenantRefreshToken(refresh_str)
        _assert_refresh_schema(old_refresh)
        user_id = old_refresh.payload.get('user_id')
        # Rotation: blacklist current refresh, issue a new pair
        old_refresh.blacklist()

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(pk=user_id)
        if not user.is_active:
            raise TokenError('User inactive')

        new_refresh = TenantRefreshToken.for_user(user)
        access = str(new_refresh.access_token)
        refresh_out = str(new_refresh)
    except Exception:
        response = Response(
            error_payload(SESSION_EXPIRED, 'Session expired. Please sign in again.'),
            status=status.HTTP_401_UNAUTHORIZED,
        )
        clear_refresh_cookie(response)
        return response

    cookie_mode = use_refresh_cookie()
    payload = {
        'access': access,
        'refresh': None if cookie_mode else refresh_out,
    }
    response = Response(payload, status=status.HTTP_200_OK)
    if cookie_mode:
        set_refresh_cookie(response, refresh_out)
    return response
