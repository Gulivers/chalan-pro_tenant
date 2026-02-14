from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CrewViewSet, TruckViewSet, TruckAssignmentViewSet, CategoryViewSet,
    CategoryListView, UserListAPIView, SupervisorCommunitiesView, CrewPermissionView
)

router = DefaultRouter()
router.register(r'crews', CrewViewSet, basename='crew')
router.register(r'trucks', TruckViewSet, basename='truck')
router.register(r'truck-assignments', TruckAssignmentViewSet, basename='truckassignment')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/categories-list/', CategoryListView.as_view(), name='category-list'),
    path('api/crew-users/', UserListAPIView.as_view(), name='crew-users-list'),
    path('api/supervisor-communities/', SupervisorCommunitiesView.as_view(), name='supervisor-communities'),
    path('api/crew/supervisor/', CrewPermissionView.as_view(), name='crew-permission-profile'),
]
