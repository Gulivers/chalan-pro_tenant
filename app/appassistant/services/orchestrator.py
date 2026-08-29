"""
Assistant query orchestrator (Increment C4 + LLM-primary flag).

Flow when ASSISTANT_LLM_PRIMARY=True (+ LLM enabled + key):
  message (+ conversation_id)
    → load/create conversation (user + schema scoped)
    → LLM planner (natural language → tool + typed params)
    → Continuity planner fallback
    → DeterministicRouter fallback
    → FilterMerger → execute_tool → persist state

Flow when ASSISTANT_LLM_PRIMARY=False (legacy):
  → DeterministicRouter (complete known queries = authority)
  → LLM planner
  → Continuity planner
  → DeterministicRouter empty / unsupported

Fail closed on tool errors (HTTP 200 + clarification blocks).
LLM never supplies tenant/user authority, SQL, or trusted entity IDs.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from uuid import UUID

from appassistant.contracts.response import build_assistant_response
from appassistant.services.active_filters import active_filters_payload
from appassistant.services.blocks import clarification_text, text_block
from appassistant.services.continuity_planner import ContinuityPlan, plan_continuity
from appassistant.services.conversations import (
    create_conversation_for_user,
    deactivate_conversation,
    get_conversation_for_user,
    get_reusable_state,
    touch_conversation,
)
from appassistant.services.deterministic_router import (
    UNSUPPORTED_CLARIFICATION,
    RouteResult,
    route,
)
from appassistant.services.filter_merger import merge_conversation_state, filters_for_tool
from appassistant.services.llm_planner import (
    LLMPlan,
    build_new_query_params_from_llm,
    llm_planner_enabled,
    llm_planner_primary_enabled,
    plan_with_llm,
)
from appassistant.services.state_builder import build_state_after_tool
from appassistant.services.vendors import AmbiguousVendorError, VendorNotFoundError
from appassistant.tools.executor import execute_tool
from appassistant.tools.registry import get_default_registry

logger = logging.getLogger('appassistant')

# Typed keys allowed in audit params_safe (never the full prompt).
_AUDIT_PARAM_KEYS = frozenset({
    'vendor',
    'vendor_id',
    'vendor_ids',
    'min_amount',
    'period',
    'months',
    'limit',
    'offset',
    'top_n',
    'include_chart',
    'date_from',
    'date_to',
    'matched_case',
    'filter_operations',
    'state_expired',
    'inherited',
    'llm_model',
    'llm_intent',
    'is_new_query',
})


@dataclass
class AssistantQueryResult:
    """API payload plus safe audit fields for the view layer."""

    payload: dict[str, Any]
    tool_name: str = ''
    params_safe: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_code: str = ''
    row_count: int = 0
    conversation_id: str = ''
    intent: str = ''
    clarification: bool = False


def sanitize_tool_params_for_audit(
    params: dict[str, Any] | None,
    *,
    matched_case: int | None = None,
    message_len: int = 0,
    context: dict | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Keep only typed tool params + message_len; never the full message."""
    safe: dict[str, Any] = {'message_len': int(message_len)}
    if matched_case is not None:
        safe['matched_case'] = matched_case
    if context:
        for key in ('view', 'route_name', 'entity_type', 'entity_id'):
            if key in context and context[key] is not None:
                safe[key] = context[key]
    for key, value in (params or {}).items():
        if key not in _AUDIT_PARAM_KEYS:
            continue
        if isinstance(value, Decimal):
            safe[key] = str(value)
        elif isinstance(value, (str, int, bool)) or value is None:
            safe[key] = value
        elif isinstance(value, list):
            safe[key] = value[:20]
        else:
            safe[key] = str(value)
    if extra:
        for key, value in extra.items():
            if key in _AUDIT_PARAM_KEYS or key in (
                'intent',
                'router',
                'conversation_id',
            ):
                safe[key] = value
    return safe


