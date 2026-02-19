# SerializedItem: document, document_line, notes; asset_tag nullable

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appinventory', '0004_serialized_items_and_movement_fields'),
        ('apptransactions', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serializeditem',
            name='asset_tag',
            field=models.CharField(
                blank=True,
                help_text='Unique tag/QR identifier',
                max_length=100,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name='serializeditem',
            name='document',
            field=models.ForeignKey(
                blank=True,
                help_text='Documento con el que fue adquirido (ej. factura de compra).',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='serialized_items',
                to='apptransactions.document',
            ),
        ),
        migrations.AddField(
            model_name='serializeditem',
            name='document_line',
            field=models.ForeignKey(
                blank=True,
                help_text='Línea del documento que originó este ítem (para compras serializadas).',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='serialized_items_created',
                to='apptransactions.documentline',
            ),
        ),
        migrations.AddField(
            model_name='serializeditem',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
