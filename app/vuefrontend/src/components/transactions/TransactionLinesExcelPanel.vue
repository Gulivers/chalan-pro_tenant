<template>
  <div
    class="transaction-lines-excel-panel border rounded-3 p-3 bg-light bg-opacity-50">
    <div class="d-flex flex-wrap align-items-center gap-3">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-file-earmark-arrow-up text-success fs-5" aria-hidden="true" />
        <div>
          <label class="form-label small fw-semibold mb-0">Import items</label>
          <input
            ref="fileInput"
            type="file"
            class="form-control form-control-sm"
            accept=".xlsx,.xls"
            :disabled="busy"
            @change="onFile" />
        </div>
      </div>
      <div class="vr d-none d-sm-block" />
      <button
        type="button"
        class="btn btn-outline-success btn-sm d-inline-flex align-items-center gap-1"
        :disabled="busy"
        @click="downloadTemplate">
        <i class="bi bi-file-earmark-excel" aria-hidden="true" />
        Download example template
      </button>
    </div>
    <p class="small text-muted mb-0 mt-2">
      Use the template: row 1 = field codes, row 2 = descriptions, data from row 3.
      Match products by <strong>SKU</strong>, units by <strong>unit code</strong>, warehouse / price type /
      brand by <strong>name</strong> (as in the system).
    </p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import * as XLSX from "xlsx";

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
  "Product SKU (required; must exist in catalog — see Inventory)",
  "Quantity (decimal)",
  "Unit code (Unit of Measure code, e.g. EA, CS — must match system)",
  "Unit price (number)",
  "Discount % (0–100)",
  "Warehouse name (exact name as in Warehouses, e.g. Main Warehouse)",
  "Price type name (exact name as in Price Types, e.g. Retail)",
  "Brand name (exact name as in Brands; optional)",
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

async function fetchProductsSkuMap() {
  const { data } = await axios.get("/api/products/", {
    params: { is_active: true },
  });
  const list = Array.isArray(data) ? data : data?.results || [];
  const map = new Map();
  list.forEach((p) => {
    if (p.sku) map.set(String(p.sku).trim().toLowerCase(), { id: p.id, name: p.name });
  });
  return map;
}

function findOptionIdByLabel(options, name, fieldLabel) {
  if (name === undefined || name === null || String(name).trim() === "") return null;
  const n = String(name).trim().toLowerCase();
  const o = options.find((x) => String(x.label).trim().toLowerCase() === n);
  if (!o) {
    throw new Error(`Unknown ${fieldLabel}: "${name}"`);
  }
  return o.value;
}

function findUnitIdByCode(options, code) {
  if (code === undefined || code === null || String(code).trim() === "") return null;
  const c = String(code).trim().toLowerCase();
  const o = options.find((x) => String(x.label).trim().toLowerCase() === c);
  if (!o) {
    throw new Error(`Unknown unit code: "${code}"`);
  }
  return o.value;
}

function buildColumnMap(headerRow) {
  const headers = headerRow.map((c) => normalizeHeader(c));
  const idxSku = findColIndex(headers, ["product_sku", "sku", "product_code"]);
  const idxQty = findColIndex(headers, ["quantity", "qty"]);
  const idxUnit = findColIndex(headers, ["unit_code", "unit", "uom"]);
  const idxPrice = findColIndex(headers, ["unit_price", "price"]);
  const idxDisc = findColIndex(headers, ["discount_percent", "disc_percent", "disc", "discount"]);
  const idxWh = findColIndex(headers, ["warehouse_name", "warehouse"]);
  const idxPt = findColIndex(headers, ["price_type_name", "price_type", "pricetype"]);
  const idxBr = findColIndex(headers, ["brand_name", "brand"]);

  const m = { idxSku, idxQty, idxUnit, idxPrice, idxDisc, idxWh, idxPt, idxBr };
  if (idxSku < 0) {
    throw new Error('Missing required column: product_sku (or "sku")');
  }
  return m;
}

function parseSheetRows(rows) {
  if (!rows || rows.length < 3) {
    throw new Error("File must have header row, description row, and at least one data row (from row 3).");
  }
  const col = buildColumnMap(rows[0]);
  const dataRows = rows.slice(2);
  return { col, dataRows };
}

