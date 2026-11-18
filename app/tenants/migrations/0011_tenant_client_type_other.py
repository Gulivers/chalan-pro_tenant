from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0010_tenant_schedule_show_crew_resources'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='client_type_other',
            field=models.CharField(
                blank=True,
                help_text=(
                    'Required when Client type is General: the trade the company '
                    'typed in onboarding.'
                ),
                max_length=50,
                null=True,
                verbose_name='Other business type',
            ),
        ),
    ]
