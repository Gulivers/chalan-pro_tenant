import asyncio
import json
import os

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync   # OAHP
from appschedule.models import Event, EventDraft, EventNote, EventChatMessage, EventChatReadStatus, EventImage
from appschedule.serializers import EventSerializer, EventDraftSerializer, EventNoteSerializer, EventChatMessageSerializer


@receiver(post_save, sender=Event)
def event_saved(sender, instance, **kwargs):
    if getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
        channel_layer = get_channel_layer()
        serializer = EventSerializer(instance)

        event_data = serializer.data
        asyncio.run(channel_layer.group_send(
            "calendar_updates",
            {
                'type': 'event.updated',
                'event_data': event_data,
            }
        ))


@receiver(post_delete, sender=Event)
def event_deleted(sender, instance, **kwargs):
    if getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
        channel_layer = get_channel_layer()
        event_data = {
            'id': instance.id,
        }
        asyncio.run(channel_layer.group_send(
            "calendar_updates",
            {
                'type': 'event.updated',
                'event_data': event_data,
            }
        ))


@receiver(post_save, sender=EventDraft)
def event_draft_saved(sender, instance, **kwargs):
    if getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
        channel_layer = get_channel_layer()
        serializer = EventDraftSerializer(instance)

        event_data = serializer.data
        asyncio.run(channel_layer.group_send(
            "calendar_updates",
            {
                'type': 'event_draft.updated',
                'event_data': event_data,
            }
        ))


@receiver(post_delete, sender=EventDraft)
def event_draft_deleted(sender, instance, **kwargs):
    if getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
        channel_layer = get_channel_layer()
        event_data = {
            'id': instance.id,
        }
        asyncio.run(channel_layer.group_send(
            "calendar_updates",
            {
                'type': 'event_draft.updated',
                'event_data': event_data,
            }
        ))

@receiver(post_save, sender=EventNote)
def event_note_saved(sender, instance, **kwargs):
    if getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
        channel_layer = get_channel_layer()
        serializer = EventNoteSerializer(instance)

        event_data = serializer.data
        asyncio.run(channel_layer.group_send(
            f"event_{instance.event_id}_notes",
            {
                'type': 'note.updated',
                'event_data': event_data,
            }
        ))


@receiver(post_save, sender=EventChatMessage)
def event_chatmessage_saved(sender, instance, created, **kwargs):
    if not created:
        return

    # Crear automáticamente el ReadStatus para el autor
    EventChatReadStatus.objects.update_or_create(
        user=instance.author,
        message=instance,
        defaults={"read_at": instance.timestamp}
    )

    if getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
        channel_layer = get_channel_layer()
        serializer = EventChatMessageSerializer(instance)
        event_data = serializer.data

        try:
            asyncio.run(channel_layer.group_send(
                f"schedule_{instance.event_id}_chat",
                {
                    'type': 'chat.updated',
                    'data': event_data,
                    'author_id': instance.author.id  # 👈 Añadido aquí
                }
            ))
        except Exception as e:
            print(f"[WebSocket Error] {e}")


@receiver(post_delete, sender=EventImage)
def delete_event_image_file(sender, instance, **kwargs):
    # Borra el archivo físico cuando se elimina el registro
    if instance.image:
        image_path = instance.image.path
        instance.image.delete(False)
        # Ahora intentamos borrar la carpeta si queda vacía
        import os
        dir_path = os.path.dirname(image_path)
        try:
            # Si la carpeta está vacía, la borra
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
        except Exception as e:
            # Si hay error (por ejemplo, permisos), solo lo imprime, no detiene el proceso
            print(f"Error al borrar carpeta vacía: {dir_path} -> {e}")