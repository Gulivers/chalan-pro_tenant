"""
Admin global para gestionar tenants desde el schema 'public'
"""
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from django.utils.html import format_html
from .models import Tenant, Domain


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    """
    Admin para gestionar tenants.
    Este admin solo es accesible desde el schema 'public'
    """
    list_display = ('name', 'logo_thumbnail', 'schema_name', 'tenant_id', 'get_domain', 'email', 'client_type', 'paid_until', 'on_trial', 'is_active', 'created_on')
    list_filter = ('is_active', 'on_trial', 'client_type', 'created_on')
    search_fields = ('name', 'schema_name', 'tenant_id', 'email')
    readonly_fields = ('schema_name', 'tenant_id', 'created_on', 'logo_preview')
    
    fieldsets = (
        ('Información del Tenant', {
            'fields': ('name', 'schema_name', 'tenant_id', 'email', 'client_type', 'logo', 'logo_preview', 'is_active')
        }),
        ('Configuración de Pago', {
            'fields': ('paid_until', 'on_trial')
        }),
        ('Metadata', {
            'fields': ('created_on',),
            'classes': ('collapse',)
        }),
    )
    
    def get_domain(self, obj):
        """Obtener el dominio principal del tenant"""
        domain = obj.domains.filter(is_primary=True).first()
        return domain.domain if domain else '-'
    get_domain.short_description = 'Dominio'
    
    def logo_thumbnail(self, obj):
        """Muestra el logo del tenant como thumbnail en el listado"""
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"/>',
                obj.logo.url
            )
        return format_html('<span style="color: #999;">Sin logo</span>')
    logo_thumbnail.short_description = 'Logo'
    
    def logo_preview(self, obj):
        """Muestra una vista previa más grande del logo en el formulario de edición"""
        if obj.logo:
            return format_html(
                '<img src="{}" width="200" style="object-fit: contain; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-top: 10px;"/>',
                obj.logo.url
            )
        return format_html('<span style="color: #999;">No hay logo cargado</span>')
    logo_preview.short_description = 'Vista Previa del Logo'


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """
    Admin para gestionar dominios de los tenants
    """
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')
