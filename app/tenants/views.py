"""
Vistas para el sistema de onboarding y gestión de tenants
"""
import logging
from django.conf import settings
from django.core.management import call_command
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Tenant, Domain

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Endpoint raíz de la API para el schema public.
    Muestra los endpoints disponibles para onboarding y gestión de tenants.
    """
    return Response({
        'message': 'Chalan-Pro API - Public Schema',
        'version': '1.0.0',
        'endpoints': {
            'onboarding': {
                'create_tenant': {
                    'url': '/api/onboarding/',
                    'method': 'POST',
                    'description': 'Crear un nuevo tenant y ambiente de trabajo',
                    'required_fields': ['company_name', 'email', 'client_type'],
                    'optional_fields': ['logo', 'address', 'admin[name]', 'admin[password]', 'preferences'],
                    'example': {
                        'company_name': 'Phoenix Electric',
                        'email': 'admin@phoenix.com',
                        'client_type': 'electric',
                        'logo': '(archivo de imagen opcional)'
                    }
                }
            },
            'admin': {
                'url': '/admin/',
                'description': 'Panel de administración global para gestionar tenants'
            }
        },
        'documentation': {
            'onboarding': 'Accede a /onboarding en el frontend para crear tu cuenta',
            'api_docs': 'Los endpoints de tenant están disponibles después de crear tu cuenta'
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_tenant_onboarding(request):
    """
    Endpoint para crear un nuevo tenant desde el onboarding.
    
    Recibe:
    - company_name: Nombre de la empresa (requerido)
    - email: Email del cliente/administrador (requerido)
    - client_type: Tipo de cliente (electric, air_conditioning, etc.) (requerido)
    - logo: Archivo de imagen (opcional)
    - address: Dirección de la empresa (opcional)
    - admin[name]: Nombre completo del administrador (opcional, si no se proporciona usa email)
    - admin[password]: Contraseña del administrador (opcional, si no se proporciona genera una temporal)
    - preferences: Array de módulos activados (opcional, ej: ["inventory", "contracts"])
    
    Retorna:
    - success: Boolean
    - message: Mensaje de éxito/error
    - url: URL del subdominio del tenant creado
    - tenant: Información del tenant creado
    - credentials: Credenciales del usuario admin
    """
    try:
        # Obtener datos del formulario - Información de la empresa
        company_name = request.data.get('company_name', '').strip()
        client_type = request.data.get('client_type', 'general')
        logo = request.FILES.get('logo', None)
        address = request.data.get('address', '').strip() or None
        
        # Obtener campos estratégicos
        monthly_operations = request.data.get('monthly_operations', '').strip() or None
        crew_count = request.data.get('crew_count', None)
        recommended_plan = request.data.get('recommended_plan', '').strip() or None
        
        # Validar y convertir crew_count a entero
        if crew_count:
            try:
                crew_count = int(crew_count)
                if crew_count < 1:
                    crew_count = None
            except (ValueError, TypeError):
                crew_count = None
        
        # Validar monthly_operations
        valid_monthly_ops = ['0-10', '11-25', '26-50', '51-100', '100+']
        if monthly_operations and monthly_operations not in valid_monthly_ops:
            monthly_operations = None
        
        # Validar recommended_plan
        valid_plans = ['Starter', 'Professional', 'Enterprise']
        if recommended_plan and recommended_plan not in valid_plans:
            recommended_plan = None
        
        # Obtener datos del administrador
        # Soporta tanto formato plano como anidado
        email = request.data.get('email', '').strip()
        if not email:
            # Intentar obtener desde admin[email]
            admin_data = request.data.get('admin', {})
            if isinstance(admin_data, dict):
                email = admin_data.get('email', '').strip()
            elif isinstance(admin_data, str):
                # Si viene como string JSON, parsearlo
                import json
                try:
                    admin_data = json.loads(admin_data)
                    email = admin_data.get('email', '').strip()
                except:
                    pass
        
        admin_name = None
        admin_password = None
        
        # Obtener nombre y contraseña del admin si están disponibles
        admin_data = request.data.get('admin', {})
        if isinstance(admin_data, dict):
            admin_name = admin_data.get('name', '').strip() or None
            admin_password = admin_data.get('password', '').strip() or None
        elif isinstance(admin_data, str):
            # Si viene como string JSON, parsearlo
            import json
            try:
                admin_data = json.loads(admin_data)
                admin_name = admin_data.get('name', '').strip() or None
                admin_password = admin_data.get('password', '').strip() or None
            except:
                pass
        
        # También intentar obtener desde campos planos (compatibilidad)
        if not admin_name:
            admin_name = request.data.get('admin_name', '').strip() or None
        if not admin_password:
            admin_password = request.data.get('admin_password', '').strip() or None
        
        # Obtener preferencias de módulos
        # FormData puede enviar preferences como string JSON o como múltiples valores
        preferences = []
        
        # Intentar obtener como lista directamente
        prefs_data = request.data.get('preferences', [])
        
        if isinstance(prefs_data, list):
            preferences = prefs_data
        elif isinstance(prefs_data, str):
            # Si viene como string JSON, parsearlo
            import json
            try:
                preferences = json.loads(prefs_data)
            except:
                # Si falla, intentar como lista separada por comas
                preferences = [p.strip() for p in prefs_data.split(',') if p.strip()]
        else:
            # Intentar obtener múltiples valores con el mismo nombre (FormData puede enviar así)
            prefs_list = request.data.getlist('preferences', [])
            if prefs_list:
                preferences = prefs_list
        
        # Validar que preferences sea una lista válida
        valid_preferences = ['inventory', 'contracts', 'schedule', 'crews', 'notes']
        preferences = [p for p in preferences if p in valid_preferences]
        
        logger.info(f"Preferencias recibidas: {preferences}")
        
        # Validaciones básicas
        if not company_name or len(company_name) < 3:
            return Response({
                'success': False,
                'error': 'El nombre de la empresa debe tener al menos 3 caracteres.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response({
                'success': False,
                'error': 'El email es requerido.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar formato de email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_email(email)
        except DjangoValidationError:
            return Response({
                'success': False,
                'error': 'Por favor, ingresa un email válido.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que el email no esté en uso
        if Tenant.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'error': 'Este email ya está registrado. Por favor, usa otro email.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que el nombre de empresa no esté en uso
        if Tenant.objects.filter(name__iexact=company_name).exists():
            return Response({
                'success': False,
                'error': 'Este nombre de empresa ya está registrado. Por favor, usa otro nombre.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar tipo de cliente
        valid_client_types = [choice[0] for choice in Tenant.CLIENT_TYPE_CHOICES]
        if client_type not in valid_client_types:
            client_type = 'general'
        
        # Paso 1: Generar schema_name y tenant_id antes de crear el objeto
        # Esto evita problemas con la creación automática del schema
        logger.info(f"Iniciando creación de tenant: {company_name}")
        
        # Generar schema_name y tenant_id temporalmente para validar
        temp_tenant = Tenant(name=company_name, email=email, client_type=client_type)
        schema_name = temp_tenant._generate_schema_name()
        tenant_id = temp_tenant._generate_tenant_id()
        
        logger.info(f"Schema name generado: {schema_name}")
        logger.info(f"Tenant ID generado: {tenant_id}")
        
        # Paso 2: Crear el tenant - django-tenants creará automáticamente el schema
        # El modelo Tenant tiene auto_create_schema=True como atributo de clase
        tenant = Tenant(
            name=company_name,
            email=email,
            client_type=client_type,
            logo=logo,
            address=address,
            preferences=preferences,
            monthly_operations=monthly_operations,
            crew_count=crew_count,
            recommended_plan=recommended_plan,
            schema_name=schema_name,
            tenant_id=tenant_id,
            on_trial=True,
            is_active=True
        )
        
        # Paso 3: Validar y guardar el tenant (django-tenants creará el schema automáticamente)
        try:
            logger.info(f"Validando tenant: {company_name}")
            tenant.full_clean()
            
            logger.info(f"Guardando tenant en base de datos: {tenant.name}")
            tenant.save()  # django-tenants creará el schema automáticamente aquí
            logger.info(f"✓ Tenant guardado exitosamente con ID: {tenant.id}, Schema: {tenant.schema_name}")
            
        except Exception as e:
            logger.error(f"✗ Error al crear tenant: {str(e)}", exc_info=True)
            import traceback
            error_details = traceback.format_exc() if settings.DEBUG else str(e)
            return Response({
                'success': False,
                'error': f'Error al crear el tenant: {str(e)}',
                'details': error_details if settings.DEBUG else None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el dominio basado en el schema_name
        # Obtener el dominio base desde settings o usar uno por defecto
        base_domain = getattr(settings, 'TENANT_BASE_DOMAIN', 'chalan-pro.net')
        # Obtener subdominio del schema_name (ahora usa guiones directamente, válido para DNS)
        subdomain = tenant.schema_to_subdomain()
        
        # Crear dominio completo
        domain_name = f"{subdomain}.{base_domain}"
        
        # Verificar que el dominio no exista
        if Domain.objects.filter(domain=domain_name).exists():
            # Si existe, agregar un número
            counter = 1
            while Domain.objects.filter(domain=f"{subdomain}{counter}.{base_domain}").exists():
                counter += 1
            domain_name = f"{subdomain}{counter}.{base_domain}"
            logger.warning(f"Dominio {subdomain}.{base_domain} ya existe, usando {domain_name}")
        
        # Crear el dominio
        try:
            domain = Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=True
            )
            logger.info(f"✓ Dominio creado: {domain_name}")
        except Exception as e:
            logger.error(f"✗ Error al crear dominio: {str(e)}", exc_info=True)
            # Intentar eliminar el tenant si falla la creación del dominio
            try:
                tenant.delete()
            except:
                pass
            return Response({
                'success': False,
                'error': f'Error al crear el dominio: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Tenant creado: {tenant.name} ({tenant.schema_name})")
        logger.info(f"Dominio creado: {domain_name}")
        
        # Verificar que el schema se haya creado correctamente
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.schemata 
                        WHERE schema_name = %s
                    )
                """, [tenant.schema_name])
                schema_exists = cursor.fetchone()[0]
            
            if not schema_exists:
                logger.error(f"✗ El schema {tenant.schema_name} no existe después de crear el tenant")
                # Intentar crear el schema manualmente
                logger.info(f"Intentando crear el schema {tenant.schema_name} manualmente...")
                with connection.cursor() as cursor:
                    cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{tenant.schema_name}"')
                logger.info(f"✓ Schema {tenant.schema_name} creado manualmente")
            else:
                logger.info(f"✓ Schema {tenant.schema_name} existe correctamente")
        except Exception as e:
            logger.error(f"✗ Error al verificar/crear schema: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error al verificar el schema del tenant: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Ejecutar migraciones para el nuevo tenant
        # django-tenants requiere que las migraciones se ejecuten después de crear el schema
        try:
            logger.info(f"Ejecutando migraciones para schema: {tenant.schema_name}")
            
            # Método 1: Intentar con migrate_schemas usando el parámetro schema
            # El comando migrate_schemas de django-tenants acepta --schema=<schema_name>
            try:
                call_command('migrate_schemas', schema=tenant.schema_name, verbosity=1)
                logger.info(f"✓ Migraciones completadas usando migrate_schemas para schema: {tenant.schema_name}")
            except Exception as e1:
                logger.warning(f"migrate_schemas con parámetro 'schema' falló: {str(e1)}")
                # Método 2: Intentar usando schema_context con migrate normal
                try:
                    logger.info(f"Intentando ejecutar migraciones usando schema_context...")
                    with schema_context(tenant.schema_name):
                        call_command('migrate', verbosity=1, interactive=False)
                    logger.info(f"✓ Migraciones completadas usando schema_context para schema: {tenant.schema_name}")
                except Exception as e2:
                    logger.error(f"✗ Error con schema_context: {str(e2)}", exc_info=True)
                    # Método 3: Intentar usando el método create_schema del tenant si está disponible
                    try:
                        logger.info(f"Intentando usar método create_schema del tenant...")
                        if hasattr(tenant, 'create_schema'):
                            tenant.create_schema(check_if_exists=True)
                            logger.info(f"✓ Schema creado/verificado usando create_schema")
                            # Intentar migraciones nuevamente
                            with schema_context(tenant.schema_name):
                                call_command('migrate', verbosity=1, interactive=False)
                            logger.info(f"✓ Migraciones completadas después de create_schema")
                        else:
                            raise Exception("El método create_schema no está disponible")
                    except Exception as e3:
                        logger.error(f"✗ Error con create_schema: {str(e3)}", exc_info=True)
                        # Si todos los métodos fallan, intentar limpiar el tenant creado
                        try:
                            tenant.delete()
                            logger.info(f"Tenant {tenant.name} eliminado debido a error en migraciones")
                        except:
                            pass
                        return Response({
                            'success': False,
                            'error': f'Error al ejecutar migraciones para el nuevo tenant. Métodos intentados: migrate_schemas ({str(e1)}), schema_context ({str(e2)}), create_schema ({str(e3)})'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"✗ Error inesperado al ejecutar migraciones: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error inesperado al ejecutar migraciones: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Crear superusuario inicial para el tenant
        # Usar el email como username base, o el nombre proporcionado
        username_base = email.split('@')[0]
        if admin_name:
            # Si hay nombre completo, usar la primera parte del nombre como username base
            name_parts = admin_name.split()
            if name_parts:
                username_base = name_parts[0].lower()
        
        username = username_base
        
        # Asegurar que el username sea único en el schema del tenant
        with schema_context(tenant.schema_name):
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Usar la contraseña proporcionada o generar una temporal
            if admin_password:
                # Validar que la contraseña tenga al menos 8 caracteres
                if len(admin_password) < 8:
                    # Si la contraseña es muy corta, generar una temporal y guardarla
                    import secrets
                    import string
                    alphabet = string.ascii_letters + string.digits + "!@#$%"
                    temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
                    logger.warning(f"Contraseña muy corta proporcionada, generando contraseña temporal para {username}")
                else:
                    temp_password = admin_password
            else:
                # Generar una contraseña temporal segura si no se proporciona
                import secrets
                import string
                # Generar contraseña temporal: 12 caracteres alfanuméricos + símbolos
                alphabet = string.ascii_letters + string.digits + "!@#$%"
                temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
                logger.info(f"No se proporcionó contraseña, generando contraseña temporal para {username}")
            
            # Crear el superusuario con nombre completo si está disponible
            user_kwargs = {
                'username': username,
                'email': email,
                'password': temp_password,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
            
            # Agregar nombre completo si está disponible
            if admin_name:
                name_parts = admin_name.split(maxsplit=1)
                user_kwargs['first_name'] = name_parts[0]
                if len(name_parts) > 1:
                    user_kwargs['last_name'] = name_parts[1]
            
            user = User.objects.create_user(**user_kwargs)
            
            logger.info(f"✓ Superusuario creado para tenant {tenant.schema_name}: {username} ({admin_name or 'Sin nombre'})")
            
            # Guardar la contraseña temporal en el tenant (solo en desarrollo o si fue generada)
            if settings.DEBUG or not admin_password:
                tenant.admin_temp_password = temp_password
                tenant.save(update_fields=['admin_temp_password'])
            
            # TODO: En producción, enviar email con credenciales al usuario
            # from django.core.mail import send_mail
            # send_mail(
            #     subject='Bienvenido a Chalan-Pro',
            #     message=f'Tu cuenta ha sido creada. Usuario: {username}, Contraseña temporal: {temp_password}',
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[email],
            #     fail_silently=False,
            # )
        
        # Construir la URL de redirección
        # En desarrollo local, usar localhost con el subdominio
        # En producción, usar el dominio completo con HTTPS
        if settings.DEBUG:
            # En desarrollo, redirigir al subdominio en el puerto del frontend (8080)
            # Obtener el puerto de FRONT_URL o usar 8080 por defecto
            from urllib.parse import urlparse
            front_url_parsed = urlparse(settings.FRONT_URL)
            frontend_port = front_url_parsed.port if front_url_parsed.port else 8080
            redirect_url = f"http://{domain_name}:{frontend_port}/login/"
        else:
            # En producción, usar HTTPS
            redirect_url = f"https://{domain_name}/login/"
        
        return Response({
            'success': True,
            'message': f'¡Tu cuenta ha sido creada exitosamente! Redirigiendo a tu ambiente...',
            'url': redirect_url,
            'tenant': {
                'name': tenant.name,
                'schema_name': tenant.schema_name,
                'domain': domain_name,
                'username': username,
                'email': email,
                'admin_name': admin_name or user.get_full_name() or username,
                'preferences': preferences,
                'monthly_operations': tenant.monthly_operations,
                'crew_count': tenant.crew_count,
                'recommended_plan': tenant.recommended_plan,
                # En desarrollo, incluir la contraseña temporal en la respuesta
                # En producción, esto debería enviarse por email
                'temp_password': temp_password if (settings.DEBUG or not admin_password) else None
            },
            'credentials': {
                'username': username,
                'password': temp_password if (settings.DEBUG or not admin_password) else None,
                'password_provided': bool(admin_password),
                'message': 'Guarda estas credenciales. En producción, se enviarán por email.' if (settings.DEBUG or not admin_password) else 'Tu contraseña ha sido configurada correctamente.'
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error inesperado en create_tenant_onboarding: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Error inesperado al crear la cuenta: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
