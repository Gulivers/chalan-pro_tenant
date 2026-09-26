# App: transactions (documentos, detalles, clientes, proveedores)

from django.db import models
from django.db.models import ProtectedError, UniqueConstraint, Q
from django.db.models.functions import Lower
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
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

class DocumentTypeQuerySet(models.QuerySet):
    def _protected_in_queryset(self):
        return self.filter(type_code__in=DocumentType.PROTECTED_TYPE_CODES)

    def update(self, **kwargs):
        protected = self._protected_in_queryset()
        if protected.exists():
            raise ValidationError(
                'The Material Request document type is required by the system and cannot be edited.'
            )
        return super().update(**kwargs)

    def bulk_update(self, objs, fields, batch_size=None):
        pks = [obj.pk for obj in objs if getattr(obj, 'pk', None)]
        if DocumentType.objects.filter(
            pk__in=pks,
            type_code__in=DocumentType.PROTECTED_TYPE_CODES,
        ).exists():
            raise ValidationError(
                'The Material Request document type is required by the system and cannot be edited.'
            )
        return super().bulk_update(objs, fields, batch_size=batch_size)

    def delete(self):
        protected = self._protected_in_queryset()
        if protected.exists():
            raise ProtectedError(
                'Material Request document types cannot be deleted.',
                set(protected),
            )
        return super().delete()


class DocumentType(models.Model):
    # Tipos que el Material Request necesita tal cual fueron sembrados.
    PROTECTED_TYPE_CODES = frozenset({'MR'})
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
    # MR y otros pedidos operativos pueden ir sin precio. Ventas y compras siguen exigiéndolo.
    prices_required = models.BooleanField(default=True)
    allow_negative_sales = models.BooleanField(default=False)  # Permitir ventas sin stock
    # Si serialized_items es True,  (ej. GRN), se abre (AssetTagAssignmentModal)
    # cuando el documento tiene serialized_items y su tipo tiene este flag activo.
    creates_serialized_items = models.BooleanField(
        default=False,
        help_text="Document type that creates/registers serialized items; opens asset tag assignment modal when document has serialized items.",
    )
    stock_movement = models.SmallIntegerField(
        choices=[(1, "+1 Entrada"), (-1, "-1 Salida"), (0, "0 Neutro")],
        default=0
    )
    # Level-1 Assistant / analytics intentions (tenant-configured; independent of type_code).
    counts_as_net_invoiced_spend = models.BooleanField(
        default=False,
        help_text="Include this type in JobRhythm Assistant Net invoiced spending (not PO/GRN/returns).",
    )
    counts_as_job_material_issue = models.BooleanField(
        default=False,
        help_text="Include this type as job/house material issue (e.g. picking to a Work Account).",
    )
    counts_as_purchase_return = models.BooleanField(
        default=False,
        help_text="Include this type as purchase returns (not mixed into net invoiced spending).",
    )
    is_active = models.BooleanField(default=True)

    objects = DocumentTypeQuerySet.as_manager()

    class Meta:
        ordering = ["type_code"]
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"

    def __str__(self):
        return f"{self.type_code} - {self.description}"

    def clean(self):
        super().clean()
        if self.counts_as_net_invoiced_spend and self.counts_as_purchase_return:
            raise ValidationError({
                'counts_as_purchase_return': (
                    'A document type cannot count as both Net invoiced spending '
                    'and Purchase return.'
                ),
            })
        self._reject_protected_edits()

    def save(self, *args, **kwargs):
        self._reject_protected_edits()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.type_code in self.PROTECTED_TYPE_CODES:
            raise ProtectedError(
                'The Material Request document type cannot be deleted.',
                {self},
            )
        return super().delete(*args, **kwargs)

    def _reject_protected_edits(self):
        if not self.pk:
            return
        previous = DocumentType.objects.filter(pk=self.pk).first()
        if previous is None or previous.type_code not in self.PROTECTED_TYPE_CODES:
            return
        for field in self._meta.concrete_fields:
            if field.primary_key:
                continue
            if getattr(self, field.attname) != getattr(previous, field.attname):
                raise ValidationError(
                    'The Material Request document type is required by the system and cannot be edited.'
                )
    
    
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
                raise ValidationError({"title": "A WorkAccount with this title already exists (case-insensitive)."})

    def get_deletion_blockers(self):
        """
        Return related records that prevent deleting this work account.
        Covers schedule chat/notes/folder plus contracts and transactions.
        """
        blockers = []

        note = self.event_notes.first()
        if note and (note.notes or "").strip():
            blockers.append(note)

        chat = self.work_account_chat_messages.first()
        if chat:
            blockers.append(chat)

        image = self.images.first()
        if image:
            blockers.append(image)

        contract = self.contracts.first()
        if contract:
            blockers.append(contract)

        document = self.documents.first()
        if document:
            blockers.append(document)

        event = self.events.first()
        if event:
            blockers.append(event)

        draft = self.event_drafts.first()
        if draft:
            blockers.append(draft)

        return blockers

    def raise_if_deletion_blocked(self):
        blockers = self.get_deletion_blockers()
        if blockers:
            raise ProtectedError(
                "Cannot delete work account while related records exist.",
                set(blockers),
            )

