from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django_tenants.test.cases import TenantTestCase
from rest_framework.test import APIClient

from appauth.testing import authenticate_api_client
from appinventory.models import Product, UnitCategory, UnitOfMeasure, Warehouse
from apptransactions.models import DocumentType, TransactionFavorite

User = get_user_model()


def grant_favorite_perms(user):
    perms = Permission.objects.filter(
        content_type__app_label='apptransactions',
        codename__in=(
            'view_transactionfavorite',
            'add_transactionfavorite',
            'change_transactionfavorite',
            'delete_transactionfavorite',
        ),
    )
    user.user_permissions.add(*perms)
    return User.objects.get(pk=user.pk)


def two_line_favorite_lines():
    """Mínimo válido para serializers/API de favoritos (no requiere Product en BD)."""
    return [
        {'product': 101, 'quantity': 1},
        {'product': 102, 'quantity': 1},
    ]


def tenant_api_client(tenant) -> APIClient:
    client = APIClient()
    domain = tenant.get_primary_domain().domain
    client.defaults['HTTP_HOST'] = domain
    return client


class _FavoriteTenantBase(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Favorites Tenant'
        tenant.email = 'favorites@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_transaction_favorites'


class TransactionFavoriteModelTests(_FavoriteTenantBase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.doc_type = DocumentType.objects.create(
            type_code='FAV',
            description='Test Document Type',
            is_active=True,
            prices_required=False,
            warehouse_required=False,
        )
        unit_cat = UnitCategory.objects.create(name='Count')
        self.unit = UnitOfMeasure.objects.create(
            code='EA',
            name='Each',
            category=unit_cat,
            reference_unit=True,
            is_active=True,
        )
        self.product = Product.objects.create(
            name='Test Product',
            sku='FAV-1',
            is_active=True,
            unit_default=self.unit,
        )
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            is_active=True,
        )

    def test_create_favorite(self):
        document_data = {
            'document_type': self.doc_type.id,
            'date': '2025-01-15',
            'notes': 'Test transaction',
        }
        lines_data = [
            {
                'product': self.product.id,
                'quantity': 5,
                'unit': self.unit.id,
                'unit_price': 10.00,
                'warehouse': self.warehouse.id,
            }
        ]
        favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            description='Test description',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user,
        )
        self.assertEqual(favorite.name, 'Test Favorite')
        self.assertEqual(favorite.created_by, self.user)
        self.assertTrue(favorite.is_active)
        self.assertIsNotNone(favorite.created_at)
        self.assertIsNotNone(favorite.updated_at)

    def test_favorite_name_uniqueness_per_user(self):
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        TransactionFavorite.objects.create(
            name='Unique Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user,
        )
        with self.assertRaises(ValidationError):
            favorite = TransactionFavorite(
                name='Unique Name',
                document_data=document_data,
                lines_data=lines_data,
                created_by=self.user,
            )
            favorite.full_clean()

    def test_favorite_name_case_insensitive_uniqueness(self):
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        TransactionFavorite.objects.create(
            name='Test Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user,
        )
        with self.assertRaises(ValidationError):
            favorite = TransactionFavorite(
                name='test name',
                document_data=document_data,
                lines_data=lines_data,
                created_by=self.user,
            )
            favorite.full_clean()

    def test_different_users_can_have_same_favorite_name(self):
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
        )
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        favorite1 = TransactionFavorite.objects.create(
            name='Same Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user,
        )
        favorite2 = TransactionFavorite.objects.create(
            name='Same Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=user2,
        )
        self.assertEqual(favorite1.name, favorite2.name)
        self.assertNotEqual(favorite1.created_by, favorite2.created_by)

    def test_get_display_name(self):
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user,
        )
        display_name = favorite.get_display_name()
        self.assertIn('Test Favorite', display_name)
        self.assertRegex(display_name, r'\d{4}-\d{2}-\d{2}')

    def test_soft_delete(self):
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user,
        )
        favorite.is_active = False
        favorite.save()
        active_favorites = TransactionFavorite.objects.filter(is_active=True)
        self.assertNotIn(favorite, active_favorites)
        all_favorites = TransactionFavorite.objects.all()
        self.assertIn(favorite, all_favorites)


