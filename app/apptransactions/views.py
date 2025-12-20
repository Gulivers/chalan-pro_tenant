import base64
from datetime import datetime
from django.db.models import Q, Prefetch
from django.utils.dateparse import parse_datetime
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import viewsets, status, filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, AllowAny
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from .models import (
    DocumentType, PartyType, PartyCategory, Party, Document, DocumentLine,
    PriceType, WorkAccount, TransactionFavorite
)
from .serializers import (
    DocumentTypeSerializer,PartyTypeSerializer,PartyCategorySerializer,PartySerializer,
    DocumentSerializer, DocumentLineSerializer, WorkAccountSerializer,
    TransactionFavoriteSerializer, TransactionFavoriteImportSerializer
)
from rest_framework.authentication import TokenAuthentication


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
class PartyTypeViewSet(viewsets.ModelViewSet):
    queryset = PartyType.objects.all()
    serializer_class = PartyTypeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
class PartyCategoryViewSet(viewsets.ModelViewSet):
    queryset = PartyCategory.objects.all()
    serializer_class = PartyCategorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    # Filtros / búsqueda / orden
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'category', 'types', 'customer_rank', 'supplier_rank']
    search_fields = ['name', 'rfc', 'email', 'phone', 'city', 'state']
    ordering_fields = ['name', 'customer_rank', 'supplier_rank', 'id']
    ordering = ['name']
    
