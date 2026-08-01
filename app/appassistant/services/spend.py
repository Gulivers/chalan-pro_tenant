"""
Spend queryset helpers for JobRhythm Assistant (Level 1).

IMPORTANT — Spend metric (product decision):
  Level 1 measures **Net invoiced spending**:
  sum of Document.total_amount on active PINV (Purchase Invoice) documents.

  - Net = document total after line discounts (Document.total_amount).
  - NOT the Sales vs Purchases chart criterion (document_type__is_purchase=True).
  - Out of scope for Level 1 (do not mix into messages/totals):
      * Gross invoiced spending
      * Purchase returns (PRN)
      * Purchase orders / committed amount (PO)

PRN / returns are out of scope (no negative spend).
"""

from __future__ import annotations

from django.db.models import QuerySet

from apptransactions.models import Document

SPEND_TYPE_CODE = 'PINV'

# Machine-oriented definition (tools, context, docs).
SPEND_DEFINITION = (
    'Net invoiced spending = active PINV Document.total_amount only; '
    'not gross, not returns (PRN), not PO/committed, '
    'not the Sales vs Purchases chart (is_purchase) criterion'
)

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
        document_type__type_code=SPEND_TYPE_CODE,
        is_active=True,
    ).select_related('document_type', 'builder', 'builder__party')
