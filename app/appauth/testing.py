"""Helpers for authenticating API clients/requests with tenant-bound JWT."""
from appauth.jwt_tokens import issue_tokens_for_user


def bearer_credentials_for_user(user) -> str:
    """Return Authorization header value: 'Bearer <access>'."""
    access, _refresh = issue_tokens_for_user(user)
    return f'Bearer {access}'


def authenticate_api_client(client, user):
    """Attach Bearer JWT credentials to a DRF APIClient."""
    client.credentials(HTTP_AUTHORIZATION=bearer_credentials_for_user(user))
    return client
