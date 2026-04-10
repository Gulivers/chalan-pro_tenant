<template>
  <div class="transaction-lines-excel-panel border rounded-3 p-2">
    <div class="d-flex flex-wrap align-items-center gap-3">
      <div class="d-flex align-items-center gap-2 mx-2">
        <i
          class="bi bi-file-earmark-arrow-up text-success fs-5 mt-4"
          aria-hidden="true" />
        <div>
          <label class="form-label small fw-semibold mb-0">Import items</label>
          <input
            ref="fileInput"
            type="file"
            class="form-control form-control-sm mx-2"
            accept=".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
            :disabled="busy"
            @change="onFile" />
        </div>
      </div>
      <div class="vr d-none d-sm-block my-2 mx-auto opacity-50" />
      <button
        type="button"
        class="btn btn-outline-success btn-sm d-inline-flex align-items-center gap-2 mt-3 mx-auto"
        :disabled="busy"
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
    <p class="small text-muted mb-0 mt-2">
      Template includes all active products; edit
      <strong>quantity</strong>
      and
      <strong>unit_price</strong>
      as needed.
    </p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import excelIconUrl from "@/assets/img/microsoft-excel-icon.svg";

/** SheetJS es pesado: se carga en un chunk aparte solo al importar Excel o descargar plantilla */
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

const props = defineProps({
  unitsOptions: { type: Array, default: () => [] },
  warehousesOptions: { type: Array, default: () => [] },
  priceTypesOptions: { type: Array, default: () => [] },
  brandsOptions: { type: Array, default: () => [] },
});

const emit = defineEmits(["import-lines"]);

const busy = ref(false);
const fileInput = ref(null);

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

function cryptoRandom() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function lineFinal(q, up, disc) {
  const qty = Number(q || 0);
  const price = Number(up || 0);
  const d = Number(disc || 0);
  return +(qty * price * (1 - d / 100)).toFixed(2);
}

