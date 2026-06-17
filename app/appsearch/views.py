import time

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appsearch.serializers import (
    SimilarTransactionSearchRequestSerializer,
    SimilarTransactionSearchResponseSerializer,
    TransactionSearchRequestSerializer,
    TransactionSearchResponseSerializer,
)
from appsearch.services.embeddings import EmbeddingServiceError
from appsearch.services.search import search_transactions
from appsearch.services.similar import SimilarSearchError, find_similar_transactions
from appsearch.services.telemetry import record_search_telemetry


class TransactionSearchAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.has_perm('apptransactions.view_document'):
            return Response(
                {'detail': 'You do not have permission to search transactions.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TransactionSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        extra_filters = {}
        if data.get('date_from'):
            extra_filters['date_from'] = data['date_from'].isoformat()
        if data.get('date_to'):
            extra_filters['date_to'] = data['date_to'].isoformat()

        started = time.perf_counter()
        try:
            payload = search_transactions(
                data['query'],
                extra_filters=extra_filters,
                limit=data.get('limit', 50),
            )
        except EmbeddingServiceError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except RuntimeError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        latency_ms = int((time.perf_counter() - started) * 1000)
        record_search_telemetry(
            operation='search',
            latency_ms=latency_ms,
            result_count=payload.get('count', 0),
            query_length=len(data['query']),
        )

        response_serializer = TransactionSearchResponseSerializer(payload)
        return Response(response_serializer.data)


class SimilarTransactionSearchAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.has_perm('apptransactions.view_document'):
            return Response(
                {'detail': 'You do not have permission to search transactions.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SimilarTransactionSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        started = time.perf_counter()
        try:
            payload = find_similar_transactions(
                document_id=data.get('document_id'),
                document_line_id=data.get('document_line_id'),
                limit=data.get('limit', 20),
            )
        except SimilarSearchError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except RuntimeError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        latency_ms = int((time.perf_counter() - started) * 1000)
        record_search_telemetry(
            operation='similar',
            latency_ms=latency_ms,
            result_count=payload.get('count', 0),
        )

        response_serializer = SimilarTransactionSearchResponseSerializer(payload)
        return Response(response_serializer.data)
