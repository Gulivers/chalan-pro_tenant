"""
Comando para crear superusuario en un tenant específico
Uso: python manage.py create_tenant_superuser --schema phoenix --username phoenix_admin --email phoenix@chalan-pro.net --password phoenix123
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crea un superusuario en un tenant específico'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            required=True,
            help='Nombre del schema del tenant (ej: phoenix)'
        )
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Nombre de usuario'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email del usuario'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Contraseña del usuario'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']
        username = options['username']
        email = options['email']
        password = options['password']
        
        User = get_user_model()
        
        try:
            with schema_context(schema_name):
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True
                    }
                )
                
                if not created:
                    user.email = email
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                
                user.set_password(password)
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Superusuario {"creado" if created else "actualizado"} en schema "{schema_name}":\n'
                        f'  Usuario: {username}\n'
                        f'  Email: {email}'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear superusuario: {str(e)}')
            )

