"""Unit tests for conversational FilterMerger (Increment C1)."""

from __future__ import annotations

from django.test import SimpleTestCase

from appassistant.services.conversation_state import (
    empty_state,
    is_state_reusable,
    validate_state,
)
from appassistant.services.filter_merger import (
    FilterOperation,
    filters_for_tool,
    merge_conversation_state,
)


def _home_depot_state(**overrides):
    state = empty_state()
    state['tool'] = 'sum_purchase_spending'
    state['filters'] = {
        'vendor_ids': [18],
        'vendors': [{'id': 18, 'name': 'Home Depot'}],
        'period_label': 'this_month',
        'date_from': '2026-07-01',
        'date_to': '2026-07-15',
        'timezone': 'UTC',
        'min_amount': '1500.00',
    }
    state.update(overrides)
    return validate_state(state)


class FilterMergerTests(SimpleTestCase):
    def test_case1_replace_period_keeps_vendor(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            tool='sum_purchase_spending',
            operations=[
                FilterOperation(
                    field='period',
                    operation='replace_period',
                    value={
                        'period_label': 'last_month',
                        'date_from': '2026-06-01',
                        'date_to': '2026-06-30',
                        'timezone': 'UTC',
                    },
                )
            ],
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.inherited)
        self.assertEqual(result.state['filters']['vendor_ids'], [18])
        self.assertEqual(result.state['filters']['date_from'], '2026-06-01')
        self.assertEqual(result.state['filters']['date_to'], '2026-06-30')
        self.assertEqual(result.state['filters']['min_amount'], '1500.00')
        self.assertNotIn('comparison_period', result.state['filters'])

    def test_case2_compare_with_period_keeps_primary(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            operations=[
                FilterOperation(
                    field='period',
                    operation='compare_with_period',
                    value={
                        'period_label': 'last_month',
                        'date_from': '2026-06-01',
                        'date_to': '2026-06-30',
                    },
                )
            ],
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.state['filters']['date_from'], '2026-07-01')
        self.assertEqual(
            result.state['filters']['comparison_period']['date_from'],
            '2026-06-01',
        )
        self.assertEqual(result.state['tool'], 'compare_vendor_spending_periods')

    def test_case3_add_min_amount(self):
        previous = _home_depot_state()
        previous['filters'].pop('min_amount')
        previous = validate_state(previous)
        result = merge_conversation_state(
            previous,
            operations=[
                FilterOperation(field='min_amount', operation='set', value='2000.00')
            ],
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.state['filters']['min_amount'], '2000.00')
        self.assertEqual(result.state['filters']['vendor_ids'], [18])

    def test_case4_replace_vendor(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            operations=[
                FilterOperation(
                    field='vendor',
                    operation='set',
                    value={'id': 22, 'name': "Lowe's"},
                )
            ],
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.state['filters']['vendor_ids'], [22])
        self.assertEqual(result.state['filters']['vendors'][0]['name'], "Lowe's")
        self.assertEqual(result.state['filters']['period_label'], 'this_month')

    def test_case5_include_another_vendor(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            operations=[
                FilterOperation(
                    field='vendor',
                    operation='add',
                    value={'id': 22, 'name': "Lowe's"},
                )
            ],
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.state['filters']['vendor_ids'], [18, 22])

    def test_case6_remove_min_amount(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            operations=[
                FilterOperation(field='min_amount', operation='clear', value=None)
            ],
        )
        self.assertTrue(result.ok)
        self.assertNotIn('min_amount', result.state['filters'])
        self.assertEqual(result.state['filters']['vendor_ids'], [18])

    def test_case7_change_tool_keeps_filters(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            tool='list_purchase_transactions',
            operations=[
                FilterOperation(
                    field='tool',
                    operation='change_tool',
                    value='list_purchase_transactions',
                )
            ],
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.state['tool'], 'list_purchase_transactions')
        self.assertEqual(result.state['filters']['vendor_ids'], [18])
        self.assertEqual(result.state['filters']['min_amount'], '1500.00')
        params = filters_for_tool(result.state, 'list_purchase_transactions')
        self.assertEqual(params['vendor_id'], 18)
        self.assertEqual(params['min_amount'], '1500.00')
        self.assertEqual(params['date_from'], '2026-07-01')

    def test_case8_change_presentation_only(self):
        previous = _home_depot_state()
        previous['tool'] = 'compare_purchases_by_vendor'
        previous = validate_state(previous)
        result = merge_conversation_state(
            previous,
            operations=[
                FilterOperation(
                    field='presentation',
                    operation='change_presentation',
                    value=['message', 'bar_chart', 'sources'],
                )
            ],
        )
        self.assertTrue(result.ok)
        self.assertEqual(
            result.state['presentation'],
            ['message', 'bar_chart', 'sources'],
        )
        self.assertEqual(result.state['filters']['vendor_ids'], [18])

    def test_case9_clarify_does_not_mutate_for_execution(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            operations=[
                FilterOperation(
                    field='vendor',
                    operation='clarify',
                    value='Which vendor do you mean: Home Depot or Lowe’s?',
                )
            ],
        )
        self.assertTrue(result.needs_clarification)
        self.assertFalse(result.ok)
        self.assertIn('Home Depot', result.clarification or '')

    def test_case10_domain_change_drops_vendor(self):
        previous = _home_depot_state()
        # Unsupported domain today → error (crews not implemented).
        result = merge_conversation_state(
            previous,
            domain='crews_jobs',
            operations=[],
        )
        self.assertIsNotNone(result.error)
        self.assertIn('Unsupported domain', result.error)

    def test_case13_reset_clears_filters(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            operations=[FilterOperation(field='*', operation='reset')],
            tool='list_purchase_transactions',
        )
        self.assertTrue(result.ok)
        self.assertFalse(result.inherited)
        self.assertEqual(result.state['filters'], {})
        self.assertEqual(result.state['tool'], 'list_purchase_transactions')

    def test_expired_state_does_not_inherit(self):
        previous = _home_depot_state()
        result = merge_conversation_state(
            previous,
            state_expired=True,
            tool='sum_purchase_spending',
            operations=[
                FilterOperation(
                    field='vendor',
                    operation='set',
                    value={'id': 18, 'name': 'Home Depot'},
                )
            ],
        )
        self.assertTrue(result.ok)
        self.assertFalse(result.inherited)
        self.assertEqual(result.state['filters']['vendor_ids'], [18])
        self.assertNotIn('min_amount', result.state['filters'])

    def test_is_state_reusable_ttl(self):
        from datetime import timedelta

        from django.utils import timezone

        now = timezone.now()
        self.assertTrue(
            is_state_reusable(
                is_active=True,
                last_activity_at=now - timedelta(hours=23),
                turn_count=1,
                now=now,
            )
        )
        self.assertFalse(
            is_state_reusable(
                is_active=True,
                last_activity_at=now - timedelta(hours=25),
                turn_count=1,
                now=now,
            )
        )
        self.assertFalse(
            is_state_reusable(
                is_active=True,
                last_activity_at=now,
                turn_count=30,
                now=now,
            )
        )
