"""Tenant-bound Simple JWT authentication for JobRhythm."""
from django.db import connection
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class TenantJWTAuthentication(JWTAuthentication):
    """
    JWTAuthentication that rejects tokens whose schema_name claim does not
    match the active django-tenants schema for this request.
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        claim_schema = validated_token.get('schema_name')
        active_schema = getattr(connection, 'schema_name', None)

        if not claim_schema or not active_schema:
            raise InvalidToken('Token is missing tenant binding.')

        if claim_schema != active_schema:
            raise AuthenticationFailed(
                'Token tenant does not match this workspace.',
                code='token_tenant_mismatch',
            )

        return user