class Document(models.Model):
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    # Writable from API/UI; frontend defaults to today on create and keeps stored date on edit.
    date = models.DateField(default=timezone.localdate)
    # Contraparte comercial (para reglas de venta/compra y cobranza)
    builder = models.ForeignKey(Builder, on_delete=models.PROTECT, null=True, blank=True)
    # Identidad de la obra (builder+job+house_model+lot/address encapsulados)
    work_account = models.ForeignKey('apptransactions.WorkAccount', on_delete=models.PROTECT, null=True, blank=True, related_name='documents')
    # Orden del día (evento de agenda). La fase es la categoría del crew, no un estado del documento.
    work_order = models.ForeignKey(
        'appschedule.Event',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='documents',
    )
    # Número legible por tipo, p. ej. MR-000184. Vacío en documentos anteriores a la secuencia.
    document_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
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
        if self.document_number:
            return self.document_number
        if getattr(self, "document_type", None) and self.date:
            return f"{self.document_type.type_code} - {self.date}"
        return "Document"

    def save(self, *args, **kwargs):
        # Si viene work_account y falta builder, auto-sincroniza builder desde work_account.builder
        if self.work_account_id and not self.builder_id:
            try:
                # Usar work_account_id para evitar acceder al objeto si no está cargado
                from apptransactions.models import WorkAccount
                work_account = WorkAccount.objects.get(id=self.work_account_id)
                wa_builder = getattr(work_account, 'builder', None)
                if wa_builder:
                    self.builder_id = wa_builder.id if hasattr(wa_builder, 'id') else wa_builder
            except WorkAccount.DoesNotExist:
                # Si el work_account no existe, continuar sin builder
                pass
            except Exception as e:
                # Log el error pero continuar
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error getting builder from work_account: {e}")
        super().save(*args, **kwargs)

class DocumentLine(models.Model):
    PRICING_MARKUP = "MARKUP"
    PRICING_MARGIN = "MARGIN"
    PRICING_MANUAL = "MANUAL"
    LINE_PRICING_RULE_CHOICES = [
        (PRICING_MARKUP, "Markup %"),
        (PRICING_MARGIN, "Margin %"),
        (PRICING_MANUAL, "Manual unit price"),
    ]

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
    # Snapshot at save time (historical pricing rule; Price Type may change later)
    pricing_rule = models.CharField(
        max_length=10,
        choices=LINE_PRICING_RULE_CHOICES,
        null=True,
        blank=True,
    )
    margin_percent = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Snapshot: markup or margin % used when the line was saved.",
    )

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


class DocumentSequence(models.Model):
    """Contador por tipo de documento. El número visible es {type_code}-{n:06d}."""

    document_type = models.OneToOneField(
        DocumentType,
        on_delete=models.PROTECT,
        related_name='sequence',
    )
    last_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.document_type.type_code} @{self.last_number}"


class DocumentStatus(models.Model):
    """
    Estado de un tipo de documento.

    En el MVP, sequence define un flujo lineal: solo se puede pasar al
    siguiente número de secuencia del mismo tipo. Si más adelante un tipo
    necesita estados alternativos o ramificaciones, esto se sustituye por
    reglas explícitas de transición sin rehacer DocumentTracking.
    """

    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name='statuses',
    )
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=80)
    sequence = models.PositiveIntegerField()
    is_initial = models.BooleanField(default=False)
    is_terminal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['document_type', 'sequence']
        constraints = [
            UniqueConstraint(
                fields=['document_type', 'code'],
                name='uniq_document_status_type_code',
            ),
            UniqueConstraint(
                fields=['document_type', 'sequence'],
                name='uniq_document_status_type_sequence',
            ),
        ]

    def __str__(self):
        return f"{self.document_type.type_code}:{self.code}"


class DocumentTracking(models.Model):
    """Estado actual de un documento. Un registro por documento."""

    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='tracking',
    )
    current_status = models.ForeignKey(
        DocumentStatus,
        on_delete=models.PROTECT,
        related_name='current_documents',
    )
    status_changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_tracking_changes',
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.document} → {self.current_status.code}"


class DocumentTrackingHistory(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='tracking_history',
    )
    from_status = models.ForeignKey(
        DocumentStatus,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='history_from',
    )
    to_status = models.ForeignKey(
        DocumentStatus,
        on_delete=models.PROTECT,
        related_name='history_to',
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_tracking_history',
    )
    changed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['changed_at', 'id']

    def __str__(self):
        origin = self.from_status.code if self.from_status_id else '—'
        return f"{self.document} {origin} → {self.to_status.code}"


class DocumentLink(models.Model):
    """
    Relación entre documentos, sin automatizar el alta del destino.

    Un Material Request podrá apuntar después a un PK (picking) o a un PO
    (purchase_order). Esos documentos no son estados del MR.
    """

    RELATION_PICKING = 'picking'
    RELATION_PURCHASE_ORDER = 'purchase_order'
    RELATION_CHOICES = [
        (RELATION_PICKING, 'Picking'),
        (RELATION_PURCHASE_ORDER, 'Purchase order'),
    ]

    source = models.ForeignKey(
        Document,
        on_delete=models.PROTECT,
        related_name='outgoing_links',
    )
    target = models.ForeignKey(
        Document,
        on_delete=models.PROTECT,
        related_name='incoming_links',
    )
    relation = models.CharField(max_length=32, choices=RELATION_CHOICES)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_links_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['source', 'target', 'relation'],
                name='uniq_document_link_source_target_relation',
            ),
        ]

    def __str__(self):
        return f"{self.source_id} -{self.relation}-> {self.target_id}"


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
