# Generated manually for multi-tenant schemas (migrate_schemas applies to all tenant DBs)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appinventory', '0010_pricing_rule_margin_snapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='model_number',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Manufacturer/catalog model reference (e.g. 14A19060W6CCT02-02).',
                max_length=128,
                verbose_name='Model #',
            ),
        ),
    ]
