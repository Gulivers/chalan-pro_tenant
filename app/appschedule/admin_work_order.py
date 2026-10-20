"""Django Admin for Work Order status catalog, progress templates, and tracking."""

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.utils.html import format_html

from appschedule.models import (
    WorkOrderProgressCheck,
    WorkOrderProgressItem,
    WorkOrderProgressTemplate,
    WorkOrderStatus,
    WorkOrderStatusHistory,
    WorkOrderTracking,
)


class WorkOrderProgressItemInline(admin.TabularInline):
    model = WorkOrderProgressItem
    extra = 0
    ordering = ('sequence',)
    fields = (
        'sequence',
        'code',
        'name',
        'is_required_for_inspection',
        'is_required_for_completion',
        'is_informational',
        'is_active',
    )


@admin.register(WorkOrderStatus)
class WorkOrderStatusAdmin(admin.ModelAdmin):
    list_display = (
        'sequence',
        'code',
        'name',
        'is_initial',
        'is_terminal',
        'requires_inspection_ready',
        'requires_completion_ready',
        'is_active',
    )
    list_display_links = ('code', 'name')
    list_filter = (
        'is_active',
        'is_initial',
        'is_terminal',
        'requires_inspection_ready',
        'requires_completion_ready',
    )
    search_fields = ('code', 'name', 'description')
    ordering = ('sequence', 'id')
    fieldsets = (
        (None, {
            'fields': ('sequence', 'code', 'name', 'description', 'is_active'),
        }),
        ('Workflow roles', {
            'fields': (
                'is_initial',
                'is_terminal',
                'requires_inspection_ready',
                'requires_completion_ready',
            ),
            'description': (
                'Initial is assigned when a Work Order is published. '
                'Inspection/completion flags gate transitions until required '
                'progress items are done.'
            ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj._is_referenced():
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except ProtectedError as exc:
            raise ValidationError(str(exc)) from exc


@admin.register(WorkOrderProgressTemplate)
class WorkOrderProgressTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'is_active',
        'is_expected_for_work_account',
        'item_count',
    )
    list_filter = ('is_active', 'is_expected_for_work_account', 'category')
    search_fields = ('name', 'description', 'category__name')
    autocomplete_fields = ('category',)
    # Enables autocomplete from WorkOrderProgressItemAdmin.
    inlines = [WorkOrderProgressItemInline]
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'category',
                'description',
                'is_active',
                'is_expected_for_work_account',
            ),
            'description': (
                'One checklist template per crew category (phase). '
                'Expected-for-Work-Account phases drive project rollup even '
                'before a Work Order exists.'
            ),
        }),
    )

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(WorkOrderProgressItem)
class WorkOrderProgressItemAdmin(admin.ModelAdmin):
    list_display = (
        'template',
        'sequence',
        'code',
        'name',
        'is_required_for_inspection',
        'is_required_for_completion',
        'is_informational',
        'is_active',
    )
    list_filter = (
        'template',
        'is_active',
        'is_required_for_inspection',
        'is_required_for_completion',
        'is_informational',
    )
    search_fields = ('code', 'name', 'template__name')
    autocomplete_fields = ('template',)
    ordering = ('template', 'sequence')


@admin.register(WorkOrderTracking)
class WorkOrderTrackingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event',
        'current_status',
        'status_changed_at',
        'changed_by',
        'phase_name',
    )
    list_filter = ('current_status', 'status_changed_at')
    search_fields = (
        'event__title',
        'event__id',
        'event__lot',
        'event__address',
        'current_status__code',
        'current_status__name',
    )
    autocomplete_fields = ('event', 'current_status', 'changed_by')
    readonly_fields = (
        'event',
        'current_status',
        'status_changed_at',
        'changed_by',
        'notes',
        'progress_readonly',
        'history_readonly',
    )
    fields = (
        'event',
        'current_status',
        'status_changed_at',
        'changed_by',
        'notes',
        'progress_readonly',
        'history_readonly',
    )

    def phase_name(self, obj):
        try:
            return obj.event.crew.category.name
        except Exception:
            return ''
    phase_name.short_description = 'Phase'

    def progress_readonly(self, obj):
        if not obj or not obj.event_id:
            return '—'
        rows = []
        for check in (
            WorkOrderProgressCheck.objects.filter(event_id=obj.event_id)
            .select_related('item', 'completed_by')
            .order_by('item__sequence', 'id')
        ):
            state = 'Done' if check.is_done else 'Pending'
            actor = getattr(check.completed_by, 'username', '') or '—'
            req = []
            if check.item.is_required_for_inspection:
                req.append('insp')
            if check.item.is_required_for_completion:
                req.append('close')
            if check.item.is_informational:
                req.append('info')
            rows.append(
                f'<tr><td>{check.item.sequence}</td><td>{check.item.name}</td>'
                f'<td>{state}</td><td>{", ".join(req) or "—"}</td>'
                f'<td>{actor}</td><td>{check.notes or ""}</td></tr>'
            )
        if not rows:
            return 'No progress checklist for this Work Order.'
        table = (
            '<table style="width:100%;border-collapse:collapse">'
            '<thead><tr><th>#</th><th>Item</th><th>State</th>'
            '<th>Flags</th><th>By</th><th>Notes</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>'
        )
        return format_html(table)
    progress_readonly.short_description = 'Progress checklist (read-only)'

    def history_readonly(self, obj):
        if not obj or not obj.event_id:
            return '—'
        rows = []
        for row in (
            WorkOrderStatusHistory.objects.filter(event_id=obj.event_id)
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
    history_readonly.short_description = 'Status history (read-only)'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('appschedule.view_workordertracking')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(WorkOrderStatusHistory)
class WorkOrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event',
        'from_status',
        'to_status',
        'changed_by',
        'changed_at',
    )
    list_filter = ('to_status', 'from_status', 'changed_at')
    search_fields = (
        'event__title',
        'event__id',
        'from_status__code',
        'to_status__code',
        'notes',
    )
    readonly_fields = (
        'event',
        'from_status',
        'to_status',
        'changed_by',
        'changed_at',
        'notes',
    )
    ordering = ('-changed_at', '-id')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(WorkOrderProgressCheck)
class WorkOrderProgressCheckAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'event',
        'item',
        'is_done',
        'completed_at',
        'completed_by',
        'source',
    )
    list_filter = ('is_done', 'source', 'item__template')
    search_fields = (
        'event__title',
        'event__id',
        'item__code',
        'item__name',
        'notes',
    )
    autocomplete_fields = ('event', 'item', 'completed_by', 'source_document')
    readonly_fields = ('completed_at',)
