"""
API de status tracking configurable (types distintos de Material Request).

MR sigue en material_request_api. Este módulo prepara el contrato para el
agente de frontend (Vue/PrimeVue) sin pantallas aquí.
"""

from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, BasePermission
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from appauth.authentication import TenantJWTAuthentication
from apptransactions.models import (
    Document,
    DocumentStatus,
    DocumentTracking,
    DocumentTrackingHistory,
)
from apptransactions.services.document_status import (
    get_document_tracking,
    next_previous_statuses,
    transition_document_status,
)


class DocumentStatusSerializer(serializers.ModelSerializer):
    document_type_code = serializers.CharField(
        source='document_type.type_code',
        read_only=True,
    )

    class Meta:
        model = DocumentStatus
        fields = [
            'id',
            'document_type',
            'document_type_code',
            'code',
            'name',
            'sequence',
            'is_initial',
            'is_terminal',
            'is_active',
        ]

    def validate(self, attrs):
        from apptransactions.models import DocumentType

        document_type = attrs.get(
            'document_type',
            getattr(self.instance, 'document_type', None),
        )
        if (
            document_type is not None
            and document_type.type_code in DocumentType.PROTECTED_TYPE_CODES
        ):
            raise serializers.ValidationError(
                'Material Request statuses are managed by the system and cannot be edited here.'
            )
        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(exc.message_dict) from exc
            raise

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise serializers.ValidationError(exc.message_dict) from exc
            raise


class DocumentStatusViewSet(viewsets.ModelViewSet):
    """
    CRUD de estados por tipo.

    GET  /api/document-statuses/?document_type=<id>
    POST /api/document-statuses/
    PATCH/PUT/DELETE /api/document-statuses/<id>/
    """

    queryset = DocumentStatus.objects.select_related('document_type').all()
    serializer_class = DocumentStatusSerializer
    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document_type', 'is_active', 'is_initial', 'is_terminal']

    def perform_destroy(self, instance):
        from apptransactions.models import DocumentType
        if instance.document_type.type_code in DocumentType.PROTECTED_TYPE_CODES:
            raise DRFValidationError(
                'Material Request statuses cannot be deleted.'
            )
        try:
            instance.delete()
        except ProtectedError as exc:
            raise DRFValidationError(
                'This status is referenced by documents or history and cannot '
                'be deleted. Set is_active=False instead.'
            ) from exc


class DocumentTrackingSerializer(serializers.ModelSerializer):
    status_code = serializers.CharField(source='current_status.code', read_only=True)
    status_name = serializers.CharField(source='current_status.name', read_only=True)
    status_sequence = serializers.IntegerField(
        source='current_status.sequence',
        read_only=True,
    )
    is_terminal = serializers.BooleanField(
        source='current_status.is_terminal',
        read_only=True,
    )
    document_type = serializers.IntegerField(
        source='document.document_type_id',
        read_only=True,
    )
    document_type_code = serializers.CharField(
        source='document.document_type.type_code',
        read_only=True,
    )
    changed_by_username = serializers.SerializerMethodField()
    next_status = serializers.SerializerMethodField()
    previous_status = serializers.SerializerMethodField()

    class Meta:
        model = DocumentTracking
        fields = [
            'id',
            'document',
            'document_type',
            'document_type_code',
            'current_status',
            'status_code',
            'status_name',
            'status_sequence',
            'is_terminal',
            'status_changed_at',
            'changed_by',
            'changed_by_username',
            'notes',
            'next_status',
            'previous_status',
        ]

    def get_changed_by_username(self, obj):
        user = obj.changed_by
        return getattr(user, 'username', None) if user else None

    def get_next_status(self, obj):
        nxt, _prev = next_previous_statuses(obj.document)
        if nxt is None:
            return None
        return {'id': nxt.id, 'code': nxt.code, 'name': nxt.name, 'sequence': nxt.sequence}

    def get_previous_status(self, obj):
        _nxt, prev = next_previous_statuses(obj.document)
        if prev is None:
            return None
        return {'id': prev.id, 'code': prev.code, 'name': prev.name, 'sequence': prev.sequence}


class DocumentTrackingHistorySerializer(serializers.ModelSerializer):
    from_status_code = serializers.CharField(
        source='from_status.code',
        read_only=True,
        allow_null=True,
    )
    from_status_name = serializers.CharField(
        source='from_status.name',
        read_only=True,
        allow_null=True,
    )
    to_status_code = serializers.CharField(source='to_status.code', read_only=True)
    to_status_name = serializers.CharField(source='to_status.name', read_only=True)
    changed_by_username = serializers.SerializerMethodField()

    class Meta:
        model = DocumentTrackingHistory
        fields = [
            'id',
            'document',
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


class DocumentStatusTransitionSerializer(serializers.Serializer):
    status_code = serializers.CharField(max_length=32)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class DocumentStatusActionPermission(BasePermission):
    """View/change document for status read/transition."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        action = getattr(view, 'action', None)
        # Lectura y transición: view_document. Editar líneas/campos sigue
        # exigiendo change_document en DocumentViewSet / formulario.
        if action in ('status', 'status_history', 'transition_status'):
            return user.has_perm('apptransactions.view_document')
        return False


class DocumentStatusActionsMixin:
    """
    Acciones anidadas en DocumentViewSet:

    GET  /api/documents/<id>/status/
    GET  /api/documents/<id>/status-history/
    POST /api/documents/<id>/transition-status/  {status_code, notes?}
    """

    @action(
        detail=True,
        methods=['get'],
        url_path='status',
        permission_classes=[IsAuthenticated, DocumentStatusActionPermission],
        authentication_classes=[TenantJWTAuthentication],
    )
    def status(self, request, pk=None):
        document = self.get_object()
        tracking = get_document_tracking(document)
        if tracking is None:
            return Response(
                {
                    'detail': 'This document has no status tracking.',
                    'uses_status_tracking': bool(
                        getattr(document.document_type, 'uses_status_tracking', False)
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(DocumentTrackingSerializer(tracking).data)

    @action(
        detail=True,
        methods=['get'],
        url_path='status-history',
        permission_classes=[IsAuthenticated, DocumentStatusActionPermission],
        authentication_classes=[TenantJWTAuthentication],
    )
    def status_history(self, request, pk=None):
        document = self.get_object()
        qs = (
            DocumentTrackingHistory.objects.filter(document=document)
            .select_related('from_status', 'to_status', 'changed_by')
            .order_by('changed_at', 'id')
        )
        return Response(DocumentTrackingHistorySerializer(qs, many=True).data)

    @action(
        detail=True,
        methods=['post'],
        url_path='transition-status',
        permission_classes=[IsAuthenticated, DocumentStatusActionPermission],
        authentication_classes=[TenantJWTAuthentication],
    )
    def transition_status(self, request, pk=None):
        document = self.get_object()
        body = DocumentStatusTransitionSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            transition_document_status(
                document=document,
                status_code=body.validated_data['status_code'],
                notes=body.validated_data.get('notes', ''),
                user=request.user,
            )
        except DRFValidationError:
            raise
        except Exception as exc:
            from django.core.exceptions import ValidationError as DjangoValidationError
            if isinstance(exc, DjangoValidationError):
                raise DRFValidationError(exc.message_dict) from exc
            raise
        tracking = get_document_tracking(document)
        return Response(DocumentTrackingSerializer(tracking).data)
