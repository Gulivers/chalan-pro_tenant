"""Safe audit helpers for JobRhythm Assistant."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from django.db import connection
from django_tenants.utils import get_public_schema_name

from appassistant.models import AssistantConversation, AssistantQueryLog

logger = logging.getLogger('appassistant.audit')


def resolve_schema_name(request=None) -> str:
    """Return the active tenant schema name, or public/unknown fallback."""
    tenant = getattr(connection, 'tenant', None)
    schema = getattr(tenant, 'schema_name', None) if tenant is not None else None
    if schema:
        return schema
    try:
        return connection.schema_name  # type: ignore[attr-defined]
    except Exception:
        return get_public_schema_name()


def sanitize_context_for_audit(context: dict | None) -> dict:
    """Keep only non-sensitive, structured context keys for audit storage."""
    if not context:
        return {}
    safe: dict[str, Any] = {}
    for key in ('view', 'route_name', 'entity_type', 'entity_id'):
        if key in context and context[key] is not None:
            safe[key] = context[key]
    return safe


def log_assistant_query(
    *,
    user,
    request_id: UUID | str,
    tool_name: str = '',
    params_safe: dict | None = None,
    success: bool,
    error_code: str = '',
    row_count: int = 0,
    duration_ms: int = 0,
    schema_name: str | None = None,
    conversation: AssistantConversation | str | UUID | None = None,
    intent: str = '',
    clarification: bool = False,
) -> AssistantQueryLog | None:
    """
    Persist a minimal audit row. Never store full prompts or result payloads.
    Failures are logged but do not break the API response.
    """
    schema = schema_name or resolve_schema_name()
    conv_obj = None
    if isinstance(conversation, AssistantConversation):
        conv_obj = conversation
    elif conversation:
        try:
            conv_obj = AssistantConversation.objects.filter(pk=conversation).first()
        except Exception:
            conv_obj = None

    payload = {
        'schema_name': schema,
        'request_id': str(request_id),
        'tool_name': tool_name or '',
        'success': success,
        'error_code': error_code or '',
        'row_count': row_count,
        'duration_ms': duration_ms,
        'intent': intent or '',
        'clarification': bool(clarification),
    }
    try:
        return AssistantQueryLog.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            conversation=conv_obj,
            schema_name=schema,
            request_id=request_id,
            tool_name=tool_name or '',
            intent=intent or '',
            clarification=bool(clarification),
            params_safe=params_safe or {},
            success=success,
            error_code=error_code or '',
            row_count=row_count,
            duration_ms=duration_ms,
        )
    except Exception:
        logger.exception('Failed to persist AssistantQueryLog', extra=payload)
        return None
