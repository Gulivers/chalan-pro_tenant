from django.contrib import admin

from .models import AssistantConversation, AssistantQueryLog


@admin.register(AssistantConversation)
class AssistantConversationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'schema_name',
        'is_active',
        'turn_count',
        'last_activity_at',
        'created_at',
    )
    list_filter = ('is_active', 'schema_name')
    search_fields = ('id', 'title', 'user__username')
    readonly_fields = (
        'id',
        'user',
        'schema_name',
        'state',
        'state_schema_version',
        'turn_count',
        'created_at',
        'updated_at',
        'last_activity_at',
    )
    ordering = ('-last_activity_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AssistantQueryLog)
class AssistantQueryLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'schema_name',
        'user',
        'conversation',
        'tool_name',
        'intent',
        'clarification',
        'success',
        'error_code',
        'row_count',
        'duration_ms',
        'request_id',
    )
    list_filter = ('success', 'clarification', 'tool_name', 'schema_name')
    search_fields = ('request_id', 'error_code', 'tool_name', 'intent')
    readonly_fields = (
        'user',
        'conversation',
        'schema_name',
        'request_id',
        'tool_name',
        'intent',
        'clarification',
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
