from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q

class DataTablePagination(LimitOffsetPagination):
    default_limit = 25
    limit_query_param = 'length'
    offset_query_param = 'start'


def handle_datatable_query(request, queryset, serializer_class, search_fields=None):
    draw = request.GET.get('draw', 1)
    search_value = request.GET.get('search[value]', '')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 25))

    # Filtro de búsqueda
    if search_value and search_fields:
        words = search_value.strip().split()  # Separa por espacios
        for word in words:
            word_filter = Q()
            for field in search_fields:
                word_filter |= Q(**{f"{field}__icontains": word})
            queryset = queryset.filter(word_filter)

    # Ordenamiento
    order_column = request.GET.get('order[0][column]')
    order_dir = request.GET.get('order[0][dir]', 'asc')

    if order_column:
        column_data = request.GET.get(f'columns[{order_column}][data]')
        if column_data:
            # ⚠️ IMPORTANTE: needs_reprint es booleano, así que si intentan ordenarlo, hay que permitirlo
            order_by = column_data if order_dir == 'asc' else f'-{column_data}'
            # Si es needs_reprint, agregar id secundariamente
            if column_data == 'needs_reprint':
                queryset = queryset.order_by(f"{'-' if order_dir == 'desc' else ''}needs_reprint", '-id')
            else:
                queryset = queryset.order_by(order_by)
    else:
        # Orden por defecto si no se manda ninguno desde el frontend
        queryset = queryset.order_by('-needs_reprint', '-id')

    total_records = queryset.count()

    # Paginación
    paginator = DataTablePagination()
    page = paginator.paginate_queryset(queryset, request)

    # Ajuste para LimitOffsetPagination
    filtered_count = total_records  # por defecto
    if search_value and search_fields:
        filtered_count = queryset.count()

    serializer = serializer_class(page, many=True)

    return Response({
        'draw': int(draw),
        'recordsTotal': total_records,
        'recordsFiltered': filtered_count,
        'data': serializer.data
    })