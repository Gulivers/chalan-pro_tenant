from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appauth', '0001_drop_authtoken_tables'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'preferred_language',
                    models.CharField(
                        choices=[('en', 'English'), ('es', 'Español')],
                        db_index=True,
                        default='en',
                        max_length=8,
                    ),
                ),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='preference',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'User preference',
                'verbose_name_plural': 'User preferences',
            },
        ),
    ]
