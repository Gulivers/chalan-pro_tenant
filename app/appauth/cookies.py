"""Refresh-token cookie helpers (default) vs optional body mode."""
from urllib.parse import urlparse

from django.conf import settings


REFRESH_COOKIE_NAME = 'jr_refresh'


def use_refresh_cookie() -> bool:
    """
    Default: HttpOnly host-only cookie (shared across tabs; works with same-origin
    SPA proxy in local and Nginx in production).

    Set AUTH_USE_REFRESH_COOKIE=False for true cross-origin body-only refresh.
    """
    return bool(getattr(settings, 'AUTH_USE_REFRESH_COOKIE', True))


def refresh_cookie_kwargs():
    return {
        'key': getattr(settings, 'AUTH_REFRESH_COOKIE_NAME', REFRESH_COOKIE_NAME),
        'max_age': int(
            getattr(settings, 'AUTH_REFRESH_COOKIE_MAX_AGE', 7 * 24 * 60 * 60)
        ),
        'httponly': True,
        'secure': bool(getattr(settings, 'AUTH_REFRESH_COOKIE_SECURE', not settings.DEBUG)),
        'samesite': getattr(settings, 'AUTH_REFRESH_COOKIE_SAMESITE', 'Lax'),
        'path': getattr(settings, 'AUTH_REFRESH_COOKIE_PATH', '/api/auth/'),
        # Host-only: do not set domain= (avoids parent-domain leakage across tenants)
    }


def set_refresh_cookie(response, refresh_token: str):
    kwargs = refresh_cookie_kwargs()
    key = kwargs.pop('key')
    response.set_cookie(key, refresh_token, **kwargs)
    return response


def clear_refresh_cookie(response):
    kwargs = refresh_cookie_kwargs()
    key = kwargs.pop('key')
    response.delete_cookie(
        key,
        path=kwargs.get('path', '/api/auth/'),
        samesite=kwargs.get('samesite', 'Lax'),
    )
    return response


def same_origin_auth_request(request) -> bool:
    """True when this auth POST comes from the same host that issued the cookie.

    The dev proxy strips the port from Host, so the SPA on :8080 must still
    match. A different hostname does not. Sec-Fetch-Site: cross-site never does.
    """
    site = (request.headers.get('Sec-Fetch-Site') or '').strip().lower()
    if site == 'cross-site':
        return False
    origin = (request.headers.get('Origin') or '').strip()
    if not origin:
        return site == 'same-origin'
    parsed = urlparse(origin)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        return False
    try:
        host = request.get_host()
    except Exception:
        return False
    request_host = host.split(':')[0].lower()
    if parsed.hostname.lower() != request_host:
        return False
    return site in ('', 'same-origin', 'same-site', 'none')


def read_refresh_from_request(request) -> str | None:
    """Cookie mode reads only jr_refresh. Body mode reads body, then header."""
    if use_refresh_cookie():
        name = getattr(settings, 'AUTH_REFRESH_COOKIE_NAME', REFRESH_COOKIE_NAME)
        cookie_val = request.COOKIES.get(name)
        return cookie_val or None

    body_refresh = None
    if hasattr(request, 'data'):
        body_refresh = request.data.get('refresh')
    if body_refresh:
        return str(body_refresh).strip() or None

    header = request.headers.get('X-Refresh-Token')
    if header:
        return header.strip() or None
    return None
