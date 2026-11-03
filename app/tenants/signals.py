# -*- coding: utf-8 -*-
"""Signals de tenants (seed post-schema, etc.)."""
from __future__ import annotations

import logging

from django.dispatch import receiver
from django_tenants.signals import post_schema_sync
from django_tenants.utils import get_public_schema_name, schema_context

logger = logging.getLogger(__name__)


@receiver(post_schema_sync)
def seed_document_masters_after_schema_sync(sender, tenant, **kwargs):
    """
    Tras create_schema + migrate_schemas (Tenant.save con auto_create_schema,
    o django_tenants create_tenant), siembra masters_document_type.json.

    El comando custom tenants.create_tenant suele quedar sombreado por
    django_tenants.create_tenant; este signal cubre ambos caminos de creación.
    """
    schema_name = getattr(tenant, 'schema_name', None)
    if not schema_name or schema_name == get_public_schema_name():
        return

    try:
        from apptransactions.services.masters_document_type import (
            seed_tenant_document_masters,
        )

        with schema_context(schema_name):
            result = seed_tenant_document_masters()
        logger.info(
            'masters_document_type sembrado en schema "%s": %s',
            schema_name,
            result,
        )
    except Exception:
        # No abortar la creación del tenant; se puede reparar con
        # seed_masters_document_type --schema <schema>.
        logger.exception(
            'Error al sembrar masters_document_type en schema "%s"',
            schema_name,
        )
