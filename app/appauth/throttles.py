"""
Rate limiting for authentication endpoints (login, password forgot/reset).
"""
import hashlib
import logging

from rest_framework.throttling import SimpleRateThrottle

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or 'unknown'


class _AuthThrottleBase(SimpleRateThrottle):
    def allow_request(self, request, view):
        if request.method != 'POST':
            return True
        allowed = super().allow_request(request, view)
        if not allowed:
            logger.warning(
                'auth_rate_limited scope=%s ip=%s path=%s',
                self.scope,
                get_client_ip(request),
                request.path,
            )
        return allowed

    def get_ident(self, request):
        return get_client_ip(request)


class LoginIPThrottle(_AuthThrottleBase):
    """Limit login attempts per client IP."""

    scope = 'auth_login_ip'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class LoginUsernameThrottle(SimpleRateThrottle):
    """Limit login attempts per username (across IPs)."""

    scope = 'auth_login_username'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        username = ''
        if hasattr(request, 'data'):
            username = (request.data.get('username') or '').strip().lower()
        if not username:
            return None
        username_hash = hashlib.sha256(username.encode('utf-8')).hexdigest()
        return self.cache_format % {'scope': self.scope, 'ident': username_hash}

    def allow_request(self, request, view):
        if request.method != 'POST':
            return True
        allowed = super().allow_request(request, view)
        if not allowed:
            logger.warning(
                'auth_rate_limited scope=%s ip=%s path=%s',
                self.scope,
                get_client_ip(request),
                request.path,
            )
        return allowed


class PasswordForgotIPThrottle(_AuthThrottleBase):
    scope = 'auth_password_forgot_ip'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class PasswordForgotEmailThrottle(SimpleRateThrottle):
    scope = 'auth_password_forgot_email'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        email = ''
        if hasattr(request, 'data'):
            email = (request.data.get('email') or '').strip().lower()
        if not email:
            return None
        email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()
        return self.cache_format % {'scope': self.scope, 'ident': email_hash}

    def allow_request(self, request, view):
        if request.method != 'POST':
            return True
        allowed = super().allow_request(request, view)
        if not allowed:
            logger.warning(
                'auth_rate_limited scope=%s ip=%s path=%s',
                self.scope,
                get_client_ip(request),
                request.path,
            )
        return allowed


class PasswordResetIPThrottle(_AuthThrottleBase):
    scope = 'auth_password_reset_ip'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }
