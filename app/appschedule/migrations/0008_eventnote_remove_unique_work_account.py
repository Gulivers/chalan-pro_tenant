# Generated manually for event-scoped EventNote (like chat)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("appschedule", "0007_protect_event_relations"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="eventnote",
            name="unique_work_account_note",
        ),
    ]
