# -*- coding: utf-8 -*-
"""
Backup MySQL via mysqldump using credentials from the environment.

IMPORTANT: A previous revision of this helper committed database credentials to
Git. Those credentials must be treated as compromised and rotated on the MySQL
server. This command never stores a password in the repository.

Required env:
  MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
Optional:
  MYSQL_HOST (default 127.0.0.1), MYSQL_PORT (default 3306),
  MYSQL_BACKUP_DIR (default ./backups)

Password is written to a temporary defaults-extra-file (mode 0600) and the file
is deleted in finally. subprocess runs without shell=True.
"""
from __future__ import annotations

import datetime
import os
import stat
import subprocess
import tempfile

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Run mysqldump using MYSQL_* environment variables (no secrets in repo).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default=None,
            help='Override MYSQL_BACKUP_DIR',
        )

    def handle(self, *args, **options):
        user = os.environ.get('MYSQL_USER', '').strip()
        password = os.environ.get('MYSQL_PASSWORD', '')
        database = os.environ.get('MYSQL_DATABASE', '').strip()
        host = os.environ.get('MYSQL_HOST', '127.0.0.1').strip() or '127.0.0.1'
        port = os.environ.get('MYSQL_PORT', '3306').strip() or '3306'
        backup_dir = (
            options.get('output_dir')
            or os.environ.get('MYSQL_BACKUP_DIR', '').strip()
            or os.path.join(os.getcwd(), 'backups')
        )

        if not user or not database:
            raise CommandError(
                'Set MYSQL_USER and MYSQL_DATABASE (and MYSQL_PASSWORD) in the environment.'
            )
        if password == '':
            raise CommandError('Set MYSQL_PASSWORD in the environment.')

        os.makedirs(backup_dir, exist_ok=True)
        stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'{database}_{stamp}.sql')

        defaults_path = None
        try:
            fd, defaults_path = tempfile.mkstemp(prefix='mysql_backup_', suffix='.cnf')
            os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                fh.write('[client]\n')
                fh.write(f'user={user}\n')
                fh.write(f'password={password}\n')
                fh.write(f'host={host}\n')
                fh.write(f'port={port}\n')

            cmd = [
                'mysqldump',
                f'--defaults-extra-file={defaults_path}',
                '--single-transaction',
                '--routines',
                '--triggers',
                database,
            ]
            with open(backup_file, 'wb') as out:
                result = subprocess.run(
                    cmd,
                    check=False,
                    stdout=out,
                    stderr=subprocess.PIPE,
                    shell=False,
                )
            if result.returncode != 0:
                err = (result.stderr or b'').decode('utf-8', errors='replace')
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                raise CommandError(f'mysqldump failed (exit {result.returncode}): {err}')
            self.stdout.write(self.style.SUCCESS(f'Backup written to {backup_file}'))
        finally:
            if defaults_path and os.path.exists(defaults_path):
                try:
                    os.remove(defaults_path)
                except OSError:
                    pass
