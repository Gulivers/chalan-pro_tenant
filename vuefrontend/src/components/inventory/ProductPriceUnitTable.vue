<template>
  <div class="price-unit-settings-section">
    <h5 class="mb-3">Price and Unit Settings</h5>
    <div class="table-responsive" style="min-height: 350px">
      <div class="d-flex justify-content-start">
        <button
      type="button"
      class="btn btn-outline-primary btn-sm mt-3 mb-3"
      @click="addRow"
      :disabled="readonly"
      v-tt
      data-title="Add a new price row">
      + Add Row
    </button>
      </div>
      <table class="table table-bordered align-middle">
        <thead>
          <tr>
            <th>Price Type</th>
            <th>Unit</th>
            <th>Purchase</th>
            <th>Sale</th>
            <th>Price</th>
            <th>Default</th>
            <th>Valid From</th>
            <th>Valid Until</th>
            <th>Active</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in priceUnitRows" :key="index">
            <!-- Price Type -->
            <td>
              <div class="d-flex align-items-center w-100" style="min-width: 240px">
                <v-select
                  :options="priceTypes"
                  v-model="row.price_type"
                  :reduce="type => type.id"
                  label="name"
                  placeholder="Select Price Type"
                  class="flex-grow-1 min-w-0"
                  :disabled="readonly"
                  @open="$emit('refresh-priceTypes')"
                  v-tt
                  data-title="Required. Choose the price policy (e.g., Contractors, Wholesale, Counter)." />
                <button
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openModal('priceType')"
                  :disabled="readonly"
                  v-tt
                  data-title="Add a new price type">
                  <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
                </button>
                <button
                  v-if="row.price_type"
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="editModal('priceType', row.price_type)"
                  :disabled="readonly"
                  v-tt
                  data-title="Edit selected price type">
                  <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15" />
                </button>
              </div>
            </td>

            <!-- Unit -->
            <td>
              <div class="d-flex align-items-center w-100" style="min-width: 240px">
                <v-select
                  :options="units"
                  v-model="row.unit"
                  :reduce="unit => unit.id"
                  label="name"
                  placeholder="Select Unit"
                  class="flex-grow-1 min-w-0"
                  :disabled="readonly"
                  @open="$emit('refresh-units')"
                  v-tt
                  data-title="Required. Unit of measure for this price (e.g., EA, Box, Pair)." />
                <button
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openModal('unit')"
                  :disabled="readonly"
                  v-tt
                  data-title="Add a new unit">
                  <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
                </button>
                <button
                  v-if="row.unit"
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="editModal('unit', row.unit)"
                  :disabled="readonly"
                  v-tt
                  data-title="Edit selected unit">
                  <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15" />
                </button>
              </div>
            </td>

            <!-- Purchase -->
            <td class="text-center">
              <input
                type="checkbox"
                v-model="row.is_purchase"
                class="form-check-input"
                :disabled="readonly"
                v-tt
                data-title="Check if this price applies to purchasing costs." />
            </td>

            <!-- Sale -->
            <td class="text-center">
              <input
                type="checkbox"
                v-model="row.is_sale"
                class="form-check-input"
                :disabled="readonly"
                v-tt
                data-title="Check if this price is used for sales." />
            </td>

            <!-- Price -->
            <td style="min-width: 105px">
              <input
                type="number"
                step="0.01"
                class="form-control form-control-sm w-100"
                v-model="row.price"
                :disabled="readonly"
                placeholder="Enter price"
                v-tt
                data-title="Numeric amount (non‑negative)." />
            </td>

            <!-- Default -->
            <td class="text-center">
              <input
                type="radio"
                name="defaultRow"
                class="form-check-input"
                :checked="row.is_default"
                :disabled="readonly || row.is_purchase"
                @change="setDefault(index)"
                v-tt
                :data-title="row.is_purchase ? 'Default price is not available for purchase prices. Only sale prices can be marked as default.' : 'Marks the primary price row. One default is recommended.'" />
            </td>

            <!-- Dates -->
            <td>
              <input
                type="date"
                v-model="row.valid_from"
                class="form-control"
                :disabled="readonly"
                v-tt
                data-title="Start date of price validity (optional)." />
            </td>
            <td>
              <input
                type="date"
                v-model="row.valid_until"
                class="form-control"
                :disabled="readonly"
                v-tt
                data-title="End date of price validity (optional)." />
            </td>

            <!-- Active -->
            <td class="text-center">
              <input
                type="checkbox"
                v-model="row.is_active"
                class="form-check-input"
                :disabled="readonly"
                v-tt
                data-title="Enable/disable this price row." />
            </td>

            <!-- Delete -->
            <td class="text-center">
              <button
                class="btn btn-sm btn-outline-danger"
                @click="removeRow(index)"
                :disabled="readonly"
                v-tt
                data-title="Remove this row (changes apply after Save).">
                ❌
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  import VSelect from 'vue-select';
  import 'vue-select/dist/vue-select.css';

  export default {
    name: 'ProductPriceUnitTable',
    components: { VSelect },
    props: {
      modelValue: { type: Array, required: true },
      priceTypes: { type: Array, default: () => [] },
      units: { type: Array, default: () => [] },
      readonly: { type: Boolean, default: false },
    },
    emits: ['update:modelValue', 'open-modal', 'edit-modal', 'refresh-priceTypes', 'refresh-units'],

    computed: {
      priceUnitRows: {
        get() {
          return this.modelValue;
        },
        set(newVal) {
          this.$emit('update:modelValue', newVal);
        },
      },
    },

    watch: {
      // ensure at least one row when parent hasn't provided any yet (create mode)
      modelValue: {
        handler(val) {
          if (!this.readonly && (!val || val.length === 0)) {
            this.addRow();
          }
        },
        immediate: true,
        deep: false,
      },
    },

    methods: {
      addRow(prefill = null) {
        const row = Object.assign(
          {
            price_type: '',
            unit: '',
            is_purchase: false,
            is_sale: false,
            price: '',
            is_default: false,
            valid_from: '',
            valid_until: '',
            is_active: true,
          },
          prefill || {}
        );
        // push directly is fine here because parent passes an array reference via v-model
        this.priceUnitRows.push(row);
      },
      removeRow(index) {
        this.priceUnitRows.splice(index, 1);
      },
      setDefault(index) {
        this.priceUnitRows.forEach((row, i) => {
          row.is_default = i === index;
        });
      },
      openModal(type) {
        this.$emit('open-modal', type);
      },
      editModal(type, id) {
        if (id) this.$emit('edit-modal', { type, id });
      },
    },
  };
</script>

<style scoped>
  .price-unit-settings-section {
    padding: 20px 0;
    min-height: 500px;
  }

  .table-responsive {
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    padding: 15px;
    background-color: #f8f9fa;
  }

  .table {
    margin-bottom: 0;
  }

  .table th {
    background-color: #e9ecef;
    border-bottom: 2px solid #dee2e6;
    font-weight: 600;
    padding: 12px 8px;
  }

  .table td {
    padding: 12px 8px;
    vertical-align: middle;
  }

  .btn-outline-primary {
    margin-top: 15px;
  }
</style>
