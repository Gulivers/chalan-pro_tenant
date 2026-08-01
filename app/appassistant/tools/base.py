"""Base interface for Level-1 read-only Assistant tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AssistantTool(ABC):
    """
    Narrow, typed, read-only tool.
    Implementations must authorize (user/tenant/perm) before functional filters.
    """

    name: str = ''
    description: str = ''

    # Net invoiced spending = PINV + is_active; NOT is_purchase / PRN / PO.
    spend_definition: str = (
        'Net invoiced spending = active PINV Document.total_amount only; '
        'not gross, not returns (PRN), not PO/committed, '
        'not the Sales vs Purchases chart (is_purchase) criterion'
    )

    @abstractmethod
    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Return normalized params or raise ValueError / validation error."""

    @abstractmethod
    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        """
        Run the tool and return structured data for the response builder.
        Must not write to business tables.
        """
