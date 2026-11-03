"""
Authenticated company-setup API for the tenant-owner Welcome assistant.
"""
from django.db import connection
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appauth.authentication import TenantJWTAuthentication
from appauth.services.tenant import is_tenant_owner, resolve_request_tenant

from .setup_progress import (
    CRITICAL_STEPS,
    SKIPPABLE_STEPS,
    STEP_ORDER,
    apply_action,
    collect_entity_counts,
    critical_ready,
    merge_auto_done,
    next_recommended_step,
    normalize_progress,
)


def _payload_for_tenant(tenant, user) -> dict:
    progress = normalize_progress(getattr(tenant, 'setup_progress', None) or {})
    seed_done = bool(getattr(tenant, 'seed_inventory_done', False))
    counts = collect_entity_counts()
    merged = merge_auto_done(progress, counts, seed_done)
    steps = merged['steps']
    ready = critical_ready(steps)
    return {
        'setup_completed': bool(getattr(tenant, 'setup_completed', False)),
        'panel_dismissed': merged['panel_dismissed'],
        'banner_dismissed': merged['banner_dismissed'],
        'welcome_modal_dismissed': merged['welcome_modal_dismissed'],
        'seed_inventory_done': seed_done,
        'is_tenant_owner': is_tenant_owner(user, tenant),
        'counts': counts,
        'steps': steps,
        'critical_steps': list(CRITICAL_STEPS),
        'skippable_steps': sorted(SKIPPABLE_STEPS),
        'step_order': list(STEP_ORDER),
        'critical_ready': ready,
        'next_recommended': next_recommended_step(steps),
    }


class TenantSetupView(APIView):
    """
    GET /api/tenant-setup/
    PATCH /api/tenant-setup/

    Progress for the post-login Welcome assistant (tenant owner / staff).
    """

    authentication_classes = [TenantJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = resolve_request_tenant(request) or getattr(connection, 'tenant', None)
        if tenant is None or getattr(tenant, 'schema_name', None) in (None, 'public'):
            return Response(
                {'detail': 'Tenant context is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(_payload_for_tenant(tenant, request.user))

    def patch(self, request):
        tenant = resolve_request_tenant(request) or getattr(connection, 'tenant', None)
        if tenant is None or getattr(tenant, 'schema_name', None) in (None, 'public'):
            return Response(
                {'detail': 'Tenant context is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (
            is_tenant_owner(request.user, tenant) or request.user.is_staff
        ):
            return Response(
                {'detail': 'Only the tenant administrator can update setup progress.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        action = (request.data.get('action') or '').strip().lower()
        step = request.data.get('step')
        progress = normalize_progress(getattr(tenant, 'setup_progress', None) or {})

        try:
            if action == 'finish':
                counts = collect_entity_counts()
                merged = merge_auto_done(
                    progress, counts, bool(tenant.seed_inventory_done)
                )
                if not critical_ready(merged['steps']):
                    return Response(
                        {
                            'detail': (
                                'Add at least one builder and one community '
                                'before finishing setup.'
                            ),
                            'critical_steps': list(CRITICAL_STEPS),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                tenant.setup_completed = True
                progress = merged
                progress['panel_dismissed'] = True
            else:
                progress = apply_action(progress, action=action, step=step)
                if action in ('reopen', 'reopen_welcome'):
                    tenant.setup_completed = False
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        tenant.setup_progress = progress
        update_fields = ['setup_progress']
        if action in ('finish', 'reopen'):
            update_fields.append('setup_completed')
        tenant.save(update_fields=update_fields)

        # Refresh from DB identity (same instance is fine).
        return Response(_payload_for_tenant(tenant, request.user))
