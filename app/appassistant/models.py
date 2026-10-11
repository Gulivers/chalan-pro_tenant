import uuid

from django.conf import settings
from django.db import models


class AssistantConversation(models.Model):
    """
    Tenant-scoped conversational state for JobRhythm Assistant (Level 1).

    Isolation:
      - schema (django-tenants TENANT_APPS)
      - user FK
      - UUID primary key (conversation_id)

    Never load by UUID alone without filtering by the authenticated user.
    Client may send conversation_id; never authoritative state from the client.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assistant_conversations',
    )
    schema_name = models.CharField(max_length=63, db_index=True)
    title = models.CharField(max_length=120, blank=True, default='')
    is_active = models.BooleanField(default=True)
    state = models.JSONField(default=dict, blank=True)
    state_schema_version = models.CharField(max_length=8, default='1')
    turn_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-last_activity_at']
        verbose_name = 'Assistant conversation'
        verbose_name_plural = 'Assistant conversations'
        indexes = [
            models.Index(fields=['user', '-last_activity_at']),
            models.Index(fields=['is_active', 'last_activity_at']),
        ]

    def __str__(self):
        status = 'active' if self.is_active else 'inactive'
        return f'{self.id} user={self.user_id} {status} turns={self.turn_count}'


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
    conversation = models.ForeignKey(
        AssistantConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='query_logs',
    )
    schema_name = models.CharField(max_length=63, db_index=True)
    request_id = models.UUIDField(db_index=True)
    tool_name = models.CharField(max_length=64, blank=True, default='')
    intent = models.CharField(max_length=64, blank=True, default='')
    clarification = models.BooleanField(default=False)
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
            models.Index(fields=['conversation', '-created_at']),
        ]

    def __str__(self):
        status = 'ok' if self.success else (self.error_code or 'error')
        tool = self.tool_name or 'none'
        return f'{self.request_id} {tool} {status}'
