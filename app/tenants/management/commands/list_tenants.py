"""
Comando para listar todos los tenants y sus dominios
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from urllib.parse import urlparse
from tenants.models import Tenant, Domain
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Lista todos los tenants con sus dominios y credenciales de admin'

    def handle(self, *args, **options):
        tenants = Tenant.objects.filter(is_active=True).order_by('name')
        
        if not tenants.exists():
            self.stdout.write(self.style.WARNING('No hay tenants activos.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n📋 Tenants Activos ({tenants.count()}):\n'))
        
        for tenant in tenants:
            # Obtener dominio principal
            domain = Domain.objects.filter(tenant=tenant, is_primary=True).first()
            domain_name = domain.domain if domain else 'Sin dominio'
            
            self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
            self.stdout.write(self.style.SUCCESS(f'🏢 Tenant: {tenant.name}'))
            self.stdout.write(f'   Schema: {tenant.schema_name}')
            self.stdout.write(f'   Domain: {domain_name}')
            self.stdout.write(f'   Email: {tenant.email or "N/A"}')
            self.stdout.write(f'   Tipo: {tenant.get_client_type_display()}')
            self.stdout.write(f'   Estado: {"✅ Activo" if tenant.is_active else "❌ Inactivo"}')
            self.stdout.write(f'   Trial: {"Sí" if tenant.on_trial else "No"}')
            
            # URL de acceso
            if domain:
                # Obtener el puerto del frontend desde FRONT_URL
                front_url_parsed = urlparse(settings.FRONT_URL)
                frontend_port = front_url_parsed.port if front_url_parsed.port else 8080
                
                self.stdout.write(self.style.SUCCESS(f'\n   🌐 URLs de Acceso:'))
                self.stdout.write(f'      Admin: http://{domain_name}:8000/admin/')
                self.stdout.write(f'      Frontend: http://{domain_name}:{frontend_port}/')
            
            # Información de usuarios admin
            try:
                with schema_context(tenant.schema_name):
                    admin_users = User.objects.filter(is_superuser=True, is_active=True)
                    if admin_users.exists():
                        self.stdout.write(self.style.SUCCESS(f'\n   👤 Usuarios Admin ({admin_users.count()}):'))
                        for user in admin_users:
                            self.stdout.write(f'      Usuario: {user.username}')
                            self.stdout.write(f'      Email: {user.email or "N/A"}')
                            
                            self.stdout.write(self.style.WARNING(
                                    f'      🔑 Contraseña: No disponible'
                                ))
                                self.stdout.write(self.style.WARNING(
                                    f'      💡 Para resetear: python manage.py create_tenant_superuser --schema {tenant.schema_name} --username {user.username} --email {user.email or "admin@example.com"} --password nueva_password'
                                ))
                    else:
                        self.stdout.write(self.style.WARNING('\n   ⚠️  No hay usuarios admin en este tenant'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n   ❌ Error al acceder al schema: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}\n'))
        self.stdout.write(self.style.SUCCESS('💡 Para acceder al admin:'))
        self.stdout.write('   1. Configura el archivo hosts (ver ACCESO_ADMIN_TENANT.md)')
        self.stdout.write('   2. Accede a: http://[subdominio].chalan-pro.net:8000/admin/')
        self.stdout.write('   3. Usa las credenciales del usuario admin listado arriba\n')

