import logging
import os

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync   # OAHP

try:
    # Captura la excepción real de Redis cuando no hay conexión.
    from redis.exceptions import ConnectionError as RedisConnectionError  # type: ignore
except ImportError:  # pragma: no cover - el paquete redis es opcional
    RedisConnectionError = Exception
from appschedule.models import Event, EventDraft, EventNote, EventChatMessage, EventChatReadStatus, EventImage
from appschedule.serializers import EventSerializer, EventDraftSerializer, EventNoteSerializer, EventChatMessageSerializer


logger = logging.getLogger(__name__)


def _notify_group(group_name: str, payload: dict) -> None:
    """// Envía mensajes a un grupo de Channels sin romper si Redis falla."""
    if not getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.debug("Channel layer no disponible; se omite notificación.")
        return

    try:
        async_to_sync(channel_layer.group_send)(group_name, payload)
    except RedisConnectionError as exc:
        logger.warning("Redis ausente, notificación omitida: %s", exc)
    except Exception as exc:  # pragma: no cover - defensivo
        logger.exception("Error enviando notificación websocket: %s", exc)


@receiver(post_save, sender=Event)
def event_saved(sender, instance, **kwargs):
    serializer = EventSerializer(instance)

    event_data = serializer.data
    _notify_group(
        "calendar_updates",
        {
            'type': 'event.updated',
            'event_data': event_data,
        }
    )


@receiver(post_delete, sender=Event)
def event_deleted(sender, instance, **kwargs):
    event_data = {
        'id': instance.id,
    }
    _notify_group(
        "calendar_updates",
        {
            'type': 'event.updated',
            'event_data': event_data,
        }
    )


@receiver(post_save, sender=EventDraft)
def event_draft_saved(sender, instance, **kwargs):
    serializer = EventDraftSerializer(instance)

    event_data = serializer.data
    _notify_group(
        "calendar_updates",
        {
            'type': 'event_draft.updated',
            'event_data': event_data,
        }
    )


@receiver(post_delete, sender=EventDraft)
def event_draft_deleted(sender, instance, **kwargs):
    event_data = {
        'id': instance.id,
    }
    _notify_group(
        "calendar_updates",
        {
            'type': 'event_draft.updated',
            'event_data': event_data,
        }
    )

@receiver(post_save, sender=EventNote)
def event_note_saved(sender, instance, **kwargs):
    serializer = EventNoteSerializer(instance)

    event_data = serializer.data
    # Usar work_account_id para el grupo de WebSocket
    work_account_id = instance.work_account_id if instance.work_account_id else None
    if work_account_id:
        _notify_group(
            f"work_account_{work_account_id}_notes",
            {
                'type': 'note.updated',
                'event_data': event_data,
            }
        )


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

    serializer = EventChatMessageSerializer(instance)
    event_data = serializer.data

    # Usar work_account_id para el grupo de WebSocket si está disponible
    work_account_id = instance.work_account_id if instance.work_account_id else None
    if work_account_id:
        _notify_group(
            f"work_account_{work_account_id}_chat",
            {
                'type': 'chat.updated',
                'data': event_data,
                'author_id': instance.author.id
            }
        )
    # Fallback a event_id para compatibilidad
    elif instance.event_id:
        _notify_group(
            f"schedule_{instance.event_id}_chat",
            {
                'type': 'chat.updated',
                'data': event_data,
                'author_id': instance.author.id
            }
        )


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