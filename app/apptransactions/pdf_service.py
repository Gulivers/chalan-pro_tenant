"""
Synchronous WeasyPrint builders for transaction / material-request PDFs.

Used by sync endpoints (compat) and by background PDF jobs.
Keep templates free of external CDN CSS so WeasyPrint does not fetch the network.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from utils.tenant_branding import get_tenant_logo_url

from .models import Document, DocumentLine
from .pdf_helpers import (
    current_status_for_pdf,
    line_product_image_pdf_uri,
    phase_name,
)
from .services.material_request import MR_TYPE_CODE

logger = logging.getLogger(__name__)


def _transaction_document_qs():
    return Document.objects.select_related(
        'document_type',
        'builder',
        'created_by',
        'work_account',
        'work_account__builder',
        'work_account__job',
        'work_account__house_model',
    ).prefetch_related(
        Prefetch(
            'lines',
            queryset=DocumentLine.objects.select_related(
                'product',
                'product__brand',
                'unit',
                'price_type',
                'brand',
                'warehouse',
            ).prefetch_related(
                'serialized_items_created',
                'product__images',
            ),
        )
    )


def build_transaction_pdf(
    document_id: int,
    request=None,
    *,
    logo_url: Optional[str] = None,
) -> tuple[bytes, str]:
    """
    Return (pdf_bytes, filename) for a transaction document.
    `logo_url` may be precomputed (background jobs without a real request).
    """
    document = get_object_or_404(_transaction_document_qs(), id=document_id)

    if logo_url is None and request is not None:
        logo_url = get_tenant_logo_url(request)

    show_product_images = bool(getattr(document.document_type, 'is_sales', False))
    line_rows = []
    for line in document.lines.all():
        line_rows.append(
            {
                'line': line,
                'image_url': (
                    line_product_image_pdf_uri(line, request)
                    if show_product_images
                    else None
                ),
            }
        )

    html = render_to_string(
        'transaction_pdf.html',
        {
            'document': document,
            'logo_url': logo_url,
            'show_product_images': show_product_images,
            'line_rows': line_rows,
        },
    )
    pdf_bytes = HTML(string=html).write_pdf(font_config=FontConfiguration())
    filename = f'{document.document_type.type_code}_{document.id}.pdf'
    return pdf_bytes, filename


def build_material_request_pdf(
    document_id: int,
    request=None,
    *,
    logo_url: Optional[str] = None,
) -> tuple[bytes, str]:
    """Return (pdf_bytes, filename) for a material-request document."""
    from appinventory.models import ProductImage
    from .models import DocumentTrackingHistory

    document = get_object_or_404(
        Document.objects.filter(document_type__type_code=MR_TYPE_CODE)
        .select_related(
            'document_type',
            'created_by',
            'work_account',
            'work_account__builder',
            'work_account__job',
            'work_account__house_model',
            'work_order__crew__category',
            'tracking__current_status',
        )
        .prefetch_related(
            Prefetch(
                'lines',
                queryset=DocumentLine.objects.select_related(
                    'product',
                    'product__brand',
                    'unit',
                    'brand',
                )
                .prefetch_related(
                    Prefetch(
                        'product__images',
                        queryset=ProductImage.objects.order_by(
                            '-is_primary', '-uploaded_at'
                        ),
                    ),
                )
                .order_by('id'),
            ),
            Prefetch(
                'tracking_history',
                queryset=DocumentTrackingHistory.objects.select_related(
                    'to_status',
                    'changed_by',
                ).order_by('changed_at', 'id'),
            ),
        ),
        pk=document_id,
    )

    if logo_url is None and request is not None:
        logo_url = get_tenant_logo_url(request)

    requested_event = None
    for row in document.tracking_history.all():
        if getattr(row.to_status, 'code', None) == 'requested':
            requested_event = row
            break

    requested_by = ''
    if requested_event and requested_event.changed_by_id:
        requested_by = requested_event.changed_by.username
    elif document.created_by_id:
        requested_by = document.created_by.username

    line_rows = [
        {
            'line': line,
            'image_url': line_product_image_pdf_uri(line, request),
        }
        for line in document.lines.all()
    ]

    current_status, status_changed_at = current_status_for_pdf(document)
    status_label = (
        (getattr(current_status, 'name', None) or '').strip()
        or (getattr(current_status, 'code', None) or '').strip()
        or 'Requested'
    )
    status_code = (
        (getattr(current_status, 'code', None) or '').strip() or 'requested'
    )

    html = render_to_string(
        'material_request_pdf.html',
        {
            'document': document,
            'line_rows': line_rows,
            'logo_url': logo_url,
            'status_label': status_label,
            'status_code': status_code,
            'status_changed_at': status_changed_at,
            'phase': phase_name(document),
            'requested_by': requested_by,
            'requested_at': (
                requested_event.changed_at if requested_event else None
            ),
        },
    )
    pdf_bytes = HTML(string=html).write_pdf(font_config=FontConfiguration())
    number = document.document_number or f'MR-{document.id}'
    filename = f'{number}_{status_code}.pdf'
    return pdf_bytes, filename


def pdf_response_payload(pdf_bytes: bytes, filename: str) -> dict[str, Any]:
    import base64

    return {
        'file': base64.b64encode(pdf_bytes).decode('utf-8'),
        'filename': filename,
        'file_type': 'application/pdf',
    }
