"""
Comando para depurar problemas de detección de tenant
"""
from django.core.management.base import BaseCommand
from tenants.models import Domain, Tenant
from django.db import connection


class Command(BaseCommand):
    help = 'Depura la detección de tenant por hostname'

    def add_arguments(self, parser):
        parser.add_argument(
            'hostname',
            type=str,
            help='Hostname a verificar (ej: globo_dyned2.chalan-pro.net:8000)',
        )

    def handle(self, *args, **options):
        hostname = options['hostname']
        
        self.stdout.write(self.style.SUCCESS(f'\n🔍 Depurando hostname: {hostname}\n'))
        
        # Remover puerto si existe
        hostname_clean = hostname.split(':')[0]
        self.stdout.write(f'Hostname limpio (sin puerto): {hostname_clean}\n')
        
        # Buscar dominio
        try:
            domain = Domain.objects.select_related('tenant').get(domain=hostname_clean)
            tenant = domain.tenant
            
            self.stdout.write(self.style.SUCCESS('✓ Dominio encontrado:'))
            self.stdout.write(f'   Domain: {domain.domain}')
            self.stdout.write(f'   Tenant: {tenant.name}')
            self.stdout.write(f'   Schema: {tenant.schema_name}')
            self.stdout.write(f'   Is Active: {tenant.is_active}')
            self.stdout.write(f'   Is Primary: {domain.is_primary}')
            
            # Verificar que el schema existe
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.schemata 
                    WHERE schema_name = %s
                )
            """, [tenant.schema_name])
            schema_exists = cursor.fetchone()[0]
            
            if schema_exists:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Schema "{tenant.schema_name}" existe en la base de datos'))
                
                # Verificar tablas del admin
                cursor.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND table_name IN ('django_admin_log', 'django_content_type', 'auth_user', 'auth_group')
                    ORDER BY table_name
                """, [tenant.schema_name])
                admin_tables = [row[0] for row in cursor.fetchall()]
                
                self.stdout.write(f'\n📋 Tablas del admin en schema "{tenant.schema_name}":')
                required_tables = ['django_admin_log', 'django_content_type', 'auth_user', 'auth_group']
                for table in required_tables:
                    status = '✓' if table in admin_tables else '✗'
                    self.stdout.write(f'   {status} {table}')
                
                if len(admin_tables) < len(required_tables):
                    self.stdout.write(self.style.WARNING(
                        f'\n⚠️  Faltan tablas del admin. Ejecuta: python manage.py migrate_schemas --schema={tenant.schema_name}'
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS('\n✓ Todas las tablas del admin existen'))
                
                # Verificar usuarios admin
                from django_tenants.utils import schema_context
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                with schema_context(tenant.schema_name):
                    admin_users = User.objects.filter(is_superuser=True, is_active=True)
                    self.stdout.write(f'\n👤 Usuarios admin en schema "{tenant.schema_name}": {admin_users.count()}')
                    for user in admin_users:
                        self.stdout.write(f'   - {user.username} ({user.email or "sin email"})')
                    
                    if admin_users.count() == 0:
                        self.stdout.write(self.style.WARNING(
                            '\n⚠️  No hay usuarios admin. Crea uno con: python manage.py createsuperuser'
                        ))
            else:
                self.stdout.write(self.style.ERROR(f'\n✗ Schema "{tenant.schema_name}" NO existe en la base de datos'))
                self.stdout.write(self.style.WARNING(
                    f'Ejecuta: python manage.py migrate_schemas --schema={tenant.schema_name}'
                ))
            
            # URLs de acceso
            from django.conf import settings
            from urllib.parse import urlparse
            
            # Obtener el puerto del frontend desde FRONT_URL
            front_url_parsed = urlparse(settings.FRONT_URL)
            frontend_port = front_url_parsed.port if front_url_parsed.port else 8080
            
            self.stdout.write(self.style.SUCCESS(f'\n URLs de acceso:'))
            self.stdout.write(f'   Admin: http://{domain.domain}:8000/admin/')
            self.stdout.write(f'   Frontend: http://{domain.domain}:{frontend_port}/')
            
        except Domain.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'\n✗ No se encontró dominio para: {hostname_clean}'))
            
            # Mostrar dominios disponibles
            domains = Domain.objects.select_related('tenant').all()
            if domains.exists():
                self.stdout.write('\n📋 Dominios disponibles:')
                for d in domains:
                    self.stdout.write(f'   - {d.domain} -> {d.tenant.name} ({d.tenant.schema_name})')
            else:
                self.stdout.write(self.style.WARNING('\n⚠️  No hay dominios configurados'))
        
        self.stdout.write('')