def run_assistant_query(
    *,
    user,
    message: str,
    context: dict | None,
    request_id: UUID | str,
    conversation_id: str | None = None,
    start_over: bool = False,
) -> AssistantQueryResult:
    ctx = deepcopy(context) if context else {}
    # Request flag start_over rotates the conversation immediately.
    # Message phrases like "start over" are handled by the continuity planner.
    conversation = _resolve_conversation(
        user=user,
        conversation_id=conversation_id,
        start_over=start_over,
    )
    prev_state, state_expired = get_reusable_state(conversation)
    conv_id = str(conversation.id)
    routed_preview: RouteResult = route(message)
    llm_primary = llm_planner_primary_enabled()

    # Fase 1: LLM interprets natural language first when the flag is on.
    if llm_primary:
        llm_plan = plan_with_llm(
            message,
            previous_state=prev_state,
            state_expired=state_expired,
            page_context=ctx,
        )
        if llm_plan.ok:
            return _run_llm_plan(
                user=user,
                message=message,
                context=ctx,
                request_id=request_id,
                conversation=conversation,
                prev_state=prev_state,
                state_expired=state_expired,
                plan=llm_plan,
            )
    elif routed_preview.tool_name:
        # Legacy: complete DeterministicRouter matches are authoritative.
        return _run_routed_query(
            user=user,
            message=message,
            context=ctx,
            request_id=request_id,
            conversation=conversation,
            state_expired=state_expired,
            routed=routed_preview,
            router_name='deterministic',
            intent=(
                f'case_{routed_preview.matched_case}'
                if routed_preview.matched_case
                else 'new_query'
            ),
        )
    elif llm_planner_enabled():
        # Legacy: LLM only when the router did not match a complete query.
        llm_plan = plan_with_llm(
            message,
            previous_state=prev_state,
            state_expired=state_expired,
            page_context=ctx,
        )
        if llm_plan.ok:
            return _run_llm_plan(
                user=user,
                message=message,
                context=ctx,
                request_id=request_id,
                conversation=conversation,
                prev_state=prev_state,
                state_expired=state_expired,
                plan=llm_plan,
            )

    continuity = plan_continuity(
        message,
        previous_state=prev_state,
        state_expired=state_expired,
    )

    if continuity.start_over:
        return _run_start_over(
            user=user,
            message=message,
            context=ctx,
            request_id=request_id,
            conversation=conversation,
            router_name='continuity',
        )

    if continuity.is_follow_up:
        return _run_follow_up(
            user=user,
            message=message,
            context=ctx,
            request_id=request_id,
            conversation=conversation,
            prev_state=prev_state,
            state_expired=state_expired,
            continuity=continuity,
        )

    # Fallback: deterministic route (match or unsupported clarification).
    # Under LLM-primary this is the rescue path after LLM/continuity miss.
    intent = 'unsupported'
    if routed_preview.tool_name and routed_preview.matched_case:
        intent = f'case_{routed_preview.matched_case}'
    elif routed_preview.tool_name:
        intent = 'new_query'
    return _run_routed_query(
        user=user,
        message=message,
        context=ctx,
        request_id=request_id,
        conversation=conversation,
        state_expired=state_expired,
        routed=routed_preview,
        router_name='deterministic',
        intent=intent,
    )


def _run_start_over(
    *,
    user,
    message: str,
    context: dict,
    request_id,
    conversation,
    router_name: str,
) -> AssistantQueryResult:
    deactivate_conversation(conversation)
    conversation = create_conversation_for_user(user)
    conv_id = str(conversation.id)
    message_out = 'Context cleared. Ask a new question when you are ready.'
    payload = build_assistant_response(
        request_id=request_id,
        message=message_out,
        blocks=[
            text_block(
                block_id='conversation-reset',
                text=message_out,
                title='New conversation',
            )
        ],
        sources=[],
        context=context,
        tools_executed=[],
        router=router_name,
        conversation_id=conv_id,
        active_filters=active_filters_payload(None),
        state_expired=False,
        intent='start_over',
    )
    return AssistantQueryResult(
        payload=payload,
        tool_name='',
        params_safe=sanitize_tool_params_for_audit(
            {},
            message_len=len(message or ''),
            context=context,
            extra={'intent': 'start_over', 'router': router_name},
        ),
        success=True,
        conversation_id=conv_id,
        intent='start_over',
        clarification=False,
    )


