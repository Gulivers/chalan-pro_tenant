"""Drop orphaned DRF authtoken tables from the public schema (Stage D cleanup).

rest_framework.authtoken was removed from INSTALLED_APPS; leftover tables and
django_migrations rows remain until this runs.
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

    dependencies = [
        ('tenants', '0006_onboarding_pending_registration'),
    ]

    operations = [
        migrations.RunPython(drop_authtoken_artifacts, noop_reverse),
    ]
