"""Sales-led access: new tenants need payment; Admin can still grant trial."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from appbilling.services.access import get_billing_access
from appbilling.services.trial import (
    mark_payment_required_for_tenant,
    start_trial_for_tenant,
)


def _tenant(**kwargs):
    base = {
        'on_trial': False,
        'trial_start': None,
        'trial_end': None,
        'paid_until': None,
        'created_on': timezone.now().date(),
        'landing_selected_plan': None,
        'recommended_plan': None,
        'crew_count': 4,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


class MarkPaymentRequiredTests(SimpleTestCase):
    def test_marks_tenant_without_open_trial(self):
        before = timezone.now()
        tenant = _tenant(on_trial=True)
        mark_payment_required_for_tenant(tenant)
        after = timezone.now()
        self.assertFalse(tenant.on_trial)
        self.assertIsNone(tenant.trial_start)
        self.assertIsNone(tenant.paid_until)
        self.assertIsNotNone(tenant.trial_end)
        self.assertGreaterEqual(tenant.trial_end, before)
        self.assertLessEqual(tenant.trial_end, after)


class BillingAccessSalesLedTests(SimpleTestCase):
    def test_payment_required_tenant_is_denied(self):
        tenant = _tenant()
        mark_payment_required_for_tenant(tenant)
        with patch('appbilling.services.access._get_subscription', return_value=None):
            with patch(
                'appbilling.services.access.get_suggested_plan_slug',
                return_value='professional',
            ):
                access = get_billing_access(tenant)
        self.assertFalse(access.allowed)
        self.assertTrue(access.needs_payment)
        self.assertFalse(access.trial_active)
        self.assertEqual(access.reason, 'trial_expired')

    def test_no_trial_end_and_no_stripe_is_denied_without_inventing_days(self):
        tenant = _tenant(trial_end=None, on_trial=False)
        with patch('appbilling.services.access._get_subscription', return_value=None):
            with patch(
                'appbilling.services.access.get_suggested_plan_slug',
                return_value='professional',
            ):
                access = get_billing_access(tenant)
        self.assertFalse(access.allowed)
        self.assertTrue(access.needs_payment)
        self.assertEqual(access.reason, 'no_subscription')
        self.assertIsNone(access.trial_end)

    def test_admin_trial_still_allows_access(self):
        tenant = _tenant()
        start_trial_for_tenant(tenant, days=7)
        with patch('appbilling.services.access._get_subscription', return_value=None):
            with patch(
                'appbilling.services.access.get_suggested_plan_slug',
                return_value='professional',
            ):
                with patch(
                    'appbilling.services.access.get_effective_plan_for_tenant',
                    return_value=SimpleNamespace(slug='professional'),
                ):
                    access = get_billing_access(tenant)
        self.assertTrue(access.allowed)
        self.assertTrue(access.trial_active)
        self.assertEqual(access.reason, 'trial')
        self.assertFalse(access.needs_payment)

    def test_expired_admin_trial_denied(self):
        tenant = _tenant(
            on_trial=True,
            trial_start=timezone.now() - timedelta(days=10),
            trial_end=timezone.now() - timedelta(days=1),
        )
        with patch('appbilling.services.access._get_subscription', return_value=None):
            with patch(
                'appbilling.services.access.get_suggested_plan_slug',
                return_value='starter',
            ):
                access = get_billing_access(tenant)
        self.assertFalse(access.allowed)
        self.assertEqual(access.reason, 'trial_expired')
