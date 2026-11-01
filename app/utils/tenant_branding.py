from django.db import connection
from django_tenants.utils import (
    get_public_schema_name,
    get_tenant,
    get_tenant_domain_model,
    schema_context,
)
import os
import re
from pathlib import Path


def _normalize_hostname(raw_host: str) -> str:
    if not raw_host:
        return ""
    # request.get_host() puede venir con puerto en desarrollo.
    return raw_host.split(":")[0].strip().lower()


def _resolve_tenant(request):
    """
    Resuelve tenant de forma robusta para vistas HTTP/PDF:
    1) connection.tenant (si ya fue fijado por TenantMainMiddleware)
    2) get_tenant(request)
    3) lookup por Domain en schema público (fallback)
    """
    public_schema = get_public_schema_name()

    conn_tenant = getattr(connection, "tenant", None)
    if conn_tenant is not None and getattr(conn_tenant, "schema_name", None) != public_schema:
        return conn_tenant

    try:
        req_tenant = get_tenant(request)
        if req_tenant is not None and getattr(req_tenant, "schema_name", None) != public_schema:
            return req_tenant
    except Exception:
        pass

    host = _normalize_hostname(request.get_host())
    if not host:
        return None

    try:
        DomainModel = get_tenant_domain_model()
        with schema_context(public_schema):
            domain = DomainModel.objects.select_related("tenant").filter(domain__iexact=host).first()
            if domain and domain.tenant:
                return domain.tenant
            # Fallback útil en local cuando a veces entra con/without www.
            if host.startswith("www."):
                domain = DomainModel.objects.select_related("tenant").filter(
                    domain__iexact=host.replace("www.", "", 1)
                ).first()
                if domain and domain.tenant:
                    return domain.tenant
    except Exception:
        return None
    return None


def get_tenant_logo_url(request):
    """
    Retorna URL absoluta del logo del tenant activo para usar en PDFs.
    Si no hay tenant o no hay logo válido, retorna None.
    """
    tenant = _resolve_tenant(request)
    if tenant is None:
        return None

    logo_field = getattr(tenant, "logo", None)
    if not logo_field:
        return None

    logo_name = logo_field.name
    try:
        if not logo_field.storage.exists(logo_name):
            # Fallback: si BD tiene sufijo aleatorio (_xxxxxxx) y en disco existe sin sufijo.
            # Ej: tenant_logos/logito3_tP9LURy.PNG -> tenant_logos/logito3.PNG
            dirname, filename = os.path.split(logo_name)
            stem, ext = os.path.splitext(filename)
            recovered = re.sub(r"_[A-Za-z0-9]{7}$", "", stem)
            if recovered != stem:
                candidate = f"{dirname}/{recovered}{ext}" if dirname else f"{recovered}{ext}"
                if logo_field.storage.exists(candidate):
                    logo_name = candidate
                else:
                    return None
            else:
                return None
    except Exception:
        return None

    return file_field_to_pdf_uri(logo_field, request=request, name=logo_name)


def file_field_to_pdf_uri(file_field, request=None, name=None):
    """
    URI usable por WeasyPrint para un FileField/ImageField.

    Prefiere file:// local; si no hay path, cae a URL HTTP absoluta.
    `name` opcional permite un path recuperado (p. ej. logo sin sufijo random).
    """
    if not file_field:
        return None

    storage_name = name or getattr(file_field, "name", None)
    if not storage_name:
        return None

    try:
        if not file_field.storage.exists(storage_name):
            return None
    except Exception:
        return None

    try:
        local_path = file_field.storage.path(storage_name)
        if local_path and os.path.exists(local_path):
            return Path(local_path).resolve().as_uri()
    except Exception:
        pass

    try:
        url = file_field.storage.url(storage_name)
    except Exception:
        return None
    if not url:
        return None
    if url.startswith(("http://", "https://", "file://")):
        return url
    if request is not None:
        return request.build_absolute_uri(url)
    return url
