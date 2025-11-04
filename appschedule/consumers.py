import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from .models import Event, EventChatMessage
from .serializers import EventChatMessageSerializer


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.calendar_group_name = 'calendar_updates'  # Define a group name
        await self.channel_layer.group_add(self.calendar_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.calendar_group_name, self.channel_name)

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
        self.event_id = self.scope['url_route']['kwargs']['pk']
        self.event_group_name = f"event_{self.event_id}_notes"

        # Join a group specific to the event
        await self.channel_layer.group_add(self.event_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the event-specific group
        await self.channel_layer.group_discard(self.event_group_name, self.channel_name)

    async def note_updated(self, event):
        event_data = event['event_data']
        # Enviar la información del evento actualizado al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'note.updated',
            'event': event_data
        }))


class EventChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room_group_name = f"schedule_{self.event_id}_chat"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

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

class UnreadNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"user_{self.user_id}_unread"

        print(f"[WS-CONNECT] User {self.user.username} joined {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def unread_updated(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread.updated",
            "event_id": event["event_id"],
            "count": event["count"]
        }))