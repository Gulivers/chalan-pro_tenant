"""
API for Work Order status catalog, progress, transitions, and Work Account rollup.

Operational UI will consume these endpoints from the Work Order Viewer later.
"""

from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, BasePermission
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from appauth.authentication import TenantJWTAuthentication
from appschedule.models import (
    Event,
    WorkOrderProgressCheck,
    WorkOrderProgressItem,
    WorkOrderProgressTemplate,
    WorkOrderStatus,
    WorkOrderStatusHistory,
    WorkOrderTracking,
)
from appschedule.services.work_order_status import (
    ensure_initial_work_order_status,
    get_work_order_tracking,
    list_active_statuses,
    missing_progress_requirements,
    set_progress_check,
    suggest_material_delivered_from_transactions,
    transition_work_order_status,
    work_account_status_summary,
)
from apptransactions.models import WorkAccount


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------


class WorkOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderStatus
        fields = [
            'id',
            'code',
            'name',
            'sequence',
            'is_initial',
            'is_terminal',
            'requires_inspection_ready',
            'requires_completion_ready',
            'is_active',
            'description',
        ]

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(
                    getattr(exc, 'message_dict', None) or exc.messages
                ) from exc
            raise

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(
                    getattr(exc, 'message_dict', None) or exc.messages
                ) from exc
            raise


class WorkOrderProgressItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderProgressItem
        fields = [
            'id',
            'template',
            'code',
            'name',
            'sequence',
            'is_required_for_inspection',
            'is_required_for_completion',
            'is_informational',
            'is_active',
        ]

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(
                    getattr(exc, 'message_dict', None) or exc.messages
                ) from exc
            raise

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(
                    getattr(exc, 'message_dict', None) or exc.messages
                ) from exc
            raise


class WorkOrderProgressTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    items = WorkOrderProgressItemSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrderProgressTemplate
        fields = [
            'id',
            'name',
            'category',
            'category_name',
            'is_active',
            'is_expected_for_work_account',
            'description',
            'items',
        ]


class WorkOrderTrackingSerializer(serializers.ModelSerializer):
    status_code = serializers.CharField(source='current_status.code', read_only=True)
    status_name = serializers.CharField(source='current_status.name', read_only=True)
    status_sequence = serializers.IntegerField(source='current_status.sequence', read_only=True)
    is_terminal = serializers.BooleanField(source='current_status.is_terminal', read_only=True)
    requires_inspection_ready = serializers.BooleanField(
        source='current_status.requires_inspection_ready',
        read_only=True,
    )
    requires_completion_ready = serializers.BooleanField(
        source='current_status.requires_completion_ready',
        read_only=True,
    )
    changed_by_username = serializers.SerializerMethodField()
    allowed_statuses = serializers.SerializerMethodField()
    missing_for_inspection = serializers.SerializerMethodField()
    missing_for_completion = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderTracking
        fields = [
            'id',
            'event',
            'current_status',
            'status_code',
            'status_name',
            'status_sequence',
            'is_terminal',
            'requires_inspection_ready',
            'requires_completion_ready',
            'status_changed_at',
            'changed_by',
            'changed_by_username',
            'notes',
            'allowed_statuses',
            'missing_for_inspection',
            'missing_for_completion',
        ]

    def get_changed_by_username(self, obj):
        user = obj.changed_by
        return getattr(user, 'username', None) if user else None

    def get_allowed_statuses(self, obj):
        current_id = obj.current_status_id
        return WorkOrderStatusSerializer(
            [s for s in list_active_statuses() if s.id != current_id],
            many=True,
        ).data

    def _missing_payload(self, obj, *, for_inspection=False, for_completion=False):
        missing = missing_progress_requirements(
            obj.event,
            for_inspection=for_inspection,
            for_completion=for_completion,
        )
        return [
            {'id': item.id, 'code': item.code, 'name': item.name}
            for item in missing
        ]

    def get_missing_for_inspection(self, obj):
        return self._missing_payload(obj, for_inspection=True)

    def get_missing_for_completion(self, obj):
        return self._missing_payload(obj, for_completion=True)


