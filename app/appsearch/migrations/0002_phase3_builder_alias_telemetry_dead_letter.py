# Generated manually for appsearch Phase 3

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ctrctsapp', '0001_initial'),
        ('appsearch', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexoutbox',
            name='dead_letter_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set when max retry attempts are exhausted (requires manual requeue).',
                null=True,
            ),
        ),
        migrations.RemoveIndex(
            model_name='indexoutbox',
            name='search_outbox_pending',
        ),
        migrations.AddIndex(
            model_name='indexoutbox',
            index=models.Index(
                condition=models.Q(('dead_letter_at__isnull', True), ('processed_at__isnull', True)),
                fields=['processed_at', 'created_at'],
                name='search_outbox_pending',
            ),
        ),
        migrations.AddIndex(
            model_name='indexoutbox',
            index=models.Index(fields=['dead_letter_at'], name='search_outbox_dead_letter'),
        ),
        migrations.CreateModel(
            name='BuilderAlias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('builder', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='search_aliases',
                    to='ctrctsapp.builder',
                )),
            ],
            options={
                'verbose_name': 'Builder search alias',
                'verbose_name_plural': 'Builder search aliases',
                'ordering': ['alias'],
                'indexes': [
                    models.Index(fields=['alias'], name='search_builder_alias'),
                ],
            },
        ),
        migrations.CreateModel(
            name='SearchTelemetry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.CharField(
                    choices=[('search', 'Transaction search'), ('similar', 'Similar transactions')],
                    max_length=16,
                )),
                ('latency_ms', models.PositiveIntegerField()),
                ('result_count', models.PositiveIntegerField(default=0)),
                ('query_length', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Search telemetry entry',
                'verbose_name_plural': 'Search telemetry entries',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['operation', 'created_at'], name='search_telemetry_op_created'),
                ],
            },
        ),
    ]
