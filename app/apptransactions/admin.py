from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import (
    Party, PartyType, PartyCategory,
    DocumentType, Document, DocumentLine, WorkAccount, TransactionFavorite
)

@admin.register(PartyType)
class PartyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(PartyCategory)
class PartyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_price_type', 'customer_rank', 'supplier_rank', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'rfc', 'email', 'phone')
    autocomplete_fields = ('category', 'default_price_type', 'types')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate()

    def get_list_filter(self, request):
        filters = list(super().get_list_filter(request))
        filters.append(('customer_rank', admin.BooleanFieldListFilter))
        filters.append(('supplier_rank', admin.BooleanFieldListFilter))
        return filters


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_code', 'description', 'stock_movement', 'is_active')
    search_fields = ('type_code', 'description')
    list_filter = ('is_active', 'stock_movement')

# Validación que aplica a cada línea del inline
class DocumentLineInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                quantity = form.cleaned_data.get('quantity')
                product = form.cleaned_data.get('product')
                if quantity is None or product is None:
                    raise ValidationError("Todas las líneas deben tener producto y cantidad.")

class DocumentLineInline(admin.TabularInline):
    model = DocumentLine
    extra = 1
    formset = DocumentLineInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        for field in ['quantity', 'product']:
            if field in formset.form.base_fields:
                formset.form.base_fields[field].required = True  # Campos obligatorios
        return formset

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'date', 'builder', 'is_active')
    search_fields = ('job', 'lot', 'notes')
    list_filter = ('document_type','is_active')
    autocomplete_fields = ('builder', 'document_type', 'created_by')
    inlines = [DocumentLineInline]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        for field in ['quantity', 'product']:
            if field in formset.form.base_fields:
                formset.form.base_fields[field].required = True
        return formset
    
@admin.register(WorkAccount)
class WorkAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'builder_name', 'party_name', 'job_name', 'house_model_name', 'lot', 'city', 'state', 'is_active', 'created_at')
    search_fields = ('title', 'builder__name', 'builder__party__name', 'job__name', 'house_model__name', 'lot', 'address', 'city', 'zipcode')
    list_filter = ('is_active', 'state', 'city')
    autocomplete_fields = ('builder', 'job', 'house_model', 'default_price_type')
    readonly_fields = ('created_at', 'created_by')
    fieldsets = (
        ("Identity", {
            "fields": ("title", "builder", "job", "house_model", "default_price_type", "is_active")
        }),
        ("Location", {
            "fields": ("lot", "address", "city", "state", "zipcode")
        }),
        ("Extra", {
            "fields": ("notes", "created_by", "created_at")
        }),
    )

    def builder_name(self, obj): return getattr(obj.builder, "name", "")
    builder_name.short_description = "Builder"
    
    def party_name(self, obj): 
        try: return getattr(obj.builder.party, 'name', '')
        except Exception: return ''
        
    def job_name(self, obj): return getattr(obj.job, "name", "")
    job_name.short_description = "Job"

    def house_model_name(self, obj): return getattr(obj.house_model, "name", "")
    house_model_name.short_description = "House Model"

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TransactionFavorite)
class TransactionFavoriteAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'is_active', 'document_type_preview')
    list_filter = ('is_active', 'created_at', 'created_by')
    search_fields = ('name', 'description', 'created_by__username')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'document_data_preview', 'lines_data_preview')
    ordering = ['-created_at']
    
    fieldsets = (
        ("Información Básica", {
            "fields": ("name", "description", "created_by", "is_active")
        }),
        ("Metadatos", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
        ("Datos del Documento", {
            "fields": ("document_data_preview",),
            "classes": ("collapse",)
        }),
        ("Datos de Líneas", {
            "fields": ("lines_data_preview",),
            "classes": ("collapse",)
        }),
        ("Datos Raw", {
            "fields": ("document_data", "lines_data"),
            "classes": ("collapse",)
        }),
    )
    
    def document_type_preview(self, obj):
        """Mostrar tipo de documento de forma legible"""
        try:
            doc_data = obj.document_data
            if isinstance(doc_data, dict) and 'document_type' in doc_data:
                doc_type_id = doc_data['document_type']
                from .models import DocumentType
                doc_type = DocumentType.objects.get(id=doc_type_id)
                return f"{doc_type.type_code} - {doc_type.description}"
        except Exception:
            pass
        return "N/A"
    document_type_preview.short_description = "Tipo de Documento"
    
    def document_data_preview(self, obj):
        """Vista previa de los datos del documento"""
        if obj.document_data:
            import json
            try:
                formatted = json.dumps(obj.document_data, indent=2, ensure_ascii=False)
                return format_html('<pre style="max-height: 200px; overflow-y: auto;">{}</pre>', formatted)
            except Exception:
                return str(obj.document_data)
        return "Sin datos"
    document_data_preview.short_description = "Vista Previa - Documento"
    
    def lines_data_preview(self, obj):
        """Vista previa de los datos de líneas"""
        if obj.lines_data:
            import json
            try:
                formatted = json.dumps(obj.lines_data, indent=2, ensure_ascii=False)
                return format_html('<pre style="max-height: 200px; overflow-y: auto;">{}</pre>', formatted)
            except Exception:
                return str(obj.lines_data)
        return "Sin datos"
    lines_data_preview.short_description = "Vista Previa - Líneas"
    
    def get_queryset(self, request):
        """Filtrar favoritos por usuario si no es superusuario"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs
    
    def save_model(self, request, obj, form, change):
        """Asignar usuario actual si no está asignado"""
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)