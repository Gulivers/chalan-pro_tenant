"""
API de Solicitud de Materiales (Material Request).

Este módulo define la interfaz de API para gestionar las solicitudes de materiales en el sistema JobRhythm.
Permite que los usuarios creen nuevas solicitudes de materiales asociadas a cuentas y órdenes de trabajo, así como consultar sus detalles y estados.

Características principales de esta API:
- No permite la creación de documentos de Picking (PK) ni de Órdenes de Compra (PO), ya que estos se gestionan en flujos separados.
- Expone endpoints REST que permiten listar, consultar y crear solicitudes de materiales (tipo MR), así como transicionar su estado según el flujo operativo.
- Valida los permisos de usuario para cada acción.
- Integra validaciones y reglas de negocio para asegurar la trazabilidad y control de los movimientos de inventario originados por una solicitud de materiales.
"""

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from django.db.models import ProtectedError, Q

from appinventory.models import Product
from appschedule.models import Event
from apptransactions.models import (
    Document,
    DocumentStatus,
    DocumentTrackingHistory,
)
from apptransactions.services.material_request import (
    MR_TYPE_CODE,
    create_material_request,
    delete_material_request,
    transition_material_request,
    update_material_request_lines,
)
from appauth.authentication import TenantJWTAuthentication


class MaterialRequestPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if view.action in ('list', 'retrieve'):
            return user.has_perm('apptransactions.view_document')
        if view.action == 'create':
            return user.has_perm('apptransactions.add_document')
        if view.action in ('transition', 'lines'):
            return user.has_perm('apptransactions.change_document')
        if view.action == 'destroy':
            return user.has_perm('apptransactions.delete_document')
        return False


def _positive_int(value, default):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


_LIST_ORDERING = {
    'id': 'id',
    'document_number': 'document_number',
    'work_account_title': 'work_account__title',
    'phase': 'work_order__crew__category__name',
    'requested_by': 'created_by__username',
    'status_name': 'tracking__current_status__name',
    'date': 'date',
}


def _list_ordering(param):
    raw = (param or '-id').strip()
    descending = raw.startswith('-')
    name = raw[1:] if descending else raw
    field = _LIST_ORDERING.get(name)
    if not field:
        return '-id'
    return f'-{field}' if descending else field


def _apply_material_request_search(queryset, search):
    words = (search or '').split()
    for word in words:
        queryset = queryset.filter(
            Q(document_number__icontains=word)
            | Q(work_account__title__icontains=word)
            | Q(work_order__crew__category__name__icontains=word)
            | Q(created_by__username__icontains=word)
            | Q(tracking__current_status__name__icontains=word)
            | Q(tracking__current_status__code__icontains=word)
        )
    return queryset


class MaterialRequestLineInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)


class MaterialRequestCreateSerializer(serializers.Serializer):
    work_account = serializers.PrimaryKeyRelatedField(
        queryset=Document._meta.get_field('work_account').related_model.objects.all()
    )
    work_order = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    lines = MaterialRequestLineInputSerializer(many=True)

    def create(self, validated_data):
        return create_material_request(
            work_account=validated_data['work_account'],
            work_order=validated_data['work_order'],
            lines=validated_data['lines'],
            notes=validated_data.get('notes') or '',
            user=self.context['request'].user,
        )


def _phase_name(document):
    event = getattr(document, 'work_order', None)
    if not event or not getattr(event, 'crew_id', None):
        return ''
    crew = event.crew
    category = getattr(crew, 'category', None)
    return category.name if category else ''


class MaterialRequestLineSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = serializers.IntegerField(source='product_id')
    product_name = serializers.CharField(source='product.name')
    sku = serializers.CharField(source='product.sku')
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)


class MaterialRequestHistorySerializer(serializers.ModelSerializer):
    from_status = serializers.CharField(source='from_status.code', allow_null=True)
    from_status_name = serializers.CharField(source='from_status.name', allow_null=True)
    to_status = serializers.CharField(source='to_status.code')
    to_status_name = serializers.CharField(source='to_status.name')
    changed_by_username = serializers.SerializerMethodField()

    class Meta:
        model = DocumentTrackingHistory
        fields = [
            'id',
            'from_status',
            'from_status_name',
            'to_status',
            'to_status_name',
            'changed_by_username',
            'changed_at',
            'notes',
        ]

    def get_changed_by_username(self, obj):
        user = obj.changed_by
        return user.username if user else ''


class MaterialRequestSerializer(serializers.ModelSerializer):
    document_number = serializers.CharField()
    work_account_title = serializers.CharField(source='work_account.title', default='')
    work_order = serializers.IntegerField(source='work_order_id', allow_null=True)
    phase = serializers.SerializerMethodField()
    requested_by = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()
    next_status = serializers.SerializerMethodField()
    next_status_name = serializers.SerializerMethodField()
    previous_status = serializers.SerializerMethodField()
    previous_status_name = serializers.SerializerMethodField()
    lines = MaterialRequestLineSerializer(many=True)
    history = MaterialRequestHistorySerializer(source='tracking_history', many=True)

    class Meta:
        model = Document
        fields = [
            'id',
            'document_number',
            'date',
            'work_account',
            'work_account_title',
            'work_order',
            'phase',
            'requested_by',
            'notes',
            'status',
            'status_name',
            'next_status',
            'next_status_name',
            'previous_status',
            'previous_status_name',
            'lines',
            'history',
        ]

    def get_phase(self, obj):
        return _phase_name(obj)

    def get_requested_by(self, obj):
        user = obj.created_by
        return user.username if user else ''

    def _tracking(self, obj):
        return getattr(obj, 'tracking', None)

    def get_status(self, obj):
        tracking = self._tracking(obj)
        if not tracking:
            return ''
        return tracking.current_status.code

    def get_status_name(self, obj):
        tracking = self._tracking(obj)
        if not tracking:
            return ''
        return tracking.current_status.name

    def _adjacent_status(self, obj, delta, cache_attr):
        tracking = self._tracking(obj)
        if not tracking:
            return None
        if delta > 0 and tracking.current_status.is_terminal:
            return None
        if hasattr(obj, cache_attr):
            return getattr(obj, cache_attr)
        found = DocumentStatus.objects.filter(
            document_type_id=obj.document_type_id,
            sequence=tracking.current_status.sequence + delta,
            is_active=True,
        ).first()
        setattr(obj, cache_attr, found)
        return found

    def get_next_status(self, obj):
        nxt = self._adjacent_status(obj, 1, '_mr_next_status')
        return nxt.code if nxt else None

    def get_next_status_name(self, obj):
        nxt = self._adjacent_status(obj, 1, '_mr_next_status')
        return nxt.name if nxt else None

    def get_previous_status(self, obj):
        previous = self._adjacent_status(obj, -1, '_mr_previous_status')
        return previous.code if previous else None

    def get_previous_status_name(self, obj):
        previous = self._adjacent_status(obj, -1, '_mr_previous_status')
        return previous.name if previous else None


