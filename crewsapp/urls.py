from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CrewViewSet, TruckViewSet, CategoryListView, CategoryListView, 
    SupervisorCommunitiesView, CrewPermissionView
)

router = DefaultRouter()
router.register(r'api/crews', CrewViewSet)
router.register(r'api/trucks', TruckViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/supervisor-communities/', SupervisorCommunitiesView.as_view(), name='supervisor-communities'),
    path('api/crew/supervisor/', CrewPermissionView.as_view(), name='crew-permission-profile'),
    
]
