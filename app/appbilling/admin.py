from django.contrib import admin

from project.admin_mixins import PublicSchemaOnlyAdminMixin
from appbilling.models import PaymentEvent, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(PublicSchemaOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'monthly_price',
        'yearly_price',
        'is_active',
        'is_recommended',
        'max_crews',
        'max_users',
        'display_order',
        'stripe_price_id_monthly',
        'stripe_price_id_yearly',
    )
    list_filter = ('is_active', 'is_recommended')
    list_editable = ('display_order', 'is_active', 'is_recommended')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'display_order',
                'is_active',
                'is_recommended',
            ),
        }),
        ('Precios (display)', {
            'fields': ('monthly_price', 'yearly_price'),
        }),
        ('Stripe', {
            'fields': (
                'stripe_product_id',
                'stripe_price_id_monthly',
                'stripe_price_id_yearly',
            ),
            'description': 'Los price IDs los usa el backend en Checkout; no confiar en el frontend.',
        }),
        ('Límites', {
            'fields': ('max_crews', 'max_users', 'module_rules'),
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(PublicSchemaOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        'tenant',
        'plan',
        'status',
        'stripe_customer_id',
        'stripe_subscription_id',
        'current_period_end',
        'last_payment_status',
    )
    list_filter = ('status', 'plan')
    search_fields = ('tenant__name', 'tenant__schema_name', 'stripe_customer_id')
    readonly_fields = (
        'stripe_customer_id',
        'stripe_subscription_id',
        'stripe_checkout_session_id',
        'created_at',
        'updated_at',
    )


@admin.register(PaymentEvent)
class PaymentEventAdmin(PublicSchemaOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('stripe_event_id', 'event_type', 'processed', 'created_at')
    list_filter = ('processed', 'event_type')
    readonly_fields = ('stripe_event_id', 'event_type', 'payload', 'created_at', 'processing_error')
