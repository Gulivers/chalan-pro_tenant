"""
Deprecated shim: password reset lives in appauth.

Re-export helpers so any residual imports keep working during Stage A cleanup.
"""
from appauth.services.password_reset import (  # noqa: F401
    GENERIC_FORGOT_MESSAGE,
    apply_password_reset,
    build_password_reset_url,
    collect_password_validation_errors,
    frontend_base_url_for_password_reset,
    send_password_reset_email,
)