class WorkAccountViewSet(viewsets.ModelViewSet):
    queryset = WorkAccount.objects.select_related("builder", "job", "house_model", "default_price_type").all()
    serializer_class = WorkAccountSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "builder__name", "job__name", "house_model__name", "lot", "address", "city", "zipcode"]
    ordering_fields = ["id", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        # oJo: permitir ?active_only=1 en el autocomplete
        active_only = self.request.query_params.get("active_only")
        if active_only in ("1", "true", "True"):
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        """Asigna automáticamente el usuario actual al campo created_by"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="sync-schedule-titles")
    def sync_schedule_titles(self, request, pk=None):
        """
        Update all related Events and EventDrafts titles (and context fields)
        from the current WorkAccount. Overwrites any customized titles.
        Returns counts of updated records.
        """
        try:
            work_account = self.get_object()

            # Import here to avoid circular imports
            from appschedule.models import Event, EventDraft

            # Only non-absence items
            events_qs = Event.objects.filter(work_account=work_account, is_absence=False)
            drafts_qs = EventDraft.objects.filter(work_account=work_account, is_absence=False)

            # Bulk update: keep context fields synced too
            updated_event_count = events_qs.update(
                title=(work_account.title or '').upper(),
                builder=work_account.builder,
                job=work_account.job,
                house_model=work_account.house_model,
                lot=work_account.lot,
                address=work_account.address,
            )

            updated_draft_count = drafts_qs.update(
                title=(work_account.title or '').upper(),
                builder=work_account.builder,
                job=work_account.job,
                house_model=work_account.house_model,
                lot=work_account.lot,
                address=work_account.address,
            )

            return Response(
                {
                    "message": "Schedule titles synchronized successfully.",
                    "updated_events": updated_event_count,
                    "updated_drafts": updated_draft_count,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to synchronize schedule titles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
# Documentos
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = (
        Document.objects
        .select_related("document_type", "builder", "created_by")
        .prefetch_related(
            Prefetch("lines", queryset=DocumentLine.objects.select_related("product", "unit", "price_type", "brand"))
        )
        .order_by("-id")
    )
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["notes", "builder__name", "job", "lot", "document_type__type_code"]
    ordering_fields = ["id", "date", "total_amount"]
    filterset_fields = ["document_type", "builder", "is_active"]

    # Filtro por rango de fechas ?date_from=2025-09-01&date_to=2025-09-30
    def get_queryset(self):
        qs = super().get_queryset()
        df = self.request.query_params.get("date_from")
        dt = self.request.query_params.get("date_to")
        if df:
            try:
                qs = qs.filter(date__gte=parse_datetime(df) or datetime.fromisoformat(df))
            except Exception:
                pass
        if dt:
            try:
                qs = qs.filter(date__lte=parse_datetime(dt) or datetime.fromisoformat(dt))
            except Exception:
                pass
        return qs

    @action(detail=True, methods=["post"], url_path="recalculate")
    def recalculate(self, request, pk=None):
        """Forzar recálculo de totales (por si se manipularon líneas fuera del flujo habitual)."""
        doc = self.get_object()
        doc.calculate_totals()
        ser = self.get_serializer(doc)
        return Response(ser.data)

    @action(detail=True, methods=["get"], url_path="lines")
    def list_lines(self, request, pk=None):
        doc = self.get_object()
        ser = DocumentLineSerializer(doc.lines.all(), many=True)
        return Response(ser.data)


# Líneas (CRUD independiente)
class DocumentLineViewSet(viewsets.ModelViewSet):
    queryset = (
        DocumentLine.objects
        .select_related("document", "product", "unit", "warehouse", "price_type", "brand")
        .order_by("-id")
    )
    serializer_class = DocumentLineSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["product__name", "document__notes", "document__lot", "document__job", "document__builder__name"]
    ordering_fields = ["id", "quantity", "unit_price", "final_price"]
    filterset_fields = ["document", "product", "warehouse", "price_type", "brand"]

    def perform_destroy(self, instance):
        doc = instance.document
        super().perform_destroy(instance)
        # Al eliminar, recalcular totales del documento
        if doc:
            doc.calculate_totals()


class TransactionFavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar favoritos de transacciones.
    Permite CRUD completo y funcionalidades especiales de importación.
    """
    serializer_class = TransactionFavoriteSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    filterset_fields = ['is_active']
    
    def get_queryset(self):
        """Obtener todos los favoritos activos"""
        return TransactionFavorite.objects.filter(
            is_active=True
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Asignar automáticamente el usuario actual"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Actualizar favorito"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete - marcar como inactivo en lugar de eliminar"""
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['get'], url_path='import')
    def import_favorite(self, request, pk=None):
        """
        Endpoint especial para importar datos de un favorito.
        Retorna los datos estructurados listos para usar en el formulario.
        """
        try:
            favorite = self.get_object()
            
            # Retornar datos estructurados para importar
            serializer = TransactionFavoriteImportSerializer(
                favorite,
                context={'request': request}
            )
            return Response(serializer.data)
            
        except TransactionFavorite.DoesNotExist:
            return Response(
                {'error': 'Favorito no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al importar favorito: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='create-from-transaction')
    def create_from_transaction(self, request):
        """
        Crear favorito desde datos de transacción actual.
        Endpoint para guardar la transacción actual como favorito.
        """
        try:
            # Validar datos de entrada
            name = request.data.get('name')
            description = request.data.get('description', '')
            document_data = request.data.get('document_data')
            lines_data = request.data.get('lines_data')
            
            if not name:
                return Response(
                    {'error': 'El nombre es requerido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not document_data or not lines_data:
                return Response(
                    {'error': 'document_data y lines_data son requeridos.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear el favorito
            favorite_data = {
                'name': name,
                'description': description,
                'document_data': document_data,
                'lines_data': lines_data
            }
            
            serializer = TransactionFavoriteSerializer(
                data=favorite_data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                favorite = serializer.save()
                return Response(
                    {
                        'message': 'Favorito creado exitosamente.',
                        'favorite': TransactionFavoriteSerializer(favorite).data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': 'Datos inválidos.', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Error al crear favorito: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='update-from-transaction')
    def update_from_transaction(self, request, pk=None):
        """
        Actualizar favorito con datos de transacción actual.
        Endpoint para actualizar un favorito existente con datos actuales.
        """
        try:
            favorite = self.get_object()
            
            # Validar datos de entrada
            document_data = request.data.get('document_data')
            lines_data = request.data.get('lines_data')
            
            if not document_data or not lines_data:
                return Response(
                    {'error': 'document_data y lines_data son requeridos.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actualizar datos del favorito
            update_data = {
                'document_data': document_data,
                'lines_data': lines_data
            }
            
            # Permitir actualizar nombre y descripción si se envían
            if 'name' in request.data:
                update_data['name'] = request.data['name']
            if 'description' in request.data:
                update_data['description'] = request.data['description']
            
            serializer = TransactionFavoriteSerializer(
                favorite,
                data=update_data,
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                updated_favorite = serializer.save()
                return Response(
                    {
                        'message': 'Favorito actualizado exitosamente.',
                        'favorite': TransactionFavoriteSerializer(updated_favorite).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Datos inválidos.', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except TransactionFavorite.DoesNotExist:
            return Response(
                {'error': 'Favorito no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar favorito: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_transaction_pdf(request, document_id):
    """
    Vista para generar y descargar el PDF de una transacción.
    Similar a download_contract_pdf pero para documentos de transacciones.
    """
    try:
        # Obtener el documento con todas las relaciones necesarias
        document = get_object_or_404(
            Document.objects.select_related(
                'document_type', 
                'builder', 
                'created_by',
                'work_account',
                'work_account__builder',
                'work_account__job',
                'work_account__house_model'
            ).prefetch_related(
                Prefetch(
                    'lines',
                    queryset=DocumentLine.objects.select_related(
                        'product', 
                        'unit', 
                        'price_type', 
                        'brand',
                        'warehouse'
                    )
                )
            ),
            id=document_id
        )

        # Determinar el logo basado en el dominio (similar al contrato)
        domain = request.get_host()
        if 'phoenixelectricandair' in domain:
            tenant_logo = 'media/tenant_logos/Logo-phoenix-w.png'
        elif '192.168.0.248:8000' in domain or 'division16llc' in domain:
            tenant_logo = 'media/tenant_logos/Logo-division-w.png'
        else:
            tenant_logo = 'media/tenant_logos/default-logo.png'

        logo_url = request.build_absolute_uri('/' + tenant_logo)

        # Preparar el contexto para el template
        context = {
            'document': document,
            'logo_url': logo_url,
        }

        # Configurar fuentes
        font_config = FontConfiguration()

        # Renderizar el HTML
        html = render_to_string('transaction_pdf.html', context)

        # Generar el PDF
        pdf_file = HTML(string=html).write_pdf(font_config=font_config)

        # Preparar la respuesta
        response = {
            'file': base64.b64encode(pdf_file).decode('utf-8'),
            'filename': f'{document.document_type.type_code}_{document.id}.pdf',
            'file_type': 'application/pdf'
        }

        return Response(response, status=status.HTTP_200_OK)

    except Document.DoesNotExist:
        return JsonResponse(
            {"error": "Documento no encontrado"}, 
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Error al generar PDF: {str(e)}"}, 
            status=500
        )