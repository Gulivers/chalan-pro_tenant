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


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(ProductCategory,  on_delete=models.PROTECT, null=True)
    brands = models.ManyToManyField(ProductBrand, related_name='products')
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_default = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


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
        unique_together = ("product", "price_type", "unit", "valid_from", "valid_until")
        
    def clean(self):
        if not self.is_purchase and not self.is_sale:
            raise ValidationError(
                "You must indicate whether this unit is for purchasing, selling, or both.")


    def __str__(self):
        return f"{self.product} | {self.price_type} | {self.unit} → ${self.price}"
    

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("product", "warehouse")


class InventoryMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        (1, 'Entrada'),
        (-1, 'Salida'),
        (0, 'Ajuste')
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

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product} ({self.quantity}) en {self.warehouse}"

    def get_converted_quantity(self):
        result = convert_to_reference_unit(self.product, self.unit, self.quantity)
        return result

    def save(self, *args, **kwargs):
        """
        Guarda el movimiento de inventario y actualiza el stock automáticamente.
        
        Mejoras v2.0:
        - Mantiene quantity como cantidad original (sin convertir)
        - Usa cantidad convertida solo para actualizar el stock
        - Evita el problema de doble conversión
        """
        if not self.product or not self.warehouse:
            raise ValueError("No se puede guardar InventoryMovement sin producto o almacén.")

        # Verificar que quantity no sea None antes de la conversión
        if self.quantity is None:
            raise ValueError("Quantity no puede ser None")

        # Calcular cantidad convertida para actualizar el stock
        # ⚠️ NO sobrescribir self.quantity - mantener la cantidad original
        try:
            converted_qty = self.get_converted_quantity() if self.unit else self.quantity
        except Exception as e:
            print(f"⚠️ Error en conversión, usando cantidad original: {e}")
            converted_qty = self.quantity

        if converted_qty is None:
            raise ValueError("Error: cantidad convertida terminó en None")

        print(f"📦 Guardando movimiento: quantity={self.quantity}, converted={converted_qty} (tipo: {type(converted_qty)})")

        # Guardar el movimiento en la base de datos
        # Nota: self.quantity se mantiene como cantidad original
        try:
            is_new = not self.pk
            super().save(*args, **kwargs)
            print(f"✅ InventoryMovement guardado exitosamente con ID: {self.id}")
        except Exception as e:
            print(f"❌ ERROR al guardar InventoryMovement: {e}")
            raise

        # Ajustar el stock usando la cantidad convertida
        stock, _ = Stock.objects.get_or_create(
            product=self.product, 
            warehouse=self.warehouse,
            defaults={'quantity': Decimal('0.00')}
        )
        old_qty = stock.quantity
        
        # Usar la cantidad convertida para actualizar el stock
        stock.quantity += converted_qty * self.movement_type
        stock.save()

        print(f"📊 Stock actualizado: {old_qty} → {stock.quantity} (producto: {self.product}, almacén: {self.warehouse})")

    def delete(self, *args, **kwargs):
        """
        Elimina el movimiento de inventario y revierte su efecto en el stock.
        """
        from .models import Stock
        
        # Calcular cantidad convertida
        converted_qty = self.get_converted_quantity()
        
        # Revertir el efecto en el stock
        stock, _ = Stock.objects.get_or_create(
            product=self.product, 
            warehouse=self.warehouse,
            defaults={'quantity': Decimal('0.00')}
        )
        old_qty = stock.quantity
        stock.quantity -= converted_qty * self.movement_type
        stock.save()
        
        print(f"🗑️ Movimiento eliminado - Stock revertido: {old_qty} → {stock.quantity} (producto: {self.product})")
        
        # Eliminar el movimiento
        super().delete(*args, **kwargs)