function normalizeHeader(cell) {
  return String(cell ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
}

function findColIndex(headers, aliases) {
  for (let i = 0; i < headers.length; i += 1) {
    const h = normalizeHeader(headers[i]);
    if (aliases.includes(h)) return i;
  }
  return -1;
}

/** Map product id → { id, name, sku } for lookup; SKU is only used to validate the reference column. */
async function fetchProductsByIdMap() {
  const { data } = await axios.get("/api/products/", {
    params: { is_active: true },
  });
  const list = Array.isArray(data) ? data : data?.results || [];
  const byId = new Map();
  list.forEach((p) => {
    byId.set(Number(p.id), {
      id: p.id,
      name: p.name || "",
      sku: (p.sku && String(p.sku)) || "",
    });
  });
  return byId;
}

const EXCEL_MIME_OK = new Set([
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.ms-excel",
]);

function isExcelFile(file) {
  if (!file?.name) return false;
  if (!/\.(xlsx|xls)$/i.test(file.name)) return false;
  const t = file.type || "";
  if (!t) return true;
  if (EXCEL_MIME_OK.has(t)) return true;
  // Algunos navegadores reportan genérico aunque la extensión sea correcta
  if (t === "application/octet-stream") return true;
  return false;
}

function findOptionIdByLabel(options, name, fieldLabel) {
  if (name === undefined || name === null || String(name).trim() === "")
    return null;
  const n = String(name).trim().toLowerCase();
  const o = options.find((x) => String(x.label).trim().toLowerCase() === n);
  if (!o) {
    throw new Error(`Unknown ${fieldLabel}: "${name}"`);
  }
  return o.value;
}

/** Resuelve unidad por código o por nombre (coincide con el grid: code en label). */
function findUnitIdByCodeOrName(options, raw) {
  if (raw === undefined || raw === null || String(raw).trim() === "")
    return null;
  const s = String(raw).trim().toLowerCase();
  const o = options.find((x) => {
    const code = String(x.code ?? x.label ?? "")
      .trim()
      .toLowerCase();
    const name = String(x.name ?? "")
      .trim()
      .toLowerCase();
    return code === s || (name && name === s);
  });
  if (!o) {
    throw new Error(`Unknown unit (code or name): "${raw}"`);
  }
  return o.value;
}

function buildColumnMap(headerRow) {
  const headers = headerRow.map((c) => normalizeHeader(c));
  const idxPid = findColIndex(headers, [
    "product_id",
    "productid",
    "id_product",
    "product_pk",
  ]);
  const idxName = findColIndex(headers, ["product_name", "name"]);
  const idxSku = findColIndex(headers, ["product_sku", "sku", "product_code"]);
  const idxQty = findColIndex(headers, ["quantity", "qty"]);
  const idxUnit = findColIndex(headers, ["unit_code", "unit", "uom"]);
  const idxPrice = findColIndex(headers, ["unit_price", "price"]);
  const idxDisc = findColIndex(headers, [
    "discount_percent",
    "disc_percent",
    "disc",
    "discount",
  ]);
  const idxWh = findColIndex(headers, ["warehouse_name", "warehouse"]);
  const idxPt = findColIndex(headers, [
    "price_type_name",
    "price_type",
    "pricetype",
  ]);
  const idxBr = findColIndex(headers, ["brand_name", "brand"]);

  const m = {
    idxPid,
    idxName,
    idxSku,
    idxQty,
    idxUnit,
    idxPrice,
    idxDisc,
    idxWh,
    idxPt,
    idxBr,
  };
  if (idxPid < 0) {
    throw new Error("Missing required column: product_id");
  }
  return m;
}

function parseSheetRows(rows) {
  if (!rows || rows.length < 3) {
    throw new Error(
      "File must have header row, description row, and at least one data row (from row 3)."
    );
  }
  const col = buildColumnMap(rows[0]);
  const dataRows = rows.slice(2);
  return { col, dataRows };
}

async function rowsToLines(col, dataRows, productById) {
  const lines = [];
  const rowErrors = [];
  const rowWarnings = [];

  for (let i = 0; i < dataRows.length; i += 1) {
    const row = dataRows[i];
    const excelRow = i + 3;
    const pidRaw = row[col.idxPid];
    if (
      pidRaw === undefined ||
      pidRaw === null ||
      String(pidRaw).trim() === ""
    ) {
      continue;
    }

    try {
      const pid = parseInt(String(pidRaw).trim(), 10);
      if (!Number.isFinite(pid)) {
        rowErrors.push(`Row ${excelRow}: invalid product_id "${pidRaw}"`);
        continue;
      }

      const prod = productById.get(pid);
      if (!prod) {
        rowErrors.push(
          `Row ${excelRow}: product_id ${pid} not found in catalog`
        );
        continue;
      }

      if (col.idxSku >= 0) {
        const skuRef = row[col.idxSku];
        if (
          skuRef !== undefined &&
          skuRef !== null &&
          String(skuRef).trim() !== ""
        ) {
          const ref = String(skuRef).trim().toLowerCase();
          const expected = String(prod.sku || "")
            .trim()
            .toLowerCase();
          if (expected && ref !== expected) {
            rowWarnings.push(
              `Row ${excelRow}: product_sku "${skuRef}" does not match product_id ${pid} (catalog SKU: "${
                prod.sku || "—"
              }") — line imported by ID`
            );
          }
        }
      }

      const qty = col.idxQty >= 0 ? Number(row[col.idxQty] ?? 1) : 1;
      const unitPrice = col.idxPrice >= 0 ? Number(row[col.idxPrice] ?? 0) : 0;
      const disc = col.idxDisc >= 0 ? Number(row[col.idxDisc] ?? 0) : 0;
      const unitCode = col.idxUnit >= 0 ? row[col.idxUnit] : "";
      const whName = col.idxWh >= 0 ? row[col.idxWh] : "";
      const ptName = col.idxPt >= 0 ? row[col.idxPt] : "";
      const brName = col.idxBr >= 0 ? row[col.idxBr] : "";

      let unitId = null;
      if (
        col.idxUnit >= 0 &&
        unitCode !== undefined &&
        String(unitCode).trim() !== ""
      ) {
        unitId = findUnitIdByCodeOrName(props.unitsOptions, unitCode);
      }

      let warehouseId = null;
      if (
        col.idxWh >= 0 &&
        whName !== undefined &&
        String(whName).trim() !== ""
      ) {
        warehouseId = findOptionIdByLabel(
          props.warehousesOptions,
          whName,
          "warehouse"
        );
      }

      let priceTypeId = null;
      if (
        col.idxPt >= 0 &&
        ptName !== undefined &&
        String(ptName).trim() !== ""
      ) {
        priceTypeId = findOptionIdByLabel(
          props.priceTypesOptions,
          ptName,
          "price type"
        );
      }

      let brandId = null;
      if (
        col.idxBr >= 0 &&
        brName !== undefined &&
        String(brName).trim() !== ""
      ) {
        brandId = findOptionIdByLabel(props.brandsOptions, brName, "brand");
      }

      lines.push({
        __key: cryptoRandom(),
        selected: false,
        id: null,
        product: prod.id,
        product_label: prod.name,
        quantity: Number.isFinite(qty) ? qty : 1,
        unit: unitId,
        unit_price: Number.isFinite(unitPrice) ? unitPrice : 0,
        discount_percentage: Number.isFinite(disc) ? disc : 0,
        final_price: lineFinal(qty, unitPrice, disc),
        warehouse: warehouseId,
        price_type: priceTypeId,
        brand: brandId,
        brands: [],
        _errors: {},
      });
    } catch (e) {
      rowErrors.push(`Row ${excelRow}: ${e.message || e}`);
    }
  }

  return { lines, rowErrors, rowWarnings };
}

async function onFile(ev) {
  const file = ev.target.files?.[0];
  if (!file) return;
  if (!isExcelFile(file)) {
    await Swal.fire({
      icon: "error",
      title: "Invalid file",
      text: "Please choose an Excel file (.xlsx or .xls) only.",
      confirmButtonText: "OK",
    });
    if (fileInput.value) fileInput.value.value = "";
    return;
  }
  busy.value = true;
  try {
    const XLSX = await getXlsx();
    const buf = await file.arrayBuffer();
    const wb = XLSX.read(buf, { type: "array" });
    const sheet = wb.Sheets[wb.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: "" });
    const { col, dataRows } = parseSheetRows(rows);

    const productById = await fetchProductsByIdMap();
    const {
      lines: newLines,
      rowErrors,
      rowWarnings,
    } = await rowsToLines(col, dataRows, productById);

    if (newLines.length === 0) {
      await Swal.fire({
        icon: "warning",
        title: "No lines imported",
        html:
          rowErrors.length > 0
            ? `<ul class="text-start small">${rowErrors
                .map((e) => `<li>${e}</li>`)
                .join("")}</ul>`
            : "No data rows with a valid product_id were found.",
        confirmButtonText: "OK",
      });
      return;
    }

    const confirm = await Swal.fire({
      icon: "question",
      title: "Replace line items?",
      html: `Import <strong>${
        newLines.length
      }</strong> line(s). Current rows in the grid will be replaced.${
        rowErrors.length
          ? `<p class="text-warning small mt-2">Some rows were skipped:</p><ul class="text-start small">${rowErrors
              .slice(0, 15)
              .map((e) => `<li>${e}</li>`)
              .join("")}${rowErrors.length > 15 ? "<li>…</li>" : ""}</ul>`
          : ""
      }`,
      showCancelButton: true,
      confirmButtonText: "Import",
      cancelButtonText: "Cancel",
    });

    if (!confirm.isConfirmed) return;

    emit("import-lines", newLines);

    if (rowWarnings.length || rowErrors.length) {
      let html = `<p>${newLines.length} row(s) loaded.</p>`;
      if (rowErrors.length) {
        html += `<p class="text-start small mt-2 mb-1">Skipped rows:</p><ul class="text-start small">${rowErrors
          .map((e) => `<li>${e}</li>`)
          .join("")}</ul>`;
      }
      if (rowWarnings.length) {
        html += `<p class="text-start small text-muted mt-2 mb-1">SKU reference (optional):</p><ul class="text-start small">${rowWarnings
          .map((w) => `<li>${w}</li>`)
          .join("")}</ul>`;
      }
      await Swal.fire({
        icon: "info",
        title: "Import finished",
        html,
        confirmButtonText: "OK",
      });
    } else {
      await Swal.fire({
        icon: "success",
        title: "Lines imported",
        text: `${newLines.length} row(s) loaded into the grid.`,
        confirmButtonText: "OK",
      });
    }
  } catch (e) {
    console.error(e);
    await Swal.fire({
      icon: "error",
      title: "Import failed",
      text: e?.message || String(e),
      confirmButtonText: "OK",
    });
  } finally {
    busy.value = false;
    if (fileInput.value) fileInput.value.value = "";
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

    const defaultWh = props.warehousesOptions[0]?.label || "";
    const defaultPt = props.priceTypesOptions[0]?.label || "";

    const dataRows = list.map((p) => {
      const brandName = p.default_brand?.name || "";
      // Nombre de unit_default (preferido); si falta, código — alineado con ProductListSerializer
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
      text: `${list.length} product row(s). Edit quantity and unit_price as needed, then import.`,
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
.transaction-lines-excel-panel {
  border-color: rgba(13, 110, 253, 0.35) !important;
}
</style>
