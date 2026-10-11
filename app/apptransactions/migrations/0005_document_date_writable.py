# Generated manually for writable Document.date

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('apptransactions', '0004_pricing_rule_margin_snapshot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date',
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
    ]
