import django_filters
from django.db.models import Q
from .models import EventDraft


class EventDraftFilter(django_filters.rest_framework.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    start_at = django_filters.DateTimeFilter(method='filter_by_date_range')
    end_at = django_filters.DateTimeFilter(method='filter_by_date_range')

    class Meta:
        model = EventDraft
        fields = ['title', 'start_at', 'end_at']

    def filter_by_date_range(self, queryset, name, value):
        if name == 'start_at':
            lookup = 'gte'
        elif name == 'end_at':
            lookup = 'lte'
        else:
            return queryset  # No debería llegar aquí

        q = Q()
        if self.request.query_params.get('start_at'):
            start_at_param = self.request.query_params.get('start_at')
            q &= (Q(date__lte=start_at_param,
                    end_dt__gte=start_at_param) |  # Empieza antes o en el inicio y termina después o en el inicio
                  Q(date__gte=start_at_param,
                    date__lte=self.request.query_params.get('end_at', start_at_param)) |  # Empieza dentro del rango
                  Q(end_dt__gte=start_at_param,
                    end_dt__lte=self.request.query_params.get('end_at', start_at_param)))  # Termina dentro del rango

        if self.request.query_params.get('end_at'):
            end_at_param = self.request.query_params.get('end_at')
            q &= (Q(date__lte=end_at_param,
                    end_dt__gte=end_at_param) |  # Empieza antes o en el fin y termina después o en el fin
                  Q(date__gte=self.request.query_params.get('start_at', end_at_param),
                    date__lte=end_at_param) |  # Empieza dentro del rango
                  Q(end_dt__gte=self.request.query_params.get('start_at', end_at_param),
                    end_dt__lte=end_at_param))  # Termina dentro del rango

        return queryset.filter(q).distinct()
