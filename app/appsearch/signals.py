from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from appsearch.services.indexer import (
    enqueue_document_line_delete,
    enqueue_document_line_upsert,
    enqueue_document_lines_for_builder,
    enqueue_document_lines_for_document,
)


def _indexing_enabled():
    return getattr(settings, 'SEARCH_INDEXING_ENABLED', True)


@receiver(post_save, sender='apptransactions.DocumentLine')
def document_line_saved(sender, instance, **kwargs):
    if not _indexing_enabled():
        return
    enqueue_document_line_upsert(instance.id)


@receiver(post_delete, sender='apptransactions.DocumentLine')
def document_line_deleted(sender, instance, **kwargs):
    if not _indexing_enabled():
        return
    enqueue_document_line_delete(instance.id)


@receiver(pre_save, sender='apptransactions.Document')
def document_pre_save(sender, instance, **kwargs):
    if not _indexing_enabled() or not instance.pk:
        instance._search_reindex_needed = True
        return

    from apptransactions.models import Document

    try:
        previous = Document.objects.get(pk=instance.pk)
    except Document.DoesNotExist:
        instance._search_reindex_needed = True
        return

    watched_fields = (
        'notes',
        'builder_id',
        'work_account_id',
        'document_type_id',
        'is_active',
        'date',
    )
    instance._search_reindex_needed = any(
        getattr(previous, field) != getattr(instance, field)
        for field in watched_fields
    )


@receiver(post_save, sender='apptransactions.Document')
def document_saved(sender, instance, **kwargs):
    if not _indexing_enabled():
        return
    if getattr(instance, '_search_reindex_needed', True):
        enqueue_document_lines_for_document(instance.id)


@receiver(pre_save, sender='ctrctsapp.Builder')
def builder_pre_save(sender, instance, **kwargs):
    if not _indexing_enabled() or not instance.pk:
        instance._search_reindex_needed = False
        return

    from ctrctsapp.models import Builder

    try:
        previous = Builder.objects.get(pk=instance.pk)
    except Builder.DoesNotExist:
        instance._search_reindex_needed = False
        return

    instance._search_reindex_needed = previous.name != instance.name


@receiver(post_save, sender='ctrctsapp.Builder')
def builder_saved(sender, instance, **kwargs):
    if not _indexing_enabled():
        return
    if getattr(instance, '_search_reindex_needed', False):
        enqueue_document_lines_for_builder(instance.id)
