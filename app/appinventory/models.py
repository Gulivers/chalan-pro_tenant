from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from appinventory.helpers import convert_to_reference_unit

# Categorías de Unidades de Medida (Longitud, Peso, Volumen...)
class UnitCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(UnitCategory,  on_delete=models.PROTECT)
    reference_unit = models.BooleanField(default=False, help_text="Unidad base para conversiones")

    SIGN_CHOICES = [
        ('ref', 'Reference Unit'),
        ('*', 'Smaller than reference (*)'),
        ('/', 'Greater than reference (/)'),
    ]
    conversion_sign = models.CharField(max_length=4, choices=SIGN_CHOICES, default='ref')
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=4, default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        if self.conversion_sign == 'ref':
            existing_ref = UnitOfMeasure.objects.filter(
                category=self.category,
                conversion_sign='ref'
            )
            if self.pk:
                existing_ref = existing_ref.exclude(pk=self.pk)
            if existing_ref.exists():
                raise ValidationError(
                    "There is already a reference unit for this category.")


class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Warehouse predeterminado para nuevas transacciones")
    truck = models.OneToOneField(
        'crewsapp.Truck',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mobile_warehouse',
        help_text='Mobile warehouse for this truck (1-to-1).',
    )

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Marca predeterminada para el producto")

    def __str__(self):
        return self.name


