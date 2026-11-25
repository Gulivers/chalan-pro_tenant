"""Lightweight liveness/readiness probe for Docker healthchecks and uptime monitors.

Keep this path cheap: no PDF, no business logic, no auth. A failed SELECT 1
returns 503 (Postgres down) without blocking Daphne under load for long.
"""

from __future__ import annotations

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "error", "db": "down"}, status=503)

    return JsonResponse({"status": "ok"}, status=200)
