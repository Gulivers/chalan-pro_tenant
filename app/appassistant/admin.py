from django.contrib import admin

from .models import AssistantQueryLog


@admin.register(AssistantQueryLog)
class AssistantQueryLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'schema_name',
        'user',
        'tool_name',
        'success',
        'error_code',
        'row_count',
        'duration_ms',
        'request_id',
    )
    list_filter = ('success', 'tool_name', 'schema_name')
    search_fields = ('request_id', 'error_code', 'tool_name')
    readonly_fields = (
        'user',
        'schema_name',
        'request_id',
        'tool_name',
        'params_safe',
        'success',
        'error_code',
        'row_count',
        'duration_ms',
        'created_at',
    )
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

