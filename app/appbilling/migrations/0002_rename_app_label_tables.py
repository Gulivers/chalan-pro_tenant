"""Align Django model state with billing_* tables after app rename.

On production, tables were already renamed manually to billing_*; this migration
originally only updated Django state (database_operations=[]).

Fresh databases (e.g. manage.py test) still have appbilling_* from 0001_initial.
Rename them here with IF EXISTS so both environments stay aligned before 0003.
"""

from django.db import migrations


# Idempotent: rename only if old name exists and new name does not.
_RENAME_SQL = """
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = 'appbilling_plan'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = 'billing_plan'
    ) THEN
        ALTER TABLE appbilling_plan RENAME TO billing_plan;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = 'appbilling_subscription'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = 'billing_subscription'
    ) THEN
        ALTER TABLE appbilling_subscription RENAME TO billing_subscription;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = 'appbilling_paymentevent'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = 'billing_paymentevent'
    ) THEN
        ALTER TABLE appbilling_paymentevent RENAME TO billing_paymentevent;
    END IF;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('appbilling', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=_RENAME_SQL,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
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
