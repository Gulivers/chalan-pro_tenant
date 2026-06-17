from django.urls import path

from appsearch.views import SimilarTransactionSearchAPIView, TransactionSearchAPIView

urlpatterns = [
    path('api/search/transactions/', TransactionSearchAPIView.as_view(), name='search-transactions'),
    path(
        'api/search/transactions/similar/',
        SimilarTransactionSearchAPIView.as_view(),
        name='search-transactions-similar',
    ),
]
