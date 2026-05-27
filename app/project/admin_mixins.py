"""Mixins compartidos para el Django admin multi-tenant."""

from django.db import connection
from django_tenants.utils import get_public_schema_name


class PublicSchemaOnlyAdminMixin:
    """
    Modelos en SHARED_APPS (schema public): solo visibles en /admin/ del dominio API/public.
    Los dominios de tenant (clientes) no deben ver ni editar estos modelos.
    """

    def _is_public_schema_admin(self, request) -> bool:
        public = get_public_schema_name()
        schema = getattr(connection, 'schema_name', None)
        if schema == public:
            return True
        tenant = getattr(request, 'tenant', None)
        if tenant is not None and getattr(tenant, 'schema_name', None) == public:
            return True
        return False

    def has_module_permission(self, request):
        return self._is_public_schema_admin(request) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return self._is_public_schema_admin(request) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return self._is_public_schema_admin(request) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return self._is_public_schema_admin(request) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._is_public_schema_admin(request) and super().has_delete_permission(request, obj)
