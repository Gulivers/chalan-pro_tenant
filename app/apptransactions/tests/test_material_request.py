from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django_tenants.test.cases import TenantTestCase
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import ProtectedError
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate

from appinventory.models import Product
from appschedule.models import Event
from apptransactions.material_request_api import MaterialRequestViewSet
from apptransactions.models import (
    Document,
    DocumentLink,
    DocumentStatus,
    DocumentTrackingHistory,
    DocumentType,
    WorkAccount,
)
from apptransactions.services.material_request import (
    create_material_request,
    transition_material_request,
    update_material_request_lines,
    delete_material_request,
)
from crewsapp.models import Category, Crew
from ctrctsapp.models import Builder

User = get_user_model()


class MaterialRequestTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Material Request Tenant'

    @classmethod
    def get_test_schema_name(cls):
        return 'test_material_request'

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='jordan', password='secret')
        for codename in ('add_document', 'change_document', 'view_document'):
            perm = Permission.objects.get(codename=codename, content_type__app_label='apptransactions')
            self.user.user_permissions.add(perm)
        self.document_type = DocumentType.objects.get(type_code='MR')
        self.builder = Builder.objects.create(name='Sky Builder')
        self.work_account = WorkAccount.objects.create(
            title='1100 SKYSAIL',
            builder=self.builder,
        )
        self.category = Category.objects.create(name='Trim')
        self.crew = Crew.objects.create(name='Trim crew', category=self.category)
        self.event = Event.objects.create(
            date=date.today(),
            end_dt=date.today(),
            crew=self.crew,
            work_account=self.work_account,
            created_by=self.user,
        )
        self.product = Product.objects.create(name='20A GFCI White', sku='GFCI-20A')

    def test_submit_creates_numbered_request_without_stock(self):
        document = create_material_request(
            work_account=self.work_account,
            work_order=self.event,
            lines=[{'product': self.product, 'quantity': Decimal('2')}],
            notes='Need material to finish master bedroom.',
            user=self.user,
        )
        self.assertEqual(document.document_number, 'MR-000001')
        self.assertEqual(document.tracking.current_status.code, 'requested')
        self.assertEqual(document.lines.get().quantity, Decimal('2'))
        self.assertEqual(document.lines.get().unit_price, Decimal('0'))
        history = document.tracking_history.get()
        self.assertIsNone(history.from_status)
        self.assertEqual(history.to_status.code, 'requested')
        self.assertEqual(document.created_by, self.user)

    def test_sequence_rejects_skip_and_accepts_next_step(self):
        document = create_material_request(
            work_account=self.work_account,
            work_order=self.event,
            lines=[{'product': self.product, 'quantity': Decimal('1')}],
            notes='',
            user=self.user,
        )
        with self.assertRaises(ValidationError):
            transition_material_request(
                document=document,
                status_code='preparing',
                notes='',
                user=self.user,
            )
        transition_material_request(
            document=document,
            status_code='approved',
            notes='Warehouse ok',
            user=self.user,
        )
        document.refresh_from_db()
        self.assertEqual(document.tracking.current_status.code, 'approved')
        self.assertEqual(DocumentTrackingHistory.objects.filter(document=document).count(), 2)

        transition_material_request(
            document=document,
            status_code='requested',
            notes='Need to review again',
            user=self.user,
        )
        document.refresh_from_db()
        self.assertEqual(document.tracking.current_status.code, 'requested')

        for code in ('approved', 'preparing', 'delivered', 'closed'):
            transition_material_request(
                document=document,
                status_code=code,
                notes='',
                user=self.user,
            )
        document.refresh_from_db()
        self.assertEqual(document.tracking.current_status.code, 'closed')
        transition_material_request(
            document=document,
            status_code='delivered',
            notes='',
            user=self.user,
        )
        document.refresh_from_db()
        self.assertEqual(document.tracking.current_status.code, 'delivered')
        with self.assertRaises(ValidationError):
            transition_material_request(
                document=document,
                status_code='requested',
                notes='',
                user=self.user,
            )

    def test_api_submit_and_list(self):
        factory = APIRequestFactory()
        payload = {
            'work_account': self.work_account.id,
            'work_order': self.event.id,
            'notes': 'Bedroom',
            'lines': [{'product': self.product.id, 'quantity': '4'}],
        }
        request = factory.post('/', payload, format='json')
        force_authenticate(request, self.user)
        response = MaterialRequestViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['status'], 'requested')
        self.assertEqual(response.data['phase'], 'Trim')
        self.assertEqual(response.data['requested_by'], 'jordan')

        list_request = factory.get('/', {'work_order': self.event.id})
        force_authenticate(list_request, self.user)
        listed = MaterialRequestViewSet.as_view({'get': 'list'})(list_request)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data['totalRows'], 1)
        self.assertEqual(len(listed.data['items']), 1)
        self.assertEqual(listed.data['items'][0]['document_number'], 'MR-000001')
        self.assertEqual(listed.data['stats']['open'], 1)

    def test_document_link_is_available_without_automation(self):
        self.assertTrue(hasattr(DocumentLink, 'RELATION_PURCHASE_ORDER'))
        self.assertEqual(Document.objects.filter(document_type=self.document_type).count(), 0)

    def test_mr_type_cannot_be_edited_or_deleted(self):
        document_type = DocumentType.objects.get(pk=self.document_type.pk)
        document_type.description = 'Renamed'
        with self.assertRaises(DjangoValidationError):
            document_type.save()
        with self.assertRaises(ProtectedError):
            document_type.delete()
        with self.assertRaises(DjangoValidationError):
            DocumentType.objects.filter(type_code='MR').update(is_active=False)
        document_type.refresh_from_db()
        self.assertEqual(document_type.description, self.document_type.description)
        self.assertTrue(document_type.is_active)
        self.assertTrue(DocumentType.objects.filter(type_code='MR').exists())

        other = DocumentType.objects.create(
            type_code='TMP',
            description='Temporary',
            stock_movement=0,
        )
        DocumentStatus.objects.create(
            document_type=other,
            code='open',
            name='Open',
            sequence=1,
            is_initial=True,
        )
        with self.assertRaises(ProtectedError):
            other.delete()
        self.assertTrue(DocumentType.objects.filter(type_code='TMP').exists())

    def test_lines_can_change_quantity_and_request_can_be_deleted(self):
        other = Product.objects.create(name='Reducing Washer', sku='WASH-114')
        document = create_material_request(
            work_account=self.work_account,
            work_order=self.event,
            lines=[
                {'product': self.product, 'quantity': Decimal('2')},
                {'product': other, 'quantity': Decimal('3')},
            ],
            notes='',
            user=self.user,
        )
        first, second = list(document.lines.order_by('id'))
        update_material_request_lines(
            document=document,
            lines=[{'id': first.id, 'quantity': Decimal('5')}],
        )
        first.refresh_from_db()
        self.assertEqual(first.quantity, Decimal('5'))
        with self.assertRaises(ValidationError):
            update_material_request_lines(
                document=document,
                lines=[
                    {'id': first.id, 'quantity': Decimal('0')},
                    {'id': second.id, 'quantity': Decimal('0')},
                ],
            )
        update_material_request_lines(
            document=document,
            lines=[{'id': second.id, 'quantity': Decimal('0')}],
        )
        self.assertEqual(document.lines.count(), 1)
        document_id = document.id
        document.delete()
        self.assertFalse(Document.objects.filter(pk=document_id).exists())

    def test_closed_request_cannot_be_deleted(self):
        document = create_material_request(
            work_account=self.work_account,
            work_order=self.event,
            lines=[{'product': self.product, 'quantity': Decimal('1')}],
            notes='',
            user=self.user,
        )
        for code in ('approved', 'preparing', 'delivered', 'closed'):
            transition_material_request(
                document=document,
                status_code=code,
                notes='',
                user=self.user,
            )
        with self.assertRaises(ValidationError):
            delete_material_request(document=document)
        self.assertTrue(Document.objects.filter(pk=document.pk).exists())
        transition_material_request(
            document=document,
            status_code='delivered',
            notes='',
            user=self.user,
        )
        delete_material_request(document=document)
        self.assertFalse(Document.objects.filter(pk=document.pk).exists())
