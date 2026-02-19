# Generated manually for serialized items and movement fields

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appinventory', '0003_productbrandassignment_and_more'),
    ]

    operations = [
        # Product: tracking_mode, alert, notes
        migrations.AddField(
            model_name='product',
            name='tracking_mode',
            field=models.CharField(
                choices=[('QUANTITY', 'By quantity (stock)'), ('SERIALIZED', 'Serialized (equipment/tool)')],
                default='QUANTITY',
                help_text='QUANTITY = stock by quantity; SERIALIZED = track by SerializedItem units',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='alert',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        # New model SerializedItem
        migrations.CreateModel(
            name='SerializedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_tag', models.CharField(help_text='Unique tag/QR identifier', max_length=100, unique=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('maintenance', 'Maintenance'), ('lost', 'Lost'), ('retired', 'Retired')], default='active', max_length=20)),
                ('condition', models.CharField(choices=[('ok', 'OK'), ('damaged', 'Damaged'), ('needs_repair', 'Needs repair')], default='ok', max_length=20)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('current_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='serialized_items', to='appinventory.warehouse')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='serialized_items', to='appinventory.product')),
            ],
            options={
                'verbose_name': 'Serialized Item',
                'verbose_name_plural': 'Serialized Items',
                'ordering': ['product', 'asset_tag'],
            },
        ),
        # InventoryMovement: serialized_item, transfer_group_id
        migrations.AddField(
            model_name='inventorymovement',
            name='serialized_item',
            field=models.ForeignKey(
                blank=True,
                help_text='If set, this movement tracks one physical unit; quantity must be 1.',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movements',
                to='appinventory.serializeditem',
            ),
        ),
        migrations.AddField(
            model_name='inventorymovement',
            name='transfer_group_id',
            field=models.CharField(
                blank=True,
                help_text='UUID or string linking OUT+IN movements of the same transfer.',
                max_length=64,
                null=True,
            ),
        ),
    ]
