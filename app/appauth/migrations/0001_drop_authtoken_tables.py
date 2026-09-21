"""Drop orphaned DRF authtoken tables from each tenant schema (Stage D cleanup).

Companion to tenants.0007_drop_authtoken_tables (public schema).
"""

from django.db import migrations


def drop_authtoken_artifacts(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS authtoken_token CASCADE')
        cursor.execute("DELETE FROM django_migrations WHERE app = %s", ['authtoken'])


def noop_reverse(apps, schema_editor):
    # Irreversible: Token auth is retired in favor of Simple JWT.
    pass


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(drop_authtoken_artifacts, noop_reverse),
    ]
