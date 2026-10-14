import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django_tenants.utils import get_tenant_model

from appauth.ws_tickets import consume_ws_ticket
from appschedule.ws_groups import tenant_ws_group


def _ticket_from_scope(scope) -> str:
    raw = scope.get('query_string') or b''
    if isinstance(raw, str):
        raw = raw.encode()
    values = parse_qs(raw.decode('utf-8', errors='ignore')).get('ticket') or []
    return values[0] if values else ''


@database_sync_to_async
def _user_from_ticket(ticket: str):
    uid, schema = consume_ws_ticket(ticket)
    tenant = get_tenant_model().objects.get(schema_name=schema)
    connection.set_tenant(tenant)
    user = get_user_model().objects.get(pk=uid, is_active=True)
    return user, schema


async def authorize_ws(scope):
    ticket = _ticket_from_scope(scope)
    if not ticket:
        return None
    try:
        return await _user_from_ticket(ticket)
    except (signing.BadSignature, signing.SignatureExpired, ObjectDoesNotExist, ValueError, TypeError):
        return None


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        authorized = await authorize_ws(self.scope)
        if authorized is None:
            await self.close(code=4401)
            return
        self.ws_user, self.ws_schema = authorized
        self.calendar_group_name = tenant_ws_group('calendar_updates', self.ws_schema)
        await self.channel_layer.group_add(self.calendar_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group = getattr(self, 'calendar_group_name', None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def event_updated(self, event):
        event_data = event['event_data']

        # Enviar la información del evento actualizado al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'event.updated',
            'event': event_data
        }))

    async def event_draft_updated(self, event):
        event_data = event['event_data']

        # Enviar la información del evento actualizado al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'event.updated_draft',
            'event': event_data
        }))

    async def receive(self, text_data):
        pass
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        #
        # # Enviar el mensaje al grupo
        # await self.channel_layer.group_send(
        #     self.calendar_group_name,
        #     {
        #         'type': 'chat.message',  # Define el tipo de evento
        #         'message': message
        #     }
        # )


class EventNoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        authorized = await authorize_ws(self.scope)
        if authorized is None:
            await self.close(code=4401)
            return
        self.ws_user, self.ws_schema = authorized
        self.event_id = self.scope['url_route']['kwargs']['pk']
        self.event_group_name = tenant_ws_group(
            f"event_{self.event_id}_notes", self.ws_schema
        )

        # Join a group specific to the event
        await self.channel_layer.group_add(self.event_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group = getattr(self, 'event_group_name', None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def note_updated(self, event):
        event_data = event['event_data']
        # Enviar la información del evento actualizado al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'note.updated',
            'event': event_data
        }))


class WorkAccountNoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        authorized = await authorize_ws(self.scope)
        if authorized is None:
            await self.close(code=4401)
            return
        self.ws_user, self.ws_schema = authorized
        self.work_account_id = self.scope['url_route']['kwargs']['work_account_id']
        self.work_account_group_name = tenant_ws_group(
            f"work_account_{self.work_account_id}_notes", self.ws_schema
        )

        # Join a group specific to the work_account
        await self.channel_layer.group_add(self.work_account_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group = getattr(self, 'work_account_group_name', None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def note_updated(self, event):
        event_data = event['event_data']
        # Enviar la información de la nota actualizada al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'note.updated',
            'event': event_data
        }))


class EventChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        authorized = await authorize_ws(self.scope)
        if authorized is None:
            await self.close(code=4401)
            return
        self.ws_user, self.ws_schema = authorized
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room_group_name = tenant_ws_group(
            f"schedule_{self.event_id}_chat", self.ws_schema
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group = getattr(self, 'room_group_name', None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass
        # text_data_json = json.loads(text_data)
        # message = text_data_json["message"]
        #
        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "chat.message", "message": message}
        # )

    async def chat_updated(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'chat.updated',
            'data': data
        }))


class WorkAccountChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        authorized = await authorize_ws(self.scope)
        if authorized is None:
            await self.close(code=4401)
            return
        self.ws_user, self.ws_schema = authorized
        self.work_account_id = self.scope['url_route']['kwargs']['work_account_id']
        self.room_group_name = tenant_ws_group(
            f"work_account_{self.work_account_id}_chat", self.ws_schema
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group = getattr(self, 'room_group_name', None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def chat_updated(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'chat.updated',
            'data': data
        }))

class UnreadNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        authorized = await authorize_ws(self.scope)
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        if authorized is None:
            await self.close(code=4401)
            return
        self.ws_user, self.ws_schema = authorized
        if str(self.ws_user.pk) != str(self.user_id):
            await self.close(code=4403)
            return
        self.user = self.ws_user
        self.group_name = tenant_ws_group(
            f"user_{self.user_id}_unread", self.ws_schema
        )
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group = getattr(self, 'group_name', None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def unread_updated(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread.updated",
            "event_id": event["event_id"],
            "count": event["count"]
        }))