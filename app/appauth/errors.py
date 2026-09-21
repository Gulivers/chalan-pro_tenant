"""Stable API error codes for JobRhythm authentication."""

INVALID_CREDENTIALS = 'invalid_credentials'
TENANT_INACTIVE = 'tenant_inactive'
THROTTLED = 'throttled'
SESSION_EXPIRED = 'session_expired'
TOKEN_INVALID = 'token_invalid'
RESET_LINK_INVALID = 'reset_link_invalid'
PASSWORD_INVALID = 'password_invalid'
PASSWORD_UPDATED = 'password_updated'
LOGOUT_OK = 'logout_ok'
NO_TOKEN = 'no_token'


def error_payload(code: str, detail: str, **extra):
    """Standard error body: {code, detail, ...}."""
    payload = {'code': code, 'detail': detail}
    payload.update(extra)
    return payload
