# Inventory Transfer Header + Movements (sin InventoryTransferLine, FK transfer reemplaza transfer_group_id)

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appinventory', '0006_warehouse_truck'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, help_text='Descripción de la transferencia', max_length=255)),
                ('status', models.CharField(
                    choices=[('completed', 'Completed'), ('reverted', 'Reverted')],
                    db_index=True,
                    default='completed',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
                ('from_warehouse', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='transfers_from',
                    to='appinventory.warehouse',
                )),
                ('to_warehouse', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='transfers_to',
                    to='appinventory.warehouse',
                )),
            ],
            options={
                'verbose_name': 'Inventory Transfer',
                'verbose_name_plural': 'Inventory Transfers',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='inventorymovement',
            name='transfer',
            field=models.ForeignKey(
                blank=True,
                help_text='Transferencia entre almacenes a la que pertenece este movimiento.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='movements',
                to='appinventory.inventorytransfer',
            ),
        ),
        migrations.RemoveField(
            model_name='inventorymovement',
            name='transfer_group_id',
        ),
    ]
