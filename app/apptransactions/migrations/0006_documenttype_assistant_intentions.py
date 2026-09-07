# Generated manually for DocumentType Assistant Level-1 intentions

from django.db import migrations, models


# Known type_code aliases (uppercase, hyphen/space stripped variants handled below).
SPEND_CODES = frozenset({'PINV', 'PO-INV', 'POINV', 'PO_INV'})
JOB_MATERIAL_CODES = frozenset({'PK', 'PICK', 'PICKING'})
PURCHASE_RETURN_CODES = frozenset({'PRN', 'PRET', 'PURRET'})


def _norm_code(code: str) -> str:
    return (code or '').strip().upper().replace(' ', '')


def backfill_assistant_intentions(apps, schema_editor):
    DocumentType = apps.get_model('apptransactions', 'DocumentType')
    for dt in DocumentType.objects.all().iterator():
        code = _norm_code(dt.type_code)
        changed = False

        if code in SPEND_CODES or code.replace('-', '').replace('_', '') in {'PINV', 'POINV'}:
            if not dt.counts_as_net_invoiced_spend:
                dt.counts_as_net_invoiced_spend = True
                changed = True
            if dt.counts_as_purchase_return:
                dt.counts_as_purchase_return = False
                changed = True

        if code in JOB_MATERIAL_CODES:
            if not dt.counts_as_job_material_issue:
                dt.counts_as_job_material_issue = True
                changed = True

        if code in PURCHASE_RETURN_CODES:
            if not dt.counts_as_purchase_return:
                dt.counts_as_purchase_return = True
                changed = True
            if dt.counts_as_net_invoiced_spend:
                dt.counts_as_net_invoiced_spend = False
                changed = True

        if changed:
            dt.save(update_fields=[
                'counts_as_net_invoiced_spend',
                'counts_as_job_material_issue',
                'counts_as_purchase_return',
            ])

    # If tenant had no spend-mapped type, do not invent from flags (INIINV collision).
    # Legacy PINV-only tenants are covered by SPEND_CODES above.


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('apptransactions', '0005_document_date_writable'),
    ]

    operations = [
        migrations.AddField(
            model_name='documenttype',
            name='counts_as_job_material_issue',
            field=models.BooleanField(
                default=False,
                help_text='Include this type as job/house material issue (e.g. picking to a Work Account).',
            ),
        ),
        migrations.AddField(
            model_name='documenttype',
            name='counts_as_net_invoiced_spend',
            field=models.BooleanField(
                default=False,
                help_text='Include this type in JobRhythm Assistant Net invoiced spending (not PO/GRN/returns).',
            ),
        ),
        migrations.AddField(
            model_name='documenttype',
            name='counts_as_purchase_return',
            field=models.BooleanField(
                default=False,
                help_text='Include this type as purchase returns (not mixed into net invoiced spending).',
            ),
        ),
        migrations.RunPython(backfill_assistant_intentions, noop_reverse),
    ]
