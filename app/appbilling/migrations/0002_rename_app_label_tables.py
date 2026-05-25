"""Align Django model state with existing billing_* tables after app rename."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appbilling', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterModelTable(
                    name='plan',
                    table='billing_plan',
                ),
                migrations.AlterModelTable(
                    name='subscription',
                    table='billing_subscription',
                ),
                migrations.AlterModelTable(
                    name='paymentevent',
                    table='billing_paymentevent',
                ),
            ],
        ),
    ]
