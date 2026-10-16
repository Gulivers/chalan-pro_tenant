from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.utils.html import format_html
from .models import (
    Party, PartyType, PartyCategory,
    DocumentType, Document, DocumentLine, WorkAccount, TransactionFavorite,
    DocumentStatus, DocumentTracking, DocumentTrackingHistory,
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


class DocumentStatusInline(admin.TabularInline):
    """Estados del tipo, estilo lineal (Requested → … → Closed)."""
    model = DocumentStatus
    extra = 0
    ordering = ('sequence',)
    fields = (
        'sequence', 'code', 'name',
        'is_initial', 'is_terminal', 'is_active',
    )


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.type_code in DocumentType.PROTECTED_TYPE_CODES:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.type_code in DocumentType.PROTECTED_TYPE_CODES:
            return False
        return super().has_delete_permission(request, obj)

    list_display = (
        'id', 'type_code', 'description', 'uses_status_tracking',
        'creates_serialized_items',
        'counts_as_net_invoiced_spend', 'counts_as_job_material_issue',
        'counts_as_purchase_return', 'stock_movement', 'is_active',
    )
    search_fields = ('type_code', 'description')
    list_filter = (
        'is_active', 'uses_status_tracking', 'stock_movement',
        'counts_as_net_invoiced_spend', 'counts_as_job_material_issue',
        'counts_as_purchase_return',
    )
    inlines = [DocumentStatusInline]
    fieldsets = (
        (None, {
            'fields': ('type_code', 'description', 'is_active', 'uses_status_tracking'),
        }),
        ('Inventory / accounting flags', {
            'fields': (
                'affects_physical', 'affects_logical', 'affects_accounting',
                'is_taxable', 'is_purchase', 'is_sales', 'warehouse_required',
                'is_operational', 'prices_required', 'allow_negative_sales',
                'creates_serialized_items', 'stock_movement',
            ),
        }),
        ('Assistant intentions', {
            'classes': ('collapse',),
            'fields': (
                'counts_as_net_invoiced_spend',
                'counts_as_job_material_issue',
                'counts_as_purchase_return',
            ),
        }),
    )


@admin.register(DocumentStatus)
class DocumentStatusAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'document_type', 'sequence', 'code', 'name',
        'is_initial', 'is_terminal', 'is_active',
    )
    list_filter = ('document_type', 'is_initial', 'is_terminal', 'is_active')
    search_fields = ('code', 'name', 'document_type__type_code')
    ordering = ('document_type__type_code', 'sequence')
    autocomplete_fields = ('document_type',)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj._is_referenced():
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except ProtectedError as exc:
            raise ValidationError(str(exc)) from exc


@admin.register(DocumentTracking)
class DocumentTrackingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'document', 'document_type_code', 'current_status',
        'status_changed_at', 'changed_by',
    )
    list_filter = ('current_status__document_type', 'current_status')
    search_fields = (
        'document__id', 'document__document_number',
        'current_status__code', 'current_status__name',
    )
    autocomplete_fields = ('document', 'current_status', 'changed_by')
    readonly_fields = (
        'document', 'current_status', 'status_changed_at', 'changed_by', 'notes',
        'history_readonly',
    )
    fields = (
        'document', 'current_status', 'status_changed_at', 'changed_by', 'notes',
        'history_readonly',
    )

    def document_type_code(self, obj):
        try:
            return obj.document.document_type.type_code
        except Exception:
            return ''
    document_type_code.short_description = 'Type'

    def history_readonly(self, obj):
        if not obj or not obj.document_id:
            return '—'
        rows = []
        for row in (
            DocumentTrackingHistory.objects.filter(document_id=obj.document_id)
            .select_related('from_status', 'to_status', 'changed_by')
            .order_by('changed_at', 'id')
        ):
            origin = row.from_status.code if row.from_status_id else '—'
            actor = getattr(row.changed_by, 'username', '') or '—'
            rows.append(
                f'<tr><td>{row.changed_at}</td><td>{origin}</td>'
                f'<td>{row.to_status.code}</td><td>{actor}</td>'
                f'<td>{row.notes or ""}</td></tr>'
            )
        if not rows:
            return 'No history yet.'
        table = (
            '<table style="width:100%;border-collapse:collapse">'
            '<thead><tr><th>When</th><th>From</th><th>To</th>'
            '<th>By</th><th>Notes</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>'
        )
        return format_html(table)
    history_readonly.short_description = 'Transition history (read-only)'

    def has_add_permission(self, request):
        # Los cambios de estado van por la lógica de negocio / API, no por Admin.
        return False

    def has_change_permission(self, request, obj=None):
        # Permitir abrir el detalle en solo lectura; los campos son readonly.
        return request.user.has_perm('apptransactions.view_documenttracking')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(DocumentTrackingHistory)
class DocumentTrackingHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'document', 'from_status', 'to_status', 'changed_by', 'changed_at',
    )
    list_filter = ('to_status__document_type', 'to_status')
    search_fields = (
        'document__id', 'document__document_number',
        'from_status__code', 'to_status__code', 'notes',
    )
    readonly_fields = (
        'document', 'from_status', 'to_status', 'changed_by', 'changed_at', 'notes',
    )
    ordering = ('-changed_at', '-id')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

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

@admin.register(DocumentLine)
class DocumentLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_id', 'document', 'product', 'quantity', 'unit')
    search_fields = ('document__id', 'product__name', 'product__sku')
    autocomplete_fields = ('document', 'product', 'unit', 'price_type', 'brand')
    list_filter = ('document__document_type',)


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
    list_display = ('id', 'document_type', 'date', 'builder', 'is_active')
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