"""Typed errors for Assistant tool validation and execution."""

from __future__ import annotations

from typing import Any


class ToolError(Exception):
    """
    Closed failure for tools.

    Codes:
      - permission
      - validation
      - ambiguous_vendor
      - not_found
    """

    def __init__(
        self,
        message: str,
        *,
        code: str,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


def permission_error(message: str = 'Missing permission to view documents.') -> ToolError:
    return ToolError(message, code='permission')


def validation_error(message: str, details: dict[str, Any] | None = None) -> ToolError:
    return ToolError(message, code='validation', details=details)


def ambiguous_vendor_error(
    message: str,
    candidates: list[dict[str, Any]],
) -> ToolError:
    return ToolError(
        message,
        code='ambiguous_vendor',
        details={'candidates': candidates},
    )


def not_found_error(message: str, details: dict[str, Any] | None = None) -> ToolError:
    return ToolError(message, code='not_found', details=details)
