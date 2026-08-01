from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from appassistant.services.periods import PeriodValidationError, resolve_period


class PeriodResolutionTests(SimpleTestCase):
    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 30))
    def test_this_month(self, _mock_today):
        start, end = resolve_period(period='this_month')
        self.assertEqual(start, date(2026, 7, 1))
        self.assertEqual(end, date(2026, 7, 31))

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 30))
    def test_last_n_months(self, _mock_today):
        start, end = resolve_period(months=3)
        self.assertEqual(start, date(2026, 5, 1))
        self.assertEqual(end, date(2026, 7, 31))

    def test_explicit_range(self):
        start, end = resolve_period(date_from='2026-01-01', date_to='2026-01-31')
        self.assertEqual(start, date(2026, 1, 1))
        self.assertEqual(end, date(2026, 1, 31))

    def test_invalid_months(self):
        with self.assertRaises(PeriodValidationError):
            resolve_period(months=13)

    def test_inverted_range(self):
        with self.assertRaises(PeriodValidationError):
            resolve_period(date_from='2026-02-01', date_to='2026-01-01')

    def test_explicit_range_rejects_span_over_366_days(self):
        with self.assertRaises(PeriodValidationError):
            resolve_period(date_from='2025-01-01', date_to='2026-01-02')

    def test_explicit_range_allows_366_days(self):
        start, end = resolve_period(date_from='2024-01-01', date_to='2024-12-31')
        self.assertEqual(start, date(2024, 1, 1))
        self.assertEqual(end, date(2024, 12, 31))

