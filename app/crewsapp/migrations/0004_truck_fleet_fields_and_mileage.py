import django.db.models.deletion
from django.db import migrations, models


def clear_trucks(apps, schema_editor):
    Truck = apps.get_model('crewsapp', 'Truck')
    TruckAssignment = apps.get_model('crewsapp', 'TruckAssignment')
    Warehouse = apps.get_model('appinventory', 'Warehouse')
    Warehouse.objects.filter(truck__isnull=False).update(truck=None)
    TruckAssignment.objects.all().delete()
    Truck.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crewsapp', '0003_work_order_status_progress'),
        ('appinventory', '0006_warehouse_truck'),
    ]

    operations = [
        migrations.RunPython(clear_trucks, migrations.RunPython.noop),
        migrations.CreateModel(
            name='TruckAssignmentTruck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starting_mileage', models.PositiveIntegerField(help_text='Odometer reading in miles when the assignment starts.', verbose_name='Starting Mileage')),
                ('ending_mileage', models.PositiveIntegerField(blank=True, help_text='Odometer reading in miles when the truck is returned.', null=True, verbose_name='Ending Mileage')),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='truck_links', to='crewsapp.truckassignment')),
                ('truck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_links', to='crewsapp.truck')),
            ],
            options={
                'verbose_name': 'Truck Assignment Reading',
                'verbose_name_plural': 'Truck Assignment Readings',
            },
        ),
        migrations.AddField(
            model_name='truck',
            name='fleet_status',
            field=models.CharField(choices=[('available', 'Available'), ('maintenance', 'Maintenance'), ('out_of_service', 'Out of Service'), ('sold', 'Sold')], default='available', max_length=32, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='truck',
            name='insurance_expiration',
            field=models.DateField(verbose_name='Insurance Expiration'),
        ),
        migrations.AddField(
            model_name='truck',
            name='make',
            field=models.CharField(max_length=100, verbose_name='Make'),
        ),
        migrations.AddField(
            model_name='truck',
            name='registration_expiration',
            field=models.DateField(verbose_name='Registration Expiration'),
        ),
        migrations.AddField(
            model_name='truck',
            name='unit_number',
            field=models.CharField(help_text='Internal identifier, e.g. TRK-001.', max_length=32, unique=True, verbose_name='Unit Number'),
        ),
        migrations.AddField(
            model_name='truck',
            name='vin',
            field=models.CharField(help_text='17-character vehicle identification number (stored uppercase).', max_length=17, unique=True, verbose_name='VIN'),
        ),
        migrations.RemoveField(
            model_name='truckassignment',
            name='trucks',
        ),
        migrations.AddField(
            model_name='truckassignment',
            name='trucks',
            field=models.ManyToManyField(blank=True, related_name='assignments', through='crewsapp.TruckAssignmentTruck', to='crewsapp.truck', verbose_name='Assigned Trucks'),
        ),
        migrations.AddConstraint(
            model_name='truckassignmenttruck',
            constraint=models.UniqueConstraint(fields=('assignment', 'truck'), name='uniq_truckassignment_truck'),
        ),
    ]
