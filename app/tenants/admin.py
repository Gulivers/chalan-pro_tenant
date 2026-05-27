"""
Global admin for tenants (public schema only).
"""
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from django.utils.html import format_html
from project.admin_mixins import PublicSchemaOnlyAdminMixin
from .models import Tenant, Domain


@admin.register(Tenant)
class TenantAdmin(PublicSchemaOnlyAdminMixin, TenantAdminMixin, admin.ModelAdmin):
    """Tenant management — accessible only from the public schema admin."""

    list_display = (
        'name', 'logo_thumbnail', 'schema_name', 'tenant_id', 'get_domain',
        'email', 'client_type', 'paid_until', 'on_trial', 'is_active', 'created_on',
    )
    list_filter = ('is_active', 'on_trial', 'client_type', 'created_on')
    search_fields = ('name', 'schema_name', 'tenant_id', 'email')
    readonly_fields = ('schema_name', 'tenant_id', 'created_on', 'logo_preview')

    fieldsets = (
        ('Tenant information', {
            'fields': (
                'name', 'schema_name', 'tenant_id', 'email', 'client_type',
                'logo', 'logo_preview', 'is_active',
            ),
        }),
        ('Billing & trial', {
            'fields': ('trial_start', 'trial_end', 'paid_until', 'on_trial'),
        }),
        ('Metadata', {
            'fields': ('created_on',),
            'classes': ('collapse',),
        }),
    )

    def get_domain(self, obj):
        domain = obj.domains.filter(is_primary=True).first()
        return domain.domain if domain else '-'
    get_domain.short_description = 'Domain'

    def logo_thumbnail(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: contain; border-radius: 4px; '
                'box-shadow: 0 2px 4px rgba(0,0,0,0.1);"/>',
                obj.logo.url,
            )
        return format_html('<span style="color: #999;">No logo</span>')
    logo_thumbnail.short_description = 'Logo'

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="200" '
                'style="object-fit: contain; border-radius: 8px; '
                'box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-top: 10px;"/>',
                obj.logo.url,
            )
        return format_html('<span style="color: #999;">No logo uploaded</span>')
    logo_preview.short_description = 'Logo preview'


@admin.register(Domain)
class DomainAdmin(PublicSchemaOnlyAdminMixin, admin.ModelAdmin):
    """Tenant domain / subdomain mapping."""

    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')
