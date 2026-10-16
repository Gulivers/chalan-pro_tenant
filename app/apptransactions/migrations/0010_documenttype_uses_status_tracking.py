# Generated manually for configurable status tracking on DocumentType.

from django.db import migrations, models


DEFAULT_STATUS_SEEDS = {
    'PO': (
        ('draft', 'Draft', 1, True, False),
        ('submitted', 'Submitted', 2, False, False),
        ('approved', 'Approved', 3, False, False),
        ('ordered', 'Ordered', 4, False, False),
        ('closed', 'Closed', 5, False, True),
    ),
    'PK': (
        ('requested', 'Requested', 1, True, False),
        ('approved', 'Approved', 2, False, False),
        ('preparing', 'Preparing', 3, False, False),
        ('picked', 'Picked', 4, False, False),
        ('closed', 'Closed', 5, False, True),
    ),
    'PR': (
        ('requested', 'Requested', 1, True, False),
        ('approved', 'Approved', 2, False, False),
        ('ordered', 'Ordered', 3, False, False),
        ('closed', 'Closed', 4, False, True),
    ),
}


def enable_mr_and_seed_default_statuses(apps, schema_editor):
    DocumentType = apps.get_model('apptransactions', 'DocumentType')
    DocumentStatus = apps.get_model('apptransactions', 'DocumentStatus')

    DocumentType.objects.filter(type_code='MR').update(uses_status_tracking=True)

    for type_code, rows in DEFAULT_STATUS_SEEDS.items():
        document_type = DocumentType.objects.filter(type_code=type_code).first()
        if document_type is None:
            continue
        # No sobrescribir personalizaciones del tenant.
        if DocumentStatus.objects.filter(document_type=document_type).exists():
            continue
        for code, name, sequence, is_initial, is_terminal in rows:
            DocumentStatus.objects.create(
                document_type=document_type,
                code=code,
                name=name,
                sequence=sequence,
                is_initial=is_initial,
                is_terminal=is_terminal,
                is_active=True,
            )


def noop_reverse(apps, schema_editor):
    # No borramos estados personalizados ni el flag de MR en reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('apptransactions', '0009_protect_document_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='documenttype',
            name='uses_status_tracking',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Enable configurable status tracking for documents of this type. '
                    'When off, documents behave as before (no tracking required).'
                ),
            ),
        ),
        migrations.AlterModelOptions(
            name='documentstatus',
            options={
                'ordering': ['document_type', 'sequence'],
                'verbose_name': 'Document Status',
                'verbose_name_plural': 'Document Statuses',
            },
        ),
        migrations.RunPython(enable_mr_and_seed_default_statuses, noop_reverse),
    ]
