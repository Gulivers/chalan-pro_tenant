from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( 
    EventViewSet, EventsListView, EventNoteViewSet, 
    EventChatViewSet, download_schedule_pdf, MyEventsView, 
    export_schedule_excel, AbsenceReasonViewSet, WeeklySupervisorStatsChartView,
    WeeklySupervisorStatsExcelView, unread_chat_counts, mark_chat_read,
    EventImageViewSet, EventReadViewSet
)

router = DefaultRouter()
router.register(r'schedule', EventViewSet)
router.register(r'event', EventReadViewSet)
router.register(r'absence-reasons', AbsenceReasonViewSet)
router.register(r'event-images', EventImageViewSet, basename='eventimage')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/schedule-list/', EventsListView.as_view()),
    path('api/events/<int:event_id>/note/', EventNoteViewSet.as_view({'get': 'retrieve', 'post': 'create'}), name='event-note'),
    path('api/events/<int:event_id>/chat/messages/', EventChatViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-chat-messages'),
    path('api/schedule-report/', download_schedule_pdf, name='download_schedule_pdf'),
    path('api/my-events/', MyEventsView.as_view(), name='my_events'),
    path('api/schedule-excel/', export_schedule_excel, name='export_schedule_excel'),
    path('api/supervisor-stats/', WeeklySupervisorStatsChartView.as_view(), name='supervisor-stats'),
    path('api/supervisor-stats-excel/', WeeklySupervisorStatsExcelView.as_view()),
    path('api/unread-chat-counts/', unread_chat_counts, name='unread_chat_counts'),
    path('api/mark-chat-read/<int:event_id>/', mark_chat_read, name='mark_chat_read'),
]
