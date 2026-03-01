BEGIN;

-- Adjust PK (Picking Ticket): operational/logical only (no accounting, no tax, no physical movement, no stock movement)
UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Picking Ticket',
  affects_physical      = FALSE,
  affects_logical       = TRUE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = FALSE,
  is_sales              = TRUE,
  warehouse_required    = TRUE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 0,
  is_active             = TRUE
WHERE type_code = 'PK';

-- Fix PO (Purchase Order): it’s purchase, not sales
UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Purchase Order',
  affects_physical      = FALSE,
  affects_logical       = TRUE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = TRUE,
  is_sales              = FALSE,
  warehouse_required    = TRUE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 0,
  is_active             = TRUE
WHERE type_code = 'PO';

-- (Optional) Re-apply canonical settings for the rest (safe if you want consistency)
UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Purchase Invoice',
  affects_physical      = FALSE,
  affects_logical       = FALSE,
  affects_accounting    = TRUE,
  is_taxable            = TRUE,
  is_purchase           = TRUE,
  is_sales              = FALSE,
  warehouse_required    = FALSE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 0,
  is_active             = TRUE
WHERE type_code = 'PINV';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Sales Quotation',
  affects_physical      = FALSE,
  affects_logical       = FALSE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = FALSE,
  is_sales              = TRUE,
  warehouse_required    = FALSE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 0,
  is_active             = TRUE
WHERE type_code = 'SQ';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Sales Order',
  affects_physical      = FALSE,
  affects_logical       = TRUE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = FALSE,
  is_sales              = TRUE,
  warehouse_required    = TRUE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 0,
  is_active             = TRUE
WHERE type_code = 'SO';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Delivery Note / Shipment',
  affects_physical      = TRUE,
  affects_logical       = TRUE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = FALSE,
  is_sales              = TRUE,
  warehouse_required    = TRUE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = -1,
  is_active             = TRUE
WHERE type_code = 'DN';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Sales Invoice',
  affects_physical      = FALSE,
  affects_logical       = FALSE,
  affects_accounting    = TRUE,
  is_taxable            = TRUE,
  is_purchase           = FALSE,
  is_sales              = TRUE,
  warehouse_required    = FALSE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 0,
  is_active             = TRUE
WHERE type_code = 'INV';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Sales Credit Note / Return',
  affects_physical      = TRUE,
  affects_logical       = TRUE,
  affects_accounting    = TRUE,
  is_taxable            = TRUE,
  is_purchase           = FALSE,
  is_sales              = TRUE,
  warehouse_required    = TRUE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 1,
  is_active             = TRUE
WHERE type_code = 'CRN';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Purchase Requisition',
  affects_physical      = FALSE,
  affects_logical       = FALSE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = TRUE,
  is_sales              = FALSE,
  warehouse_required    = FALSE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 0,
  is_active             = TRUE
WHERE type_code = 'PR';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Goods Receipt Note',
  affects_physical      = TRUE,
  affects_logical       = TRUE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = TRUE,
  is_sales              = FALSE,
  warehouse_required    = TRUE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = 1,
  is_active             = TRUE
WHERE type_code = 'GRN';

UPDATE test_dominio_local.apptransactions_documenttype
SET
  description           = 'Purchase Return',
  affects_physical      = TRUE,
  affects_logical       = TRUE,
  affects_accounting    = FALSE,
  is_taxable            = FALSE,
  is_purchase           = TRUE,
  is_sales              = FALSE,
  warehouse_required    = TRUE,
  is_operational        = FALSE,
  allow_negative_sales  = FALSE,
  stock_movement        = -1,
  is_active             = TRUE
WHERE type_code = 'PRN';

COMMIT;