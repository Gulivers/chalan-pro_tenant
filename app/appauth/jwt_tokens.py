"""Simple JWT token classes with mandatory schema_name claim."""
from datetime import datetime, timezone as dt_timezone

from django.db import connection
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


def current_schema_name() -> str | None:
    return getattr(connection, 'schema_name', None)


def _register_outstanding(token: RefreshToken, user) -> None:
    """Persist refresh JTI so password-reset / logout-all can revoke it."""
    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

        exp = token.get('exp')
        iat = token.get('iat')
        expires_at = datetime.fromtimestamp(exp, tz=dt_timezone.utc)
        created_at = datetime.fromtimestamp(iat, tz=dt_timezone.utc)
        OutstandingToken.objects.update_or_create(
            jti=token['jti'],
            defaults={
                'user': user,
                'created_at': created_at,
                'token': str(token),
                'expires_at': expires_at,
            },
        )
    except Exception:
        # Blacklist app may not be migrated yet in some management contexts.
        pass


class TenantRefreshToken(RefreshToken):
    """Refresh token that embeds and validates schema_name."""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        schema = current_schema_name()
        if not schema:
            raise InvalidToken('Cannot issue token without an active tenant schema.')
        token['schema_name'] = schema
        _register_outstanding(token, user)
        return token

    @property
    def access_token(self):
        access = super().access_token
        schema = self.get('schema_name') or current_schema_name()
        if not schema:
            raise InvalidToken('Cannot issue access token without schema_name.')
        access['schema_name'] = schema
        return access


def issue_tokens_for_user(user) -> tuple[str, str]:
    """
    Return (access, refresh) JWT strings bound to the current tenant schema.
    """
    refresh = TenantRefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Not used for login view directly; kept for SimpleJWT compatibility."""

    @classmethod
    def get_token(cls, user):
        return TenantRefreshToken.for_user(user)