class WorkOrderStatusHistorySerializer(serializers.ModelSerializer):
    from_status_code = serializers.CharField(
        source='from_status.code', read_only=True, allow_null=True,
    )
    from_status_name = serializers.CharField(
        source='from_status.name', read_only=True, allow_null=True,
    )
    to_status_code = serializers.CharField(source='to_status.code', read_only=True)
    to_status_name = serializers.CharField(source='to_status.name', read_only=True)
    changed_by_username = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderStatusHistory
        fields = [
            'id',
            'event',
            'from_status',
            'from_status_code',
            'from_status_name',
            'to_status',
            'to_status_code',
            'to_status_name',
            'changed_by',
            'changed_by_username',
            'changed_at',
            'notes',
        ]

    def get_changed_by_username(self, obj):
        user = obj.changed_by
        return getattr(user, 'username', None) if user else None


class WorkOrderProgressCheckSerializer(serializers.ModelSerializer):
    item_code = serializers.CharField(source='item.code', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_sequence = serializers.IntegerField(source='item.sequence', read_only=True)
    is_required_for_inspection = serializers.BooleanField(
        source='item.is_required_for_inspection', read_only=True,
    )
    is_required_for_completion = serializers.BooleanField(
        source='item.is_required_for_completion', read_only=True,
    )
    is_informational = serializers.BooleanField(
        source='item.is_informational', read_only=True,
    )
    completed_by_username = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderProgressCheck
        fields = [
            'id',
            'event',
            'item',
            'item_code',
            'item_name',
            'item_sequence',
            'is_required_for_inspection',
            'is_required_for_completion',
            'is_informational',
            'is_done',
            'completed_at',
            'completed_by',
            'completed_by_username',
            'notes',
            'source',
            'source_document',
        ]
        read_only_fields = [
            'event',
            'item',
            'completed_at',
            'completed_by',
            'source',
            'source_document',
        ]

    def get_completed_by_username(self, obj):
        user = obj.completed_by
        return getattr(user, 'username', None) if user else None


class WorkOrderTransitionSerializer(serializers.Serializer):
    status_code = serializers.CharField(max_length=64)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class WorkOrderProgressUpdateSerializer(serializers.Serializer):
    is_done = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class WorkOrderOpsPermission(BasePermission):
    """Read status/progress with view_event; transition/update with change_event."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        action = getattr(view, 'action', None) or getattr(view, 'ops_action', None)
        if action in (
            'status',
            'status_history',
            'progress',
            'material_suggestions',
            'retrieve',
            'list',
        ):
            return user.has_perm('appschedule.view_event')
        if action in ('transition_status', 'update_progress', 'partial_update', 'update'):
            return user.has_perm('appschedule.change_event')
        return False


# ---------------------------------------------------------------------------
# Catalog ViewSets (admin / configuration)
# ---------------------------------------------------------------------------


class WorkOrderStatusViewSet(viewsets.ModelViewSet):
    """
    CRUD catalog — tenant admin.

    GET/POST /api/work-order-statuses/
    """

    queryset = WorkOrderStatus.objects.all()
    serializer_class = WorkOrderStatusSerializer
    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'is_active',
        'is_initial',
        'is_terminal',
        'requires_inspection_ready',
        'requires_completion_ready',
    ]

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as exc:
            raise DRFValidationError(
                'This status is referenced by Work Orders or history and cannot '
                'be deleted. Set is_active=False instead.'
            ) from exc


class WorkOrderProgressTemplateViewSet(viewsets.ModelViewSet):
    queryset = (
        WorkOrderProgressTemplate.objects.select_related('category')
        .prefetch_related('items')
        .all()
    )
    serializer_class = WorkOrderProgressTemplateSerializer
    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active', 'is_expected_for_work_account']


class WorkOrderProgressItemViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderProgressItem.objects.select_related('template').all()
    serializer_class = WorkOrderProgressItemSerializer
    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'template',
        'is_active',
        'is_required_for_inspection',
        'is_required_for_completion',
        'is_informational',
    ]


# ---------------------------------------------------------------------------
# Per-Event operational endpoints
# ---------------------------------------------------------------------------


class WorkOrderEventStatusViewSet(viewsets.ViewSet):
    """
    Nested operational actions on a published Event (Work Order).

    GET  /api/events/<event_id>/work-order-status/
    POST /api/events/<event_id>/work-order-status/transition/
    GET  /api/events/<event_id>/work-order-status/history/
    GET  /api/events/<event_id>/work-order-progress/
    PATCH /api/events/<event_id>/work-order-progress/<check_id>/
    GET  /api/events/<event_id>/work-order-progress/material-suggestions/
    """

    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated, WorkOrderOpsPermission]

    def _event(self, event_id):
        return get_object_or_404(
            Event.objects.select_related('crew__category', 'work_account'),
            pk=event_id,
        )

    def retrieve(self, request, event_id=None):
        self.ops_action = 'status'
        event = self._event(event_id)
        tracking = get_work_order_tracking(event)
        if tracking is None:
            tracking = ensure_initial_work_order_status(
                event=event,
                user=request.user,
            )
        if tracking is None:
            return Response(
                {
                    'detail': 'This event does not use Work Order status tracking.',
                    'is_absence': bool(event.is_absence),
                    'deleted': bool(event.deleted),
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(WorkOrderTrackingSerializer(tracking).data)

    @action(detail=False, methods=['post'], url_path='transition')
    def transition_status(self, request, event_id=None):
        self.ops_action = 'transition_status'
        event = self._event(event_id)
        body = WorkOrderTransitionSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            tracking = transition_work_order_status(
                event=event,
                status_code=body.validated_data['status_code'],
                notes=body.validated_data.get('notes', ''),
                user=request.user,
            )
        except DRFValidationError:
            raise
        return Response(WorkOrderTrackingSerializer(tracking).data)

    @action(detail=False, methods=['get'], url_path='history')
    def status_history(self, request, event_id=None):
        self.ops_action = 'status_history'
        event = self._event(event_id)
        qs = (
            WorkOrderStatusHistory.objects.filter(event=event)
            .select_related('from_status', 'to_status', 'changed_by')
            .order_by('changed_at', 'id')
        )
        return Response(WorkOrderStatusHistorySerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='progress')
    def progress(self, request, event_id=None):
        self.ops_action = 'progress'
        event = self._event(event_id)
        ensure_initial_work_order_status(event=event, user=request.user)
        qs = (
            WorkOrderProgressCheck.objects.filter(event=event)
            .select_related('item', 'completed_by')
            .order_by('item__sequence', 'id')
        )
        return Response(WorkOrderProgressCheckSerializer(qs, many=True).data)

    @action(
        detail=False,
        methods=['patch'],
        url_path=r'progress/(?P<check_id>[0-9]+)',
    )
    def update_progress(self, request, event_id=None, check_id=None):
        self.ops_action = 'update_progress'
        event = self._event(event_id)
        check = get_object_or_404(
            WorkOrderProgressCheck.objects.select_related('item'),
            pk=check_id,
            event=event,
        )
        body = WorkOrderProgressUpdateSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        check = set_progress_check(
            check=check,
            is_done=body.validated_data['is_done'],
            notes=body.validated_data.get('notes', ''),
            user=request.user,
        )
        return Response(WorkOrderProgressCheckSerializer(check).data)

    @action(detail=False, methods=['get'], url_path='progress/material-suggestions')
    def material_suggestions(self, request, event_id=None):
        self.ops_action = 'material_suggestions'
        event = self._event(event_id)
        return Response(suggest_material_delivered_from_transactions(event))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def work_account_progress_view(request, work_account_id):
    """
    GET /api/work-accounts/<id>/work-order-progress/
    Derived overall project state from expected phases + Work Orders.
    """
    if not request.user.has_perm('apptransactions.view_workaccount'):
        # Fallback: allow schedule viewers to see rollup for WA they can reach.
        if not request.user.has_perm('appschedule.view_event'):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    work_account = get_object_or_404(WorkAccount, pk=work_account_id)
    return Response(work_account_status_summary(work_account))
