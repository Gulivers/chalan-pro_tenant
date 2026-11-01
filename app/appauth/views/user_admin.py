from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from appauth.authentication import TenantJWTAuthentication
from appauth.permissions import IsTenantStaff
from appauth.serializers.user_admin import (
    GroupListSerializer,
    GroupSerializer,
    PermissionCatalogSerializer,
    UserAdminListSerializer,
    UserAdminSerializer,
    groups_queryset,
    permissions_queryset,
    users_queryset,
)

User = get_user_model()


class PermissionCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/auth/admin/permissions/ — catalog for PickList source lists."""

    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsTenantStaff]
    serializer_class = PermissionCatalogSerializer
    pagination_class = None

    def get_queryset(self):
        qs = permissions_queryset()
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(codename__icontains=search)
                | Q(content_type__app_label__icontains=search)
                | Q(content_type__model__icontains=search)
            )
        return qs


class GroupAdminViewSet(viewsets.ModelViewSet):
    """CRUD for auth.Group (roles) within the current tenant schema."""

    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsTenantStaff]
    pagination_class = None

    def get_queryset(self):
        qs = groups_queryset()
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupListSerializer
        return GroupSerializer


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD for tenant users.

    - Superuser status is never writable (Django Admin only).
    - Non-superuser staff cannot edit or delete superusers.
    - Users cannot delete themselves.
    """

    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsTenantStaff]
    pagination_class = None

    def get_queryset(self):
        qs = users_queryset()
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return UserAdminListSerializer
        return UserAdminSerializer

    def _guard_superuser_target(self, target):
        actor = self.request.user
        if target.is_superuser and not actor.is_superuser:
            raise PermissionDenied(
                'Only a superuser can change another superuser account.'
            )

    def update(self, request, *args, **kwargs):
        target = self.get_object()
        self._guard_superuser_target(target)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        target = self.get_object()
        self._guard_superuser_target(target)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        target = self.get_object()
        if target.pk == request.user.pk:
            raise ValidationError({'detail': 'You cannot delete your own account.'})
        self._guard_superuser_target(target)
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
