from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContractViewSet, WorkPriceViewSet, ContractDetailsViewSet, 
    BuilderViewSet, JobViewSet, HouseModelViewSet, LoginView,
    validate_token, logout_view, weekly_summary, weekly_summary_list,
    monthly_summary, login_view, user_permissions, request_password_reset, reset_password_confirm, 
    UserDetailView, get_house_model_jobs, geocode_view, download_contract_pdf,
    BuilderReadOnlyViewSet, JobReadOnlyViewSet, HouseReadOnlyViewSet
)
from .views_schema import BuilderSchemaView, JobSchemaView, HouseModelSchemaView

router = DefaultRouter()
router.register('contract', ContractViewSet, basename='contract')
router.register('workprice', WorkPriceViewSet, basename='workprice')
router.register('contract_details', ContractDetailsViewSet, basename='contract_details')
router.register('builder', BuilderViewSet, basename='builder')
router.register('job', JobViewSet, basename='job')
router.register('house_model', HouseModelViewSet, basename='house_model')
router.register('api/builders', BuilderReadOnlyViewSet, basename='api-builders')
router.register('api/jobs', JobReadOnlyViewSet, basename='api-jobs')
router.register('api/houses', HouseReadOnlyViewSet, basename='api-houses')

urlpatterns = [
    path('api/', include(router.urls)), 
    path('api/jobs_by_builder/', JobViewSet.as_view({'get': 'jobs_by_builder'}), name='jobs-by-builder'),
    path('api/house_models_by_job/', HouseModelViewSet.as_view({'get': 'house_models_by_job'}), name='house-models-by-job'),
    path('api/house_models/<int:house_model_id>/jobs/', get_house_model_jobs, name='get_house_model_jobs'), # http://localhost:8000/api/house_models/55/jobs/
    path('api/login/', LoginView.as_view(), name='login'),  # Usar la vista personalizada
    path('api/validate-token/', validate_token, name='validate-token'),
    path('api/logout/', logout_view, name='logout'),
    path('api/login/', login_view, name='api_login'),
    path('api/user-permissions/', user_permissions, name='user_permissions'),
    path('api/request-password-reset/', request_password_reset, name='request_password_reset'),
    path('api/password-reset-confirm/<uidb64>/<token>/', reset_password_confirm, name='password_reset_confirm'),
    path('api/weekly_summary/', weekly_summary, name='weekly_summary'),
    path('api/weekly_summary_list/', weekly_summary_list, name='weekly_summary_list'),
    path('api/monthly_summary/', monthly_summary, name='monthly_summary'),
    path('api/user_detail/', UserDetailView.as_view(), name='user_detail'),
    path('api/geocode/', geocode_view, name='geocode'),
    path('web/contract-pdf/<int:contract_id>', download_contract_pdf, name='contract-pdf'),
    path('api/builder/<int:pk>/workprices/', BuilderViewSet.as_view({'get': 'workprices'}), name='builder-workprices'),
    path('api/builder/<int:pk>/assign-workprices/', BuilderViewSet.as_view({'post': 'assign_workprices'}), name='assign-workprices'),
    
    # Schema endpoints
    path('api/schema/builder/', BuilderSchemaView.as_view(), name='builder-schema'),
    path('api/schema/job/', JobSchemaView.as_view(), name='job-schema'),
    path('api/schema/house-model/', HouseModelSchemaView.as_view(), name='house-model-schema'),

] + router.urls