class MaterialRequestListSerializer(MaterialRequestSerializer):
    """Fila de /material-requests. El detalle sigue incluyendo líneas e historial."""

    class Meta:
        model = Document
        fields = [
            'id',
            'document_number',
            'date',
            'work_account',
            'work_account_title',
            'work_order',
            'phase',
            'requested_by',
            'status',
            'status_name',
        ]


class MaterialRequestLineChangeItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)


class MaterialRequestLineChangeSerializer(serializers.Serializer):
    lines = MaterialRequestLineChangeItemSerializer(many=True)

    def validate_lines(self, value):
        if not value:
            raise serializers.ValidationError('Add at least one line change.')
        return value


class MaterialRequestTransitionSerializer(serializers.Serializer):
    status_code = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class MaterialRequestViewSet(viewsets.GenericViewSet):
    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated, MaterialRequestPermission]
    queryset = Document.objects.filter(document_type__type_code=MR_TYPE_CODE)

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related(
                'work_account',
                'work_order__crew__category',
                'created_by',
                'tracking__current_status',
                'document_type',
            )
            .prefetch_related(
                'lines__product',
                'tracking_history__from_status',
                'tracking_history__to_status',
                'tracking_history__changed_by',
            )
            .order_by('-id')
        )
        work_account = self.request.query_params.get('work_account')
        work_order = self.request.query_params.get('work_order')
        status_code = self.request.query_params.get('status')
        if work_account:
            qs = qs.filter(work_account_id=work_account)
        if work_order:
            qs = qs.filter(work_order_id=work_order)
        if status_code:
            qs = qs.filter(tracking__current_status__code=status_code)
        return qs

    def list(self, request):
        qs = (
            Document.objects.filter(document_type__type_code=MR_TYPE_CODE)
            .select_related(
                'work_account',
                'work_order__crew__category',
                'created_by',
                'tracking__current_status',
            )
        )
        work_account = request.query_params.get('work_account')
        work_order = request.query_params.get('work_order')
        if work_account:
            qs = qs.filter(work_account_id=work_account)
        if work_order:
            qs = qs.filter(work_order_id=work_order)
        qs = _apply_material_request_search(qs, request.query_params.get('search', ''))
        closed = qs.filter(tracking__current_status__code='closed').count()
        total = qs.count()
        status_code = (request.query_params.get('status') or '').strip()
        if status_code:
            qs = qs.filter(tracking__current_status__code=status_code)
        qs = qs.order_by(_list_ordering(request.query_params.get('ordering')))
        total_rows = qs.count()
        page = _positive_int(request.query_params.get('page'), 1)
        per_page = min(_positive_int(request.query_params.get('per_page'), 25), 200)
        start = (page - 1) * per_page
        serializer = MaterialRequestListSerializer(qs[start:start + per_page], many=True)
        return Response({
            'items': serializer.data,
            'totalRows': total_rows,
            'stats': {
                'total': total,
                'open': total - closed,
                'closed': closed,
            },
        })

    def retrieve(self, request, pk=None):
        document = self.get_object()
        return Response(MaterialRequestSerializer(document).data)

    def create(self, request):
        if not request.user.has_perm('apptransactions.add_document'):
            raise PermissionDenied()
        serializer = MaterialRequestCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        try:
            document = serializer.save()
        except ValidationError:
            raise
        document = self.get_queryset().get(pk=document.pk)
        return Response(MaterialRequestSerializer(document).data, status=201)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        document = self.get_object()
        body = MaterialRequestTransitionSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        transition_material_request(
            document=document,
            status_code=body.validated_data['status_code'],
            notes=body.validated_data.get('notes') or '',
            user=request.user,
        )
        document = self.get_queryset().get(pk=document.pk)
        return Response(MaterialRequestSerializer(document).data)

    @action(detail=True, methods=['patch'])
    def lines(self, request, pk=None):
        document = self.get_object()
        body = MaterialRequestLineChangeSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        update_material_request_lines(
            document=document,
            lines=body.validated_data['lines'],
        )
        document = self.get_queryset().get(pk=document.pk)
        return Response(MaterialRequestSerializer(document).data)

    def destroy(self, request, pk=None):
        document = self.get_object()
        try:
            delete_material_request(document=document)
        except ProtectedError as exc:
            raise ValidationError(
                'This material request cannot be deleted while related records exist.'
            ) from exc
        return Response(status=status.HTTP_204_NO_CONTENT)
