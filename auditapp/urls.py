from django.urls import path
from .views import LogUserActionView

urlpatterns = [
    path('api/log-action/', LogUserActionView.as_view(), name='log_user_action'),
]