def _run_llm_plan(
    *,
    user,
    message: str,
    context: dict,
    request_id,
    conversation,
    prev_state: dict,
    state_expired: bool,
    plan: LLMPlan,
) -> AssistantQueryResult:
    conv_id = str(conversation.id)
    audit_extra = {
        'intent': plan.intent,
        'router': 'llm',
        'llm_model': plan.model,
        'llm_intent': plan.intent,
        'is_new_query': plan.is_new_query,
        'state_expired': state_expired,
        **(plan.audit or {}),
    }

    if plan.start_over:
        return _run_start_over(
            user=user,
            message=message,
            context=context,
            request_id=request_id,
            conversation=conversation,
            router_name='llm',
        )

    if plan.needs_clarification:
        clarification = plan.clarification or 'Please clarify your request.'
        payload = build_assistant_response(
            request_id=request_id,
            message=clarification,
            blocks=[
                clarification_text(
                    block_id='llm-clarification',
                    message=clarification,
                )
            ],
            sources=[],
            context=context,
            tools_executed=[],
            router='llm',
            conversation_id=conv_id,
            active_filters=active_filters_payload(
                None if state_expired else prev_state
            ),
            state_expired=state_expired,
            intent=plan.intent or 'clarify',
        )
        return AssistantQueryResult(
            payload=payload,
            params_safe=sanitize_tool_params_for_audit(
                {},
                message_len=len(message or ''),
                context=context,
                extra=audit_extra,
            ),
            success=True,
            conversation_id=conv_id,
            intent=plan.intent or 'clarify',
            clarification=True,
        )

    # Authoritative new query from LLM (params resolved server-side).
    if plan.is_new_query and plan.tool:
        try:
            params = build_new_query_params_from_llm(plan)
        except AmbiguousVendorError as exc:
            labels = ', '.join(f'{c.name}' for c in exc.candidates[:5])
            clarification = (
                f'Multiple vendors match. Please clarify: {labels}.'
            )
            payload = build_assistant_response(
                request_id=request_id,
                message=clarification,
                blocks=[
                    clarification_text(
                        block_id='llm-ambiguous-vendor',
                        message=clarification,
                        candidates=[
                            {'id': c.id, 'name': c.name} for c in exc.candidates[:5]
                        ],
                    )
                ],
                sources=[],
                context=context,
                tools_executed=[],
                router='llm',
                conversation_id=conv_id,
                active_filters=active_filters_payload(prev_state),
                state_expired=state_expired,
                intent='clarify_vendor',
            )
            return AssistantQueryResult(
                payload=payload,
                conversation_id=conv_id,
                intent='clarify_vendor',
                clarification=True,
                params_safe=sanitize_tool_params_for_audit(
                    {},
                    message_len=len(message or ''),
                    context=context,
                    extra=audit_extra,
                ),
            )
        except VendorNotFoundError as exc:
            clarification = exc.message
            payload = build_assistant_response(
                request_id=request_id,
                message=clarification,
                blocks=[
                    clarification_text(
                        block_id='llm-vendor-not-found',
                        message=clarification,
                    )
                ],
                sources=[],
                context=context,
                tools_executed=[],
                router='llm',
                conversation_id=conv_id,
                active_filters=active_filters_payload(prev_state),
                state_expired=state_expired,
                intent='not_found',
            )
            return AssistantQueryResult(
                payload=payload,
                conversation_id=conv_id,
                intent='not_found',
                clarification=True,
                params_safe=sanitize_tool_params_for_audit(
                    {},
                    message_len=len(message or ''),
                    context=context,
                    extra=audit_extra,
                ),
            )

        return _execute_and_persist(
            user=user,
            message=message,
            context=context,
            request_id=request_id,
            conversation=conversation,
            tool_name=plan.tool,
            params=params,
            router_name='llm',
            intent=plan.intent or 'new_query',
            state_expired=state_expired,
            base_state=None,
            filter_operations=[{
                'field': '*',
                'operation': 'reset',
                'value': None,
            }],
            inherited=False,
        )

    # Follow-up style plan → FilterMerger (same path as continuity).
    continuity = ContinuityPlan(
        is_follow_up=True,
        intent=plan.intent or 'follow_up',
        tool=plan.tool,
        operations=list(plan.operations),
        clarification=plan.clarification,
        needs_clarification=False,
    )
    if plan.presentation and continuity.tool:
        from appassistant.services.filter_merger import FilterOperation

        continuity.operations.append(
            FilterOperation(
                field='presentation',
                operation='change_presentation',
                value=plan.presentation,
            )
        )
    return _run_follow_up(
        user=user,
        message=message,
        context=context,
        request_id=request_id,
        conversation=conversation,
        prev_state=prev_state,
        state_expired=state_expired,
        continuity=continuity,
        router_name='llm',
        audit_extra=audit_extra,
    )


