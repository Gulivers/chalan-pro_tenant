"""
Cloudflare Turnstile verification for public onboarding.
"""
import logging
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'


def get_turnstile_site_key() -> str:
    return getattr(settings, 'TURNSTILE_SITE_KEY', '') or ''


def is_turnstile_configured() -> bool:
    return bool(get_turnstile_site_key() and getattr(settings, 'TURNSTILE_SECRET_KEY', ''))


def verify_turnstile_token(token: Optional[str], remote_ip: Optional[str] = None) -> tuple[bool, str]:
    """
    Validate a Turnstile response token server-side.
    Returns (ok, error_message).
    """
    secret = getattr(settings, 'TURNSTILE_SECRET_KEY', '') or ''
    if not secret:
        if settings.DEBUG:
            logger.warning('turnstile: secret not configured; skipping verification (DEBUG only)')
            return True, ''
        return False, 'CAPTCHA is not configured on the server.'

    if not token or not str(token).strip():
        return False, 'Please complete the CAPTCHA verification.'

    payload = {
        'secret': secret,
        'response': str(token).strip(),
    }
    if remote_ip:
        payload['remoteip'] = remote_ip

    try:
        response = requests.post(TURNSTILE_VERIFY_URL, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.exception('turnstile: verification request failed: %s', exc)
        return False, 'Could not verify CAPTCHA. Please try again.'

    if data.get('success'):
        return True, ''

    error_codes = data.get('error-codes') or []
    logger.warning('turnstile: verification failed codes=%s', error_codes)
    return False, 'CAPTCHA verification failed. Please try again.'
