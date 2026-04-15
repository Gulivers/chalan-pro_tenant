<template>
  <div
    class="product-prices-bulk-excel-panel border rounded-3 p-3 bg-body-secondary bg-opacity-25">
    <h6 class="small fw-semibold mb-2 text-primary">
      Update inventory prices &amp; units of measure
    </h6>
    <p class="small text-muted mb-3">
      Download the same template used for transaction lines, then edit
      <strong>unit_code</strong>
      ,
      <strong>unit_price</strong>
      and
      <strong>price_type_name</strong>
      per product. Upload the file to insert or update
      <strong>sale</strong>
      prices; if
      <strong>unit_code</strong>
      is filled, the product default unit is updated.
    </p>
    <div class="product-prices-bulk-actions">
      <div class="d-flex align-items-start gap-2 gap-sm-3">
        <i
          class="bi bi-file-earmark-arrow-up text-success fs-5 mt-4 flex-shrink-0"
          aria-hidden="true" />
        <div class="flex-grow-1 min-w-0">
          <label
            class="form-label small fw-semibold text-body mb-2 mb-sm-1"
            for="bulk-prices-file-input">
            Apply to inventory
          </label>
          <div
            class="d-flex flex-column flex-sm-row align-items-stretch align-items-sm-center gap-2 gap-sm-3">
            <input
              id="bulk-prices-file-input"
              ref="bulkPricesFileInput"
              type="file"
              class="form-control form-control-sm min-w-0 product-prices-bulk-file-input"
              accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              :disabled="busy || optionsLoading"
              @change="onBulkPricesFile" />
            <button
              type="button"
              class="btn btn-outline-success btn-sm d-inline-flex align-items-center justify-content-center gap-2 flex-shrink-0 product-prices-bulk-download-btn"
              :disabled="busy || optionsLoading"
              @click="downloadTemplate">
              <img
                :src="excelIconUrl"
                alt=""
                width="20"
                height="20"
                class="excel-template-icon flex-shrink-0" />
              Download Excel template
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import excelIconUrl from "@/assets/img/microsoft-excel-icon.svg";

const emit = defineEmits(["updated"]);

let xlsxModulePromise = null;
async function getXlsx() {
  if (!xlsxModulePromise) {
    xlsxModulePromise = import("xlsx").then((m) => {
      const mod =
        m?.default && typeof m.default.read === "function" ? m.default : m;
      return mod;
    });
  }
  return xlsxModulePromise;
}

const HEADER_CODES = [
  "product_id",
  "product_name",
  "product_sku",
  "quantity",
  "unit_code",
  "unit_price",
  "discount_percent",
  "warehouse_name",
  "price_type_name",
  "brand_name",
];

const HEADER_DESC = [
  "Product ID (required for import — from Inventory)",
  "Product name (reference only — not imported; for your review)",
  "Product SKU (reference only — should match product_id)",
  "Quantity — edit as needed (default 1)",
  "Unit (code or name) — default from product’s unit of measure (edit if needed)",
  "Unit price — edit as needed (default 0)",
  "Discount % — default 0",
  "Warehouse name (exact name as in Warehouses, e.g. Main Warehouse) — default: first warehouse if set",
  "Price type name (exact name as in Price Types, e.g. Retail) — default: first price type if set",
  "Brand name (exact name as in Brands) — default: product default brand when set",
];

const busy = ref(false);
const optionsLoading = ref(true);
const bulkPricesFileInput = ref(null);
const priceTypesOptions = ref([]);
const warehousesOptions = ref([]);

async function loadTemplateOptions() {
  optionsLoading.value = true;
  try {
    const [whRes, ptRes] = await Promise.all([
      axios.get("/api/warehouses/", { params: { is_active: true } }),
      axios.get("/api/pricetypes/", { params: { is_active: true } }),
    ]);
    const whList = Array.isArray(whRes.data)
      ? whRes.data
      : whRes.data?.results || [];
    const ptList = Array.isArray(ptRes.data)
      ? ptRes.data
      : ptRes.data?.results || [];
    warehousesOptions.value = whList.map((w) => ({
      value: w.id,
      label: w.name,
    }));
    priceTypesOptions.value = ptList.map((pt) => ({
      value: pt.id,
      label: pt.name,
    }));
  } catch (e) {
    console.error(e);
  } finally {
    optionsLoading.value = false;
  }
}

onMounted(() => {
  loadTemplateOptions();
});

