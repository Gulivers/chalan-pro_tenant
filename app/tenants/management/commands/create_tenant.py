"""
Comando de gestión para crear nuevos tenants
Uso: python manage.py create_tenant --name "Phoenix Electric" --schema phoenix --domain phoenix.chalan-pro.net
"""
import os
import re

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django_tenants.utils import schema_context

from tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Crea un nuevo tenant con su schema y dominio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Nombre del tenant (ej: "Phoenix Electric")'
        )
        parser.add_argument(
            '--schema',
            type=str,
            required=True,
            help='Nombre del schema (ej: "phoenix") - debe ser único y válido para PostgreSQL'
        )
        parser.add_argument(
            '--domain',
            type=str,
            required=True,
            help='Dominio completo (ej: "phoenix.chalan-pro.net")'
        )
        parser.add_argument(
            '--paid-until',
            type=str,
            required=False,
            help='Fecha de pago hasta (formato: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--trial',
            action='store_true',
            help='Marcar como tenant en periodo de prueba'
        )

    def handle(self, *args, **options):
        name = options['name']
        schema_name = options['schema']
        domain = options['domain']
        paid_until = options.get('paid_until')
        on_trial = options.get('trial', False)

        # Validar que el schema_name sea válido para PostgreSQL
        # Ahora permitimos guiones en lugar de guiones bajos
        if not re.match(r'^[a-z][a-z0-9-]*$', schema_name.lower()):
            self.stdout.write(
                self.style.ERROR(
                    f'Error: El schema "{schema_name}" no es válido. '
                    'Debe contener solo letras minúsculas, números y guiones, y debe empezar con letra.'
                )
            )
            return

        # Verificar si el tenant ya existe
        if Tenant.objects.filter(schema_name=schema_name).exists():
            self.stdout.write(
                self.style.ERROR(f'Error: Ya existe un tenant con el schema "{schema_name}"')
            )
            return

        if Domain.objects.filter(domain=domain).exists():
            self.stdout.write(
                self.style.ERROR(f'Error: Ya existe un dominio "{domain}"')
            )
            return

        try:
            # Crear el tenant (esto creará automáticamente el schema)
            tenant = Tenant.objects.create(
                name=name,
                schema_name=schema_name,
                paid_until=paid_until,
                on_trial=on_trial,
                is_active=True
            )

            # Crear el dominio asociado
            Domain.objects.create(
                domain=domain,
                tenant=tenant,
                is_primary=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Tenant "{name}" creado exitosamente\n'
                    f'  Schema: {schema_name}\n'
                    f'  Dominio: {domain}\n'
                    f'  URL Admin: http://{domain}/admin/'
                )
            )

            # Ejecutar migraciones para el nuevo tenant
            self.stdout.write(self.style.WARNING('Ejecutando migraciones para el nuevo tenant...'))
            call_command('migrate_schemas', schema_name=schema_name)

            self.stdout.write(
                self.style.SUCCESS('✓ Migraciones completadas para el nuevo tenant')
            )

            # Seed inicial de tipos de documento (apptransactions.documenttype)
            try:
                fixture_doc_types = os.path.join(
                    settings.BASE_DIR,
                    'apptransactions',
                    'fixtures',
                    'masters_document_type.json',
                )
                if os.path.exists(fixture_doc_types):
                    self.stdout.write('Cargando tipos de documento iniciales desde masters_document_type.json...')
                    with schema_context(schema_name):
                        call_command('loaddata', fixture_doc_types, verbosity=0)
                    self.stdout.write(self.style.SUCCESS('✓ Tipos de documento iniciales cargados.'))
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            'Fixture masters_document_type.json no encontrado; se omite seed de tipos de documento.'
                        )
                    )
            except Exception as e:
                # No abortar la creación del tenant si falla el seed; solo informar.
                self.stdout.write(
                    self.style.ERROR(f'Error al cargar masters_document_type.json para el nuevo tenant: {e}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear el tenant: {str(e)}')
            )

