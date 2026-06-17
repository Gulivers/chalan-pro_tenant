from django.conf import settings
from django.utils import timezone

from appsearch.models import SearchTelemetry


def record_search_telemetry(
    *,
    operation: str,
    latency_ms: int,
    result_count: int,
    query_length: int = 0,
) -> None:
    if not getattr(settings, 'SEARCH_TELEMETRY_ENABLED', True):
        return

    SearchTelemetry.objects.create(
        operation=operation,
        latency_ms=max(0, int(latency_ms)),
        result_count=max(0, int(result_count)),
        query_length=max(0, min(int(query_length), 500)),
    )


def percentile(values: list[int], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = int(round((pct / 100.0) * (len(ordered) - 1)))
    index = max(0, min(index, len(ordered) - 1))
    return float(ordered[index])


def summarize_telemetry(*, operation: str | None = None, days: int = 7) -> dict:
    since = timezone.now() - timezone.timedelta(days=max(1, days))
    qs = SearchTelemetry.objects.filter(created_at__gte=since)
    if operation:
        qs = qs.filter(operation=operation)

    latencies = list(qs.values_list('latency_ms', flat=True))
    total = len(latencies)
    if total == 0:
        return {
            'days': days,
            'operation': operation or 'all',
            'count': 0,
            'latency_avg_ms': None,
            'latency_p95_ms': None,
        }

    return {
        'days': days,
        'operation': operation or 'all',
        'count': total,
        'latency_avg_ms': round(sum(latencies) / total, 2),
        'latency_p95_ms': round(percentile(latencies, 95) or 0, 2),
    }
