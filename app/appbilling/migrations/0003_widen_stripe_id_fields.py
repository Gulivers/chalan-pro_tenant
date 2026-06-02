from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appbilling', '0002_rename_app_label_tables'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='stripe_customer_id',
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='stripe_checkout_session_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='last_invoice_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='paymentevent',
            name='stripe_event_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
