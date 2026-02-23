<template>
  <div class="container-fluid position-relative my-2">
    <h3 class="text-center text-warning mb-2">Inventory Transfer</h3>
    <div class="card shadow mb-2 mx-3">
      <div class="card-header">
        <div class="d-none d-md-flex align-items-center justify-content-between">
          <h6 class="mb-0 text-primary">{{ formTitle }}</h6>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary" type="button" @click="goBack">Back</button>
            <button
              v-if="!isViewMode && !isReverted"
              class="btn btn-primary"
              type="button"
              :disabled="submitting"
              @click="handleSubmit">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ submitting ? "Saving..." : "Save" }}
            </button>
          </div>
        </div>
        <div class="d-md-none">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="mb-0 text-primary">{{ formTitle }}</h6>
          </div>
          <div class="d-flex gap-1 flex-wrap">
            <button class="btn btn-outline-secondary btn-sm flex-fill" type="button" @click="goBack">Back</button>
            <button
              v-if="!isViewMode && !isReverted"
              class="btn btn-primary btn-sm flex-fill"
              type="button"
              :disabled="submitting"
              @click="handleSubmit">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              {{ submitting ? "Saving..." : "Save" }}
            </button>
          </div>
        </div>
      </div>

      <div class="card-body">
        <div class="row g-3 mb-3">
          <div class="col-12 col-md-4">
            <label class="form-label" for="from_warehouse">
              From Warehouse <span class="text-danger">*</span>
            </label>
            <v-select
              id="from_warehouse"
              v-model="form.from_warehouse"
              :options="warehousesOptions"
              :reduce="o => o.value"
              label="label"
              placeholder="Select warehouse..."
              :disabled="isViewMode || isReverted"
              v-tt
              data-title="Origin warehouse for the transfer"
              :class="{ 'is-invalid': errors.from_warehouse }" />
            <div class="text-danger small" v-if="errors.from_warehouse">{{ errors.from_warehouse[0] }}</div>
          </div>
          <div class="col-12 col-md-4">
            <label class="form-label" for="to_warehouse">
              To Warehouse <span class="text-danger">*</span>
            </label>
            <v-select
              id="to_warehouse"
              v-model="form.to_warehouse"
              :options="warehousesOptions"
              :reduce="o => o.value"
              label="label"
              placeholder="Select warehouse..."
              :disabled="isViewMode || isReverted"
              v-tt
              data-title="Destination warehouse for the transfer"
              :class="{ 'is-invalid': errors.to_warehouse }" />
            <div class="text-danger small" v-if="errors.to_warehouse">{{ errors.to_warehouse[0] }}</div>
          </div>
          <div class="col-12 col-md-4">
            <label class="form-label" for="description">Description</label>
            <input
              id="description"
              v-model.trim="form.description"
              type="text"
              class="form-control"
              :class="{ 'is-invalid': errors.description }"
              placeholder="Description of the transfer"
              v-tt
              data-title="Optional description or reference for this transfer"
              :disabled="isViewMode || isReverted" />
            <div class="text-danger small" v-if="errors.description">{{ errors.description[0] }}</div>
          </div>
          <div class="col-12" v-if="form.id">
            <div class="d-flex gap-3 small text-muted">
              <span v-if="form.status">
                <strong>Status:</strong>
                <span :class="form.status === 'reverted' ? 'text-danger' : 'text-success'">{{ form.status }}</span>
              </span>
              <span v-if="form.created_at">Created: {{ formatDateTime(form.created_at) }}</span>
              <span v-if="form.last_updated">Last updated: {{ formatDateTime(form.last_updated) }}</span>
              <span v-if="form.created_by_username">By: {{ form.created_by_username }}</span>
            </div>
          </div>
        </div>

        <div v-if="form.from_warehouse && form.to_warehouse && form.from_warehouse !== form.to_warehouse" class="mb-3">
          <h6
            class="text-primary mb-2"
            v-tt
            data-title="Each line creates an OUT movement from origin warehouse and an IN movement to destination warehouse">
            Lines (one line = two movements: OUT + IN)
          </h6>
          <TransferLinesGrid
            ref="linesGridRef"
            v-model:lines="form.lines"
            :from-warehouse-id="form.from_warehouse"
            :to-warehouse-id="form.to_warehouse"
            :warehouses-options="warehousesOptions"
            :units-options="unitsOptions"
            :is-read-only="isViewMode || isReverted" />
        </div>
        <div v-else class="alert alert-info">
          Select From Warehouse and To Warehouse (they must be different) to add lines.
        </div>

        <p class="small text-muted mt-3 mb-0">
          <span class="text-danger">*</span> Indicates required fields.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, getCurrentInstance } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';
import TransferLinesGrid from './TransferLinesGrid.vue';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === 'inventory-transfer-view');
const isEditMode = computed(() => !!id && route.name === 'inventory-transfer-edit');

