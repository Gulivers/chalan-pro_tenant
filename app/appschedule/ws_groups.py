"""Channel-layer group names scoped to the current tenant schema."""
from django.db import connection


def tenant_ws_group(name: str, schema: str | None = None) -> str:
    """Prefix a group so one workspace cannot receive another's events."""
    raw_schema = schema or getattr(connection, 'schema_name', None) or 'public'

    def _clean(value: str) -> str:
        return ''.join(
            ch if ch.isalnum() or ch in '-_.' else '_'
            for ch in str(value)
        )

    return f'{_clean(raw_schema)}.{_clean(name)}'[:99]
