from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0007_drop_authtoken_tables'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='setup_completed',
            field=models.BooleanField(
                default=False,
                help_text='True when the tenant owner finished the post-login company setup assistant.',
                verbose_name='Admin setup completed',
            ),
        ),
        migrations.AddField(
            model_name='tenant',
            name='setup_progress',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Step statuses, panel/banner dismiss flags for the Welcome assistant.',
                verbose_name='Admin setup progress',
            ),
        ),
    ]
