"""JobRhythm Assistant API views (Level 1 — Increment C2 conversation)."""

from __future__ import annotations

import logging
import time
import uuid

from django.conf import settings
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .contracts.request import AssistantRequestError, parse_assistant_request
from .contracts.response import validate_response_payload
from .permissions import HasDocumentViewPermission
from .services.audit import log_assistant_query, resolve_schema_name, sanitize_context_for_audit
from .services.orchestrator import run_assistant_query

logger = logging.getLogger('appassistant')


def assistant_enabled() -> bool:
    return getattr(settings, 'ASSISTANT_ENABLED', True) is True


class AssistantQueryView(APIView):
    """
    POST /api/assistant/query/

    Auth + permission → conversation state → continuity/router → tool → response.
    No LLM (C4). Client may send conversation_id; never authoritative state.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, HasDocumentViewPermission]

    def post(self, request):
        started = time.monotonic()
        request_id = uuid.uuid4()

        if not assistant_enabled():
            log_assistant_query(
                user=request.user,
                request_id=request_id,
                success=False,
                error_code='assistant_disabled',
                duration_ms=_elapsed_ms(started),
            )
            return Response(
                {
                    'detail': 'JobRhythm Assistant is temporarily unavailable.',
                    'code': 'assistant_disabled',
                    'meta': {'request_id': str(request_id)},
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            parsed = parse_assistant_request(request.data)
        except AssistantRequestError as exc:
            log_assistant_query(
                user=request.user,
                request_id=request_id,
                success=False,
                error_code=exc.code,
                params_safe={},
                duration_ms=_elapsed_ms(started),
            )
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

        result = run_assistant_query(
            user=request.user,
            message=parsed['message'],
            context=parsed['context'],
            request_id=request_id,
            conversation_id=parsed.get('conversation_id'),
            start_over=bool(parsed.get('start_over')),
        )
        payload = result.payload
        errors = validate_response_payload(payload)
        if errors:
            logger.error(
                'assistant.response_contract_invalid request_id=%s errors=%s',
                request_id,
                errors,
            )
            log_assistant_query(
                user=request.user,
                request_id=request_id,
                success=False,
                error_code='response_contract_error',
                params_safe=sanitize_context_for_audit(parsed['context']),
                duration_ms=_elapsed_ms(started),
                conversation=result.conversation_id or None,
                intent=result.intent,
                clarification=result.clarification,
            )
            return Response(
                {'detail': 'Internal response contract error.', 'code': 'response_contract_error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        duration_ms = _elapsed_ms(started)
        log_assistant_query(
            user=request.user,
            request_id=request_id,
            tool_name=result.tool_name,
            params_safe=result.params_safe,
            success=result.success,
            error_code=result.error_code,
            row_count=result.row_count,
            duration_ms=duration_ms,
            schema_name=resolve_schema_name(request),
            conversation=result.conversation_id or None,
            intent=result.intent,
            clarification=result.clarification,
        )
        logger.info(
            'assistant.query ok request_id=%s user_id=%s schema=%s tool=%s '
            'conversation_id=%s intent=%s success=%s row_count=%s duration_ms=%s',
            request_id,
            getattr(request.user, 'pk', None),
            resolve_schema_name(request),
            result.tool_name or 'none',
            result.conversation_id or '',
            result.intent or '',
            result.success,
            result.row_count,
            duration_ms,
        )
        return Response(payload, status=status.HTTP_200_OK)


def _elapsed_ms(started: float) -> int:
    return max(0, int((time.monotonic() - started) * 1000))
