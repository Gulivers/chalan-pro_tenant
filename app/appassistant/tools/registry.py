"""Allowlisted tool registry for JobRhythm Assistant (Level 1)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import AssistantTool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, AssistantTool] = {}

    def register(self, tool: AssistantTool) -> None:
        if not tool.name:
            raise ValueError('Tool must define a non-empty name.')
        if tool.name in self._tools:
            raise ValueError(f'Tool "{tool.name}" is already registered.')
        self._tools[tool.name] = tool

    def get(self, name: str) -> AssistantTool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._tools


_default_registry: ToolRegistry | None = None


def _register_level1_tools(registry: ToolRegistry) -> None:
    from .compare_purchases_by_vendor import ComparePurchasesByVendorTool
    from .list_purchase_transactions import ListPurchaseTransactionsTool
    from .purchases_by_vendor import PurchasesByVendorTool
    from .spending_timeseries import SpendingTimeseriesTool
    from .sum_purchase_spending import SumPurchaseSpendingTool
    from .top_vendors_by_spending import TopVendorsBySpendingTool

    for tool_cls in (
        ListPurchaseTransactionsTool,
        SumPurchaseSpendingTool,
        PurchasesByVendorTool,
        ComparePurchasesByVendorTool,
        TopVendorsBySpendingTool,
        SpendingTimeseriesTool,
    ):
        registry.register(tool_cls())


def get_default_registry() -> ToolRegistry:
    """Level-1 registry with the six spend tools (Increment B)."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
        _register_level1_tools(_default_registry)
    return _default_registry


def reset_default_registry() -> ToolRegistry:
    """Test helper: rebuild the singleton registry."""
    global _default_registry
    _default_registry = None
    return get_default_registry()
