"""
Spend queryset helpers for JobRhythm Assistant (Level 1).

IMPORTANT — Spend metric (product decision):
  Level 1 measures **Net invoiced spending**:
  sum of Document.total_amount on active documents whose DocumentType has
  ``counts_as_net_invoiced_spend=True`` (tenant-configured intention).

  - Net = document total after line discounts (Document.total_amount).
  - NOT the Sales vs Purchases chart criterion (document_type__is_purchase=True).
  - NOT hard-coded type_code PINV/PO-INV (tenants may rename codes).
  - Out of scope for Level 1 (do not mix into messages/totals):
      * Gross invoiced spending
      * Purchase returns (counts_as_purchase_return)
      * Purchase orders / committed amount (PO)
      * Job material issue / picking (counts_as_job_material_issue)

PRN / returns are out of scope (no negative spend).
"""

from __future__ import annotations

from django.db.models import QuerySet

from appassistant.spend_definition import SPEND_DEFINITION
from apptransactions.models import Document

# Legacy default type_code used in fixtures / smoke when creating a spend type.
# Runtime filtering uses counts_as_net_invoiced_spend, not this code.
SPEND_TYPE_CODE = 'PINV'

# User-facing metric labels (English UI).
SPEND_METRIC_KEY = 'net_invoiced_spending'
SPEND_METRIC_LABEL = 'Net invoiced spending'
SPEND_METRIC_SHORT = 'Net spending'


def spend_documents_qs() -> QuerySet[Document]:
    """
    Authorized base queryset for spend tools within the current tenant schema.

    Caller must already enforce view_document. Never accepts tenant_id.
    """
    return Document.objects.filter(
        document_type__counts_as_net_invoiced_spend=True,
        is_active=True,
    ).select_related('document_type', 'builder', 'builder__party')


def job_material_documents_qs() -> QuerySet[Document]:
    """Base QS for job/house material issue intention (future tools)."""
    return Document.objects.filter(
        document_type__counts_as_job_material_issue=True,
        is_active=True,
    ).select_related('document_type', 'builder', 'work_account', 'builder__party')


def purchase_return_documents_qs() -> QuerySet[Document]:
    """Base QS for purchase-return intention (future tools; not mixed into spend)."""
    return Document.objects.filter(
        document_type__counts_as_purchase_return=True,
        is_active=True,
    ).select_related('document_type', 'builder', 'builder__party')
