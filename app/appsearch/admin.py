from django.contrib import admin

from appsearch.models import BuilderAlias, IndexOutbox, SearchIndex, SearchTelemetry


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'source_type',
        'source_id',
        'embedding_model',
        'indexed_at',
        'updated_at',
    )
    list_filter = ('source_type', 'embedding_model', 'indexed_at')
    search_fields = ('chunk_text', 'metadata')
    readonly_fields = (
        'source_type',
        'source_id',
        'chunk_text',
        'embedding',
        'search_vector',
        'metadata',
        'content_hash',
        'embedding_model',
        'indexed_at',
        'created_at',
        'updated_at',
    )


@admin.register(IndexOutbox)
class IndexOutboxAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'action',
        'source_type',
        'source_id',
        'attempts',
        'processed_at',
        'dead_letter_at',
        'created_at',
    )
    list_filter = ('action', 'source_type', 'processed_at', 'dead_letter_at')
    search_fields = ('source_id', 'last_error')
    readonly_fields = (
        'source_type',
        'source_id',
        'action',
        'attempts',
        'last_error',
        'processed_at',
        'dead_letter_at',
        'created_at',
    )


@admin.register(BuilderAlias)
class BuilderAliasAdmin(admin.ModelAdmin):
    list_display = ('id', 'alias', 'builder', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('alias', 'builder__name')
    autocomplete_fields = ('builder',)


@admin.register(SearchTelemetry)
class SearchTelemetryAdmin(admin.ModelAdmin):
    list_display = ('id', 'operation', 'latency_ms', 'result_count', 'query_length', 'created_at')
    list_filter = ('operation', 'created_at')
    readonly_fields = (
        'operation',
        'latency_ms',
        'result_count',
        'query_length',
        'created_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
