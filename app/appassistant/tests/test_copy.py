from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from appassistant.services.copy import (
    format_money_display,
    invoice_count_label,
    net_spending_message,
    source_display,
)
from appassistant.tools._common import tool_result


class CopyHelpersTests(SimpleTestCase):
    def test_format_money_display(self):
        self.assertEqual(format_money_display(Decimal('22966.78')), '$22,966.78')
        self.assertEqual(format_money_display(Decimal('0')), '$0.00')

    def test_invoice_count_label(self):
        self.assertEqual(invoice_count_label(1), '1 purchase invoice')
        self.assertEqual(invoice_count_label(3), '3 purchase invoices')

    def test_source_display(self):
        self.assertEqual(source_display(3), 'Source: 3 purchase invoices')

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 15))
    def test_net_spending_message_this_month(self, _mock):
        msg = net_spending_message(
            vendor_name='Home Depot',
            amount=Decimal('22966.78'),
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 31),
            invoice_count=3,
        )
        self.assertEqual(
            msg,
            'Net spending with Home Depot this month is $22,966.78, '
            'based on 3 purchase invoices.',
        )

    def test_tool_result_user_facing_source(self):
        result = tool_result(
            tool_name='sum_purchase_spending',
            message='ok',
            blocks=[],
            row_count=3,
            invoice_count=3,
        )
        self.assertEqual(result['sources'][0]['display'], 'Source: 3 purchase invoices')
        self.assertEqual(result['sources'][0]['label'], '3 purchase invoices')
        self.assertEqual(result['sources'][0]['tool_name'], 'sum_purchase_spending')
