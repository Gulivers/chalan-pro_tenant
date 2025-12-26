from django.urls import re_path
from . import consumers
from .consumers import UnreadNotificationConsumer 

websocket_urlpatterns = [
    re_path(r"^ws/calendar-updates/$", consumers.EventConsumer.as_asgi()),
    re_path(r"^ws/schedule/event/(?P<pk>\d+)/$", consumers.EventNoteConsumer.as_asgi()),  # Legacy, mantiene compatibilidad
    re_path(r"^ws/schedule/work-account/(?P<work_account_id>\d+)/notes/$", consumers.WorkAccountNoteConsumer.as_asgi()),
    re_path(r"^ws/schedule/event/(?P<event_id>\d+)/chat/$", consumers.EventChatConsumer.as_asgi()),  # Legacy, mantiene compatibilidad
    re_path(r"^ws/schedule/work-account/(?P<work_account_id>\d+)/chat/$", consumers.WorkAccountChatConsumer.as_asgi()),
    re_path(r'^ws/schedule/unread/user/(?P<user_id>\d+)/$', UnreadNotificationConsumer.as_asgi()),
]