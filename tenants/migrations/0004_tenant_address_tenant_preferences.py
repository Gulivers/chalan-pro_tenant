# Generated manually for Onboarding 2.0

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0003_tenant_admin_temp_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='address',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Dirección'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='preferences',
            field=models.JSONField(blank=True, default=list, help_text='Lista de módulos activados para este tenant', verbose_name='Módulos Activados'),
        ),
    ]

