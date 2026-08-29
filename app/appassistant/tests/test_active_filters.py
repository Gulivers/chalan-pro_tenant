"""Active filter chips payload (parameter trace)."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from appassistant.services.active_filters import active_filters_payload
from appassistant.services.spend import SPEND_METRIC_LABEL


@override_settings(TIME_ZONE='UTC')
class ActiveFiltersPayloadTests(SimpleTestCase):
    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 1))
    def test_chips_include_tool_vendor_amount_period(self, _mock):
        state = {
            'domain': 'purchase_documents',
            'metric': 'net_invoiced_spend',
            'tool': 'list_purchase_transactions',
            'filters': {
                'vendors': [{'id': 7, 'name': 'Home Depot'}],
                'vendor_ids': [7],
                'min_amount': '100.00',
                'period_label': 'this_month',
                'date_from': '2026-08-01',
                'date_to': '2026-08-01',
            },
            'presentation': ['message', 'table', 'sources'],
        }
        payload = active_filters_payload(state)
        by_key = {}
        for chip in payload['chips']:
            by_key.setdefault(chip['key'], chip)
        self.assertEqual(by_key['tool']['label'], 'Transactions')
        self.assertFalse(by_key['tool']['removable'])
        self.assertEqual(by_key['vendor']['label'], 'Home Depot')
        self.assertTrue(by_key['vendor']['removable'])
        self.assertEqual(by_key['min_amount']['label'], 'Over $100.00')
        self.assertEqual(by_key['period']['label'], 'this month')
        self.assertEqual(by_key['metric']['label'], SPEND_METRIC_LABEL)
        self.assertTrue(payload['inherited'])
