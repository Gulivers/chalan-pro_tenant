"""Typed request contract for POST /api/assistant/query/."""

from __future__ import annotations

from typing import Any


SCHEMA_VERSION = '1'
MAX_MESSAGE_LENGTH = 2000
ALLOWED_ENTITY_TYPES = frozenset({'document', 'builder', None})
# tenant_id / user_id / schema_name are never accepted as authority.
IGNORED_AUTHORITY_KEYS = frozenset({'tenant_id', 'user_id', 'schema_name', 'tenant'})


class AssistantRequestError(Exception):
    def __init__(self, detail: dict | str, code: str = 'validation_error'):
        self.detail = detail
        self.code = code
        super().__init__(str(detail))


def _optional_str(value: Any, field: str, max_len: int = 128) -> str | None:
    if value is None or value == '':
        return None
    if not isinstance(value, str):
        raise AssistantRequestError({field: ['Must be a string or null.']})
    value = value.strip()
    if not value:
        return None
    if len(value) > max_len:
        raise AssistantRequestError({field: [f'Must be at most {max_len} characters.']})
    return value


def _optional_int(value: Any, field: str) -> int | None:
    if value is None or value == '':
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise AssistantRequestError({field: ['Must be an integer or null.']})
    if value < 1:
        raise AssistantRequestError({field: ['Must be a positive integer.']})
    return value


def parse_assistant_request(data: Any) -> dict:
    """
    Validate and normalize the Assistant query payload.
    Authority keys (tenant/user) in the body are ignored, never trusted.
    """
    if not isinstance(data, dict):
        raise AssistantRequestError({'non_field_errors': ['Request body must be a JSON object.']})

    schema_version = data.get('schema_version', SCHEMA_VERSION)
    if schema_version != SCHEMA_VERSION:
        raise AssistantRequestError(
            {'schema_version': [f'Unsupported schema_version. Expected "{SCHEMA_VERSION}".']}
        )

    message = data.get('message')
    if not isinstance(message, str) or not message.strip():
        raise AssistantRequestError({'message': ['This field is required.']})
    message = message.strip()
    if len(message) > MAX_MESSAGE_LENGTH:
        raise AssistantRequestError(
            {'message': [f'Must be at most {MAX_MESSAGE_LENGTH} characters.']}
        )

    raw_context = data.get('context') or {}
    if not isinstance(raw_context, dict):
        raise AssistantRequestError({'context': ['Must be an object or null.']})

    # Copy before cleaning so we never mutate request.data in place.
    raw_context = dict(raw_context)

    # Explicitly drop authority keys; never use them.
    for key in IGNORED_AUTHORITY_KEYS:
        raw_context.pop(key, None)

    view = _optional_str(raw_context.get('view'), 'context.view')
    route_name = _optional_str(raw_context.get('route_name'), 'context.route_name')
    entity_type = _optional_str(raw_context.get('entity_type'), 'context.entity_type')
    if entity_type is not None and entity_type not in ('document', 'builder'):
        raise AssistantRequestError(
            {'context': {'entity_type': ['Must be "document", "builder", or null.']}}
        )
    entity_id = _optional_int(raw_context.get('entity_id'), 'context.entity_id')

    return {
        'schema_version': SCHEMA_VERSION,
        'message': message,
        'context': {
            'view': view,
            'route_name': route_name,
            'entity_type': entity_type,
            'entity_id': entity_id,
        },
    }
