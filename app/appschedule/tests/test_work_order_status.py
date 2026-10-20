"""Work Order status catalog, progress gates, and Work Account rollup."""

from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import ProtectedError
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from appauth.testing import authenticate_api_client
from appschedule.models import (
    Event,
    WorkOrderProgressCheck,
    WorkOrderProgressItem,
    WorkOrderProgressTemplate,
    WorkOrderStatus,
    WorkOrderStatusHistory,
    WorkOrderTracking,
)
from appschedule.services.work_order_status import (
    ensure_initial_work_order_status,
    seed_work_order_defaults,
    set_progress_check,
    transition_work_order_status,
    work_account_status_summary,
)
from apptransactions.models import WorkAccount
from crewsapp.models import Category, Crew
from ctrctsapp.models import Builder

User = get_user_model()


def tenant_api_client(tenant) -> APIClient:
    client = APIClient()
    domain = tenant.get_primary_domain().domain
    client.defaults['HTTP_HOST'] = domain
    return client


class WorkOrderStatusTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'WO Status Tenant'
        tenant.email = 'owner@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_work_order_status'

    def setUp(self):
        super().setUp()
        seed_work_order_defaults()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='wo_user',
            email='wo@example.com',
            password='ValidPass123!',
        )
        for codename in (
            'view_event',
            'change_event',
            'add_event',
            'view_workorderstatus',
            'view_workaccount',
        ):
            perm = Permission.objects.filter(
                codename=codename,
            ).first()
            if perm:
                self.user.user_permissions.add(perm)
        authenticate_api_client(self.client, self.user)

        self.category = Category.objects.create(name='Rough In')
        self.crew = Crew.objects.create(name='Rough crew', category=self.category)
        self.builder = Builder.objects.create(name='WO Builder')
        self.work_account = WorkAccount.objects.create(
            title='1200 TEST LOT',
            builder=self.builder,
            lot='1200',
            address='1200 Test St',
        )
        # Re-seed templates now that Rough category exists.
        seed_work_order_defaults()

    def _make_event(self, **kwargs):
        defaults = dict(
            date=date.today(),
            end_dt=date.today(),
            crew=self.crew,
            work_account=self.work_account,
            created_by=self.user,
            title='1200 TEST LOT',
            lot='1200',
            address='1200 Test St',
        )
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    def test_seed_creates_six_statuses_once(self):
        self.assertEqual(WorkOrderStatus.objects.count(), 6)
        self.assertTrue(
            WorkOrderStatus.objects.filter(code='scheduled', is_initial=True).exists()
        )
        self.assertTrue(
            WorkOrderStatus.objects.filter(
                code='passed_closed',
                is_terminal=True,
                requires_completion_ready=True,
            ).exists()
        )
        again = seed_work_order_defaults()
        self.assertEqual(again['statuses'], 0)

    def test_event_create_gets_scheduled_and_progress(self):
        event = self._make_event()
        tracking = WorkOrderTracking.objects.get(event=event)
        self.assertEqual(tracking.current_status.code, 'scheduled')
        self.assertEqual(
            WorkOrderStatusHistory.objects.filter(event=event).count(),
            1,
        )
        self.assertGreater(event.progress_checks.count(), 0)

    def test_date_change_does_not_reset_status(self):
        event = self._make_event()
        for check in event.progress_checks.select_related('item'):
            if check.item.is_required_for_inspection:
                set_progress_check(check=check, is_done=True, user=self.user)
        transition_work_order_status(
            event=event,
            status_code='in_progress',
            user=self.user,
        )
        event.date = date(2099, 1, 1)
        event.end_dt = date(2099, 1, 1)
        event.save()
        event.work_order_tracking.refresh_from_db()
        self.assertEqual(event.work_order_tracking.current_status.code, 'in_progress')

    def test_cannot_close_with_pending_required_progress(self):
        event = self._make_event()
        with self.assertRaises(ValidationError) as ctx:
            transition_work_order_status(
                event=event,
                status_code='passed_closed',
                user=self.user,
            )
        self.assertIn('missing_requirements', ctx.exception.detail)

    def test_inspection_gate_and_flexible_corrections_loop(self):
        event = self._make_event()
        with self.assertRaises(ValidationError):
            transition_work_order_status(
                event=event,
                status_code='pending_inspection',
                user=self.user,
            )
        for check in event.progress_checks.select_related('item'):
            if check.item.is_required_for_inspection:
                set_progress_check(check=check, is_done=True, user=self.user)

        transition_work_order_status(
            event=event,
            status_code='pending_inspection',
            user=self.user,
        )
        transition_work_order_status(
            event=event,
            status_code='corrections_required',
            user=self.user,
        )
        tracking = transition_work_order_status(
            event=event,
            status_code='pending_inspection',
            notes='Ready for re-inspection',
            user=self.user,
        )
        tracking.refresh_from_db()
        self.assertEqual(tracking.current_status.code, 'pending_inspection')
        self.assertGreaterEqual(
            WorkOrderStatusHistory.objects.filter(event=event).count(),
            4,
        )

    def test_referenced_status_cannot_be_deleted(self):
        event = self._make_event()
        status_obj = event.work_order_tracking.current_status
        with self.assertRaises(ProtectedError):
            status_obj.delete()

    def test_work_account_rollup_not_completed_if_phase_missing(self):
        event = self._make_event()
        for check in event.progress_checks.select_related('item'):
            if check.item.is_required_for_completion:
                set_progress_check(check=check, is_done=True, user=self.user)
        transition_work_order_status(
            event=event,
            status_code='passed_closed',
            user=self.user,
        )
        # Add another expected phase template without a WO.
        tug = Category.objects.create(name='TUG')
        WorkOrderProgressTemplate.objects.create(
            name='TUG',
            category=tug,
            is_active=True,
            is_expected_for_work_account=True,
        )
        summary = work_account_status_summary(self.work_account)
        self.assertEqual(summary['overall_state'], 'in_progress')
        self.assertGreaterEqual(summary['expected_phases_total'], 2)

    def test_api_status_transition_and_progress(self):
        event = self._make_event()
        listed = self.client.get('/api/work-order-statuses/')
        self.assertEqual(listed.status_code, status.HTTP_200_OK)

        current = self.client.get(f'/api/events/{event.id}/work-order-status/')
        self.assertEqual(current.status_code, status.HTTP_200_OK)
        self.assertEqual(current.data['status_code'], 'scheduled')

        progress = self.client.get(f'/api/events/{event.id}/work-order-progress/')
        self.assertEqual(progress.status_code, status.HTTP_200_OK)
        self.assertGreater(len(progress.data), 0)

        check_id = progress.data[0]['id']
        patched = self.client.patch(
            f'/api/events/{event.id}/work-order-progress/{check_id}/',
            {'is_done': True, 'notes': 'ok'},
            format='json',
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertTrue(patched.data['is_done'])

        moved = self.client.post(
            f'/api/events/{event.id}/work-order-status/transition/',
            {'status_code': 'in_progress', 'notes': 'crew on site'},
            format='json',
        )
        self.assertEqual(moved.status_code, status.HTTP_200_OK)
        self.assertEqual(moved.data['status_code'], 'in_progress')

        history = self.client.get(
            f'/api/events/{event.id}/work-order-status/history/'
        )
        self.assertEqual(history.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(history.data), 2)

        rollup = self.client.get(
            f'/api/work-accounts/{self.work_account.id}/work-order-progress/'
        )
        self.assertEqual(rollup.status_code, status.HTTP_200_OK)
        self.assertIn('overall_state', rollup.data)
