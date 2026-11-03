# -*- coding: utf-8 -*-
"""Permisos Django reutilizables para vistas API fuera de ViewSets."""
from __future__ import annotations

import logging

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class HasDjangoPerm(BasePermission):
    """Exige IsAuthenticated implícito vía has_perm + un codename fijo en la vista."""

    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        perm = getattr(view, 'required_perm', None)
        if not perm:
            return False
        return user.has_perm(perm)


def require_user_perm(user, perm: str, detail: str | None = None) -> None:
    if not user or not user.is_authenticated or not user.has_perm(perm):
        raise PermissionDenied(detail or 'You do not have permission to perform this action.')


def fixed_server_error(exc: Exception, *, message: str = 'An unexpected error occurred.'):
    logger.exception(message)
    return Response({'detail': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
