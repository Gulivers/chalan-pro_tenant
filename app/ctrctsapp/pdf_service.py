"""WeasyPrint builders for contract PDFs."""
from __future__ import annotations

import math
from typing import Optional

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from utils.tenant_branding import get_tenant_logo_url, _resolve_tenant

from .models import Contract


def lighting_circuits(sqft):
    if not sqft:
        return 0
    num = sqft * 3 / 120 / 15
    return math.ceil(num)


def build_contract_pdf(
    contract_id: int,
    request=None,
    *,
    logo_url: Optional[str] = None,
) -> tuple[bytes, str]:
    contract = get_object_or_404(Contract, id=contract_id)

    if contract.type == 'Trim':
        details = contract.contract_details.filter(cdtrim__gt=0)
    else:
        details = contract.contract_details.filter(cdrough__gt=0)

    mid_index = details.count() // 2
    left_details = details[:mid_index]
    right_details = details[mid_index:]

    if logo_url is None and request is not None:
        logo_url = get_tenant_logo_url(request)

    tenant = _resolve_tenant(request) if request is not None else None
    if tenant is None:
        from django.db import connection

        tenant = getattr(connection, 'tenant', None)

    show_lighting_circuits = (
        tenant is not None
        and getattr(tenant, 'client_type', None) == 'electric'
    )

    html = render_to_string(
        'contract_pdf.html',
        {
            'contract': contract,
            'left_details': left_details,
            'right_details': right_details,
            'lighting_circuits': (
                lighting_circuits(contract.sqft) if show_lighting_circuits else None
            ),
            'show_lighting_circuits': show_lighting_circuits,
            'logo_url': logo_url,
        },
    )
    pdf_bytes = HTML(string=html).write_pdf(font_config=FontConfiguration())
    filename = f'contract_{contract.pk}.pdf'
    return pdf_bytes, filename