class TransactionFavoriteSerializerTests(_FavoriteTenantBase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.doc_type = DocumentType.objects.create(
            type_code='FAVS',
            description='Test Document Type',
            is_active=True,
            prices_required=False,
            warehouse_required=False,
        )

    def test_serializer_validation(self):
        from apptransactions.serializers import TransactionFavoriteSerializer

        valid_data = {
            'name': 'Test Favorite',
            'description': 'Test description',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': two_line_favorite_lines(),
        }
        serializer = TransactionFavoriteSerializer(
            data=valid_data,
            context={'request': type('MockRequest', (), {'user': self.user})()},
        )
        self.assertTrue(serializer.is_valid())

    def test_serializer_name_validation(self):
        from apptransactions.serializers import TransactionFavoriteSerializer

        TransactionFavorite.objects.create(
            name='Existing Name',
            document_data={'document_type': self.doc_type.id},
            lines_data=[],
            created_by=self.user,
        )
        duplicate_data = {
            'name': 'Existing Name',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': two_line_favorite_lines(),
        }
        serializer = TransactionFavoriteSerializer(
            data=duplicate_data,
            context={'request': type('MockRequest', (), {'user': self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_serializer_document_data_validation(self):
        from apptransactions.serializers import TransactionFavoriteSerializer

        invalid_data = {
            'name': 'Test Favorite',
            'document_data': 'not a dict',
            'lines_data': two_line_favorite_lines(),
        }
        serializer = TransactionFavoriteSerializer(
            data=invalid_data,
            context={'request': type('MockRequest', (), {'user': self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('document_data', serializer.errors)

    def test_serializer_lines_data_validation(self):
        from apptransactions.serializers import TransactionFavoriteSerializer

        invalid_data = {
            'name': 'Test Favorite',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': 'not a list',
        }
        serializer = TransactionFavoriteSerializer(
            data=invalid_data,
            context={'request': type('MockRequest', (), {'user': self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('lines_data', serializer.errors)

    def test_serializer_rejects_less_than_two_lines_with_product(self):
        from apptransactions.serializers import TransactionFavoriteSerializer

        invalid_data = {
            'name': 'One line only',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': [{'product': 1, 'quantity': 1}],
        }
        serializer = TransactionFavoriteSerializer(
            data=invalid_data,
            context={'request': type('MockRequest', (), {'user': self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('lines_data', serializer.errors)


class TransactionFavoriteViewSetTests(_FavoriteTenantBase):
    def setUp(self):
        super().setUp()
        self.client = tenant_api_client(self.tenant)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
        )
        self.doc_type = DocumentType.objects.create(
            type_code='FAVV',
            description='Test Document Type',
            is_active=True,
            prices_required=False,
            warehouse_required=False,
        )
        self.favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            description='Test description',
            document_data={'document_type': self.doc_type.id},
            lines_data=[],
            created_by=self.user,
        )
        self.user = grant_favorite_perms(self.user)
        self.other_user = grant_favorite_perms(self.other_user)

    def test_user_can_only_see_own_favorites(self):
        authenticate_api_client(self.client, self.user)
        response = self.client.get('/api/transaction-favorites/')
        self.assertEqual(response.status_code, 200)
        rows = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['id'], self.favorite.id)

    def test_user_cannot_access_other_user_favorites(self):
        authenticate_api_client(self.client, self.other_user)
        response = self.client.get(f'/api/transaction-favorites/{self.favorite.id}/')
        self.assertEqual(response.status_code, 404)

    def test_create_favorite_from_transaction(self):
        authenticate_api_client(self.client, self.user)
        data = {
            'name': 'New Favorite',
            'description': 'New description',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': two_line_favorite_lines(),
        }
        response = self.client.post(
            '/api/transaction-favorites/create-from-transaction/',
            data,
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['favorite']['name'], 'New Favorite')
        favorite = TransactionFavorite.objects.get(name='New Favorite')
        self.assertEqual(favorite.created_by, self.user)

    def test_import_favorite(self):
        authenticate_api_client(self.client, self.user)
        response = self.client.get(f'/api/transaction-favorites/{self.favorite.id}/import/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.favorite.id)
        self.assertIn('document_data', response.data)
        self.assertIn('lines_data', response.data)

    def test_update_favorite_from_transaction(self):
        authenticate_api_client(self.client, self.user)
        new_data = {
            'document_data': {'document_type': self.doc_type.id, 'notes': 'Updated notes'},
            'lines_data': two_line_favorite_lines(),
        }
        response = self.client.post(
            f'/api/transaction-favorites/{self.favorite.id}/update-from-transaction/',
            new_data,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.favorite.refresh_from_db()
        self.assertEqual(self.favorite.document_data['notes'], 'Updated notes')

    def test_soft_delete_favorite(self):
        authenticate_api_client(self.client, self.user)
        response = self.client.delete(f'/api/transaction-favorites/{self.favorite.id}/')
        self.assertEqual(response.status_code, 204)
        self.favorite.refresh_from_db()
        self.assertFalse(self.favorite.is_active)
        response = self.client.get('/api/transaction-favorites/')
        rows = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(rows), 0)
