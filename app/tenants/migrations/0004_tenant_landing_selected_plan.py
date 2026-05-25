# Generated manually for JobRhythm onboarding (landing plan persistence)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0003_remove_admin_temp_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='landing_selected_plan',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Starter', 'Starter'),
                    ('Professional', 'Professional'),
                    ('Enterprise', 'Enterprise'),
                ],
                help_text='Plan chosen on the landing page (e.g. URL query) when provided',
                max_length=20,
                null=True,
                verbose_name='Plan selected from marketing',
            ),
        ),
    ]
