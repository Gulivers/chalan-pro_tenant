"""
Rate limiting for public onboarding endpoints.
"""
import hashlib
import logging

from rest_framework.throttling import SimpleRateThrottle

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """Client IP behind reverse proxy (nginx sets X-Forwarded-For)."""
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class _OnboardingThrottleBase(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }

    def allow_request(self, request, view):
        if request.method != 'POST':
            return True
        allowed = super().allow_request(request, view)
        if not allowed:
            logger.warning(
                'onboarding_rate_limited scope=%s ip=%s path=%s',
                self.scope,
                get_client_ip(request),
                request.path,
            )
        return allowed

    def get_ident(self, request):
        return get_client_ip(request)


class OnboardingCreateIPThrottle(_OnboardingThrottleBase):
    """Limit tenant creation attempts per client IP."""

    scope = 'onboarding_create_ip'


def _get_request_email(request) -> str:
    if hasattr(request, 'data'):
        email = request.data.get('email')
    else:
        email = request.POST.get('email')
    return (email or '').strip().lower()


class OnboardingCreateEmailThrottle(SimpleRateThrottle):
    """Limit onboarding attempts per email address (including failed validations)."""

    scope = 'onboarding_create_email'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        email = _get_request_email(request)
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
                'onboarding_rate_limited scope=%s ip=%s path=%s',
                self.scope,
                get_client_ip(request),
                request.path,
            )
        return allowed


class OnboardingVerifyIPThrottle(_OnboardingThrottleBase):
    """Limit email-verification completion attempts per IP."""

    scope = 'onboarding_verify_ip'

