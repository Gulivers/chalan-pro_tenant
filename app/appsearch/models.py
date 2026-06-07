from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from pgvector.django import HnswIndex, VectorField


class SearchIndex(models.Model):
    """
    Índice de búsqueda persistido por tenant: una fila por entidad indexable
    (hoy DocumentLine). Guarda el texto denormalizado, embedding vectorial,
    FTS y metadata filtrable; es lo que consulta la búsqueda semántica.
    """

    SOURCE_DOCUMENT_LINE = 'document_line'
    SOURCE_DOCUMENT = 'document'
    SOURCE_BUILDER = 'builder'

    SOURCE_TYPE_CHOICES = [
        (SOURCE_DOCUMENT_LINE, 'Document line'),
        (SOURCE_DOCUMENT, 'Document'),
        (SOURCE_BUILDER, 'Builder'),
    ]

    source_type = models.CharField(max_length=32, choices=SOURCE_TYPE_CHOICES)
    source_id = models.PositiveBigIntegerField()
    chunk_text = models.TextField()
    embedding = VectorField(
        dimensions=getattr(settings, 'SEARCH_EMBEDDING_DIMENSIONS', 1536),
        null=True,
        blank=True,
    )
    search_vector = SearchVectorField(null=True, editable=False)
    metadata = models.JSONField(default=dict, blank=True)
    content_hash = models.CharField(max_length=64, db_index=True)
    embedding_model = models.CharField(max_length=64, default='text-embedding-3-small')
    indexed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Search index entry'
        verbose_name_plural = 'Search index entries'
        constraints = [
            models.UniqueConstraint(
                fields=['source_type', 'source_id'],
                name='uniq_searchindex_source',
            ),
        ]
        indexes = [
            GinIndex(fields=['search_vector'], name='searchindex_search_vector_gin'),
            GinIndex(fields=['metadata'], name='searchindex_metadata_gin'),
            models.Index(fields=['source_type', 'indexed_at'], name='searchindex_type_indexed'),
            HnswIndex(
                name='searchindex_embedding_hnsw',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.source_type}:{self.source_id}'


class IndexOutbox(models.Model):
    """
    Cola de trabajo desacoplada: registra qué entidad debe reindexarse o
    eliminarse del SearchIndex. Las señales encolan aquí; process_index_outbox
    procesa las entradas pendientes sin bloquear el guardado de transacciones.
    IndexOutbox mantiene SearchIndex al día con el catálogo de transacciones.
    Las preguntas del usuario se procesan contra SearchIndex, no pasan por el outbox.
    """

    ACTION_UPSERT = 'upsert'
    ACTION_DELETE = 'delete'

    ACTION_CHOICES = [
        (ACTION_UPSERT, 'Upsert'),
        (ACTION_DELETE, 'Delete'),
    ]

    source_type = models.CharField(max_length=32, choices=SearchIndex.SOURCE_TYPE_CHOICES)
    source_id = models.PositiveBigIntegerField()
    action = models.CharField(max_length=16, choices=ACTION_CHOICES, default=ACTION_UPSERT)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Index outbox entry'
        verbose_name_plural = 'Index outbox entries'
        indexes = [
            models.Index(
                fields=['processed_at', 'created_at'],
                name='search_outbox_pending',
                condition=models.Q(processed_at__isnull=True),
            ),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f'{self.action} {self.source_type}:{self.source_id}'
