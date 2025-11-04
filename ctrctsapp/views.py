import base64
import logging
import json
import math
from decimal import Decimal

from rest_framework.views import APIView # Importa la clase APIView de Django Rest Framework, que es la base para crear vistas basadas en clases para APIs
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from .models import Contract, WorkPrice, ContractDetails, Builder, Job, HouseModel
from .serializers import (
    ContractSerializer, WorkPriceSerializer, ContractDetailsSerializer,
    BuilderSerializer, JobSerializer, HouseModelSerializer,
    JobFilteredByBuilderSerializer, HouseModelFilteredByJobSerializer,
    BuilderListSerializer, JobListSerializer, HouseListSerializer, ContractListSerializer, ContractListLiteSerializer
)
from django.db.models import Sum, Count
from django.db.models.functions import TruncWeek, TruncMonth
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .utils import geocode_address
from utils.datatable import handle_datatable_query

from weasyprint import (
    CSS,
    HTML,
)
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


def geocode_view(request):
    """
    Vista para geocodificar una dirección y devolver latitud y longitud.
    """
    address = request.GET.get(
        "address")  # La dirección debe ser pasada como parámetro GET
    if not address:
        return JsonResponse({"error": "Address parameter is required"}, status=400)

    latitude, longitude = geocode_address(address)
    if latitude and longitude:
        return JsonResponse({"address": address, "latitude": latitude, "longitude": longitude})
    else:
        return JsonResponse({"error": "Could not geocode address"}, status=404)


