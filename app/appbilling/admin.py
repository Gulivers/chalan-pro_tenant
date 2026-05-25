from django.contrib import admin

from appbilling.models import PaymentEvent, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'monthly_price',
        'yearly_price',
        'is_active',
        'is_recommended',
        'max_crews',
        'display_order',
    )
    list_filter = ('is_active', 'is_recommended')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'tenant',
        'plan',
        'status',
        'stripe_customer_id',
        'stripe_subscription_id',
        'current_period_end',
    )
    list_filter = ('status', 'plan')
    search_fields = ('tenant__name', 'tenant__schema_name', 'stripe_customer_id')


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = ('stripe_event_id', 'event_type', 'processed', 'created_at')
    list_filter = ('processed', 'event_type')
    readonly_fields = ('stripe_event_id', 'event_type', 'payload', 'created_at')