async function onBulkPricesFile(ev) {
  const file = ev.target.files?.[0];
  if (!file) return;
  if (!/\.xlsx$/i.test(file.name)) {
    await Swal.fire({
      icon: "error",
      title: "Invalid file",
      text: "Use a .xlsx file (download the template above).",
      confirmButtonText: "OK",
    });
    if (bulkPricesFileInput.value) bulkPricesFileInput.value.value = "";
    return;
  }
  const ok = await Swal.fire({
    icon: "question",
    title: "Update product prices?",
    html: "This will insert or update <strong>sale</strong> prices in inventory for each row (price type, unit, price) and optionally set the product default unit when <strong>unit_code</strong> is filled.",
    showCancelButton: true,
    confirmButtonText: "Apply",
    cancelButtonText: "Cancel",
  });
  if (!ok.isConfirmed) {
    if (bulkPricesFileInput.value) bulkPricesFileInput.value.value = "";
    return;
  }

  busy.value = true;
  try {
    const fd = new FormData();
    fd.append("file", file);
    const { data } = await axios.post(
      "/api/master-data/bulk-product-prices-import/",
      fd
    );
    const errList = Array.isArray(data.errors) ? data.errors : [];
    const errHtml =
      errList.length > 0
        ? `<p class="text-start small mb-1">Row issues (${
            errList.length
          }):</p><ul class="text-start small" style="max-height:220px;overflow:auto">${errList
            .slice(0, 40)
            .map(
              (e) =>
                `<li>Row ${e.row}: ${e.message || e.detail || String(e)}</li>`
            )
            .join("")}${errList.length > 40 ? "<li>…</li>" : ""}</ul>`
        : "";
    await Swal.fire({
      icon: errList.length && !data.rows_applied ? "warning" : "success",
      title: "Inventory prices",
      html: `<p class="mb-1">Rows applied: <strong>${
        data.rows_applied ?? 0
      }</strong></p>
        <p class="mb-1 small">Created: ${data.created ?? 0} · Updated: ${
        data.updated ?? 0
      } · Default unit changed: ${data.unit_default_updated ?? 0}</p>
        ${errHtml}`,
      confirmButtonText: "OK",
    });
    if (data.rows_applied > 0) {
      emit("updated");
    }
  } catch (e) {
    console.error(e);
    const msg =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      e?.message ||
      String(e);
    await Swal.fire({
      icon: "error",
      title: "Bulk update failed",
      text: typeof msg === "string" ? msg : JSON.stringify(msg),
      confirmButtonText: "OK",
    });
  } finally {
    busy.value = false;
    if (bulkPricesFileInput.value) bulkPricesFileInput.value.value = "";
  }
}

async function downloadTemplate() {
  busy.value = true;
  try {
    const XLSX = await getXlsx();
    const { data } = await axios.get("/api/products/", {
      params: { is_active: true, ordering: "name" },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    if (list.length === 0) {
      await Swal.fire({
        icon: "info",
        title: "No products",
        text: "There are no active products in inventory. Add products before downloading the template.",
        confirmButtonText: "OK",
      });
      return;
    }

    const defaultWh = warehousesOptions.value[0]?.label || "";
    const defaultPt = priceTypesOptions.value[0]?.label || "";

    const dataRows = list.map((p) => {
      const brandName = p.default_brand?.name || "";
      const unitCell = (p.unit_name || p.unit_default_code || "").trim();
      return [
        p.id,
        p.name || "",
        p.sku || "",
        1,
        unitCell,
        0,
        0,
        defaultWh,
        defaultPt,
        brandName,
      ];
    });

    const rows = [HEADER_CODES, HEADER_DESC, ...dataRows];

    const ws = XLSX.utils.aoa_to_sheet(rows);
    ws["!cols"] = [
      { wch: 10 },
      { wch: 36 },
      { wch: 18 },
      { wch: 10 },
      { wch: 12 },
      { wch: 12 },
      { wch: 14 },
      { wch: 28 },
      { wch: 24 },
      { wch: 22 },
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Lines");

    const safeDate = new Date().toISOString().slice(0, 10);
    XLSX.writeFile(
      wb,
      `jobrithm_transaction_lines_all_products_${safeDate}.xlsx`
    );

    await Swal.fire({
      icon: "success",
      title: "Template ready",
      text: `${list.length} product row(s). Edit unit_code, unit_price, and price_type_name, then upload using Apply to inventory.`,
      confirmButtonText: "OK",
    });
  } catch (e) {
    console.error(e);
    await Swal.fire({
      icon: "error",
      title: "Could not build template",
      text: e?.message || String(e),
    });
  } finally {
    busy.value = false;
  }
}
</script>

<style scoped>
.product-prices-bulk-excel-panel {
  border-color: rgba(25, 135, 84, 0.35) !important;
}
/* Input file: como máximo 50% del ancho del bloque (en móvil, ancho completo) */
.product-prices-bulk-file-input {
  width: 100%;
  max-width: 50%;
}
@media (max-width: 575.98px) {
  .product-prices-bulk-file-input {
    max-width: 100%;
  }
}
/* ≥sm: fila con botón a la derecha del input */
.product-prices-bulk-actions .product-prices-bulk-download-btn {
  white-space: nowrap;
}
@media (max-width: 575.98px) {
  .product-prices-bulk-actions .product-prices-bulk-download-btn {
    white-space: normal;
    text-align: center;
  }
}
</style>
