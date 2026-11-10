"""Auth-adjacent models stored in each tenant schema."""
from django.conf import settings
from django.db import models


class UserPreference(models.Model):
    """Per-user UI preferences (language, etc.) for the current tenant."""

    LANG_EN = 'en'
    LANG_ES = 'es'
    LANGUAGE_CHOICES = [
        (LANG_EN, 'English'),
        (LANG_ES, 'Español'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preference',
    )
    preferred_language = models.CharField(
        max_length=8,
        choices=LANGUAGE_CHOICES,
        default=LANG_EN,
        db_index=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User preference'
        verbose_name_plural = 'User preferences'

    def __str__(self):
        return f'{self.user_id}:{self.preferred_language}'
