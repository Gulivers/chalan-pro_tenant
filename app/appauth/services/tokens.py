"""Invalidate authentication material for a user in the current tenant schema."""


def invalidate_user_auth_tokens(user) -> int:
    """
    Blacklist all outstanding Simple JWT refresh tokens for this user.
    Returns the number of outstanding tokens blacklisted.
    """
    count = 0
    try:
        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
            OutstandingToken,
        )

        outstanding = OutstandingToken.objects.filter(user=user)
        for token in outstanding:
            BlacklistedToken.objects.get_or_create(token=token)
            count += 1
    except Exception:
        pass
    return count
