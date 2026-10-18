from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.core import signing

from appauth.authentication import TenantJWTAuthentication
from appauth.errors import TOKEN_INVALID, error_payload
from appauth.ws_tickets import issue_ws_ticket
from appauth.services.tenant import (
    is_tenant_owner,
    resolve_request_tenant,
    tenant_branding_payload,
)


class TenantContextView(APIView):
    """
    GET /api/auth/tenant-context/

    Public branding for the tenant resolved from the request host.
    No user identity is required or returned.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        tenant = resolve_request_tenant(request)
        payload = tenant_branding_payload(tenant)
        payload.pop('schema_name', None)
        return Response(payload)


class MeView(APIView):
    """
    GET /api/auth/me/

    Authenticated user context for the current tenant schema.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [TenantJWTAuthentication]

    def get(self, request):
        user = request.user
        tenant = resolve_request_tenant(request)
        branding = tenant_branding_payload(tenant)
        return Response(
            {
                'id': user.pk,
                'username': user.get_username(),
                'email': user.email or '',
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_tenant_owner': is_tenant_owner(user, tenant),
                'permissions': list(user.get_all_permissions()),
                **branding,
            }
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def permissions_view(request):
    """GET /api/auth/permissions/ — Django permissions for UX gating."""
    return Response({'permissions': list(request.user.get_all_permissions())})


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_token_view(request):
    """
    GET /api/auth/validate/

    Validates the Bearer access JWT (tenant-bound). Used by the Vue router
    until it relies solely on silent refresh.
    """
    auth = TenantJWTAuthentication()
    try:
        result = auth.authenticate(request)
    except (InvalidToken, TokenError, Exception):
        return Response(
            {
                'valid': False,
                **error_payload(TOKEN_INVALID, 'Invalid or missing token.'),
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if result is None:
        return Response(
            {
                'valid': False,
                **error_payload(TOKEN_INVALID, 'Invalid or missing token.'),
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user, _validated = result
    if not user.is_active:
        return Response(
            {
                'valid': False,
                **error_payload(TOKEN_INVALID, 'Invalid or missing token.'),
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return Response({'valid': True}, status=status.HTTP_200_OK)


class WsTicketView(APIView):
    """
    POST /api/auth/ws-ticket/

    Exchange the current access JWT for a one-minute, one-time WebSocket ticket.
    """

    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            ticket = issue_ws_ticket(request.user)
        except signing.BadSignature:
            return Response(
                error_payload(TOKEN_INVALID, 'Could not issue a WebSocket ticket.'),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'ticket': ticket})
