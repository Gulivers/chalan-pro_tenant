"""
Billing models live in the public schema (SHARED_APPS) alongside tenants.Tenant.
"""
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """Local catalog mapped to Stripe Products/Prices."""

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=32, unique=True)
    stripe_product_id = models.CharField(max_length=64, blank=True)
    stripe_price_id_monthly = models.CharField(max_length=64, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=64, blank=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False)
    max_users = models.PositiveIntegerField(null=True, blank=True)
    max_crews = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Null = unlimited (Enterprise).',
    )
    module_rules = models.JSONField(default=dict, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'slug']
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        db_table = 'billing_plan'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Stripe subscription state per tenant (public schema)."""

    STATUS_CHOICES = [
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('past_due', 'Past due'),
        ('unpaid', 'Unpaid'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete expired'),
        ('paused', 'Paused'),
    ]

    tenant = models.OneToOneField(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='billing_subscription',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions',
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, default='incomplete', choices=STATUS_CHOICES)
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    last_payment_status = models.CharField(max_length=32, blank=True)
    last_invoice_id = models.CharField(max_length=255, blank=True)
    past_due_since = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When status became past_due (for grace period).',
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        db_table = 'billing_subscription'

    def __str__(self):
        return f'{self.tenant_id} ({self.status})'


class PaymentEvent(models.Model):
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=128)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment event'
        verbose_name_plural = 'Payment events'
        db_table = 'billing_paymentevent'

    def __str__(self):
        return f'{self.event_type} ({self.stripe_event_id})'