@permission_classes([AllowAny])
class UserDetailView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONT_URL}/reset-password-confirm?uid={uid}&token={token}"
            text = f'Hello {user.username}! \n\n\nSomeone requested a link to change your password. Click the link below to proceed. \n\n\n{reset_url}'
            html_content = render_to_string(
                "forgot_password_instructions.html",
                context={"username": user.username, 'reset_url': reset_url},
            )
            msg = EmailMultiAlternatives(
                'Reset password instructions',
                text,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return JsonResponse({'message': 'Email sent'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Error for recovery password'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request, uidb64, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_password = data.get('new_password')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return JsonResponse({'message': 'Password reset successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid token'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    permissions = list(request.user.get_all_permissions())
    # print(f"Permissions in View>>: {permissions}")
    return Response({'permissions': permissions})

@api_view(['GET'])
def validate_token(request):
    token_key = request.headers.get('Authorization')
    if token_key:
        # Obtener solo el valor del token
        token_key = token_key.replace('Token ', '')
        try:
            token = Token.objects.get(key=token_key)
            # print(f"Token found in View>>: {token}")
            return Response({'valid': True}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Permite acceso sin autenticación

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        # print(f"Intentando LoginView: {username} {password}")
        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            permissions = list(user.get_all_permissions())
            return Response({
                'token': token.key,
                'permissions': permissions
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # print("Request data:", request.data)
    username = request.data.get('username')
    password = request.data.get('password')
    # print(f"Intentando login_view: {username} {password}")
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    try:
        token = request.auth
        token.delete()  # Eliminar el token del usuario actual
        response = Response({"message": "Session closed successfully."}, status=200)
        response.delete_cookie('userPermissions')  # Eliminar la cookie de permisos
        
        # Agregar instrucciones para eliminar datos de sessionStorage
        response['X-Delete-Session-Storage'] = 'authToken,userPermissions'
        
        return response
    except AttributeError:
        return Response({"error": "No token found."}, status=400)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def monthly_summary(request): # BarChart.vue component
    # Calcular la fecha de hace 12 meses desde hoy
    twelve_months_ago = timezone.now() - timezone.timedelta(days=365)
    # Consulta que agrupa los contratos por mes y tipo de trabajo (trim o rough)
    summary = (
        Contract.objects
        .filter(doc_type="Contract", date_created__gte=twelve_months_ago) # solo contratos de los últimos 12 meses
        .annotate(month=TruncMonth('date_created'))  # Agrupar por mes
        .values('month', 'type')  # Seleccionar mes y tipo de trabajo
        .annotate(total_contracts=Count('id'))  # Contar contratos por grupo
        .order_by('month', 'type')  # Ordenar por mes y tipo
    )

    # Formatear los datos para devolver en JSON
    result = [
        {
            'month': entry['month'].strftime('%Y-%m'),  # Formato 'YYYY-MM'
            'job_type': entry['type'],  # Tipo de trabajo (trim o rough)
            'total_contracts': entry['total_contracts']  # Total de contratos en ese mes/tipo
        }
        for entry in summary
    ]

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_summary_list(request): # WeeklySummaryListComponent.vue component
    # Obtener fechas desde los parámetros de la solicitud
    start_date_str = request.GET.get('start_date', '2024-07-01')  # Default si no se proporciona
    end_date_str = request.GET.get('end_date', '2025-08-31')      # Default si no se proporciona

    # Convertir a objetos datetime
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    # end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    contracts = Contract.objects.filter(
        date_created__gte=start_date, doc_type="Contract"
    ).annotate(week=TruncWeek('date_created')).values(
        'week', 'job__name', 'type'
    ).annotate(total_contracts=Count('id')).order_by('week', 'job__name', 'type')

    result = []
    for contract in contracts:
        week_start = contract['week']
        week_end = week_start + timedelta(days=6)
        result.append({
            'start_of_week': week_start,
            'end_of_week': week_end,
            'job__name': contract['job__name'],
            'total_contracts': contract['total_contracts'],
        })

    return JsonResponse(result, safe=False)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def weekly_summary(request): # AreaChart.vue component
    # Calcular la fecha de hace 52 semanas desde hoy
    one_year_ago = timezone.now() - timezone.timedelta(weeks=52)

    # Consulta que agrupa por semana y tipo de contrato (Trim o Rough)
    data = (
        Contract.objects
        .filter(doc_type="Contract")
        .annotate(week=TruncWeek('date_created'))
        .values('week', 'type')
        .annotate(total=Sum('total'), total_contracts=Count('id'))
        .order_by('week', 'type')
    )

    # Formatear las fechas de la semana
    formatted_data = [
        {
            "week": entry["week"].strftime('%m-%d-%Y'),  # Formatear la fecha
            "type": entry["type"],
            "total": entry["total"],
            "total_contracts": entry["total_contracts"],
        }
        for entry in data
    ]

    return Response(formatted_data)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        # Log the incoming request data
        # print("Request data:", request.data)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # Log the serializer errors
        logger.error("Serializer errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)

        # Log the incoming request data
        #print("Request data (update):", request.data)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)

        # Log the serializer errors
        logger.error("Serializer errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def to_internal_value(self, data):
        if 'lot' in data and (data['lot'] is None or (data['lot'] == '' or data['lot'] == "null")):
            data['lot'] = None
        return super().to_internal_value(data)

    @action(detail=False, methods=['get'], url_path='validate-lot')
    def validate_contract(self, request):
        lot = request.GET.get('lot')
        type_ = request.GET.get('type')
        job_id = request.GET.get('job')
        address = request.GET.get('address')

        if not type_:
            return JsonResponse({'error': 'Type is a required parameter.'}, status=400)

        # Validar por lote
        if lot:
            if job_id == 'S/L':
                lot_exists = Contract.objects.filter(
                    lot=lot, type=type_, address=address).exists()
            else:
                lot_exists = Contract.objects.filter(
                    lot=lot, type=type_, job_id=job_id).exists()
            if lot_exists:
                return JsonResponse({'exists': True})

        # Validar por dirección cuando no hay lote
        if address and (not lot or lot == ''):
            address_exists = Contract.objects.filter(
                address=address, type=type_).exists()
            if address_exists:
                return JsonResponse({'exists': True})

        return JsonResponse({'exists': False})
    
    @action(detail=False, methods=['get'], url_path='user-contracts')
    def get_user_contracts(self, request):
        user = request.user
        # Check if the user is in any crew
        user_jobs = Job.objects.filter(crews__members=user)
        # If the user is part of a crew, filter contracts by user's jobs
        if user_jobs.exists(): 
            contracts = Contract.objects.filter(job__in=user_jobs)
        else:
            # If the user is not in any crew, return all contracts
            contracts = Contract.objects.all()
        serializer = self.get_serializer(contracts, many=True)
        return Response(serializer.data)    


    def perform_update(self, serializer):
        # Obtener el objeto original (instancia del contrato)
        instance = self.get_object()

        # Lista de campos relevantes que deben ser monitoreados para cambios
        relevant_fields = ['total', 'total_options', 'comment', 'lot', 'address']

        # Inicializamos la bandera needs_reprint en False
        needs_reprint = instance.needs_reprint  # Mantener el valor actual si no hay cambios

        # Iteramos sobre los campos relevantes para verificar si alguno ha cambiado
        for field in relevant_fields:
            # Obtener el nuevo valor (de la solicitud)
            new_value = self.request.data.get(field, None)
            # Obtener el valor actual del campo en la base de datos
            old_value = getattr(instance, field, None)

            # Compara valores de tipo str
            if isinstance(new_value, str) and isinstance(old_value, str):
                if new_value.strip() != old_value.strip():
                    needs_reprint = True  # Marcar como modificado si hay diferencia
                    break  # Si encontramos una diferencia, no es necesario seguir verificando

            # Compara valores de tipo decimal (por ejemplo, 'total' o 'total_options')
            elif isinstance(new_value, str) and isinstance(old_value, Decimal):
                try:
                    new_value = Decimal(new_value)  # Convertir el nuevo valor a Decimal
                    if new_value != old_value:
                        needs_reprint = True  # Marcar como modificado si hay diferencia
                        break
                except ValueError:
                    pass  # En caso de que no se pueda convertir, no cambiamos needs_reprint

            # Compara otros casos en los que los valores deben ser tratados como str (por ejemplo, 'lot', 'address')
            elif isinstance(new_value, str) and isinstance(old_value, str):
                if new_value.strip() != old_value.strip():
                    needs_reprint = True  # Marcar como modificado si hay diferencia
                    break

        # 🚀 **Modificación clave:** No marcar needs_reprint si es un "Bid"
        if instance.doc_type == 'Bid':
            needs_reprint = False

        # Guardamos el contrato con el valor actualizado de 'needs_reprint'
        serializer.save(needs_reprint=needs_reprint)

        # Realizamos la actualización del contrato
        super().perform_update(serializer)


    @action(detail=True, methods=['put'], url_path='mark-printed')
    def mark_as_printed(self, request, pk=None):
        # Obtener el contrato con el ID proporcionado en la URL
        contract = self.get_object()

        # Actualizar el campo 'needs_reprint' a False
        contract.needs_reprint = False
        contract.save()  # Guardar los cambios en la base de datos

        return Response({'status': 'Contract marked as printed'}) 

    # Remplaza datatable_contracts sin Lazy Load
    # Lazy Load para DataTable de Contratos con filtros por supervisor
    # Obsoleto: datatable-contracts eliminado en favor de contracts-provider

    @action(detail=False, methods=['get'], url_path='contracts-provider', permission_classes=[AllowAny])
    def contracts_provider(self, request):
        """
        Provider endpoint para BootstrapVue Next BTable (server-side):
        - page, per_page, search, ordering
        Devuelve: { items: [...], totalRows: N, stats: {...} }
        """
        try:
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 25))
            search = request.GET.get('search', '').strip()
            ordering = request.GET.get('ordering', '-id')

            qs = Contract.objects.all().select_related('builder', 'job', 'house_model')

            if search:
                from django.db.models import Q
                words = search.split()
                for w in words:
                    q = (
                        Q(id__icontains=w) |
                        Q(doc_type__icontains=w) |
                        Q(type__icontains=w) |
                        Q(builder__name__icontains=w) |
                        Q(job__name__icontains=w) |
                        Q(house_model__name__icontains=w) |
                        Q(lot__icontains=w) |
                        Q(address__icontains=w)
                    )
                    qs = qs.filter(q)

            # Ordering seguro
            safe_order_fields = {
                'id': 'id',
                '-id': '-id',
                'date_created': 'date_created',
                '-date_created': '-date_created',
                'total': 'total',
                '-total': '-total',
            }
            qs = qs.order_by(safe_order_fields.get(ordering, '-id'))

            total_rows = qs.count()
            start = (page - 1) * per_page
            end = start + per_page
            page_qs = qs[start:end]

            items = ContractListLiteSerializer(page_qs, many=True).data

            # Opcional: estadísticas superiores
            from django.db.models import Sum, Count
            stats = {
                'total': total_rows,
                'active': total_rows,  # placeholder, ajustar si hay flag
                'inactive': 0,
            }

            return Response({
                'items': items,
                'totalRows': total_rows,
                'stats': stats,
            })
        except Exception as e:
            logger.exception("contracts_provider error: %s", e)
            return Response({'detail': str(e)}, status=500)

class ContractDetailsViewSet(viewsets.ModelViewSet):
    queryset = ContractDetails.objects.all()
    serializer_class = ContractDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


class WorkPriceViewSet(viewsets.ModelViewSet):
    queryset = WorkPrice.objects.all()
    serializer_class = WorkPriceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        queryset = super().get_queryset()
        builder_id = self.request.query_params.get('builder', None)
        if builder_id:
            queryset = queryset.filter(builders__id=builder_id)
        return queryset


class BuilderViewSet(viewsets.ModelViewSet):
    queryset = Builder.objects.all()
    serializer_class = BuilderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        name = params.get('name')
        rfc = params.get('rfc')
        exclude_id = params.get('exclude_id')

        if name:
            qs = qs.filter(name__iexact=name.strip())
        if rfc:
            qs = qs.filter(rfc=rfc.strip())
        if exclude_id:
            try:
                qs = qs.exclude(pk=int(exclude_id))
            except (TypeError, ValueError):
                pass
        return qs

    @action(detail=True, methods=["get"])
    def workprices(self, request, pk=None):
        """Get Work Prices assigned to a specific Builder"""
        builder = self.get_object()
        work_prices = builder.work_prices.all()
        serializer = WorkPriceSerializer(work_prices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def assign_workprices(self, request, pk=None):
        """Assign Work Prices to a Builder"""
        builder = self.get_object()
        work_price_ids = request.data.get("work_price_ids", [])

        # Assign selected Work Prices
        builder.work_prices.set(WorkPrice.objects.filter(id__in=work_price_ids))

        return Response({"message": "Assignments updated successfully"}, status=status.HTTP_200_OK)


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().select_related("builder").prefetch_related("crews")
    serializer_class = JobSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    @action(detail=False, methods=['get'])
    def jobs_by_builder(self, request):
        builder_id = request.query_params.get('builder_id')
        if builder_id:
            jobs = Job.objects.filter(builder_id=builder_id)
        else:
            jobs = Job.objects.none()
        serializer = JobFilteredByBuilderSerializer(jobs, many=True)
        return Response(serializer.data)


class HouseModelViewSet(viewsets.ModelViewSet):
    queryset = HouseModel.objects.all()
    serializer_class = HouseModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    def get_serializer_context(self):
        """
        Add builder_id to serializer context for validation
        """
        context = super().get_serializer_context()
        builder_id = self.request.data.get('builder_id')
        print(f"DEBUG VIEWSET: builder_id from request.data = {builder_id}")
        if builder_id:
            context['builder_id'] = builder_id
        print(f"DEBUG VIEWSET: context = {context}")
        return context

    @action(detail=False, methods=['get'])
    def house_models_by_job(self, request):
        job_id = request.query_params.get('job_id')
        if job_id:
            house_models = HouseModel.objects.filter(jobs__id=job_id)
        else:
            house_models = HouseModel.objects.none()
        serializer = HouseModelFilteredByJobSerializer(house_models, many=True)
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_house_model_jobs(request, house_model_id):
    try:
        house_model = HouseModel.objects.get(id=house_model_id)
        jobs = house_model.jobs.all()  # Get all jobs related to the house model

        # Prepare the data to return
        job_data = [
            {
                "id": job.id,
                "name": job.name,
                "builder_id": job.builder.id,
                "builder_name": job.builder.name
            }
            for job in jobs
        ]

        return JsonResponse({"houseModel": {"id": house_model.id, "name": house_model.name}, "jobs": job_data})
    except HouseModel.DoesNotExist:
        return JsonResponse({"error": "House Model not found"}, status=404)


def lighting_circuits(sqft):
  if sqft == 0:
    return 0
  num = sqft * 3 / 120 / 15
  return math.ceil(num)  # Siempre redondea hacia arriba

@api_view(['GET'])
def download_contract_pdf(request, contract_id):
    try:
        contract = Contract.objects.get(id=contract_id)

        if contract.type == "Trim":
            details = contract.contract_details.filter(cdtrim__gt=0)
        else:  # If type is "Rough"
            details = contract.contract_details.filter(cdrough__gt=0)
            
        mid_index = details.count() // 2  # Integer division
        left_details = details[:mid_index]
        right_details = details[mid_index:]
        
        domain = request.get_host()
        if 'phoenixelectricandair' in domain:
            tenant_logo = 'media/tenant_logos/Logo-phoenix-w.png'
        elif '192.168.0.248:8000' in domain or 'division16llc' in domain:
            tenant_logo = 'media/tenant_logos/Logo-division-w.png'
        else:
            tenant_logo = 'media/tenant_logos/default-logo.png'

        logo_url = request.build_absolute_uri('/' + tenant_logo)

        # Prepare the data to return
        context = {
            'contract': contract,
            'left_details': left_details,
            'right_details': right_details,
            'lighting_circuits': lighting_circuits(contract.sqft),
            'logo_url': logo_url,
        }
        font_config = FontConfiguration()

        html = render_to_string('contract_pdf.html', context)

        pdf_file = HTML(string=html).write_pdf(font_config=font_config)
        response = {
            'file': base64.b64encode(pdf_file),
            'filename': f'contract_{contract.pk}.pdf',
            'file_type': 'application/pdf'
        }
        return Response(response, status=status.HTTP_200_OK)
    except HouseModel.DoesNotExist:
        return JsonResponse({"error": "House Model not found"}, status=404)


class BuilderReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = Builder.objects.all()
    serializer_class = BuilderListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class JobReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Job.objects.all().select_related('builder')
        builder_id = self.request.query_params.get('builder_id')
        q = self.request.query_params.get('q')

        if builder_id:
            qs = qs.filter(builder_id=builder_id)

        if q:
            qs = qs.filter(name__icontains=q)

        return qs.order_by('name')


class HouseReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = HouseModel.objects.all()
    serializer_class = HouseListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
