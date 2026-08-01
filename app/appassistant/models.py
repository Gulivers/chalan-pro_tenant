from django.conf import settings
from django.db import models


class AssistantQueryLog(models.Model):
    """
    Minimal tenant-aware audit for Assistant queries.
    Does not store full prompts or result payloads.
    Tenant isolation is by schema; schema_name is denormalized for queries.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assistant_query_logs',
    )
    schema_name = models.CharField(max_length=63, db_index=True)
    request_id = models.UUIDField(db_index=True)
    tool_name = models.CharField(max_length=64, blank=True, default='')
    params_safe = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=False)
    error_code = models.CharField(max_length=64, blank=True, default='')
    row_count = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Assistant query log'
        verbose_name_plural = 'Assistant query logs'
        indexes = [
            models.Index(fields=['schema_name', '-created_at']),
            models.Index(fields=['tool_name', '-created_at']),
        ]

    def __str__(self):
        status = 'ok' if self.success else (self.error_code or 'error')
        tool = self.tool_name or 'none'
        return f'{self.request_id} {tool} {status}'
