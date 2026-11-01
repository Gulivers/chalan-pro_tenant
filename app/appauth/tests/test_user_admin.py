from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.test import APIClient

from appauth.testing import authenticate_api_client

User = get_user_model()


def tenant_api_client(tenant) -> APIClient:
    client = APIClient()
    domain = tenant.get_primary_domain().domain
    client.defaults['HTTP_HOST'] = domain
    return client


class UserAdminApiTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'User Admin Tenant'
        tenant.email = 'owner@example.com'
        tenant.is_active = True

    @classmethod
    def get_test_schema_name(cls):
        return 'test_appauth_user_admin'

    def setUp(self):
        super().setUp()
        self.client = tenant_api_client(self.tenant)
        self.staff = User.objects.create_user(
            username='staffer',
            email='staffer@example.com',
            password='ValidPass123!',
            is_staff=True,
        )
        self.regular = User.objects.create_user(
            username='worker',
            email='worker@example.com',
            password='ValidPass123!',
            is_staff=False,
        )
        self.super = User.objects.create_superuser(
            username='boss',
            email='boss@example.com',
            password='ValidPass123!',
        )
        ct = ContentType.objects.get_for_model(User)
        self.perm = Permission.objects.filter(content_type=ct).first()

    def test_non_staff_forbidden(self):
        authenticate_api_client(self.client, self.regular)
        response = self.client.get('/api/auth/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_list_and_create_group_with_permissions(self):
        authenticate_api_client(self.client, self.staff)
        create = self.client.post(
            '/api/auth/admin/groups/',
            {'name': 'Warehouse', 'permissions': [self.perm.id]},
            format='json',
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data['name'], 'Warehouse')
        self.assertEqual(create.data['permissions'], [self.perm.id])
        listing = self.client.get('/api/auth/admin/groups/')
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertTrue(any(row['name'] == 'Warehouse' for row in listing.data))

    def test_staff_can_create_user_without_superuser(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'newhire',
                'password': 'ValidPass123!',
                'password_confirm': 'ValidPass123!',
                'first_name': 'New',
                'last_name': 'Hire',
                'email': 'newhire@example.com',
                'is_active': True,
                'is_staff': False,
                'is_superuser': True,
                'groups': [],
                'user_permissions': [self.perm.id],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = User.objects.get(username='newhire')
        self.assertFalse(created.is_superuser)
        self.assertEqual(
            list(created.user_permissions.values_list('id', flat=True)),
            [self.perm.id],
        )

    def test_create_user_requires_matching_password_confirm(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'mismatch',
                'password': 'ValidPass123!',
                'password_confirm': 'OtherPass123!',
                'email': 'mismatch@example.com',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_create_user_rejects_weak_password(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'weakuser',
                'password': '12345678',
                'password_confirm': '12345678',
                'email': 'weak@example.com',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_update_user_password_requires_confirm(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.patch(
            f'/api/auth/admin/users/{self.regular.pk}/',
            {
                'password': 'BrandNewPass99!',
                'password_confirm': 'BrandNewPass99!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular.refresh_from_db()
        self.assertTrue(self.regular.check_password('BrandNewPass99!'))

    def test_create_user_requires_email(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'noemail',
                'password': 'ValidPass123!',
                'password_confirm': 'ValidPass123!',
                'first_name': 'No',
                'last_name': 'Email',
                'email': '',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_user_requires_first_and_last_name(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'noname',
                'password': 'ValidPass123!',
                'password_confirm': 'ValidPass123!',
                'first_name': '',
                'last_name': '   ',
                'email': 'noname@example.com',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

    def test_create_user_rejects_duplicate_email(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'copycat',
                'password': 'ValidPass123!',
                'password_confirm': 'ValidPass123!',
                'first_name': 'Copy',
                'last_name': 'Cat',
                'email': 'WORKER@example.com',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('already exists', str(response.data['email']).lower())

    def test_update_user_can_keep_own_email(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.patch(
            f'/api/auth/admin/users/{self.regular.pk}/',
            {'email': 'worker@example.com', 'first_name': 'Work'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular.refresh_from_db()
        self.assertEqual(self.regular.email, 'worker@example.com')
        self.assertEqual(self.regular.first_name, 'Work')

    def test_closed_superuser_edit_by_non_superuser(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.patch(
            f'/api/auth/admin/users/{self.super.pk}/',
            {'first_name': 'Nope'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_self(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.delete(f'/api/auth/admin/users/{self.staff.pk}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_permission_catalog(self):
        authenticate_api_client(self.client, self.staff)
        response = self.client.get('/api/auth/admin/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertIn('label', response.data[0])
