from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( 
    EventViewSet, EventsListView, EventNoteViewSet, 
    EventChatViewSet, download_schedule_pdf, MyEventsView, 
    export_schedule_excel, AbsenceReasonViewSet, WeeklySupervisorStatsChartView,
    WeeklySupervisorStatsExcelView, unread_chat_counts, mark_chat_read,
    EventImageViewSet, EventReadViewSet
)
from .work_order_status_api import (
    WorkOrderStatusViewSet,
    WorkOrderProgressTemplateViewSet,
    WorkOrderProgressItemViewSet,
    WorkOrderEventStatusViewSet,
    work_account_progress_view,
)

router = DefaultRouter()
router.register(r'schedule', EventViewSet)
router.register(r'event', EventReadViewSet)
router.register(r'absence-reasons', AbsenceReasonViewSet)
router.register(r'event-images', EventImageViewSet, basename='eventimage')
router.register(r'work-order-statuses', WorkOrderStatusViewSet, basename='work-order-statuses')
router.register(
    r'work-order-progress-templates',
    WorkOrderProgressTemplateViewSet,
    basename='work-order-progress-templates',
)
router.register(
    r'work-order-progress-items',
    WorkOrderProgressItemViewSet,
    basename='work-order-progress-items',
)

work_order_event = WorkOrderEventStatusViewSet.as_view({
    'get': 'retrieve',
})
work_order_event_transition = WorkOrderEventStatusViewSet.as_view({
    'post': 'transition_status',
})
work_order_event_history = WorkOrderEventStatusViewSet.as_view({
    'get': 'status_history',
})
work_order_event_progress = WorkOrderEventStatusViewSet.as_view({
    'get': 'progress',
})
work_order_event_progress_update = WorkOrderEventStatusViewSet.as_view({
    'patch': 'update_progress',
})
work_order_event_material = WorkOrderEventStatusViewSet.as_view({
    'get': 'material_suggestions',
})

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/schedule-list/', EventsListView.as_view()),
    path('api/events/<int:event_id>/note/', EventNoteViewSet.as_view({'get': 'retrieve', 'post': 'create'}), name='event-note'),
    path('api/events/<int:event_id>/chat/messages/', EventChatViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-chat-messages'),
    path(
        'api/events/<int:event_id>/work-order-status/',
        work_order_event,
        name='event-work-order-status',
    ),
    path(
        'api/events/<int:event_id>/work-order-status/transition/',
        work_order_event_transition,
        name='event-work-order-status-transition',
    ),
    path(
        'api/events/<int:event_id>/work-order-status/history/',
        work_order_event_history,
        name='event-work-order-status-history',
    ),
    path(
        'api/events/<int:event_id>/work-order-progress/',
        work_order_event_progress,
        name='event-work-order-progress',
    ),
    path(
        'api/events/<int:event_id>/work-order-progress/<int:check_id>/',
        work_order_event_progress_update,
        name='event-work-order-progress-update',
    ),
    path(
        'api/events/<int:event_id>/work-order-progress/material-suggestions/',
        work_order_event_material,
        name='event-work-order-material-suggestions',
    ),
    path(
        'api/work-accounts/<int:work_account_id>/work-order-progress/',
        work_account_progress_view,
        name='work-account-work-order-progress',
    ),
    path('api/schedule-report/', download_schedule_pdf, name='download_schedule_pdf'),
    path('api/my-events/', MyEventsView.as_view(), name='my_events'),
    path('api/schedule-excel/', export_schedule_excel, name='export_schedule_excel'),
    path('api/supervisor-stats/', WeeklySupervisorStatsChartView.as_view(), name='supervisor-stats'),
    path('api/supervisor-stats-excel/', WeeklySupervisorStatsExcelView.as_view()),
    path('api/unread-chat-counts/', unread_chat_counts, name='unread_chat_counts'),
    path('api/mark-chat-read/<int:event_id>/', mark_chat_read, name='mark_chat_read'),
]
