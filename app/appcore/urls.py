from django.urls import path

from appcore.views.password_reset import (
    request_password_reset,
    reset_password_confirm,
)

urlpatterns = [
    path(
        "api/request-password-reset/",
        request_password_reset,
        name="request_password_reset",
    ),
    path(
        "api/password-reset-confirm/<uidb64>/<token>/",
        reset_password_confirm,
        name="password_reset_confirm",
    ),
]
