from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0004_tenant_landing_selected_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='trial_start',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Inicio del trial'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='trial_end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fin del trial'),
        ),
    ]
