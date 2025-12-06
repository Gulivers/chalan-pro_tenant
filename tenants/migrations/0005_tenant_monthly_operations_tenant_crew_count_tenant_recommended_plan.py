# Generated manually
from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0004_tenant_address_tenant_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='monthly_operations',
            field=models.CharField(
                blank=True,
                choices=[
                    ('0-10', '0–10 homes per month'),
                    ('11-25', '11–25 homes per month'),
                    ('26-50', '26–50 homes per month'),
                    ('51-100', '51–100 homes per month'),
                    ('100+', '100+ homes per month'),
                ],
                help_text='How many projects or homes the company handles each month',
                max_length=10,
                null=True,
                verbose_name='Monthly Operations Volume'
            ),
        ),
        migrations.AddField(
            model_name='tenant',
            name='crew_count',
            field=models.IntegerField(
                blank=True,
                help_text='How many active crews the company manages',
                null=True,
                validators=[MinValueValidator(1)],
                verbose_name='Number of Active Crews'
            ),
        ),
        migrations.AddField(
            model_name='tenant',
            name='recommended_plan',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Starter', 'Starter'),
                    ('Professional', 'Professional'),
                    ('Enterprise', 'Enterprise'),
                ],
                help_text='Recommended plan based on crew count',
                max_length=20,
                null=True,
                verbose_name='Recommended Plan'
            ),
        ),
    ]

