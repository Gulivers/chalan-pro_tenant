from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication

from appsearch.serializers import (
    TransactionSearchRequestSerializer,
    TransactionSearchResponseSerializer,
)
from appsearch.services.embeddings import EmbeddingServiceError
from appsearch.services.search import search_transactions


class TransactionSearchAPIView(APIView):
    """
    Hybrid semantic search over indexed DocumentLine rows.
    Returns ranked documents with snippets and structured filter metadata.
    """

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

        try:
            payload = search_transactions(
                data['query'],
                extra_filters=extra_filters,
                limit=data.get('limit', 50),
            )
        except EmbeddingServiceError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except RuntimeError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = TransactionSearchResponseSerializer(payload)
        return Response(response_serializer.data)
