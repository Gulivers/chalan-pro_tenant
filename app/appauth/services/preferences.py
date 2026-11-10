"""Helpers for per-user UI preferences."""
from appauth.models import UserPreference

ALLOWED_LANGUAGES = {UserPreference.LANG_EN, UserPreference.LANG_ES}


def get_or_create_preference(user) -> UserPreference:
    pref, _created = UserPreference.objects.get_or_create(user=user)
    return pref


def preferred_language_for(user) -> str:
    pref = get_or_create_preference(user)
    lang = pref.preferred_language or UserPreference.LANG_EN
    return lang if lang in ALLOWED_LANGUAGES else UserPreference.LANG_EN


def set_preferred_language(user, language: str) -> UserPreference:
    lang = (language or '').strip().lower()
    if lang not in ALLOWED_LANGUAGES:
        raise ValueError('preferred_language must be "en" or "es".')
    pref = get_or_create_preference(user)
    if pref.preferred_language != lang:
        pref.preferred_language = lang
        pref.save(update_fields=['preferred_language', 'updated_at'])
    return pref
