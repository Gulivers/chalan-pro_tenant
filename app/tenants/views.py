"""
Vistas para el sistema de onboarding y gestión de tenants
"""
import logging
import os
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from django.template.loader import render_to_string
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Tenant, Domain

logger = logging.getLogger(__name__)
User = get_user_model()


def _send_onboarding_welcome_email(
    *,
    recipient_email: str,
    company_name: str,
    login_url: str,
    username: str,
    temp_password: str,
    user_chose_strong_password: bool,
    admin_name: Optional[str],
) -> None:
    """Envía confirmación de onboarding desde DEFAULT_FROM_EMAIL (p. ej. noreply@jobrhythm.net)."""
    admin_display = (admin_name or "").strip() or None
    context = {
        "company_name": company_name,
        "login_url": login_url,
        "username": username,
        "temp_password": temp_password,
        "user_chose_strong_password": user_chose_strong_password,
        "admin_display_name": admin_display,
    }
    text_body = (
        f"Your JobRhythm workspace is ready.\n\n"
        f"Company: {company_name}\n"
        f"Username: {username}\n"
        f"Sign-in link: {login_url}\n\n"
    )
    if user_chose_strong_password:
        text_body += "Use the password you set during signup.\n"
    else:
        text_body += f"Temporary password: {temp_password}\n"
    html_body = render_to_string("onboarding_welcome_email.html", context)
    msg = EmailMultiAlternatives(
        "Your JobRhythm workspace is ready",
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def landing_contact(request):
    """
    Public landing contact form (getjobrhythm.com). Sends email to LANDING_CONTACT_TO_EMAIL.
    """
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError as DjangoValidationError

    if not getattr(settings, 'EMAIL_HOST_PASSWORD', None):
        logger.warning('landing_contact: SMTP not configured (EMAIL_HOST_PASSWORD empty)')
        return Response(
            {'success': False, 'error': 'Email delivery is not configured.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    data = request.data
    if not isinstance(data, dict):
        return Response({'success': False, 'error': 'Invalid JSON body.'}, status=status.HTTP_400_BAD_REQUEST)

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    subject_key = (data.get('subject') or 'demo').strip()
    team_size = (data.get('team_size') or '').strip()
    message = (data.get('message') or '').strip()
    locale = (data.get('locale') or 'en').strip().lower()

    if not name or len(name) > 200:
        return Response({'success': False, 'error': 'Please provide a valid name.'}, status=status.HTTP_400_BAD_REQUEST)
    if not message or len(message) > 8000:
        return Response({'success': False, 'error': 'Please provide a message.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_email(email)
    except DjangoValidationError:
        return Response({'success': False, 'error': 'Please provide a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)

    allowed_subjects = {'demo', 'sales', 'support'}
    if subject_key not in allowed_subjects:
        subject_key = 'demo'

    subject_labels = {
        'demo': ('Product demo request', 'Solicitud de demo de producto'),
        'sales': ('Talk to sales', 'Hablar con ventas'),
        'support': ('Support', 'Soporte'),
    }
    subj_en, subj_es = subject_labels[subject_key]
    topic = subj_es if locale == 'es' else subj_en

    to_email = getattr(settings, 'LANDING_CONTACT_TO_EMAIL', None) or settings.DEFAULT_FROM_EMAIL
    mail_subject = f"[JobRhythm Contact] {topic} — {name}"

    text_body = (
        f"New contact form submission (locale={locale})\n\n"
        f"Topic: {subject_key} ({topic})\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Team size: {team_size or '—'}\n\n"
        f"Message:\n{message}\n"
    )

    msg = EmailMultiAlternatives(
        mail_subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        reply_to=[email],
    )
    try:
        msg.send(fail_silently=False)
    except Exception as exc:
        logger.exception('landing_contact: send failed: %s', exc)
        return Response(
            {'success': False, 'error': 'Could not send your message. Please try again later.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({'success': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Endpoint raíz de la API para el schema public.
    Muestra los endpoints disponibles para onboarding y gestión de tenants.
    """
    return Response({
        'message': 'JobRhythm API - Public Schema',
        'version': '1.0.0',
        'endpoints': {
            'onboarding': {
                'create_tenant': {
                    'url': '/api/onboarding/',
                    'method': 'POST',
                    'description': 'Create a new tenant and workspace',
                    'required_fields': ['company_name', 'email', 'client_type'],
                    'optional_fields': ['logo', 'address', 'admin[name]', 'admin[password]', 'preferences'],
                    'example': {
                        'company_name': 'Phoenix Electric',
                        'email': 'admin@phoenix.com',
                        'client_type': 'electric',
                        'logo': '(optional image file)'
                    }
                }
            },
            'admin': {
                'url': '/admin/',
                'description': 'Global admin panel to manage tenants'
            }
        },
        'documentation': {
            'onboarding': 'Open /onboarding in the frontend to create your account',
            'api_docs': 'Tenant endpoints are available after you create your account'
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
    - landing_selected_plan: Starter | Professional | Enterprise (opcional, p. ej. desde ?plan= en la landing)
    
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
        landing_selected_plan = request.data.get('landing_selected_plan', '').strip() or None
        
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
        
        # Validar recommended_plan y landing_selected_plan
        valid_plans = ['Starter', 'Professional', 'Enterprise']
        if recommended_plan and recommended_plan not in valid_plans:
            recommended_plan = None
        if landing_selected_plan and landing_selected_plan not in valid_plans:
            landing_selected_plan = None
        
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
        # Aligned with JobRhythm SPA navbar (exclude Dashboard + backend-only apps)
        valid_preferences = [
            'operations',
            'inventory',
            'contracts_pricing',
            'entities',
            'crews_fleet',
            'communities',
            # Legacy slugs still accepted when present in older payloads
            'contracts',
            'schedule',
            'crews',
            'notes',
        ]
        preferences = [p for p in preferences if p in valid_preferences]
        
        logger.info(f"Preferencias recibidas: {preferences}")
        
        # Validaciones básicas
        if not company_name or len(company_name) < 3:
            return Response({
                'success': False,
                'error': 'Company name must be at least 3 characters long.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar formato de email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_email(email)
        except DjangoValidationError:
            return Response({
                'success': False,
                'error': 'Please enter a valid email address.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que el email no esté en uso
        if Tenant.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'error': 'This email is already registered. Please use a different email.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que el nombre de empresa no esté en uso
        if Tenant.objects.filter(name__iexact=company_name).exists():
            return Response({
                'success': False,
                'error': 'This company name is already registered. Please choose a different name.'
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
            landing_selected_plan=landing_selected_plan,
            schema_name=schema_name,
            tenant_id=tenant_id,
            on_trial=True,
            is_active=True
        )
        from appbilling.services.trial import start_trial_for_tenant
        start_trial_for_tenant(tenant)

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
                'error': f'Could not create tenant: {str(e)}',
                'details': error_details if settings.DEBUG else None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el dominio basado en el schema_name
        # Obtener el dominio base desde settings o usar uno por defecto
        base_domain = getattr(settings, 'TENANT_BASE_DOMAIN', 'jobrhythm.net')
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
                'error': f'Could not create domain: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Forzar actualización de ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS para que
        # el nuevo subdominio sea accesible de inmediato (sin esperar el TTL de 5 min).
        try:
            from project.middleware.dynamic_hosts_utils import refresh_dynamic_domains
            refresh_dynamic_domains()
            logger.info("✓ Dominios dinámicos actualizados (tenant accesible de inmediato)")
        except Exception as e:
            logger.warning("No se pudo actualizar dominios dinámicos: %s", e)
        
        # Asegurar que el dominio esté confirmado en BD para otros workers (p. ej. Daphne).
        try:
            from django.db import connection
            connection.ensure_connection()
            if hasattr(connection, "commit"):
                connection.commit()
                logger.debug("Commit explícito para dominio visible en todos los workers")
        except Exception as e:
            logger.debug("Commit explícito (opcional): %s", e)
        
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
                'error': f'Could not verify tenant schema: {str(e)}'
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
                            'error': f'Could not run migrations for the new tenant. Attempts: migrate_schemas ({str(e1)}), schema_context ({str(e2)}), create_schema ({str(e3)})'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"✗ Error inesperado al ejecutar migraciones: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Unexpected error while running migrations: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Crear datos iniciales dentro del schema del tenant
        with schema_context(tenant.schema_name):
            # 1) Seed de tipos de documento (transactions)
            try:
                fixture_doc_types = os.path.join(
                    settings.BASE_DIR,
                    'apptransactions',
                    'fixtures',
                    'masters_document_type.json',
                )
                if os.path.exists(fixture_doc_types):
                    call_command('loaddata', fixture_doc_types, verbosity=0)
                    logger.info(
                        "✓ Tipos de documento iniciales cargados desde masters_document_type.json "
                        "para tenant %s",
                        tenant.schema_name,
                    )
                else:
                    logger.warning(
                        "Fixture masters_document_type.json no encontrado; "
                        "se omite seed de tipos de documento para tenant %s",
                        tenant.schema_name,
                    )
            except Exception as e:
                # No bloquear la creación del tenant si falla el seed; solo loguear.
                logger.error(
                    "✗ Error al cargar masters_document_type.json para tenant %s: %s",
                    tenant.schema_name,
                    e,
                    exc_info=True,
                )

            # 2) Crear superusuario inicial para el tenant
            # Usar el email como username base, o el nombre proporcionado
            username_base = email.split('@')[0]
            if admin_name:
                # Si hay nombre completo, usar la primera parte del nombre como username base (se conserva el caso)
                name_parts = admin_name.split()
                if name_parts:
                    username_base = name_parts[0]
            
            username = username_base
            
            # Asegurar que el username sea único en el schema del tenant
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
            
            user_chose_strong_password = bool(admin_password and len(admin_password) >= 8)

            # URL de login del tenant (misma lógica que la redirección del frontend)
            if settings.DEBUG:
                from urllib.parse import urlparse
                front_url_parsed = urlparse(settings.FRONT_URL)
                frontend_port = front_url_parsed.port if front_url_parsed.port else 8080
                redirect_url = f"http://{domain_name}:{frontend_port}/login/"
            else:
                redirect_url = f"https://{domain_name}/login/"

            email_sent = False
            if getattr(settings, "EMAIL_HOST_PASSWORD", ""):
                try:
                    _send_onboarding_welcome_email(
                        recipient_email=email,
                        company_name=company_name,
                        login_url=redirect_url,
                        username=username,
                        temp_password=temp_password,
                        user_chose_strong_password=user_chose_strong_password,
                        admin_name=admin_name,
                    )
                    email_sent = True
                    logger.info("Correo de onboarding enviado a %s", email)
                except Exception as exc:
                    logger.exception("No se pudo enviar el correo de onboarding: %s", exc)

            # Mostrar contraseña en JSON solo en dev o si falló el envío (solo si no eligió una fuerte)
            expose_generated_password = (
                not user_chose_strong_password
                and (settings.DEBUG or not email_sent)
            )

        cred_message = (
            "Check your email to continue."
            if email_sent
            else (
                "Save these credentials; we could not send the confirmation email."
                if not user_chose_strong_password
                else "Your password was set successfully."
            )
        )

        return Response({
            'success': True,
            'message': 'Your account was created successfully. Redirecting to your workspace…',
            'url': redirect_url,
            'email_sent': email_sent,
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
                'landing_selected_plan': tenant.landing_selected_plan,
                'temp_password': temp_password if expose_generated_password else None
            },
            'credentials': {
                'username': username,
                'password': temp_password if expose_generated_password else None,
                'password_provided': bool(admin_password),
                'message': cred_message
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error inesperado en create_tenant_onboarding: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': f'Unexpected error while creating account: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
