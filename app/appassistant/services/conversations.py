"""
Load / expire helpers for AssistantConversation.

Security: never fetch by UUID alone — always scope to authenticated user.
Tenant isolation is provided by the active schema (TENANT_APPS).
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from django.utils import timezone

from appassistant.models import AssistantConversation
from appassistant.services.audit import resolve_schema_name
from appassistant.services.conversation_state import (
    CONVERSATION_RETENTION,
    MAX_TURN_COUNT,
    empty_state,
    is_state_reusable,
    validate_state,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


def get_conversation_for_user(
    user: 'AbstractBaseUser',
    conversation_id: UUID | str | None,
) -> AssistantConversation | None:
    """Return the conversation only if it belongs to ``user`` in this schema."""
    if not user or not getattr(user, 'is_authenticated', False):
        return None
    if conversation_id is None or conversation_id == '':
        return None
    try:
        return AssistantConversation.objects.get(id=conversation_id, user=user)
    except (AssistantConversation.DoesNotExist, ValueError, TypeError):
        return None


def create_conversation_for_user(user: 'AbstractBaseUser') -> AssistantConversation:
    return AssistantConversation.objects.create(
        user=user,
        schema_name=resolve_schema_name(),
        state=empty_state(),
        state_schema_version='1',
        turn_count=0,
        is_active=True,
    )


def conversation_allows_inheritance(conversation: AssistantConversation, *, now=None) -> bool:
    return is_state_reusable(
        is_active=conversation.is_active,
        last_activity_at=conversation.last_activity_at,
        turn_count=conversation.turn_count,
        now=now,
    )


def get_reusable_state(conversation: AssistantConversation | None, *, now=None) -> tuple[dict, bool]:
    """
    Returns (state, state_expired).

    When expired / inactive / over turn cap, returns empty_state and True.
    """
    if conversation is None:
        return empty_state(), True
    if not conversation_allows_inheritance(conversation, now=now):
        return empty_state(), True
    try:
        return validate_state(conversation.state), False
    except Exception:
        return empty_state(), True


def touch_conversation(
    conversation: AssistantConversation,
    *,
    state: dict,
    increment_turn: bool = True,
) -> AssistantConversation:
    """Persist validated state and bump activity (C2 will call this after tools)."""
    conversation.state = validate_state(state)
    conversation.state_schema_version = '1'
    if increment_turn:
        conversation.turn_count = min(conversation.turn_count + 1, MAX_TURN_COUNT)
    conversation.last_activity_at = timezone.now()
    conversation.is_active = True
    conversation.save(
        update_fields=[
            'state',
            'state_schema_version',
            'turn_count',
            'last_activity_at',
            'is_active',
            'updated_at',
        ]
    )
    return conversation


def deactivate_conversation(conversation: AssistantConversation) -> AssistantConversation:
    """Start-over: keep row for audit FK, stop inheritance."""
    conversation.is_active = False
    conversation.state = empty_state()
    conversation.last_activity_at = timezone.now()
    conversation.save(
        update_fields=['is_active', 'state', 'last_activity_at', 'updated_at']
    )
    return conversation


def conversations_eligible_for_purge(*, now=None, retention: timedelta | None = None):
    """Queryset helper for the purge command (hard delete after retention)."""
    current = now or timezone.now()
    cutoff = current - (retention or CONVERSATION_RETENTION)
    return AssistantConversation.objects.filter(last_activity_at__lt=cutoff)
