"""
Execute a single allowlisted Assistant tool by name.

Increment B: registry + executor ready. DeterministicRouter / LLM wiring is Increment C.
"""

from __future__ import annotations

from typing import Any

from appassistant.services.blocks import clarification_text
from appassistant.tools.errors import ToolError
from appassistant.tools.registry import ToolRegistry, get_default_registry


def execute_tool(
    tool_name: str,
    *,
    user,
    params: dict[str, Any] | None = None,
    registry: ToolRegistry | None = None,
) -> dict[str, Any]:
    """
    Validate params and execute one tool.

    Returns the tool contract:
      {message, blocks, sources, row_count, partial}

    On ToolError, returns a closed failure payload with the same shape
    (partial=False, row_count=0) and raises nothing — callers that need the
    exception can use execute_tool_strict.
    """
    reg = registry or get_default_registry()
    tool = reg.get(tool_name)
    if tool is None:
        return {
            'message': f'Unknown tool: {tool_name}',
            'blocks': [
                clarification_text(
                    block_id='unknown-tool',
                    message=f'Tool "{tool_name}" is not available.',
                )
            ],
            'sources': [],
            'row_count': 0,
            'partial': False,
            'error_code': 'not_found',
        }

    try:
        normalized = tool.validate_params(params or {})
        result = tool.execute(user=user, params=normalized)
    except ToolError as exc:
        blocks = [
            clarification_text(
                block_id=f'tool-error-{exc.code}',
                message=exc.message,
                candidates=exc.details.get('candidates') if exc.code == 'ambiguous_vendor' else None,
            )
        ]
        return {
            'message': exc.message,
            'blocks': blocks,
            'sources': [],
            'row_count': 0,
            'partial': False,
            'error_code': exc.code,
            'error_details': exc.details,
        }

    # Tools already return the contract; ensure required keys.
    return {
        'message': result.get('message', ''),
        'blocks': result.get('blocks') or [],
        'sources': result.get('sources') or [
            {'type': 'tool', 'name': tool_name, 'row_count': int(result.get('row_count') or 0)}
        ],
        'row_count': int(result.get('row_count') or 0),
        'partial': bool(result.get('partial', False)),
    }


def execute_tool_strict(
    tool_name: str,
    *,
    user,
    params: dict[str, Any] | None = None,
    registry: ToolRegistry | None = None,
) -> dict[str, Any]:
    """Like execute_tool but re-raises ToolError and unknown-tool as ToolError."""
    reg = registry or get_default_registry()
    tool = reg.get(tool_name)
    if tool is None:
        raise ToolError(f'Unknown tool: {tool_name}', code='not_found')
    normalized = tool.validate_params(params or {})
    return tool.execute(user=user, params=normalized)
