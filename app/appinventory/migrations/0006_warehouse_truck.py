# Warehouse: 1-to-1 link to Truck for mobile warehouses

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appinventory', '0005_serializeditem_document_notes'),
        ('crewsapp', '0002_truck_assignment_trucks_m2m'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='truck',
            field=models.OneToOneField(
                blank=True,
                help_text='Mobile warehouse for this truck (1-to-1).',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='mobile_warehouse',
                to='crewsapp.truck',
            ),
        ),
    ]