async function rowsToLines(col, dataRows, skuMap) {
  const lines = [];
  const rowErrors = [];

  for (let i = 0; i < dataRows.length; i += 1) {
    const row = dataRows[i];
    const excelRow = i + 3;
    const skuRaw = row[col.idxSku];
    if (skuRaw === undefined || skuRaw === null || String(skuRaw).trim() === "") {
      continue;
    }

    try {
      const skuKey = String(skuRaw).trim().toLowerCase();
      const prod = skuMap.get(skuKey);
      if (!prod) {
        rowErrors.push(`Row ${excelRow}: SKU "${skuRaw}" not found in products`);
        continue;
      }

      const qty =
        col.idxQty >= 0 ? Number(row[col.idxQty] ?? 1) : 1;
      const unitPrice =
        col.idxPrice >= 0 ? Number(row[col.idxPrice] ?? 0) : 0;
      const disc =
        col.idxDisc >= 0 ? Number(row[col.idxDisc] ?? 0) : 0;
      const unitCode = col.idxUnit >= 0 ? row[col.idxUnit] : "";
      const whName = col.idxWh >= 0 ? row[col.idxWh] : "";
      const ptName = col.idxPt >= 0 ? row[col.idxPt] : "";
      const brName = col.idxBr >= 0 ? row[col.idxBr] : "";

      let unitId = null;
      if (col.idxUnit >= 0 && unitCode !== undefined && String(unitCode).trim() !== "") {
        unitId = findUnitIdByCode(props.unitsOptions, unitCode);
      }

      let warehouseId = null;
      if (col.idxWh >= 0 && whName !== undefined && String(whName).trim() !== "") {
        warehouseId = findOptionIdByLabel(props.warehousesOptions, whName, "warehouse");
      }

      let priceTypeId = null;
      if (col.idxPt >= 0 && ptName !== undefined && String(ptName).trim() !== "") {
        priceTypeId = findOptionIdByLabel(props.priceTypesOptions, ptName, "price type");
      }

      let brandId = null;
      if (col.idxBr >= 0 && brName !== undefined && String(brName).trim() !== "") {
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

  return { lines, rowErrors };
}

async function onFile(ev) {
  const file = ev.target.files?.[0];
  if (!file) return;
  busy.value = true;
  try {
    const buf = await file.arrayBuffer();
    const wb = XLSX.read(buf, { type: "array" });
    const sheet = wb.Sheets[wb.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: "" });
    const { col, dataRows } = parseSheetRows(rows);

    const skuMap = await fetchProductsSkuMap();
    const { lines: newLines, rowErrors } = await rowsToLines(col, dataRows, skuMap);

    if (newLines.length === 0) {
      await Swal.fire({
        icon: "warning",
        title: "No lines imported",
        html:
          rowErrors.length > 0
            ? `<ul class="text-start small">${rowErrors.map((e) => `<li>${e}</li>`).join("")}</ul>`
            : "No data rows with a valid SKU were found.",
        confirmButtonText: "OK",
      });
      return;
    }

    const confirm = await Swal.fire({
      icon: "question",
      title: "Replace line items?",
      html: `Import <strong>${newLines.length}</strong> line(s). Current rows in the grid will be replaced.${
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

    if (rowErrors.length) {
      await Swal.fire({
        icon: "info",
        title: "Import finished with notes",
        html: `<ul class="text-start small">${rowErrors.map((e) => `<li>${e}</li>`).join("")}</ul>`,
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

function downloadTemplate() {
  try {
    const exampleWh =
      props.warehousesOptions[0]?.label ||
      "(replace with your warehouse name)";
    const examplePt =
      props.priceTypesOptions[0]?.label || "(replace with your price type)";
    const exampleBrand =
      props.brandsOptions[0]?.label || "(optional brand name)";
    const exampleUnit = props.unitsOptions[0]?.label || "EA";

    const sampleSku = "REPLACE-WITH-VALID-SKU";
    const rows = [
      HEADER_CODES,
      HEADER_DESC,
      [sampleSku, 1, exampleUnit, 0, 0, exampleWh, examplePt, exampleBrand],
    ];

    const ws = XLSX.utils.aoa_to_sheet(rows);
    ws["!cols"] = [
      { wch: 14 },
      { wch: 10 },
      { wch: 12 },
      { wch: 12 },
      { wch: 14 },
      { wch: 28 },
      { wch: 22 },
      { wch: 22 },
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Lines");

    XLSX.writeFile(wb, "jobrithm_transaction_lines_template.xlsx");
  } catch (e) {
    console.error(e);
    Swal.fire({
      icon: "error",
      title: "Could not build template",
      text: e?.message || String(e),
    });
  }
}
</script>

<style scoped>
.transaction-lines-excel-panel {
  border-color: rgba(13, 110, 253, 0.35) !important;
}
</style>