def _run_follow_up(
    *,
    user,
    message: str,
    context: dict,
    request_id,
    conversation,
    prev_state: dict,
    state_expired: bool,
    continuity,
    router_name: str = 'continuity',
    audit_extra: dict | None = None,
) -> AssistantQueryResult:
    conv_id = str(conversation.id)
    base_audit = {
        'intent': continuity.intent or 'follow_up',
        'router': router_name,
        'state_expired': state_expired,
        **(audit_extra or {}),
    }

    if continuity.needs_clarification:
        clarification = continuity.clarification or 'Please clarify your request.'
        payload = build_assistant_response(
            request_id=request_id,
            message=clarification,
            blocks=[
                clarification_text(
                    block_id='continuity-clarification',
                    message=clarification,
                )
            ],
            sources=[],
            context=context,
            tools_executed=[],
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(prev_state),
            state_expired=state_expired,
            intent=continuity.intent or 'clarify',
        )
        return AssistantQueryResult(
            payload=payload,
            params_safe=sanitize_tool_params_for_audit(
                {},
                message_len=len(message or ''),
                context=context,
                extra=base_audit,
            ),
            success=True,
            conversation_id=conv_id,
            intent=continuity.intent or 'clarify',
            clarification=True,
        )

    if continuity.unsupported_message:
        payload = build_assistant_response(
            request_id=request_id,
            message=continuity.unsupported_message,
            blocks=[
                text_block(
                    block_id='continuity-unsupported',
                    text=continuity.unsupported_message,
                    title='Not available yet',
                )
            ],
            sources=[],
            context=context,
            tools_executed=[],
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(prev_state),
            state_expired=state_expired,
            intent=continuity.intent or 'unsupported',
        )
        return AssistantQueryResult(
            payload=payload,
            params_safe=sanitize_tool_params_for_audit(
                {},
                message_len=len(message or ''),
                context=context,
                extra=base_audit,
            ),
            success=True,
            conversation_id=conv_id,
            intent=continuity.intent or 'unsupported',
            clarification=True,
        )

    merge = merge_conversation_state(
        prev_state,
        operations=continuity.operations,
        tool=continuity.tool,
        state_expired=state_expired,
        intent=continuity.intent,
    )
    if merge.needs_clarification:
        clarification = merge.clarification or 'Please clarify your request.'
        payload = build_assistant_response(
            request_id=request_id,
            message=clarification,
            blocks=[
                clarification_text(
                    block_id='merge-clarification',
                    message=clarification,
                )
            ],
            sources=[],
            context=context,
            tools_executed=[],
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(prev_state),
            state_expired=state_expired,
            intent=continuity.intent or 'clarify',
        )
        return AssistantQueryResult(
            payload=payload,
            params_safe=sanitize_tool_params_for_audit(
                {},
                message_len=len(message or ''),
                context=context,
                extra=base_audit,
            ),
            success=True,
            conversation_id=conv_id,
            intent=continuity.intent or 'clarify',
            clarification=True,
        )

    if merge.error or not merge.state.get('tool'):
        message_out = merge.error or UNSUPPORTED_CLARIFICATION
        payload = build_assistant_response(
            request_id=request_id,
            message=message_out,
            blocks=[
                clarification_text(
                    block_id='merge-error',
                    message=message_out,
                )
            ],
            sources=[],
            context=context,
            tools_executed=[],
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(prev_state),
            state_expired=state_expired,
            intent=continuity.intent or 'error',
        )
        return AssistantQueryResult(
            payload=payload,
            params_safe=sanitize_tool_params_for_audit(
                {},
                message_len=len(message or ''),
                context=context,
                extra=base_audit,
            ),
            success=False,
            error_code='validation',
            conversation_id=conv_id,
            intent=continuity.intent or 'error',
            clarification=True,
        )

    tool_name = merge.state['tool']
    if get_default_registry().get(tool_name) is None:
        message_out = (
            f'The follow-up requires "{tool_name}", which is not available yet. '
            'Your previous filters were kept.'
        )
        payload = build_assistant_response(
            request_id=request_id,
            message=message_out,
            blocks=[
                text_block(
                    block_id='tool-not-available',
                    text=message_out,
                    title='Not available yet',
                )
            ],
            sources=[],
            context=context,
            tools_executed=[],
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(prev_state),
            state_expired=state_expired,
            intent=continuity.intent or 'unsupported',
        )
        return AssistantQueryResult(
            payload=payload,
            params_safe=sanitize_tool_params_for_audit(
                {},
                message_len=len(message or ''),
                context=context,
                extra=base_audit,
            ),
            success=True,
            conversation_id=conv_id,
            intent=continuity.intent or 'unsupported',
            clarification=True,
        )

    params = filters_for_tool(merge.state, tool_name)

    return _execute_and_persist(
        user=user,
        message=message,
        context=context,
        request_id=request_id,
        conversation=conversation,
        tool_name=tool_name,
        params=params,
        router_name=router_name,
        intent=continuity.intent or 'follow_up',
        state_expired=state_expired,
        base_state=merge.state,
        filter_operations=merge.applied_operations,
        inherited=merge.inherited,
    )


