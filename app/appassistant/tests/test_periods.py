from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from appassistant.services.periods import PeriodValidationError, resolve_period


class PeriodResolutionTests(SimpleTestCase):
    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 30))
    def test_this_month_is_month_to_date(self, _mock_today):
        start, end = resolve_period(period='this_month')
        self.assertEqual(start, date(2026, 7, 1))
        self.assertEqual(end, date(2026, 7, 30))

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 30))
    def test_calendar_month_full(self, _mock_today):
        start, end = resolve_period(period='calendar_month')
        self.assertEqual(start, date(2026, 7, 1))
        self.assertEqual(end, date(2026, 7, 31))

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 30))
    def test_last_month(self, _mock_today):
        start, end = resolve_period(period='last_month')
        self.assertEqual(start, date(2026, 6, 1))
        self.assertEqual(end, date(2026, 6, 30))

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 1))
    def test_previous_calendar_months_span(self, _mock_today):
        self.assertEqual(
            resolve_period(period='previous_calendar_month'),
            (date(2026, 7, 1), date(2026, 7, 31)),
        )
        self.assertEqual(
            resolve_period(period='previous_2_calendar_months'),
            (date(2026, 6, 1), date(2026, 7, 31)),
        )
        self.assertEqual(
            resolve_period(period='last_two_calendar_months'),
            (date(2026, 6, 1), date(2026, 7, 31)),
        )

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 30))
    def test_last_n_months_ends_today(self, _mock_today):
        start, end = resolve_period(months=3)
        self.assertEqual(start, date(2026, 5, 1))
        self.assertEqual(end, date(2026, 7, 30))

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

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_today_yesterday_weeks(self, _mock_today):
        self.assertEqual(resolve_period(period='today'), (date(2026, 7, 15), date(2026, 7, 15)))
        self.assertEqual(
            resolve_period(period='yesterday'),
            (date(2026, 7, 14), date(2026, 7, 14)),
        )
        # 2026-07-15 is Wednesday → week starts Monday 13th
        self.assertEqual(
            resolve_period(period='this_week'),
            (date(2026, 7, 13), date(2026, 7, 15)),
        )
        self.assertEqual(
            resolve_period(period='last_week'),
            (date(2026, 7, 6), date(2026, 7, 12)),
        )

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_quarters_and_ytd(self, _mock_today):
        self.assertEqual(
            resolve_period(period='this_quarter'),
            (date(2026, 7, 1), date(2026, 7, 15)),
        )
        self.assertEqual(
            resolve_period(period='last_quarter'),
            (date(2026, 4, 1), date(2026, 6, 30)),
        )
        self.assertEqual(
            resolve_period(period='this_year'),
            (date(2026, 1, 1), date(2026, 7, 15)),
        )

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 7, 15))
    def test_last_six_months_alias(self, _mock_today):
        start, end = resolve_period(period='last_six_months')
        self.assertEqual(start, date(2026, 2, 1))
        self.assertEqual(end, date(2026, 7, 15))

    @override_settings(TIME_ZONE='UTC')
    @patch('appassistant.services.periods._today', return_value=date(2026, 8, 1))
    def test_last_3_months_alias(self, _mock_today):
        start, end = resolve_period(period='last_3_months')
        self.assertEqual(start, date(2026, 6, 1))
        self.assertEqual(end, date(2026, 8, 1))

