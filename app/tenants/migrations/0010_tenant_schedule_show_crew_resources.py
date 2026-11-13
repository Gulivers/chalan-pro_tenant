from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0009_media_upload_to_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='schedule_show_crew_resources',
            field=models.BooleanField(
                default=True,
                help_text=(
                    'When True, the schedule uses a Crew resource column. '
                    'When False, crews are assigned in the event modal and named on event cards / PDF cells.'
                ),
                verbose_name='Show crews as schedule resources',
            ),
        ),
    ]
