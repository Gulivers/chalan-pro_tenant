# -*- coding: utf-8 -*-
"""
Deprecated entrypoint. Use:

  python manage.py mysql_backup

Credentials come only from MYSQL_* environment variables. Never commit passwords.

A previous revision of this file contained hardcoded database credentials. Those
credentials are compromised and must be rotated on the MySQL server.
"""
raise SystemExit(
    'This script no longer runs backups directly. '
    'Use: python manage.py mysql_backup (see MYSQL_* env vars). '
    'Rotate any credentials that were previously committed to Git.'
)
