# Generated manually for appbilling app (SHARED_APPS / public schema)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0005_tenant_trial_dates'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=32, unique=True)),
                ('stripe_product_id', models.CharField(blank=True, max_length=64)),
                ('stripe_price_id_monthly', models.CharField(blank=True, max_length=64)),
                ('stripe_price_id_yearly', models.CharField(blank=True, max_length=64)),
                ('monthly_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('yearly_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_recommended', models.BooleanField(default=False)),
                ('max_users', models.PositiveIntegerField(blank=True, null=True)),
                ('max_crews', models.PositiveIntegerField(blank=True, help_text='Null = unlimited (Enterprise).', null=True)),
                ('module_rules', models.JSONField(blank=True, default=dict)),
                ('display_order', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Plan',
                'verbose_name_plural': 'Plans',
                'ordering': ['display_order', 'slug'],
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(blank=True, db_index=True, max_length=64)),
                ('stripe_subscription_id', models.CharField(blank=True, db_index=True, max_length=64)),
                ('stripe_checkout_session_id', models.CharField(blank=True, max_length=64)),
                ('status', models.CharField(choices=[('trialing', 'Trialing'), ('active', 'Active'), ('past_due', 'Past due'), ('unpaid', 'Unpaid'), ('canceled', 'Canceled'), ('incomplete', 'Incomplete'), ('incomplete_expired', 'Incomplete expired'), ('paused', 'Paused')], default='incomplete', max_length=32)),
                ('trial_start', models.DateTimeField(blank=True, null=True)),
                ('trial_end', models.DateTimeField(blank=True, null=True)),
                ('current_period_start', models.DateTimeField(blank=True, null=True)),
                ('current_period_end', models.DateTimeField(blank=True, null=True)),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('canceled_at', models.DateTimeField(blank=True, null=True)),
                ('last_payment_status', models.CharField(blank=True, max_length=32)),
                ('last_invoice_id', models.CharField(blank=True, max_length=64)),
                ('past_due_since', models.DateTimeField(blank=True, help_text='When status became past_due (for grace period).', null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='appbilling.plan')),
                ('tenant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='billing_subscription', to='tenants.tenant')),
            ],
            options={
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
            },
        ),
        migrations.CreateModel(
            name='PaymentEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_event_id', models.CharField(max_length=64, unique=True)),
                ('event_type', models.CharField(max_length=128)),
                ('processed', models.BooleanField(default=False)),
                ('processing_error', models.TextField(blank=True)),
                ('payload', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Payment event',
                'verbose_name_plural': 'Payment events',
                'ordering': ['-created_at'],
            },
        ),
    ]
