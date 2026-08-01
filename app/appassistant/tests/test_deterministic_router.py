"""DeterministicRouter unit tests (Increment C) — no DB."""

from __future__ import annotations

from django.test import SimpleTestCase

from appassistant.services.deterministic_router import UNSUPPORTED_CLARIFICATION, route


class DeterministicRouterTests(SimpleTestCase):
    def test_case1_list_purchase_transactions(self):
        result = route('Show me Harbor Freight transactions over $1,500 this month.')
        self.assertEqual(result.matched_case, 1)
        self.assertEqual(result.tool_name, 'list_purchase_transactions')
        self.assertEqual(result.params['vendor'], 'Harbor Freight')
        self.assertEqual(result.params['min_amount'], '1500.00')
        self.assertEqual(result.params['period'], 'this_month')

    def test_case1_money_variants(self):
        for msg in (
            'show me harbor freight transactions over $1500 this month',
            'HARBOR FREIGHT TRANSACTIONS OVER 1500 THIS MONTH',
            'Show me Harbor Freight transactions over $1,500.00 this month.',
        ):
            result = route(msg)
            self.assertEqual(result.matched_case, 1, msg)
            self.assertEqual(result.params['min_amount'], '1500.00', msg)
            self.assertEqual(result.params['vendor'].lower(), 'harbor freight', msg)

    def test_case2_sum_purchase_spending(self):
        result = route('How much did we spend with Harbor Freight this month?')
        self.assertEqual(result.matched_case, 2)
        self.assertEqual(result.tool_name, 'sum_purchase_spending')
        self.assertEqual(result.params, {
            'vendor': 'Harbor Freight',
            'period': 'this_month',
        })

    def test_case3_purchases_by_vendor(self):
        result = route('Show purchases by vendor this month.')
        self.assertEqual(result.matched_case, 3)
        self.assertEqual(result.tool_name, 'purchases_by_vendor')
        self.assertEqual(result.params, {'period': 'this_month'})

    def test_case3_supplier_synonym(self):
        result = route('show purchases by supplier this month')
        self.assertEqual(result.matched_case, 3)
        self.assertEqual(result.tool_name, 'purchases_by_vendor')

    def test_case4_compare_six_months(self):
        for msg in (
            'Compare purchases by supplier for the last six months.',
            'compare purchases by vendors for the last 6 months',
        ):
            result = route(msg)
            self.assertEqual(result.matched_case, 4, msg)
            self.assertEqual(result.tool_name, 'compare_purchases_by_vendor', msg)
            self.assertEqual(result.params, {'months': 6}, msg)

    def test_case5_top_vendors_default_months_12(self):
        """Highest spending without period → months=12 (documented product choice)."""
        result = route('Show the five vendors with the highest spending.')
        self.assertEqual(result.matched_case, 5)
        self.assertEqual(result.tool_name, 'top_vendors_by_spending')
        self.assertEqual(result.params, {'limit': 5, 'months': 12})

    def test_case5_digit_and_suppliers(self):
        result = route('Show the 5 suppliers with the highest spending')
        self.assertEqual(result.matched_case, 5)
        self.assertEqual(result.params['limit'], 5)
        self.assertEqual(result.params['months'], 12)

    def test_case5_explicit_last_n_months(self):
        result = route('Show the five vendors with the highest spending for the last 3 months')
        self.assertEqual(result.matched_case, 5)
        self.assertEqual(result.params, {'limit': 5, 'months': 3})

    def test_case6_spending_timeseries(self):
        for msg in (
            'Graph spending for the last three months.',
            'graph spending for the last 3 months',
            'Chart spending for the last three months',
        ):
            result = route(msg)
            self.assertEqual(result.matched_case, 6, msg)
            self.assertEqual(result.tool_name, 'spending_timeseries', msg)
            self.assertEqual(result.params, {'months': 3}, msg)

    def test_list_before_sum_specificity(self):
        # Must not route amount+transactions as a sum query.
        result = route('Show me Harbor Freight transactions over $1,500 this month.')
        self.assertEqual(result.tool_name, 'list_purchase_transactions')

    def test_timeseries_before_compare(self):
        result = route('Graph spending for the last six months.')
        self.assertEqual(result.matched_case, 6)
        self.assertEqual(result.tool_name, 'spending_timeseries')
        self.assertEqual(result.params['months'], 6)

    def test_unsupported(self):
        result = route('What is the weather in Miami?')
        self.assertIsNone(result.tool_name)
        self.assertIsNone(result.matched_case)
        self.assertEqual(result.params, {})
        self.assertIn('not supported', result.clarification.lower())
        self.assertEqual(result.clarification, UNSUPPORTED_CLARIFICATION)

    def test_empty_message(self):
        result = route('   ')
        self.assertIsNone(result.tool_name)
        self.assertIsNotNone(result.clarification)