def _run_routed_query(
    *,
    user,
    message: str,
    context: dict,
    request_id,
    conversation,
    state_expired: bool,
    routed: RouteResult,
    router_name: str,
    intent: str,
) -> AssistantQueryResult:
    conv_id = str(conversation.id)
    base_safe = sanitize_tool_params_for_audit(
        routed.params,
        matched_case=routed.matched_case,
        message_len=len(message or ''),
        context=context,
        extra={'intent': intent, 'router': router_name, 'state_expired': state_expired},
    )

    if not routed.tool_name:
        clarification = routed.clarification or UNSUPPORTED_CLARIFICATION
        payload = build_assistant_response(
            request_id=request_id,
            message=clarification,
            blocks=[
                text_block(
                    block_id='unsupported-query',
                    text=clarification,
                    title='Query not supported',
                )
            ],
            sources=[],
            context=context,
            tools_executed=[],
            partial=False,
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(
                None if state_expired else get_reusable_state(conversation)[0]
            ),
            state_expired=state_expired,
            intent=intent,
        )
        return AssistantQueryResult(
            payload=payload,
            tool_name='',
            params_safe=base_safe,
            success=True,
            error_code='',
            row_count=0,
            conversation_id=conv_id,
            intent=intent,
            clarification=True,
        )

    # New full query replaces prior filters (do not inherit incompatible ones).
    return _execute_and_persist(
        user=user,
        message=message,
        context=context,
        request_id=request_id,
        conversation=conversation,
        tool_name=routed.tool_name,
        params=routed.params,
        router_name=router_name,
        intent=intent,
        state_expired=state_expired,
        base_state=None,
        filter_operations=[{
            'field': '*',
            'operation': 'reset',
            'value': None,
        }],
        inherited=False,
        matched_case=routed.matched_case,
    )


