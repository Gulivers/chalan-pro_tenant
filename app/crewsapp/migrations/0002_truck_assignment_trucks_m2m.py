# Generated manually for truck -> trucks (M2M) migration

from django.db import migrations, models


def migrate_truck_to_trucks(apps, schema_editor):
    """Copy truck FK to trucks M2M for existing assignments."""
    TruckAssignment = apps.get_model("crewsapp", "TruckAssignment")
    for assignment in TruckAssignment.objects.all():
        if hasattr(assignment, "truck_id") and assignment.truck_id:
            assignment.trucks.add(assignment.truck_id)


def reverse_migrate(apps, schema_editor):
    """Reverse: copy first truck from trucks back to truck (not reversible for multi-truck)."""
    pass  # No reverse - old truck FK is removed


class Migration(migrations.Migration):

    dependencies = [
        ("crewsapp", "0001_initial"),
    ]

    operations = [
        # 1. Add trucks M2M (blank=True)
        migrations.AddField(
            model_name="truckassignment",
            name="trucks",
            field=models.ManyToManyField(
                blank=True,
                related_name="assignments",
                to="crewsapp.truck",
                verbose_name="Assigned Trucks",
            ),
        ),
        # 2. Migrate data
        migrations.RunPython(migrate_truck_to_trucks, reverse_migrate),
        # 3. Remove truck FK
        migrations.RemoveField(
            model_name="truckassignment",
            name="truck",
        ),
    ]
