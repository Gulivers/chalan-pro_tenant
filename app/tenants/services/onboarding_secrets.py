"""Seal/unseal sensitive onboarding fields stored temporarily before email verification."""
from django.core.signing import BadSignature, Signer

_SIGNER = Signer(salt='onboarding-pending-password-v1')


def seal_admin_password(raw_password: str) -> str:
    return _SIGNER.sign(raw_password)


def unseal_admin_password(sealed_password: str) -> str:
    return _SIGNER.unsign(sealed_password)


def safe_unseal_admin_password(sealed_password: str) -> str:
    if not sealed_password:
        return ''
    try:
        return unseal_admin_password(sealed_password)
    except BadSignature:
        return ''
