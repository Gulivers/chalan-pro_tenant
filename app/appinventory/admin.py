from django.contrib import admin
from .models import (
    UnitCategory, UnitOfMeasure, Warehouse,
    ProductCategory, ProductBrand, Product,
    PriceType, ProductPrice,
    Stock, InventoryMovement
)

@admin.register(UnitCategory)
class UnitCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name',)


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'reference_unit', 'conversion_sign', 'conversion_factor', 'is_active')
    list_filter = ('category', 'reference_unit', 'is_active')
    search_fields = ('name', 'code')
    autocomplete_fields = ['category']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_default', 'is_active')
    search_fields = ('name', 'location')
    list_filter = ('is_active', 'is_default')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)


@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'is_active')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name',)


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 1
    autocomplete_fields = ['unit', 'price_type']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'default_brand_display', 'unit_default', 'is_active')
    list_filter = ('category', 'brands', 'is_active')
    search_fields = ('name', 'sku')
    autocomplete_fields = ['category', 'unit_default']
    filter_horizontal = ['brands']
    inlines = [ProductPriceInline]
    
    def default_brand_display(self, obj):
        """Muestra la marca predeterminada del producto"""
        default_brand = obj.get_default_brand()
        return default_brand.name if default_brand else 'Sin marca'
    default_brand_display.short_description = 'Marca Predeterminada'


@admin.register(PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity')
    list_filter = ('warehouse',)
    search_fields = ('product__name', 'warehouse__name')
    autocomplete_fields = ['product', 'warehouse']


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity', 'movement_type', 'unit', 'document', 'timestamp')
    list_filter = ('movement_type', 'timestamp', 'warehouse')
    search_fields = ('product__name', 'document')
    autocomplete_fields = ['product', 'warehouse', 'unit', 'created_by']
