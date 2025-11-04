# App: transactions (documentos, detalles, clientes, proveedores)

from django.db import models
from django.db.models import UniqueConstraint, Q
from django.db.models.functions import Lower
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from appinventory.models import Product, UnitOfMeasure, Warehouse, PriceType, ProductBrand
from ctrctsapp.models import Builder, Job, HouseModel

User = get_user_model()

class PartyType(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)  # optional
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Party Type"
        verbose_name_plural = "Party Types"
        ordering = ["-id"]

    def __str__(self):
        return self.name

class PartyCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Party Category"
        verbose_name_plural = "Party Categories"
        ordering = ["-id"]

    def __str__(self):
        return self.name

class Party(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rfc = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=100, blank=True)
    floor_office = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    types = models.ManyToManyField(PartyType)
    category = models.ForeignKey(PartyCategory, on_delete=models.SET_NULL, null=True)
    default_price_type = models.ForeignKey(PriceType, on_delete=models.SET_NULL, null=True, blank=True)
    customer_rank = models.PositiveIntegerField(default=0)
    supplier_rank = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_customer(self):
        return self.customer_rank > 0

    def is_supplier(self):
        return self.supplier_rank > 0

    def is_both(self):
        return self.customer_rank > 0 and self.supplier_rank > 0

    def __str__(self):
        return self.name

