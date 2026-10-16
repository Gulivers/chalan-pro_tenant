"""Status tracking configurable por DocumentType (excluye rediseño de MR)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import ProtectedError
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.test import APIClient

from appauth.testing import authenticate_api_client
from apptransactions.models import (
    Document,
    DocumentStatus,
    DocumentTracking,
    DocumentTrackingHistory,
    DocumentType,
)
from apptransactions.services.document_status import (
    ensure_initial_tracking,
    seed_default_document_statuses,
    transition_document_status,
)

User = get_user_model()


def tenant_api_client(tenant) -> APIClient:
    client = APIClient()
    domain = tenant.get_primary_domain().domain
    client.defaults['HTTP_HOST'] = domain
    return client


class DocumentStatusTrackingTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Status Tracking Tenant'
        tenant.email = 'owner@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_document_status_tracking'

    def setUp(self):
        super().setUp()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='tracker',
            email='tracker@example.com',
            password='ValidPass123!',
        )
        for codename in (
            'view_document', 'add_document', 'change_document',
            'view_documenttype', 'change_documenttype',
            'view_documentstatus', 'add_documentstatus',
            'change_documentstatus', 'delete_documentstatus',
        ):
            perm = Permission.objects.filter(
                codename=codename,
                content_type__app_label='apptransactions',
            ).first()
            if perm:
                self.user.user_permissions.add(perm)
        authenticate_api_client(self.client, self.user)

        self.po_type, _ = DocumentType.objects.get_or_create(
            type_code='PO',
            defaults={
                'description': 'Purchase Order',
                'is_purchase': True,
                'warehouse_required': True,
                'stock_movement': 0,
                'uses_status_tracking': False,
            },
        )
        seed_default_document_statuses()

    def test_seed_is_idempotent_and_leaves_tracking_off(self):
        # Vaciar y reseedar para comprobar que no pisa personalizaciones.
        DocumentStatus.objects.filter(document_type=self.po_type).delete()
        first = seed_default_document_statuses()
        second = seed_default_document_statuses()
        self.assertGreater(first, 0)
        self.assertEqual(second, 0)
        self.po_type.refresh_from_db()
        self.assertFalse(self.po_type.uses_status_tracking)
        self.assertTrue(
            DocumentStatus.objects.filter(
                document_type=self.po_type,
                code='draft',
                is_initial=True,
            ).exists()
        )

    def test_new_document_without_flag_has_no_tracking(self):
        doc = Document.objects.create(
            document_type=self.po_type,
            created_by=self.user,
        )
        self.assertFalse(hasattr(doc, 'tracking') and DocumentTracking.objects.filter(document=doc).exists())
        self.assertFalse(DocumentTracking.objects.filter(document=doc).exists())

    def test_enable_tracking_rejects_missing_initial_when_statuses_exist(self):
        other, _ = DocumentType.objects.get_or_create(
            type_code='SQ',
            defaults={'description': 'Sales Quotation', 'is_sales': True},
        )
        DocumentStatus.objects.create(
            document_type=other,
            code='open',
            name='Open',
            sequence=1,
            is_initial=False,
            is_terminal=False,
        )
        other.uses_status_tracking = True
        with self.assertRaises(DjangoValidationError):
            other.save()

        initial = DocumentStatus.objects.get(document_type=other, code='open')
        initial.is_initial = True
        initial.save()
        other.uses_status_tracking = True
        other.save()

        doc = Document.objects.create(document_type=other, created_by=self.user)
        tracking = DocumentTracking.objects.get(document=doc)
        self.assertEqual(tracking.current_status.code, 'open')
        self.assertEqual(
            DocumentTrackingHistory.objects.filter(document=doc).count(),
            1,
        )

    def test_transition_is_linear_and_atomic_history(self):
        self.po_type.uses_status_tracking = True
        self.po_type.save()
        doc = Document.objects.create(document_type=self.po_type, created_by=self.user)
        self.assertEqual(doc.tracking.current_status.code, 'draft')

        transition_document_status(
            document=doc,
            status_code='submitted',
            notes='sent to vendor',
            user=self.user,
        )
        doc.tracking.refresh_from_db()
        self.assertEqual(doc.tracking.current_status.code, 'submitted')
        self.assertEqual(DocumentTrackingHistory.objects.filter(document=doc).count(), 2)

        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            transition_document_status(
                document=doc,
                status_code='ordered',
                notes='',
                user=self.user,
            )

    def test_cannot_disable_tracking_with_in_progress_docs(self):
        self.po_type.uses_status_tracking = True
        self.po_type.save()
        Document.objects.create(document_type=self.po_type, created_by=self.user)
        self.po_type.uses_status_tracking = False
        with self.assertRaises(DjangoValidationError):
            self.po_type.save()

    def test_referenced_status_cannot_be_deleted(self):
        self.po_type.uses_status_tracking = True
        self.po_type.save()
        doc = Document.objects.create(document_type=self.po_type, created_by=self.user)
        status_obj = doc.tracking.current_status
        with self.assertRaises(ProtectedError):
            status_obj.delete()
        status_obj.is_active = False
        status_obj.save()
        status_obj.refresh_from_db()
        self.assertFalse(status_obj.is_active)

    def test_api_list_statuses_and_transition(self):
        self.po_type.uses_status_tracking = True
        self.po_type.save()
        listed = self.client.get(
            f'/api/document-statuses/?document_type={self.po_type.id}'
        )
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        codes = {row['code'] for row in listed.data}
        self.assertIn('draft', codes)

        doc = Document.objects.create(document_type=self.po_type, created_by=self.user)
        current = self.client.get(f'/api/documents/{doc.id}/status/')
        self.assertEqual(current.status_code, status.HTTP_200_OK)
        self.assertEqual(current.data['status_code'], 'draft')

        moved = self.client.post(
            f'/api/documents/{doc.id}/transition-status/',
            {'status_code': 'submitted', 'notes': 'ok'},
            format='json',
        )
        self.assertEqual(moved.status_code, status.HTTP_200_OK)
        self.assertEqual(moved.data['status_code'], 'submitted')

        history = self.client.get(f'/api/documents/{doc.id}/status-history/')
        self.assertEqual(history.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history.data), 2)

    def test_mr_keeps_uses_status_tracking_true(self):
        mr = DocumentType.objects.filter(type_code='MR').first()
        self.assertIsNotNone(mr)
        self.assertTrue(mr.uses_status_tracking)

    def test_ensure_initial_tracking_idempotent(self):
        self.po_type.uses_status_tracking = True
        self.po_type.save()
        doc = Document.objects.create(document_type=self.po_type, created_by=self.user)
        first = ensure_initial_tracking(document=doc, user=self.user)
        second = ensure_initial_tracking(document=doc, user=self.user)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(DocumentTracking.objects.filter(document=doc).count(), 1)
        self.assertEqual(DocumentTrackingHistory.objects.filter(document=doc).count(), 1)
