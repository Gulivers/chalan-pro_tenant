"""Canonical Level-1 spend metric definition (no Django model imports)."""

SPEND_DEFINITION = (
    'Net invoiced spending = active Document.total_amount whose DocumentType has '
    'counts_as_net_invoiced_spend=True (tenant-configured; often a Purchase Invoice '
    'code such as PINV or PO-INV); '
    'not gross, not purchase returns, not PO/committed, '
    'not job material issue/picking, '
    'not the Sales vs Purchases chart (is_purchase) criterion'
)
