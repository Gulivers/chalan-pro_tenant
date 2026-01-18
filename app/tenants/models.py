"""
Modelo Tenant para django-tenants
Cada tenant tiene su propio schema en PostgreSQL
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django_tenants.models import TenantMixin, DomainMixin
import re


class Tenant(TenantMixin):
    """
    Modelo principal del tenant.
    Cada instancia representa un cliente con su propio schema.
    """
    # Nombre del tenant (ej: "Phoenix Electric")
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Cliente")
    
    # Nombre del schema (ej: "phoenix")
    # django-tenants usa este campo para crear el schema
    schema_name = models.CharField(max_length=63, unique=True, db_index=True, verbose_name="Schema Name", blank=True)
    
    # Tenant ID único
    tenant_id = models.CharField(max_length=100, unique=True, verbose_name="Tenant ID", blank=True)
    
    # Información de contacto
    email = models.EmailField(max_length=255, verbose_name="Correo Electrónico", blank=True, null=True)
    
    # Tipo de cliente (para personalización)
    CLIENT_TYPE_CHOICES = [
        ('electric', 'Electric'),
        ('air_conditioning', 'Air Conditioning'),
        ('solar', 'Solar'),
        ('plumbing', 'Plumbing'),
        ('hvac', 'HVAC'),
        ('general', 'General'),
    ]
    client_type = models.CharField(
        max_length=50,
        choices=CLIENT_TYPE_CHOICES,
        default='general',
        verbose_name="Tipo de Cliente"
    )
    
    # Logo del cliente
    logo = models.ImageField(
        upload_to='tenant_logos/',
        blank=True,
        null=True,
        verbose_name="Logo del Cliente"
    )
    
    # Dirección de la empresa (opcional)
    address = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Dirección"
    )
    
    # Preferencias de módulos activados (JSON array)
    # Ejemplo: ["inventory", "contracts", "schedule"]
    preferences = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Módulos Activados",
        help_text="Lista de módulos activados para este tenant"
    )
    
    # Campos estratégicos del onboarding
    MONTHLY_OPERATIONS_CHOICES = [
        ('0-10', '0–10 homes per month'),
        ('11-25', '11–25 homes per month'),
        ('26-50', '26–50 homes per month'),
        ('51-100', '51–100 homes per month'),
        ('100+', '100+ homes per month'),
    ]
    monthly_operations = models.CharField(
        max_length=10,
        choices=MONTHLY_OPERATIONS_CHOICES,
        blank=True,
        null=True,
        verbose_name="Monthly Operations Volume",
        help_text="How many projects or homes the company handles each month"
    )
    
    crew_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Number of Active Crews",
        help_text="How many active crews the company manages",
        validators=[MinValueValidator(1)]
    )
    
    RECOMMENDED_PLAN_CHOICES = [
        ('Starter', 'Starter'),
        ('Professional', 'Professional'),
        ('Enterprise', 'Enterprise'),
    ]
    recommended_plan = models.CharField(
        max_length=20,
        choices=RECOMMENDED_PLAN_CHOICES,
        blank=True,
        null=True,
        verbose_name="Recommended Plan",
        help_text="Recommended plan based on crew count"
    )
    
    # Configuraciones del tenant
    paid_until = models.DateField(null=True, blank=True, verbose_name="Pagado hasta")
    on_trial = models.BooleanField(default=True, verbose_name="En período de prueba")
    
    # Metadata adicional
    created_on = models.DateField(auto_now_add=True, verbose_name="Creado el")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    # Flag para controlar si se han importado los datos maestros de inventario
    seed_inventory_done = models.BooleanField(
        default=False,
        verbose_name="Datos Maestros de Inventario Importados",
        help_text="Indica si los datos maestros de inventario han sido importados para este tenant"
    )
    
    # Configuración de django-tenants
    auto_create_schema = True
    auto_drop_schema = False
    
    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ['name']
        # IMPORTANTE: django-tenants requiere que este modelo esté en el schema 'public'
        # No agregar 'tenant' aquí
    
    def clean(self):
        """Valida el schema_name según las restricciones de PostgreSQL"""
        super().clean()
        
        # Si no hay schema_name, se generará en save()
        if self.schema_name:
            # Validar formato: solo letras minúsculas, números y guiones bajos
            # PostgreSQL permite guiones bajos sin necesidad de comillas
            if not re.match(r'^[a-z][a-z0-9_]*$', self.schema_name):
                raise ValidationError({
                    'schema_name': 'El schema name solo puede contener letras minúsculas, números y guiones bajos, y debe comenzar con letra.'
                })
            
            # Validar longitud máxima
            if len(self.schema_name) > 63:
                raise ValidationError({
                    'schema_name': 'El schema name no puede exceder 63 caracteres.'
                })
    
    def _generate_schema_name(self):
        """
        Genera un nombre de schema válido basado en el nombre del tenant.
        Usa guiones bajos (_) para el schema_name, que es el formato estándar en PostgreSQL.
        """
        if not self.name:
            return None
        
        # Convertir a slug (slugify usa guiones por defecto)
        base_name = slugify(self.name)
        
        # Reemplazar guiones por guiones bajos para el schema_name
        base_name = base_name.replace('-', '_')
        
        # Limpiar: solo letras minúsculas, números y guiones bajos
        base_name = re.sub(r'[^a-z0-9_]', '', base_name.lower())
        
        # Si está vacío o comienza con número, agregar prefijo
        if not base_name or base_name[0].isdigit():
            base_name = f"tenant_{base_name}" if base_name else "tenant_unnamed"
        
        # Limitar longitud a 63 caracteres (máximo de PostgreSQL)
        max_len = 50  # Dejar espacio para "_9999"
        if len(base_name) > max_len:
            base_name = base_name[:max_len]
        
        schema_name = base_name
        
        # Verificar unicidad y agregar número si es necesario
        counter = 1
        original_schema = schema_name
        while Tenant.objects.filter(schema_name=schema_name).exclude(pk=self.pk if self.pk else None).exists():
            counter_str = f"_{counter}"
            max_base_len = 63 - len(counter_str)
            schema_name = f"{original_schema[:max_base_len]}{counter_str}"
            counter += 1
            if counter > 9999:
                raise ValidationError("No se pudo generar un schema_name único. Intenta con un nombre diferente.")
        
        return schema_name
    
    def schema_to_subdomain(self):
        """
        Convierte el schema_name a un subdominio válido para DNS.
        Los guiones bajos (_) del schema_name se convierten a guiones (-) para el subdominio,
        ya que los guiones bajos no son válidos en nombres de dominio DNS según RFC 1034/1035.
        
        Ejemplo:
            schema_name: 'globo_dyned2' -> subdomain: 'globo-dyned2'
            schema_name: 'phoenix' -> subdomain: 'phoenix'
        """
        if not self.schema_name:
            return None
        # Convertir guiones bajos a guiones para el subdominio DNS
        return self.schema_name.replace('_', '-')
    
    def _generate_tenant_id(self):
        """Genera un tenant_id único basado en el nombre del tenant"""
        if not self.name:
            return None
        
        # Usar slugify y convertir guiones a guiones bajos para consistencia con schema_name
        base_id = slugify(self.name).replace('-', '_')[:30]
        
        if base_id and base_id[0].isdigit():
            base_id = f"t_{base_id}"
        elif not base_id:
            base_id = "tenant_unnamed"
        
        tenant_id = f"{base_id}_001"
        
        # Verificar unicidad
        counter = 1
        original_id = tenant_id
        while Tenant.objects.filter(tenant_id=tenant_id).exclude(pk=self.pk if self.pk else None).exists():
            tenant_id = f"{original_id.rsplit('_', 1)[0]}_{counter:03d}"
            counter += 1
            if counter > 9999:
                raise ValidationError("No se pudo generar un tenant_id único. Intenta con un nombre diferente.")
        
        return tenant_id
    
    def save(self, *args, **kwargs):
        """Genera automáticamente schema_name y tenant_id si no están proporcionados"""
        # Generar schema_name si está vacío
        if not self.schema_name:
            self.schema_name = self._generate_schema_name()
        
        # Generar tenant_id si está vacío
        if not self.tenant_id:
            self.tenant_id = self._generate_tenant_id()
        
        # Validar antes de guardar
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.schema_name})"
    
    def get_logo_url(self):
        """Retorna la URL del logo o None"""
        if self.logo:
            return self.logo.url
        return None


class Domain(DomainMixin):
    """
    Modelo para los dominios/subdominios de cada tenant.
    Ejemplo: phoenix.chalan-pro.net -> tenant "phoenix"
    """
    pass
    
    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"