def _execute_and_persist(
    *,
    user,
    message: str,
    context: dict,
    request_id,
    conversation,
    tool_name: str,
    params: dict[str, Any],
    router_name: str,
    intent: str,
    state_expired: bool,
    base_state: dict | None,
    filter_operations: list | None,
    inherited: bool,
    matched_case: int | None = None,
) -> AssistantQueryResult:
    conv_id = str(conversation.id)
    tools_executed = [tool_name]
    base_safe = sanitize_tool_params_for_audit(
        params,
        matched_case=matched_case,
        message_len=len(message or ''),
        context=context,
        extra={
            'intent': intent,
            'router': router_name,
            'state_expired': state_expired,
            'inherited': inherited,
            'filter_operations': filter_operations or [],
        },
    )

    try:
        tool_result = execute_tool(tool_name, user=user, params=params)
    except Exception:
        logger.exception('assistant.tool_unexpected_error tool=%s', tool_name)
        message_out = 'Unable to complete this query. Please try again or rephrase.'
        payload = build_assistant_response(
            request_id=request_id,
            message=message_out,
            blocks=[
                clarification_text(
                    block_id='tool-internal-error',
                    message=message_out,
                )
            ],
            sources=[{'type': 'tool', 'name': tool_name, 'row_count': 0}],
            context=context,
            tools_executed=tools_executed,
            partial=False,
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(base_state),
            state_expired=state_expired,
            intent=intent,
        )
        return AssistantQueryResult(
            payload=payload,
            tool_name=tool_name,
            params_safe=base_safe,
            success=False,
            error_code='internal',
            row_count=0,
            conversation_id=conv_id,
            intent=intent,
            clarification=True,
        )

    error_code = tool_result.get('error_code') or ''
    row_count = int(tool_result.get('row_count') or 0)

    if error_code:
        blocks = tool_result.get('blocks') or [
            clarification_text(
                block_id='tool-error',
                message=tool_result.get('message') or 'Unable to complete this query.',
            )
        ]
        payload = build_assistant_response(
            request_id=request_id,
            message=tool_result.get('message') or 'Unable to complete this query.',
            blocks=blocks,
            sources=tool_result.get('sources') or [],
            context=context,
            tools_executed=tools_executed,
            partial=False,
            router=router_name,
            conversation_id=conv_id,
            active_filters=active_filters_payload(base_state),
            state_expired=state_expired,
            intent=intent,
        )
        return AssistantQueryResult(
            payload=payload,
            tool_name=tool_name,
            params_safe=base_safe,
            success=False,
            error_code=error_code,
            row_count=0,
            conversation_id=conv_id,
            intent=intent,
            clarification=True,
        )

    new_state = build_state_after_tool(
        tool_name=tool_name,
        params=params,
        tool_result=tool_result,
        base_state=base_state,
        filter_operations=filter_operations,
    )
    touch_conversation(conversation, state=new_state, increment_turn=True)
    active = active_filters_payload(new_state)

    payload = build_assistant_response(
        request_id=request_id,
        message=tool_result.get('message') or '',
        blocks=tool_result.get('blocks') or [],
        sources=tool_result.get('sources') or [],
        context=context,
        tools_executed=tools_executed,
        partial=bool(tool_result.get('partial', False)),
        router=router_name,
        conversation_id=conv_id,
        active_filters=active,
        state_expired=False,
        intent=intent,
    )
    return AssistantQueryResult(
        payload=payload,
        tool_name=tool_name,
        params_safe=base_safe,
        success=True,
        error_code='',
        row_count=row_count,
        conversation_id=conv_id,
        intent=intent,
        clarification=False,
    )


def _resolve_conversation(*, user, conversation_id: str | None, start_over: bool):
    existing = get_conversation_for_user(user, conversation_id)
    if start_over:
        if existing is not None:
            deactivate_conversation(existing)
        return create_conversation_for_user(user)
    if existing is not None:
        return existing
    return create_conversation_for_user(user)

