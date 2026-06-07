from django.contrib import admin

from appsearch.models import IndexOutbox, SearchIndex


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
        'created_at',
    )
    list_filter = ('action', 'source_type', 'processed_at')
    search_fields = ('source_id', 'last_error')
    readonly_fields = (
        'source_type',
        'source_id',
        'action',
        'attempts',
        'last_error',
        'processed_at',
        'created_at',
    )
