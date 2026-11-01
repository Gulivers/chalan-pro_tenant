"""Short-lived, one-time tickets for the WebSocket handshake.

The SPA keeps the access JWT in memory and cannot set Authorization on a
WebSocket. It exchanges that access token for a ticket and passes ?ticket=.
"""
import secrets

from django.core import signing
from django.core.cache import cache

from appauth.jwt_tokens import current_schema_name

_SALT = 'jr-ws-ticket'
_MAX_AGE_SECONDS = 60


def issue_ws_ticket(user) -> str:
    schema = current_schema_name()
    if not schema:
        raise signing.BadSignature('Cannot issue a WebSocket ticket without a tenant.')
    payload = {
        'uid': user.pk,
        'schema': schema,
        'nonce': secrets.token_urlsafe(18),
    }
    return signing.dumps(payload, salt=_SALT)


def consume_ws_ticket(token: str) -> tuple[int, str]:
    """Return (user_id, schema_name). A ticket can be used only once."""
    data = signing.loads(token, salt=_SALT, max_age=_MAX_AGE_SECONDS)
    uid = data.get('uid')
    schema = data.get('schema')
    nonce = data.get('nonce')
    if not uid or not schema or not nonce:
        raise signing.BadSignature('Incomplete WebSocket ticket.')
    cache_key = f'ws-ticket:{schema}:{nonce}'
    if not cache.add(cache_key, 1, timeout=_MAX_AGE_SECONDS + 5):
        raise signing.BadSignature('WebSocket ticket already used.')
    return int(uid), str(schema)
