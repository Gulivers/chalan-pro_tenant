from django.urls import path

from appsearch.views import TransactionSearchAPIView

urlpatterns = [
    path('api/search/transactions/', TransactionSearchAPIView.as_view(), name='search-transactions'),
]