class DocumentType(models.Model):
    type_code = models.CharField(max_length=20, unique=True) # Ej: INCOME, ADJUSTMENT_OUT, PICK
    description = models.CharField(max_length=255)
    affects_physical = models.BooleanField(default=True)  # INVFIS
    affects_logical = models.BooleanField(default=True)   # INVLOG
    affects_accounting = models.BooleanField(default=False)  # INVCON
    is_taxable = models.BooleanField(default=False)       # IVA
    is_purchase = models.BooleanField(default=False)      # LIBCOM
    is_sales = models.BooleanField(default=False)         # LIBVTA
    warehouse_required = models.BooleanField(default=True)  # ALMACE
    is_operational = models.BooleanField(default=False)   # Requiere Work Account
    allow_negative_sales = models.BooleanField(default=False)  # Permitir ventas sin stock
    stock_movement = models.SmallIntegerField(
        choices=[(1, "+1 Entrada"), (-1, "-1 Salida"), (0, "0 Neutro")],
        default=0
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["type_code"]
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"

    def __str__(self):
        return f"{self.type_code} - {self.description}"
    
    
JOB_FK = 'ctrctsapp.Job'
HOUSEMODEL_FK = 'ctrctsapp.HouseModel'
BUILDER_FK = 'ctrctsapp.Builder'

class WorkAccount(models.Model):
    """
    Identidad transversal (tipo 'paciente') para programaciones, contratos y transacciones.
    Permite seleccionar por 'title' y mostrar builder/job/lot/address como contexto.
    """
    # Identificador amigable y único (case-insensitive)
    title = models.CharField(max_length=200, unique=False)
    builder = models.ForeignKey(BUILDER_FK, on_delete=models.PROTECT, related_name='work_accounts')
    # Datos opcionales (si tus modelos existen en otra app, dejamos FK por string)
    job = models.ForeignKey(JOB_FK, on_delete=models.PROTECT, null=True, blank=True)
    house_model = models.ForeignKey(HOUSEMODEL_FK, on_delete=models.PROTECT, null=True, blank=True)
    # Contexto del sitio
    lot = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    # Preferencias por cuenta
    default_price_type = models.ForeignKey(PriceType,  on_delete=models.PROTECT, null=True, blank=True)
    # Meta
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Work Account"
        verbose_name_plural = "Work Accounts"
        constraints = [
            # Unicidad de title (CI) entre activos
            UniqueConstraint(Lower('title'), condition=Q(is_active=True), name='uniq_workaccount_title_ci_active'),
            # Unicidad por lot cuando lot no es vacío
            UniqueConstraint(
                'builder', 'job', Lower('lot'),
                condition=Q(is_active=True) & ~Q(lot=""),
                name='uniq_workaccount_builder_job_lot_ci_active'
            ),
            # Si no hay lot, usar address para la unicidad (CI)
            UniqueConstraint(
                'builder', 'job', Lower('address'),
                condition=Q(is_active=True) & Q(lot="") & ~Q(address=""),
                name='uniq_workaccount_builder_job_address_ci_active_when_no_lot'
            ),
        ]
        indexes = [
            models.Index(Lower('title'), name='idx_workaccount_title_ci'),
        ]

    def __str__(self):
        parts = [self.title]
        # Contexto para vistas/admin
        ctx = []
        if self.builder_id:
            try:
                ctx.append(self.builder.name)
            except Exception:
                pass
        if self.job_id:
            try:
                ctx.append(getattr(self.job, "name", ""))
            except Exception:
                pass
        if self.house_model_id:
            try:
                ctx.append(getattr(self.house_model, "name", ""))
            except Exception:
                pass
        if self.lot:
            ctx.append(f"Lot {self.lot}")
        if ctx:
            parts.append("• " + " • ".join([c for c in ctx if c]))
        return " ".join(parts).strip()
    
    @property
    def party(self):
        """Acceso conveniente al Party (empresa) a través del Builder."""
        try:
            return self.builder.party
        except Exception:
            return None

    def clean(self):
        # Validación friendly (además del constraint en DB): title único (CI) cuando is_active=True
        if self.is_active and self.title:
            existing = WorkAccount.objects.filter(is_active=True).annotate(
                title_ci=Lower("title")
            ).filter(title_ci=self.title.lower())
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError({"title": "A WorkAccount with this title already exists (case-insensitive)."})

class Document(models.Model):
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    # Contraparte comercial (para reglas de venta/compra y cobranza)
    builder = models.ForeignKey(Builder, on_delete=models.PROTECT, null=True, blank=True)
    # Identidad de la obra (builder+job+house_model+lot/address encapsulados)
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def clean(self):
        if not self.document_type:
            return
        
        # Para documentos operacionales, no validar Builder porque se obtiene del Work Account
        if self.document_type.is_operational:
            return
            
        # Solo validar Builder para documentos no operacionales
        if self.document_type.is_sales and (not self.builder or not self.builder.is_customer()):
            raise ValidationError("Selected builder is not a customer.")
        if self.document_type.is_purchase and (not self.builder or not self.builder.is_supplier()):
            raise ValidationError("Selected builder is not a supplier.")

    def calculate_totals(self):
        total = 0
        total_discount = 0
        for line in self.lines.all():
            total += line.final_price or 0
            discount = line.unit_price * line.quantity * (line.discount_percentage / 100)
            total_discount += discount
        self.total_amount = total
        self.total_discount = total_discount
        self.save()

    def __str__(self):
        if getattr(self, "document_type", None) and self.date:
            return f"{self.document_type.type_code} - {self.date}"
        return "Document"

    def save(self, *args, **kwargs):
        # Si viene work_account y falta builder, auto-sincroniza builder desde work_account.builder
        if self.work_account and not self.builder_id:
            wa_builder = getattr(self.work_account, 'builder', None)
            if wa_builder and wa_builder.id:
                self.builder_id = wa_builder.id
        super().save(*args, **kwargs)

class DocumentLine(models.Model):
    document = models.ForeignKey(Document, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True)
    price_type = models.ForeignKey(PriceType, on_delete=models.PROTECT, null=True, blank=True)
    brand = models.ForeignKey(ProductBrand, on_delete=models.PROTECT, null=True, blank=True)  # Marca específica usada en esta línea, útil para trazabilidad

    def clean(self):
        errors = {}
        if self.quantity is None:
            errors['quantity'] = 'La cantidad no puede estar vacía.'
        if self.product is None:
            errors['product'] = 'Debe seleccionar un producto.'
        # si el tipo de documento requiere almacén, la línea debe tener warehouse
        doc = getattr(self, "document", None)
        if doc and doc.document_type and doc.document_type.warehouse_required:
            if not self.warehouse:
                errors['warehouse'] = 'Este tipo de documento requiere almacén en cada línea.'
        if errors:
            raise ValidationError(errors)
        
    def save(self, *args, **kwargs):
        print(" 1 🧼 apptransactions\models.py -> DocumentLine: def save(self, *args, **kwargs).")
        
        discount = self.discount_percentage / 100
        adjusted_price = self.unit_price

        # El precio se mantiene tal cual viene del formulario (por unidad seleccionada)
        # No se aplica conversión aquí — solo se usa la unidad seleccionada

        self.final_price = adjusted_price * self.quantity * (1 - discount)

        # Si el usuario no seleccionó el tipo de precio, se usa el default del cliente o proveedor.
        if not self.price_type and self.document and self.document.builder and self.document.builder.default_price_type:
            self.price_type = self.document.builder.default_price_type

        super().save(*args, **kwargs)

        # Recalcular totales del documento
        if self.document:
            self.document.calculate_totals()

    def __str__(self):
        unit_code = self.unit.code if self.unit else "unit"
        return f"{self.product.name} x {self.quantity} {unit_code}" if self.product else "Detail"


class TransactionFavorite(models.Model):
    """
    Modelo para guardar transacciones como favoritos para reutilización.
    Permite a los usuarios guardar documentos completos con sus líneas para importarlos posteriormente.
    """
    name = models.CharField(max_length=200, help_text="Nombre descriptivo del favorito")
    description = models.TextField(blank=True, help_text="Descripción opcional del favorito")
    
    # Datos completos de la transacción en formato JSON
    document_data = models.JSONField(help_text="Datos del documento (tipo, builder, work_account, etc.)")
    lines_data = models.JSONField(help_text="Array de líneas de la transacción")
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_favorites')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction Favorite"
        verbose_name_plural = "Transaction Favorites"
        constraints = [
            # Unicidad de nombre por usuario (case-insensitive)
            models.UniqueConstraint(
                fields=['name', 'created_by'],
                condition=models.Q(is_active=True),
                name='unique_favorite_name_per_user'
            )
        ]
        indexes = [
            models.Index(fields=['created_by', 'is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.created_by.username})"
    
    def clean(self):
        """Validación personalizada para el modelo"""
        if self.is_active and self.name:
            # Verificar unicidad de nombre por usuario (case-insensitive)
            existing = TransactionFavorite.objects.filter(
                name__iexact=self.name,
                created_by=self.created_by,
                is_active=True
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    'name': 'Ya existe un favorito con este nombre para tu usuario.'
                })
    
    def get_display_name(self):
        """Retorna el nombre de visualización con contexto"""
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"
