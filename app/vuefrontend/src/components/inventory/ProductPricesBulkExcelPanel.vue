<template>
  <div id="product-bulk-prices-panel" class="jr-bulk-excel">
    <h2 class="jr-bulk-excel__title">
      Update inventory prices &amp; units of measure
    </h2>
    <p class="jr-bulk-excel__hint">
      Download the same template used for transaction lines, then edit
      <strong>unit_code</strong>,
      <strong>unit_price</strong>
      and
      <strong>price_type_name</strong>
      per product. Upload the file to insert or update
      <strong>sale</strong>
      prices; if
      <strong>unit_code</strong>
      is filled, the product default unit is updated.
    </p>

    <JRField
      label="Apply to inventory"
      hint="Use a .xlsx file from the template. This can overwrite existing sale prices.">
      <FileUpload
        ref="fileUpload"
        class="jr-bulk-excel__upload"
        mode="basic"
        name="file"
        accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        :auto="false"
        customUpload
        :disabled="busy || optionsLoading"
        chooseLabel="Choose .xlsx"
        :chooseButtonProps="{ fluid: true }"
        @select="onFileSelect" />
    </JRField>

    <JRButton
      type="button"
      variant="secondary"
      :disabled="busy || optionsLoading"
      :fluid="true"
      @click="downloadTemplate">
      <img
        :src="excelIconUrl"
        alt=""
        width="20"
        height="20"
        class="jr-bulk-excel__excel-icon" />
      Download Excel template
    </JRButton>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import FileUpload from "primevue/fileupload";
import { JRButton, JRField } from "@ui";
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
const fileUpload = ref(null);
const priceTypesOptions = ref([]);
const warehousesOptions = ref([]);

function resetFileInput() {
  fileUpload.value?.clear?.();
}

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

async function onFileSelect(event) {
  const file = event?.files?.[0];
  if (!file) return;
  if (!/\.xlsx$/i.test(file.name)) {
    await Swal.fire({
      icon: "error",
      title: "Invalid file",
      text: "Use a .xlsx file (download the template above).",
      confirmButtonText: "OK",
    });
    resetFileInput();
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
    resetFileInput();
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
    resetFileInput();
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
      `jobrhythm_transaction_lines_all_products_${safeDate}.xlsx`
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
.jr-bulk-excel {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 1rem;
  text-align: left;
}

.jr-bulk-excel__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-bulk-excel__hint {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-bulk-excel__hint strong {
  color: var(--color-jr-text);
  font-weight: 600;
}

.jr-bulk-excel__excel-icon {
  display: block;
  flex-shrink: 0;
}

.jr-bulk-excel__upload {
  width: 100%;
}

.jr-bulk-excel__upload :deep(.p-fileupload-basic),
.jr-bulk-excel__upload :deep(.p-fileupload-basic-content) {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
  gap: 0.5rem;
}

.jr-bulk-excel__upload :deep(.p-fileupload-file-label),
.jr-bulk-excel__upload :deep(.p-fileupload-filename) {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}
</style>
