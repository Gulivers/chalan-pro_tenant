"""
Assistant query orchestrator (Increment C).

Flow: message → DeterministicRouter → execute_tool → structured response.
No LLM. Fail closed on tool errors (HTTP 200 + clarification blocks).
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from uuid import UUID

from appassistant.contracts.response import build_assistant_response
from appassistant.services.blocks import clarification_text, text_block
from appassistant.services.deterministic_router import (
    UNSUPPORTED_CLARIFICATION,
    RouteResult,
    route,
)
from appassistant.tools.executor import execute_tool

logger = logging.getLogger('appassistant')

# Typed keys allowed in audit params_safe (never the full prompt).
_AUDIT_PARAM_KEYS = frozenset({
    'vendor',
    'vendor_id',
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


def sanitize_tool_params_for_audit(
    params: dict[str, Any] | None,
    *,
    matched_case: int | None = None,
    message_len: int = 0,
    context: dict | None = None,
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
        else:
            safe[key] = str(value)
    return safe


def run_assistant_query(
    *,
    user,
    message: str,
    context: dict | None,
    request_id: UUID | str,
) -> AssistantQueryResult:
    """
    Route → execute (if matched) → build full API response payload.

    On unmatched route or tool error_code: still return a valid 200 payload
    with clarification text blocks; success=False for audit when a tool failed.
    """
    ctx = deepcopy(context) if context else {}
    routed: RouteResult = route(message)
    base_safe = sanitize_tool_params_for_audit(
        routed.params,
        matched_case=routed.matched_case,
        message_len=len(message or ''),
        context=ctx,
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
            context=ctx,
            tools_executed=[],
            partial=False,
            router='deterministic',
        )
        return AssistantQueryResult(
            payload=payload,
            tool_name='',
            params_safe=base_safe,
            success=True,
            error_code='',
            row_count=0,
        )

    tools_executed = [routed.tool_name]
    try:
        tool_result = execute_tool(
            routed.tool_name,
            user=user,
            params=routed.params,
        )
    except Exception:
        # Unexpected failures must not leak internals; fail closed with clarification.
        logger.exception(
            'assistant.tool_unexpected_error tool=%s',
            routed.tool_name,
        )
        message = 'Unable to complete this query. Please try again or rephrase.'
        payload = build_assistant_response(
            request_id=request_id,
            message=message,
            blocks=[
                clarification_text(
                    block_id='tool-internal-error',
                    message=message,
                )
            ],
            sources=[{'type': 'tool', 'name': routed.tool_name, 'row_count': 0}],
            context=ctx,
            tools_executed=tools_executed,
            partial=False,
            router='deterministic',
        )
        return AssistantQueryResult(
            payload=payload,
            tool_name=routed.tool_name,
            params_safe=base_safe,
            success=False,
            error_code='internal',
            row_count=0,
        )

    error_code = tool_result.get('error_code') or ''
    row_count = int(tool_result.get('row_count') or 0)

    if error_code:
        # Fail closed to the user: clarification blocks, HTTP 200.
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
            context=ctx,
            tools_executed=tools_executed,
            partial=False,
            router='deterministic',
        )
        return AssistantQueryResult(
            payload=payload,
            tool_name=routed.tool_name,
            params_safe=base_safe,
            success=False,
            error_code=error_code,
            row_count=0,
        )

    payload = build_assistant_response(
        request_id=request_id,
        message=tool_result.get('message') or '',
        blocks=tool_result.get('blocks') or [],
        sources=tool_result.get('sources') or [],
        context=ctx,
        tools_executed=tools_executed,
        partial=bool(tool_result.get('partial', False)),
        router='deterministic',
    )
    return AssistantQueryResult(
        payload=payload,
        tool_name=routed.tool_name,
        params_safe=base_safe,
        success=True,
        error_code='',
        row_count=row_count,
    )
