"""
Seed JobRhythm plans (public schema). Stripe price IDs from environment.

Usage:
  python manage.py seed_plans
"""
import os

from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context, get_public_schema_name

from appbilling.models import Plan


PLAN_DEFAULTS = [
    {
        'slug': 'starter',
        'name': 'Starter',
        'monthly_price': '436.00',
        'yearly_price': '4447.00',
        'is_recommended': False,
        'max_crews': 3,
        'max_users': 1,
        'display_order': 1,
        'env_prefix': 'STRIPE_STARTER',
    },
    {
        'slug': 'professional',
        'name': 'Professional',
        'monthly_price': '877.00',
        'yearly_price': '8945.00',
        'is_recommended': True,
        'max_crews': 10,
        'max_users': 10,
        'display_order': 2,
        'env_prefix': 'STRIPE_PROFESSIONAL',
    },
    {
        'slug': 'enterprise',
        'name': 'Enterprise',
        'monthly_price': '1758.00',
        'yearly_price': '17931.00',
        'is_recommended': False,
        'max_crews': None,
        'max_users': None,
        'display_order': 3,
        'env_prefix': 'STRIPE_ENTERPRISE',
    },
]


class Command(BaseCommand):
    help = 'Seed billing plans with Stripe IDs from environment variables.'

    def handle(self, *args, **options):
        public = get_public_schema_name()
        with schema_context(public):
            for spec in PLAN_DEFAULTS:
                prefix = spec['env_prefix']
                product_id = os.environ.get(f'{prefix}_PRODUCT_ID', '')
                monthly_id = os.environ.get(f'{prefix}_PRICE_MONTHLY', '')
                yearly_id = os.environ.get(f'{prefix}_PRICE_YEARLY', '')

                plan, created = Plan.objects.update_or_create(
                    slug=spec['slug'],
                    defaults={
                        'name': spec['name'],
                        'monthly_price': spec['monthly_price'],
                        'yearly_price': spec['yearly_price'],
                        'is_active': True,
                        'is_recommended': spec['is_recommended'],
                        'max_crews': spec['max_crews'],
                        'max_users': spec['max_users'],
                        'display_order': spec['display_order'],
                        'stripe_product_id': product_id,
                        'stripe_price_id_monthly': monthly_id,
                        'stripe_price_id_yearly': yearly_id,
                    },
                )
                action = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(f'{action} plan {plan.slug}'))

        self.stdout.write(
            self.style.WARNING(
                'Set STRIPE_*_PRODUCT_ID and STRIPE_*_PRICE_MONTHLY/YEARLY in env before checkout works.'
            )
        )
