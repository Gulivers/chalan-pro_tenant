import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count, Min

from appschedule.models import Event


"""
Uso:
  # Solo reporta (no borra ni hace backup)
  python manage.py dedupe_events
  docker compose exec web python manage.py dedupe_events

  # Aplica borrado + backup automático
  python manage.py dedupe_events --apply
  docker compose exec web python manage.py dedupe_events --apply

  # Aplica borrado PERO sin backup previo
  python manage.py dedupe_events --apply --no-backup
  docker compose exec web python manage.py dedupe_events --apply --no-backup


  # Con backup en directorio custom
  python manage.py dedupe_events --apply --backup-dir /home/superadmin/backups
  docker compose exec web python manage.py dedupe_events --apply --backup-dir /home/superadmin/backups

  # Prefijo custom para el archivo de backup (por defecto: <DB>_backup_)
  python manage.py dedupe_events --apply --backup-prefix chalan_division_backup_
"""


class Command(BaseCommand):
    help = (
        "Detects and deletes duplicate Events by (crew, date, title), "
        "keeping the lowest id. Optionally performs a DB backup before deletion."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually delete duplicates (otherwise dry-run)"
        )
        parser.add_argument(
            "--no-backup",
            action="store_true",
            help="Skip full DB backup before deleting (only relevant with --apply)"
        )
        parser.add_argument(
            "--backup-dir",
            type=str,
            default=None,
            help="Directory to store the SQL dump (default: <BASE>/backups)"
        )
        parser.add_argument(
            "--backup-prefix",
            type=str,
            default=None,
            help="Filename prefix for the SQL dump (default: <DB>_backup_)"
        )
        parser.add_argument(
            "--mysqldump-path",
            type=str,
            default="mysqldump",
            help="Path to the mysqldump binary (default: 'mysqldump')"
        )

    # ----------------------
    # Helpers
    # ----------------------
    def _get_db_creds(self):
        """
        Lee credenciales de MySQL desde variables de entorno (.env en tu setup Docker).
        NO imprime secretos.
        """
        host = os.environ.get("MYSQL_HOST", "localhost")
        user = os.environ.get("MYSQL_USER", "root")
        password = os.environ.get("MYSQL_PASSWORD")
        database = os.environ.get("MYSQL_DATABASE")

        if not database:
            raise CommandError("MYSQL_DATABASE no está definido en el entorno.")

        return host, user, password, database

    def _resolve_backup_path(self, backup_dir, backup_prefix, database):
        """
        Calcula ruta final del archivo de backup, creando el directorio si no existe.
        """
        ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        dir_path = Path(backup_dir) if backup_dir else Path.cwd() / "backups"
        dir_path.mkdir(parents=True, exist_ok=True)

        prefix = backup_prefix if backup_prefix is not None else f"{database}_backup_"
        filename = f"{prefix}{ts}.sql"
        return dir_path / filename

    def _run_backup(self, mysqldump_path, backup_file_path):
        """
        Ejecuta mysqldump con credenciales del entorno.
        Usa MYSQL_PWD para no exponer la clave en el argv.
        """
        host, user, password, database = self._get_db_creds()

        cmd = [
            mysqldump_path,
            "-u", user,
            "-h", host,
            "--single-transaction",
            "--quick",
            "--lock-tables=false",
            database,
        ]

        # Heredamos el entorno actual y agregamos MYSQL_PWD solo para el subproceso
        env = os.environ.copy()
        if password:
            env["MYSQL_PWD"] = password  # Nota: más seguro que pasar --password

        self.stdout.write(
            f"• Realizando backup de '{database}' en: {backup_file_path}"
        )

        try:
            with open(backup_file_path, "wb") as f:
                # Enviamos stdout al archivo; capturamos stderr para logs
                proc = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env=env,
                    check=False
                )
            if proc.returncode != 0:
                stderr = proc.stderr.decode("utf-8", errors="ignore")
                raise CommandError(
                    f"mysqldump falló (code={proc.returncode}). Detalle:\n{stderr}"
                )
        except FileNotFoundError:
            raise CommandError(
                f"No se encontró '{mysqldump_path}'. "
                f"Instálalo o especifica la ruta con --mysqldump-path."
            )

        self.stdout.write(self.style.SUCCESS("✓ Backup completado"))

    # ----------------------
    # Main
    # ----------------------
    def handle(self, *args, **opts):
        # 1) Detectar duplicados
        dupes = (
            Event.objects
            .values("crew", "date", "title")
            .annotate(c=Count("id"), keep_id=Min("id"))
            .filter(c__gt=1)
        )

        total_groups = dupes.count()
        self.stdout.write(f"Duplicate groups: {total_groups}")

        if not opts["apply"]:
            self.stdout.write("Dry-run. Usa --apply para eliminar.")
            return

        # 2) Backup (a menos que pidan explícitamente omitirlo)
        if not opts["no_backup"]:
            host, user, password, database = self._get_db_creds()
            backup_path = self._resolve_backup_path(
                backup_dir=opts.get("backup_dir"),
                backup_prefix=opts.get("backup_prefix"),
                database=database,
            )
            self._run_backup(
                mysqldump_path=opts.get("mysqldump_path", "mysqldump"),
                backup_file_path=backup_path,
            )
        else:
            self.stdout.write("⚠️  Omitiendo backup por --no-backup")

        # 3) Borrado de duplicados (manteniendo el menor id)
        with transaction.atomic():
            deleted = 0
            for g in dupes:
                crew, date, title, keep_id = g["crew"], g["date"], g["title"], g["keep_id"]
                qs = Event.objects.filter(crew=crew, date=date, title=title).exclude(id=keep_id)
                batch = qs.count()
                if batch:
                    deleted += batch
                    qs.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted duplicate rows: {deleted}"))