const submitting = ref(false);
const warehousesOptions = ref([]);
const unitsOptions = ref([]);
const linesGridRef = ref(null);

const form = ref({
  id: null,
  from_warehouse: null,
  to_warehouse: null,
  description: '',
  status: '',
  created_at: null,
  last_updated: null,
  created_by_username: null,
  lines: [],
});

const errors = ref({});
const isReverted = computed(() => form.value.status === 'reverted');

const formTitle = computed(() => {
  if (isViewMode.value) return 'View Inventory Transfer';
  if (isEditMode.value) return 'Edit Inventory Transfer';
  return 'New Inventory Transfer';
});

function formatDateTime(val) {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return val;
  return d.toLocaleString();
}

function goBack() {
  router.push({ name: 'inventory-transfer-list' });
}

function buildPayload() {
  const payload = {
    from_warehouse: form.value.from_warehouse,
    to_warehouse: form.value.to_warehouse,
    description: form.value.description || '',
  };
  const lines = (form.value.lines || []).filter(
    l => l.product && ((l.isSerialized && l.serialized_item) || (!l.isSerialized && l.quantity > 0))
  );
  payload.lines = lines.map(l => ({
    product_id: l.product,
    quantity: Number(l.quantity) || 1,
    unit_id: l.unit || null,
    serialized_item_id: l.isSerialized ? l.serialized_item : null,
  }));
  return payload;
}

async function handleSubmit() {
  errors.value = {};
  if (!form.value.from_warehouse) {
    errors.value.from_warehouse = ['From Warehouse is required'];
    return;
  }
  if (!form.value.to_warehouse) {
    errors.value.to_warehouse = ['To Warehouse is required'];
    return;
  }
  if (form.value.from_warehouse === form.value.to_warehouse) {
    errors.value.to_warehouse = ['To Warehouse must be different from From Warehouse'];
    return;
  }
  if (!linesGridRef.value?.validateLines?.()) {
    return;
  }

  const payload = buildPayload();
  if (!payload.lines.length) {
    proxy?.notifyToastError?.('Add at least one line.');
    return;
  }

  submitting.value = true;
  try {
    const url = id ? `/api/inventory-transfers/${id}/` : '/api/inventory-transfers/';
    const method = id ? 'put' : 'post';
    const { data } = await axios[method](url, payload);
    proxy?.notifyToastSuccess?.(id ? 'Transfer updated.' : 'Transfer created.');
    router.push({ name: 'inventory-transfer-list' });
  } catch (err) {
    if (err.response?.data) {
      const d = err.response.data;
      if (typeof d === 'object') {
        errors.value = d;
        if (d.lines) {
          (form.value.lines || []).forEach((row, i) => {
            if (d.lines[i]) row._errors = { ...(row._errors || {}), ...d.lines[i] };
          });
        }
      }
      proxy?.notifyToastError?.(d.detail || d.error || 'Error saving transfer.');
    } else {
      proxy?.notifyToastError?.('Error saving transfer.');
    }
  } finally {
    submitting.value = false;
  }
}

async function loadOptions() {
  try {
    const [whRes, uRes] = await Promise.all([
      axios.get('/api/warehouses/?is_active=true'),
      axios.get('/api/unitsofmeasure/?is_active=true'),
    ]);
    const whList = Array.isArray(whRes.data) ? whRes.data : whRes.data?.results || [];
    const uList = Array.isArray(uRes.data) ? uRes.data : uRes.data?.results || [];
    warehousesOptions.value = whList.map(w => ({ value: w.id, label: w.name }));
    unitsOptions.value = uList.map(u => ({ value: u.id, label: u.code || u.name }));
  } catch (e) {
    console.error('Error loading options:', e);
  }
}

async function loadTransfer() {
  if (!id) return;
  try {
    const { data } = await axios.get(`/api/inventory-transfers/${id}/`);
    form.value = {
      id: data.id,
      from_warehouse: data.from_warehouse,
      to_warehouse: data.to_warehouse,
      description: data.description || '',
      status: data.status || '',
      created_at: data.created_at,
      last_updated: data.last_updated,
      created_by_username: data.created_by_username,
      lines: (data.lines || []).map(l => ({
        __key: `line-${l.product_id}-${l.serialized_item_id || 0}`,
        product: l.product_id,
        product_label: l.product_name,
        quantity: l.quantity,
        unit: l.unit_id,
        serialized_item: l.serialized_item_id,
        isSerialized: !!l.serialized_item_id,
        serializedOptions: l.serialized_item_asset_tag
          ? [{
              value: l.serialized_item_id,
              label: l.serialized_item_asset_tag,
              status: l.serialized_item_status,
              condition: l.serialized_item_condition,
            }]
          : [],
      })),
    };
  } catch (e) {
    proxy?.notifyToastError?.('Error loading transfer.');
    router.push({ name: 'inventory-transfer-list' });
  }
}

onMounted(async () => {
  await loadOptions();
  await loadTransfer();
});
</script>
