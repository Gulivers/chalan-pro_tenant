from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import (
    UnitCategory, UnitOfMeasure, Warehouse,
    ProductCategory, ProductBrand, Product, ProductBrandAssignment,
    PriceType, ProductPrice,
    Stock, InventoryMovement, ProductImage
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


@admin.register(ProductBrandAssignment)
class ProductBrandAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'brand', 'created_at')
    list_filter = ('brand', 'created_at')
    search_fields = ('product__name', 'brand__name')
    autocomplete_fields = ['product', 'brand']


class ProductBrandAssignmentInline(admin.TabularInline):
    model = ProductBrandAssignment
    extra = 1
    autocomplete_fields = ['brand']


def get_brand_image_inline(assignment):
    """
    Genera una clase Inline dinámica para una marca específica de un producto.
    """
    brand_name = assignment.brand.name
    brand_id = assignment.brand.id
    assignment_id = assignment.id

    class BrandImageForm(forms.ModelForm):
        class Meta:
            model = ProductImage
            fields = ['image', 'is_primary', 'description']

        def save(self, commit=True):
            instance = super().save(commit=False)
            instance.assignment = assignment
            instance.product = assignment.product
            if commit:
                instance.save()
            return instance

    class BrandImageInline(admin.TabularInline):
        model = ProductImage
        form = BrandImageForm
        extra = 1
        verbose_name = f"Images for {brand_name}"
        verbose_name_plural = f"Images for {brand_name}"
        fields = ('image', 'is_primary', 'description', 'image_preview')
        readonly_fields = ('image_preview',)
        
        def get_queryset(self, request):
            return super().get_queryset(request).filter(assignment_id=assignment_id)

        def image_preview(self, obj):
            if obj.image:
                return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
            return 'No image'
        image_preview.short_description = 'Preview'

    # Asignamos un nombre único a la clase para evitar conflictos en el registro del admin
    BrandImageInline.__name__ = f"BrandImageInline_{brand_id}"
    return BrandImageInline


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 1
    autocomplete_fields = ['unit', 'price_type']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'default_brand_display', 'unit_default', 'is_active')
    list_filter = ('category', 'brand_assignments__brand', 'is_active')
    search_fields = ('name', 'sku')
    autocomplete_fields = ['category', 'unit_default']
    # filter_horizontal = ['brands']  # Usamos inlines para manejar marcas y sus imágenes
    inlines = [ProductPriceInline, ProductBrandAssignmentInline]

    def get_inlines(self, request, obj=None):
        """
        Agrega inlines dinámicos para cada marca asignada al producto.
        """
        current_inlines = list(self.inlines)
        if obj:
            # Para cada marca asignada, creamos un inline de imágenes
            assignments = obj.brand_assignments.select_related('brand').all()
            for assignment in assignments:
                current_inlines.append(get_brand_image_inline(assignment))
        return current_inlines

    def default_brand_display(self, obj):
        """Shows the default brand of the product"""
        default_brand = obj.get_default_brand()
        return default_brand.name if default_brand else 'No brand'
    default_brand_display.short_description = 'Default Brand'


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


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'get_brand', 'image_preview', 'is_primary', 'uploaded_at', 'uploaded_by')
    list_filter = ('is_primary', 'assignment__brand', 'uploaded_at', 'product__category')
    search_fields = ('product__name', 'product__sku', 'assignment__brand__name', 'description')
    autocomplete_fields = ['product', 'assignment', 'uploaded_by']
    readonly_fields = ('uploaded_at', 'image_preview_large')
    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'assignment')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large', 'is_primary', 'description')
        }),
        ('Metadata', {
            'fields': ('uploaded_at', 'uploaded_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_brand(self, obj):
        return obj.assignment.brand.name if obj.assignment else "-"
    get_brand.short_description = 'Brand'

    def image_preview(self, obj):
        """Shows a thumbnail of the image in the list"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        """Shows a larger preview in the detail view"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 400px; max-width: 400px;" />', obj.image.url)
        return 'No image'
    image_preview_large.short_description = 'Preview'
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('product', 'assignment__brand', 'uploaded_by')
    
    def save_model(self, request, obj, form, change):
        """Automatically assign the user uploading the image"""
        if not change:  # Only on creation
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
