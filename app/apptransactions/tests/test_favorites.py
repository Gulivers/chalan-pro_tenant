from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apptransactions.models import TransactionFavorite, DocumentType, Document, DocumentLine
from appinventory.models import Product, UnitOfMeasure, Warehouse
from decimal import Decimal
import json

User = get_user_model()


class TransactionFavoriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doc_type = DocumentType.objects.create(
            type_code='TEST',
            description='Test Document Type',
            is_active=True
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            is_active=True
        )
        
        self.unit = UnitOfMeasure.objects.create(
            code='EA',
            name='Each',
            is_active=True
        )
        
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            is_active=True
        )

    def test_create_favorite(self):
        """Test creating a transaction favorite"""
        document_data = {
            'document_type': self.doc_type.id,
            'date': '2025-01-15',
            'notes': 'Test transaction'
        }
        
        lines_data = [
            {
                'product': self.product.id,
                'quantity': 5,
                'unit': self.unit.id,
                'unit_price': 10.00,
                'warehouse': self.warehouse.id
            }
        ]
        
        favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            description='Test description',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user
        )
        
        self.assertEqual(favorite.name, 'Test Favorite')
        self.assertEqual(favorite.created_by, self.user)
        self.assertTrue(favorite.is_active)
        self.assertIsNotNone(favorite.created_at)
        self.assertIsNotNone(favorite.updated_at)

    def test_favorite_name_uniqueness_per_user(self):
        """Test that favorite names are unique per user"""
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        
        # Create first favorite
        TransactionFavorite.objects.create(
            name='Unique Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user
        )
        
        # Try to create second favorite with same name for same user
        with self.assertRaises(ValidationError):
            favorite = TransactionFavorite(
                name='Unique Name',
                document_data=document_data,
                lines_data=lines_data,
                created_by=self.user
            )
            favorite.full_clean()

    def test_favorite_name_case_insensitive_uniqueness(self):
        """Test that favorite names are case-insensitive unique"""
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        
        # Create first favorite
        TransactionFavorite.objects.create(
            name='Test Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user
        )
        
        # Try to create second favorite with different case
        with self.assertRaises(ValidationError):
            favorite = TransactionFavorite(
                name='test name',
                document_data=document_data,
                lines_data=lines_data,
                created_by=self.user
            )
            favorite.full_clean()

    def test_different_users_can_have_same_favorite_name(self):
        """Test that different users can have favorites with same name"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        
        # Create favorite for first user
        favorite1 = TransactionFavorite.objects.create(
            name='Same Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user
        )
        
        # Create favorite for second user with same name
        favorite2 = TransactionFavorite.objects.create(
            name='Same Name',
            document_data=document_data,
            lines_data=lines_data,
            created_by=user2
        )
        
        self.assertEqual(favorite1.name, favorite2.name)
        self.assertNotEqual(favorite1.created_by, favorite2.created_by)

    def test_get_display_name(self):
        """Test the get_display_name method"""
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        
        favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user
        )
        
        display_name = favorite.get_display_name()
        self.assertIn('Test Favorite', display_name)
        self.assertIn('2025', display_name)  # Should contain current year

    def test_soft_delete(self):
        """Test that favorites are soft deleted (marked as inactive)"""
        document_data = {'document_type': self.doc_type.id}
        lines_data = []
        
        favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            document_data=document_data,
            lines_data=lines_data,
            created_by=self.user
        )
        
        # Soft delete
        favorite.is_active = False
        favorite.save()
        
        # Should not appear in active queryset
        active_favorites = TransactionFavorite.objects.filter(is_active=True)
        self.assertNotIn(favorite, active_favorites)
        
        # Should still exist in database
        all_favorites = TransactionFavorite.objects.all()
        self.assertIn(favorite, all_favorites)


class TransactionFavoriteSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doc_type = DocumentType.objects.create(
            type_code='TEST',
            description='Test Document Type',
            is_active=True
        )

    def test_serializer_validation(self):
        """Test serializer validation"""
        from apptransactions.serializers import TransactionFavoriteSerializer
        
        # Valid data
        valid_data = {
            'name': 'Test Favorite',
            'description': 'Test description',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': []
        }
        
        serializer = TransactionFavoriteSerializer(
            data=valid_data,
            context={'request': type('MockRequest', (), {'user': self.user})()}
        )
        
        self.assertTrue(serializer.is_valid())

    def test_serializer_name_validation(self):
        """Test serializer name validation"""
        from apptransactions.serializers import TransactionFavoriteSerializer
        
        # Create existing favorite
        TransactionFavorite.objects.create(
            name='Existing Name',
            document_data={'document_type': self.doc_type.id},
            lines_data=[],
            created_by=self.user
        )
        
        # Try to create duplicate
        duplicate_data = {
            'name': 'Existing Name',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': []
        }
        
        serializer = TransactionFavoriteSerializer(
            data=duplicate_data,
            context={'request': type('MockRequest', (), {'user': self.user})()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_serializer_document_data_validation(self):
        """Test serializer document_data validation"""
        from apptransactions.serializers import TransactionFavoriteSerializer
        
        # Invalid document_data (not a dict)
        invalid_data = {
            'name': 'Test Favorite',
            'document_data': 'not a dict',
            'lines_data': []
        }
        
        serializer = TransactionFavoriteSerializer(
            data=invalid_data,
            context={'request': type('MockRequest', (), {'user': self.user})()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('document_data', serializer.errors)

    def test_serializer_lines_data_validation(self):
        """Test serializer lines_data validation"""
        from apptransactions.serializers import TransactionFavoriteSerializer
        
        # Invalid lines_data (not a list)
        invalid_data = {
            'name': 'Test Favorite',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': 'not a list'
        }
        
        serializer = TransactionFavoriteSerializer(
            data=invalid_data,
            context={'request': type('MockRequest', (), {'user': self.user})()}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('lines_data', serializer.errors)


class TransactionFavoriteViewSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.doc_type = DocumentType.objects.create(
            type_code='TEST',
            description='Test Document Type',
            is_active=True
        )
        
        self.favorite = TransactionFavorite.objects.create(
            name='Test Favorite',
            description='Test description',
            document_data={'document_type': self.doc_type.id},
            lines_data=[],
            created_by=self.user
        )

    def test_user_can_only_see_own_favorites(self):
        """Test that users can only see their own favorites"""
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        
        # Create token for user
        token = Token.objects.create(user=self.user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # Get favorites
        response = client.get('/api/transaction-favorites/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.favorite.id)

    def test_user_cannot_access_other_user_favorites(self):
        """Test that users cannot access other users' favorites"""
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        
        # Create token for other user
        token = Token.objects.create(user=self.other_user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # Try to access favorite created by first user
        response = client.get(f'/api/transaction-favorites/{self.favorite.id}/')
        
        self.assertEqual(response.status_code, 404)

    def test_create_favorite_from_transaction(self):
        """Test creating favorite from transaction data"""
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        
        # Create token for user
        token = Token.objects.create(user=self.user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # Data for creating favorite
        data = {
            'name': 'New Favorite',
            'description': 'New description',
            'document_data': {'document_type': self.doc_type.id},
            'lines_data': []
        }
        
        response = client.post('/api/transaction-favorites/create-from-transaction/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['favorite']['name'], 'New Favorite')
        
        # Verify favorite was created
        favorite = TransactionFavorite.objects.get(name='New Favorite')
        self.assertEqual(favorite.created_by, self.user)

    def test_import_favorite(self):
        """Test importing favorite data"""
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        
        # Create token for user
        token = Token.objects.create(user=self.user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # Import favorite
        response = client.get(f'/api/transaction-favorites/{self.favorite.id}/import/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.favorite.id)
        self.assertIn('document_data', response.data)
        self.assertIn('lines_data', response.data)

    def test_update_favorite_from_transaction(self):
        """Test updating favorite with new transaction data"""
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        
        # Create token for user
        token = Token.objects.create(user=self.user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # New transaction data
        new_data = {
            'document_data': {'document_type': self.doc_type.id, 'notes': 'Updated notes'},
            'lines_data': []
        }
        
        response = client.post(f'/api/transaction-favorites/{self.favorite.id}/update-from-transaction/', new_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify favorite was updated
        self.favorite.refresh_from_db()
        self.assertEqual(self.favorite.document_data['notes'], 'Updated notes')

    def test_soft_delete_favorite(self):
        """Test soft deleting a favorite"""
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        
        # Create token for user
        token = Token.objects.create(user=self.user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        # Delete favorite
        response = client.delete(f'/api/transaction-favorites/{self.favorite.id}/')
        
        self.assertEqual(response.status_code, 204)
        
        # Verify favorite is soft deleted
        self.favorite.refresh_from_db()
        self.assertFalse(self.favorite.is_active)
        
        # Verify favorite doesn't appear in active list
        response = client.get('/api/transaction-favorites/')
        self.assertEqual(len(response.data['results']), 0)