class ProductBrandAssignment(models.Model):
    """
    Modelo intermedio para asociar productos con marcas.
    Permite agrupar imágenes y otros datos por la relación producto-marca.
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='brand_assignments')
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE, related_name='product_assignments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'brand')
        verbose_name = "Product Brand Assignment"
        verbose_name_plural = "Product Brand Assignments"

    def __str__(self):
        product_name = self.product.name if self.product else "Unknown"
        brand_name = self.brand.name if self.brand else "Unknown"
        return f"{product_name} - {brand_name}"


class Product(models.Model):
    TRACKING_QUANTITY = 'QUANTITY'
    TRACKING_SERIALIZED = 'SERIALIZED'
    TRACKING_MODE_CHOICES = [
        (TRACKING_QUANTITY, 'By quantity (stock)'),
        (TRACKING_SERIALIZED, 'Serialized (equipment/tool)'),
    ]

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(ProductCategory,  on_delete=models.PROTECT, null=True)
    brands = models.ManyToManyField(ProductBrand, related_name='products', through=ProductBrandAssignment)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_default = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    tracking_mode = models.CharField(
        max_length=20,
        choices=TRACKING_MODE_CHOICES,
        default=TRACKING_QUANTITY,
        help_text='QUANTITY = stock by quantity; SERIALIZED = track by SerializedItem units',
    )
    alert = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)


    def clean(self):
        """Valida que el producto tenga al menos una marca asignada"""
        super().clean()
        if self.pk:  # Solo validar si el objeto ya existe
            if self.brands.count() == 0:
                raise ValidationError("El producto debe tener al menos una marca asignada.")

    def get_default_brand(self):
        """Obtiene la marca predeterminada del producto"""
        default_brand = self.brands.filter(is_default=True).first()
        if default_brand:
            return default_brand
        # Si no hay marca default, retorna la primera disponible
        return self.brands.first()

    def ensure_default_brand(self):
        """Asegura que el producto tenga una marca predeterminada"""
        if self.brands.exists():
            # Si no hay marca default pero hay marcas, marcar la primera como default
            if not self.brands.filter(is_default=True).exists():
                first_brand = self.brands.first()
                first_brand.is_default = True
                first_brand.save()

    def __str__(self):
        default_brand = self.get_default_brand()
        brand_str = f" ({default_brand.name})" if default_brand else ""
        return f"{self.name}{brand_str}"

class PriceType(models.Model):
    name = models.CharField(max_length=15, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, related_name="prices", on_delete=models.CASCADE)
    price_type = models.ForeignKey(PriceType, on_delete=models.PROTECT)
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_default = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    is_purchase = models.BooleanField(default=False)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            "product",
            "price_type",
            "unit",
            "is_purchase",
            "is_sale",
            "valid_from",
            "valid_until",
        )
        
    def clean(self):
        if not self.is_purchase and not self.is_sale:
            raise ValidationError(
                "You must indicate whether this unit is for purchasing, selling, or both.")


    def __str__(self):
        return f"{self.product} | {self.price_type} | {self.unit} → ${self.price}"
    

class SerializedItem(models.Model):
    STATUS_ACTIVE = 'Active'
    STATUS_MAINTENANCE = 'Maintenance'
    STATUS_LOST = 'Lost'
    STATUS_RETIRED = 'Retired'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_MAINTENANCE, 'Maintenance'),
        (STATUS_LOST, 'Lost'),
        (STATUS_RETIRED, 'Retired'),
    ]
    CONDITION_OK = 'ok'
    CONDITION_DAMAGED = 'damaged'
    CONDITION_NEEDS_REPAIR = 'needs_repair'
    CONDITION_CHOICES = [
        (CONDITION_OK, 'OK'),
        (CONDITION_DAMAGED, 'Damaged'),
        (CONDITION_NEEDS_REPAIR, 'Needs repair'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='serialized_items')
    asset_tag = models.CharField(
        max_length=100, unique=True, help_text='Unique tag/QR identifier', null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default=CONDITION_OK)
    purchase_date = models.DateField(null=True, blank=True)
    current_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name='serialized_items'
    )
    document = models.ForeignKey(
        'apptransactions.Document',
        on_delete=models.CASCADE,
        related_name='serialized_items',
        null=True,
        blank=True,
        help_text='Documento con el que fue adquirido (ej. factura de compra).',
    )
    document_line = models.ForeignKey(
        'apptransactions.DocumentLine',
        on_delete=models.CASCADE,
        related_name='serialized_items_created',
        null=True,
        blank=True,
        help_text='Línea del documento que originó este ítem (para compras serializadas).',
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['product', 'asset_tag']
        verbose_name = 'Serialized Item'
        verbose_name_plural = 'Serialized Items'

    def __str__(self):
        return f"{self.asset_tag or '(sin tag)'} ({self.product})"


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("product", "warehouse")


class InventoryTransfer(models.Model):
    """
    Document header para transferencias entre almacenes.
    Las líneas son InventoryMovement asociados via transfer_id (par OUT/IN por producto).
    """
    STATUS_COMPLETED = 'completed'
    STATUS_REVERTED = 'reverted'

    from_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name='transfers_from'
    )
    to_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name='transfers_to'
    )
    description = models.CharField(
        max_length=255, blank=True,
        help_text='Descripción de la transferencia'
    )
    status = models.CharField(
        max_length=20,
        choices=[(STATUS_COMPLETED, 'Completed'), (STATUS_REVERTED, 'Reverted')],
        default=STATUS_COMPLETED,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inventory Transfer'
        verbose_name_plural = 'Inventory Transfers'

    def __str__(self):
        return f'{self.from_warehouse} → {self.to_warehouse} ({self.created_at.date()})'


class InventoryMovement(models.Model):
    MOVEMENT_TYPE_ENTRADA = 1
    MOVEMENT_TYPE_SALIDA = -1
    MOVEMENT_TYPE_AJUSTE = 0
    MOVEMENT_TYPE_CHOICES = [
        (1, 'Entrada'),
        (-1, 'Salida'),
        (0, 'Ajuste/Transfer (Neutral)'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    movement_type = models.SmallIntegerField(choices=MOVEMENT_TYPE_CHOICES)
    reason = models.CharField(max_length=255, blank=True, null=True)
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, null=True, blank=True)
    document = models.CharField(max_length=100, blank=True, null=True)
    line_id = models.PositiveIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    serialized_item = models.ForeignKey(
        'SerializedItem', on_delete=models.PROTECT, null=True, blank=True,
        related_name='movements',
        help_text='If set, this movement tracks one physical unit; quantity must be 1.',
    )
    transfer = models.ForeignKey(
        'InventoryTransfer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='movements',
        help_text='Transferencia entre almacenes a la que pertenece este movimiento.',
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        if self.serialized_item:
            return f"{self.get_movement_type_display()} - {self.serialized_item.asset_tag} ({self.product}) en {self.warehouse}"
        return f"{self.get_movement_type_display()} - {self.product} ({self.quantity}) en {self.warehouse}"

    def get_converted_quantity(self):
        result = convert_to_reference_unit(self.product, self.unit, self.quantity)
        return result

    def clean(self):
        super().clean()
        if self.transfer_id and (not self.reason or not str(self.reason).strip()):
            raise ValidationError(
                'El campo reason no puede quedar vacío para movimientos de transferencia.'
            )
        if self.serialized_item_id:
            item = self.serialized_item
            if self.product_id != item.product_id:
                raise ValidationError(
                    'Movement product must match serialized item product.'
                )
            if self.quantity != Decimal('1'):
                raise ValidationError(
                    'Quantity must be 1 when moving a serialized item.'
                )
            if not item.current_warehouse_id:
                raise ValidationError(
                    'Serialized item must have a current_warehouse.'
                )
            if self.movement_type == self.MOVEMENT_TYPE_SALIDA:
                if item.current_warehouse_id != self.warehouse_id:
                    raise ValidationError(
                        'Salida: warehouse must match serialized item current_warehouse.'
                    )

    def save(self, *args, **kwargs):
        """
        Saves the movement. If serialized_item is set: validates product/quantity=1,
        does NOT update Stock, and on Entrada (1) updates serialized_item.current_warehouse.
        """
        if not self.product or not self.warehouse:
            raise ValueError("No se puede guardar InventoryMovement sin producto o almacén.")
        if self.quantity is None:
            raise ValueError("Quantity no puede ser None")

        if self.serialized_item_id:
            self.full_clean()
            # Save first
            super().save(*args, **kwargs)
            # Update SerializedItem location when it's an arrival (Entrada o Ajuste/Transfer IN)
            if self.movement_type in (self.MOVEMENT_TYPE_ENTRADA, self.MOVEMENT_TYPE_AJUSTE):
                item = SerializedItem.objects.get(pk=self.serialized_item_id)
                if item.current_warehouse_id != self.warehouse_id:
                    item.current_warehouse = self.warehouse
                    item.save(update_fields=['current_warehouse'])
            return

        # Non-serialized: convert and update stock
        try:
            converted_qty = self.get_converted_quantity() if self.unit else self.quantity
        except Exception as e:
            print(f"⚠️ Error en conversión, usando cantidad original: {e}")
            converted_qty = self.quantity
        if converted_qty is None:
            raise ValueError("Error: cantidad convertida terminó en None")

        super().save(*args, **kwargs)

        stock, _ = Stock.objects.get_or_create(
            product=self.product,
            warehouse=self.warehouse,
            defaults={'quantity': Decimal('0.00')}
        )
        stock.quantity += converted_qty * self.movement_type
        stock.save()

    def delete(self, *args, **kwargs):
        """Reverts stock only for non-serialized movements."""
        if self.serialized_item_id:
            super().delete(*args, **kwargs)
            return
        converted_qty = self.get_converted_quantity()
        stock, _ = Stock.objects.get_or_create(
            product=self.product,
            warehouse=self.warehouse,
            defaults={'quantity': Decimal('0.00')}
        )
        stock.quantity -= converted_qty * self.movement_type
        stock.save()
        super().delete(*args, **kwargs)


def product_image_upload_to(instance, filename):
    """
    Función para determinar la ruta de subida de imágenes de productos.
    Estructura: products/{product_id}/{brand_id}/{filename}
    """
    import os
    from django.utils import timezone
    
    # Obtener extensión del archivo
    ext = os.path.splitext(filename)[1]
    # Generar nombre único basado en timestamp
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.splitext(filename)[0]
    # Limpiar nombre base (remover caracteres especiales)
    base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
    base_name = base_name.replace(' ', '_')
    
    # Construir ruta: products/{product_id}/{brand_id}/{timestamp}_{base_name}{ext}
    product_id = instance.assignment.product.id if instance.assignment and instance.assignment.product else 'unknown'
    brand_id = instance.assignment.brand.id if instance.assignment and instance.assignment.brand else 'unknown'
    
    return f'products/{product_id}/{brand_id}/{timestamp}_{base_name}{ext}'


class ProductImage(models.Model):
    """
    Modelo para almacenar imágenes de productos asociadas a marcas específicas a través de la relación de marca.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', null=True)
    assignment = models.ForeignKey(ProductBrandAssignment, on_delete=models.CASCADE, related_name='images', null=True)
    image = models.ImageField(upload_to=product_image_upload_to)
    is_primary = models.BooleanField(
        default=False,
        help_text="Indica si esta es la imagen principal para esta marca del producto"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    description = models.CharField(max_length=255, blank=True, help_text="Descripción opcional de la imagen")

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']
        indexes = [
            models.Index(fields=['assignment']),
            models.Index(fields=['assignment', 'is_primary']),
        ]
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def clean(self):
        """Valida que la asignación pertenezca al producto"""
        super().clean()
        if hasattr(self, 'assignment') and hasattr(self, 'product'):
            if self.assignment.product != self.product:
                raise ValidationError(
                    f"La asignación de marca '{self.assignment}' no pertenece al producto '{self.product.name}'."
                )

    def save(self, *args, **kwargs):
        """Override save para aplicar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Si se marca como principal, desmarcar otras principales de la misma asignación
        if self.is_primary:
            ProductImage.objects.filter(
                assignment=self.assignment,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

    def __str__(self):
        product_name = self.assignment.product.name if self.assignment and self.assignment.product else "Unknown"
        brand_name = self.assignment.brand.name if self.assignment and self.assignment.brand else "Unknown"
        primary_tag = " [PRIMARY]" if self.is_primary else ""
        return f"{product_name} - {brand_name}{primary_tag}"
