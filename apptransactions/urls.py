from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentTypeViewSet, PartyTypeViewSet, PartyCategoryViewSet, PartyViewSet,
    DocumentViewSet, DocumentLineViewSet, WorkAccountViewSet, TransactionFavoriteViewSet,
    download_transaction_pdf
)

router = DefaultRouter()
router.register(r'document-types', DocumentTypeViewSet)
router.register(r'party-types', PartyTypeViewSet)
router.register(r'party-categories', PartyCategoryViewSet)
router.register(r'parties', PartyViewSet)
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'document-lines', DocumentLineViewSet, basename='document-lines')
router.register(r'work-accounts', WorkAccountViewSet, basename='work-accounts')
router.register(r'transaction-favorites', TransactionFavoriteViewSet, basename='transaction-favorites')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/documents/<int:document_id>/pdf/', download_transaction_pdf, name='download-transaction-pdf'),
]