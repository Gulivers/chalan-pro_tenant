<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" :description="pageDescription">
      <template #actions>
        <div
          v-if="hasPermission('ctrctsapp.add_contract')"
          class="jr-contract-form__bid">
          <JRCheckbox
            inputId="docTypeCheckbox"
            v-model="isBid"
            ariaLabel="Bid"
            :disabled="isReadOnly"
            @update:modelValue="toggleDocType" />
          <label class="jr-contract-form__bid-label" for="docTypeCheckbox">Bid</label>
        </div>
      </template>
    </JRPageHeader>

    <p v-if="errorMessage" class="jr-form-banner" role="alert">
      {{ errorMessage }}
    </p>

    <p v-if="loading" class="jr-contract-form__loading" role="status">
      {{ loading_text }}…
    </p>

    <form
      v-show="!loading && !errorMessage"
      class="jr-contract-form"
      @submit.prevent="createOrUpdateContract"
      @keydown.enter.capture="onEnterAdvance"
      novalidate>
      <div
        v-if="event"
        class="jr-contract-form__event"
        role="note">
        <strong>Event:</strong> {{ event.title }}
        <span aria-hidden="true"> · </span>
        <strong>Crew:</strong> {{ event.crew_title }}
      </div>

      <div class="jr-contract-form__split">
        <JRSection title="Job details">
          <div class="jr-contract-form__identity">
            <div class="jr-form-grid jr-contract-form__grid--identity">
              <!-- 1. Job Type -->
              <JRField
                class="jr-contract-form__field--type"
                v-slot="{ describedby, invalid }"
                label="Job Type"
                required
                inputId="type"
                :error="validationErrors.type">
                <!-- Backend Contract.type is CharField max_length=5 with choices Rough|Trim only — not a Category FK. Submit the name string, never category id. -->
                <div data-jr-focus="type">
                  <JRSelect
                    inputId="type"
                    v-model="newContract.type"
                    :options="jobTypeOptions"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select type"
                    :disabled="isReadOnly"
                    :invalid="invalid"
                    :ariaDescribedby="describedby"
                    @update:modelValue="onJobTypeChange" />
                </div>
              </JRField>

              <!-- 2. Work Account -->
              <JRField
                class="jr-contract-form__field--wa"
                v-slot="{ describedby, invalid }"
                label="Work Account"
                required
                inputId="work-account"
                :error="validationErrors.work_account">
                <div data-jr-focus="work_account" class="jr-contract-form__wa">
                  <WorkAccountSelector
                    inputId="work-account"
                    v-model="newContract.work_account"
                    :showLabel="false"
                    :disabled="isReadOnly"
                    :error="validationErrors.work_account"
                    :ariaDescribedby="describedby"
                    @change="onWorkAccountChanged" />
                </div>
              </JRField>

              <!-- 3. House Model -->
              <JRField
                class="jr-contract-form__field--hm"
                v-slot="{ describedby, invalid }"
                label="House Model"
                required
                inputId="houseModel"
                :error="validationErrors.house_model">
                <div data-jr-focus="house_model">
                  <JRSelectAddon
                    inputId="houseModel"
                    v-model="newContract.house_model"
                    :options="houseModels"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select House Model"
                    filter
                    showClear
                    :disabled="isReadOnly"
                    :invalid="invalid"
                    :required="true"
                    :ariaDescribedby="describedby"
                    :showAdd="true"
                    :showEdit="!!newContract.house_model"
                    :addDisabled="
                      isReadOnly ||
                      !hasPermission('ctrctsapp.add_housemodel')
                    "
                    :editDisabled="
                      isReadOnly ||
                      !hasPermission('ctrctsapp.change_housemodel')
                    "
                    addLabel="Add a new house model to the system"
                    editLabel="Edit the currently selected house model"
                    @add="openModal('add')"
                    @edit="openModal('edit', newContract.house_model)" />
                </div>
              </JRField>

              <!-- 4. Address or Lot -->
              <div class="jr-contract-form__location" role="group" aria-label="Address or Lot">
                <JRField
                  v-slot="{ describedby, invalid }"
                  label="Address"
                  required
                  inputId="address"
                  :error="validationErrors.address"
                  hint="Required for Spot Lot (empty lot + address).">
                  <div data-jr-focus="address">
                    <JRInput
                      inputId="address"
                      v-model="newContract.address"
                      :disabled="isReadOnly"
                      :invalid="invalid"
                      :ariaDescribedby="describedby"
                      @focus="selectText" />
                  </div>
                </JRField>

                <JRField
                  v-slot="{ describedby, invalid }"
                  label="Lot"
                  inputId="lot"
                  :error="validationErrors.lot"
                  hint="Optional for Spot Lot. Whole numbers only (max 10 digits).">
                  <div data-jr-focus="lot">
                    <JRInput
                      inputId="lot"
                      :modelValue="lotDisplay"
                      :disabled="isReadOnly"
                      :invalid="invalid"
                      :ariaDescribedby="describedby"
                      inputmode="numeric"
                      autocomplete="off"
                      @update:modelValue="onLotInput"
                      @focus="selectText" />
                  </div>
                </JRField>
              </div>
            </div>

            <!-- Informational readout — outside fill path -->
            <aside
              v-if="showLightingCircuits"
              class="jr-contract-form__lighting"
              aria-live="polite">
              <span class="jr-contract-form__lighting-label" id="lighting-circuits-label">
                Lighting Circuits
              </span>
              <span
                class="jr-contract-form__lighting-value"
                id="lighting-circuits"
                aria-labelledby="lighting-circuits-label">
                {{ lightingCircuits() }}
              </span>
            </aside>
          </div>
        </JRSection>

        <JRSection title="Pricing">
          <div class="jr-form-grid jr-contract-form__grid--pricing">
            <JRField
              v-slot="{ describedby, invalid }"
              label="SqFt"
              required
              inputId="sqft"
              :error="validationErrors.sqft">
              <div data-jr-focus="sqft">
                <JRInput
                  inputId="sqft"
                  v-model="newContract.sqft"
                  type="number"
                  :min="0"
                  :disabled="isReadOnly"
                  :invalid="invalid"
                  :ariaDescribedby="describedby"
                  @update:modelValue="calculatePrice"
                  @focus="selectText" />
              </div>
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Travel Price"
              required
              inputId="travelPrice"
              :error="validationErrors.travel_price">
              <div data-jr-focus="travel_price">
                <JRInput
                  inputId="travelPrice"
                  v-model="newContract.travel_price"
                  type="number"
                  :min="0"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  :disabled="isReadOnly"
                  :invalid="invalid"
                  :ariaDescribedby="describedby"
                  @update:modelValue="onTravelPriceInput"
                  @focus="selectText" />
              </div>
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Job Price"
              required
              inputId="jobPrice"
              :error="validationErrors.job_price">
              <JRInput
                inputId="jobPrice"
                v-model="newContract.job_price"
                type="number"
                :minFractionDigits="2"
                :maxFractionDigits="2"
                :disabled="isReadOnly"
                :invalid="invalid"
                :ariaDescribedby="describedby"
                @update:modelValue="calculateTotal"
                @focus="selectText" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Total Options"
              required
              inputId="totalOptions"
              :error="validationErrors.total_options">
              <JRInput
                inputId="totalOptions"
                v-model="newContract.total_options"
                type="number"
                :minFractionDigits="2"
                :maxFractionDigits="2"
                :disabled="isReadOnly"
                :invalid="invalid"
                :ariaDescribedby="describedby"
                @update:modelValue="calculateTotal"
                @focus="selectText" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Total"
              required
              inputId="total"
              :error="validationErrors.total">
              <JRInput
                inputId="total"
                v-model="newContract.total"
                type="number"
                :minFractionDigits="2"
                :maxFractionDigits="2"
                :disabled="isReadOnly"
                :invalid="invalid"
                :ariaDescribedby="describedby"
                @focus="selectText" />
            </JRField>

            <JRField
              v-slot="{ describedby }"
              label="Comment"
              inputId="comment"
              class="jr-contract-form__comment-field">
              <JRTextarea
                inputId="comment"
                v-model="newContract.comment"
                :rows="2"
                :disabled="isReadOnly"
                :ariaDescribedby="describedby" />
            </JRField>
          </div>
        </JRSection>
      </div>

      <JRSection
        v-if="($route.path == '/contract-form' && (newContract.work_account || newContract.builder)) || $route.path !== '/contract-form'"
        title="Options">
        <!-- Create: work price qty grid — two columns -->
        <div v-if="$route.path == '/contract-form'" class="jr-contract-form__options-split">
          <div
            v-for="(col, colIdx) in createOptionColumns"
            :key="'wp-col-' + colIdx"
            class="jr-contract-form__options">
            <div class="jr-contract-form__options-head">
              <span>Qty</span>
              <span class="jr-contract-form__options-title">Options: {{ newContract.type }}</span>
              <span>Amount</span>
            </div>
            <div
              v-for="row in col"
              :key="'wp-' + row.index"
              class="jr-contract-form__options-row">
              <template v-if="newContract.type === 'Trim'">
                <input
                  type="number"
                  min="0"
                  step="1"
                  :id="'trim_qty' + row.index"
                  class="jr-contract-form__opt-input jr-contract-form__opt-qty"
                  :aria-label="`Quantity for ${row.price.name || 'option'}`"
                  v-model.number="row.price.trim_qty"
                  @focus="selectText"
                  @input="updateAmount(row.index)" />
                <input
                  type="text"
                  class="jr-contract-form__opt-input jr-contract-form__opt-name"
                  :aria-label="`Option name ${row.price.name || row.index + 1}`"
                  v-model="row.price.name"
                  :placeholder="row.price.name"
                  tabindex="-1" />
                <input
                  type="number"
                  class="jr-contract-form__opt-input jr-contract-form__opt-amount"
                  :aria-label="`Amount for ${row.price.name || 'option'}`"
                  v-model.number="row.price.trim"
                  @input="updateTotalOptions"
                  @focus="selectText"
                  :disabled="!row.price.trim_qty" />
              </template>
              <template v-else-if="newContract.type === 'Rough'">
                <input
                  type="number"
                  min="0"
                  step="1"
                  :id="'rough_qty' + row.index"
                  class="jr-contract-form__opt-input jr-contract-form__opt-qty"
                  :aria-label="`Quantity for ${row.price.name || 'option'}`"
                  v-model.number="row.price.rough_qty"
                  @focus="selectText"
                  @input="updateAmount(row.index)" />
                <input
                  type="text"
                  class="jr-contract-form__opt-input jr-contract-form__opt-name"
                  :aria-label="`Option name ${row.price.name || row.index + 1}`"
                  v-model="row.price.name"
                  :placeholder="row.price.name"
                  tabindex="-1" />
                <input
                  type="number"
                  class="jr-contract-form__opt-input jr-contract-form__opt-amount"
                  :aria-label="`Amount for ${row.price.name || 'option'}`"
                  v-model.number="row.price.rough"
                  @input="updateTotalOptions"
                  @focus="selectText"
                  :disabled="!row.price.rough_qty" />
              </template>
            </div>
          </div>
        </div>

        <!-- Edit/View: contract_details qty grid — two columns -->
        <div v-else class="jr-contract-form__options-split">
          <div
            v-for="(col, colIdx) in editOptionColumns"
            :key="'cd-col-' + colIdx"
            class="jr-contract-form__options">
            <div class="jr-contract-form__options-head">
              <span>Qty</span>
              <span class="jr-contract-form__options-title">Options: {{ newContract.type }}</span>
              <span>Amount</span>
            </div>
            <div
              v-for="row in col"
              :key="'cd-' + row.index"
              class="jr-contract-form__options-row">
              <template v-if="newContract.type === 'Trim'">
                <input
                  type="number"
                  min="0"
                  step="1"
                  :id="'detail_qty' + row.index"
                  class="jr-contract-form__opt-input jr-contract-form__opt-qty"
                  :aria-label="`Quantity for ${row.detail.cdname || 'option'}`"
                  v-model="row.detail.cdtrim_qty"
                  @focus="selectText"
                  @input="updateDetailAmount(row.index)"
                  :disabled="isReadOnly" />
                <input
                  type="text"
                  class="jr-contract-form__opt-input jr-contract-form__opt-name"
                  :aria-label="`Option name ${row.detail.cdname || row.index + 1}`"
                  v-model="row.detail.cdname"
                  :placeholder="row.detail.cdname"
                  :disabled="isReadOnly"
                  tabindex="-1" />
                <input
                  type="number"
                  class="jr-contract-form__opt-input jr-contract-form__opt-amount"
                  :aria-label="`Amount for ${row.detail.cdname || 'option'}`"
                  v-model.number="row.detail.cdtrim"
                  @input="updateTotalOptions"
                  @focus="selectText"
                  :disabled="row.detail.cdtrim_qty <= 0.00 || isReadOnly" />
              </template>
              <template v-else-if="newContract.type === 'Rough'">
                <input
                  type="number"
                  min="0"
                  step="1"
                  :id="'detail_qty' + row.index"
                  class="jr-contract-form__opt-input jr-contract-form__opt-qty"
                  :aria-label="`Quantity for ${row.detail.cdname || 'option'}`"
                  v-model="row.detail.cdrough_qty"
                  @focus="selectText"
                  @input="updateDetailAmount(row.index)"
                  :disabled="isReadOnly" />
                <input
                  type="text"
                  class="jr-contract-form__opt-input jr-contract-form__opt-name"
                  :aria-label="`Option name ${row.detail.cdname || row.index + 1}`"
                  v-model="row.detail.cdname"
                  :placeholder="row.detail.cdname"
                  :disabled="isReadOnly"
                  tabindex="-1" />
                <input
                  type="number"
                  class="jr-contract-form__opt-input jr-contract-form__opt-amount"
                  :aria-label="`Amount for ${row.detail.cdname || 'option'}`"
                  v-model.number="row.detail.cdrough"
                  @input="updateTotalOptions"
                  @focus="selectText"
                  :disabled="row.detail.cdrough_qty <= 0.00 || isReadOnly" />
              </template>
            </div>
          </div>
        </div>
      </JRSection>

      <div class="jr-contract-form__actions">
        <template v-if="!isReadOnly">
          <JRButton type="submit" variant="primary">
            Save Contract
          </JRButton>
          <JRButton type="button" variant="secondary" @click="$router.push('/contracts')">
            Cancel
          </JRButton>
        </template>
        <JRButton v-else type="button" variant="secondary" @click="$router.push('/contracts')">
          Back to list
        </JRButton>
      </div>
    </form>

    <JRDrawer
      class="jr-catalog-drawer"
      :visible="houseModelDrawerVisible"
      :header="houseModelDrawerHeader"
      position="right"
      @update:visible="onHouseModelDrawerVisible">
      <DynamicForm
        v-if="houseModelDrawerVisible"
        :key="houseModelFormKey"
        schema-endpoint="/api/schema/house-model/"
        api-endpoint="/api/house_model/"
        :object-id="houseModelEditId"
        :form-title="houseModelFormTitle"
        :is-modal="true"
        @saved="onHouseModelSaved"
        @cancel="closeHouseModelDrawer" />
    </JRDrawer>

    <JRDialog
      :visible="sqftConfirmVisible"
      header="Confirm large SqFt"
      :message="sqftConfirmMessage"
      confirmLabel="Continue"
      cancelLabel="Cancel"
      @update:visible="onSqftConfirmVisible"
      @confirm="confirmLargeSqft" />
  </JRPage>
</template>

<script>
import axios from 'axios';
import '@assets/css/base.css';
import DynamicForm from '@/components/parties/DynamicForm.vue';
import { openPdf } from "@helpers";
import WorkAccountSelector from '@/components/transactions/WorkAccountSelector.vue';
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRSelect,
  JRSelectAddon,
  JRTextarea,
  JRCheckbox,
  JRButton,
  JRDialog,
  JRDrawer,
} from '@ui';


export default {
  name: 'ContractFormComponent',
  components: {
      DynamicForm,
      WorkAccountSelector,
      JRPage,
      JRPageHeader,
      JRSection,
      JRField,
      JRInput,
      JRSelect,
      JRSelectAddon,
      JRTextarea,
      JRCheckbox,
      JRButton,
      JRDialog,
      JRDrawer,
  },

  data() {
      return {
          loading: true, // OAHP: Se inicializa loading
          errorMessage: "",
          isEditedRough: false, // OAHP: flag detalles con 0 al inicio
          isEditedTrim: false,
          loading_text: 'Loading contracts',
          savedContractId: null,
          savedNeedsReprint: false,
          sqftConfirmVisible: false,
          sqftConfirmMessage: '',
          sqftConfirmAccepted: false,
          // Initial state of newContract and other data properties
          // Estado inicial de newContract y otras propiedades de datos
          newContract: {
              created_by: null,
              date_created: '',
              last_updated: '',
              type: 'Rough',
              doc_type: 'Contract',
              work_account: null,
              house_model: '',
              builder: '',
              job: '',
              lot: null,
              sqft: 0,
              address: '',
              job_price: 0,
              travel_price: 0,
              total_options: 0,
              total: 0,
              comment: 'Required to finish at 100%',
              file: null,
              needs_reprint: false,
              contract_details: [],

          },
          builders: [],
          jobs: [],
          houseModels: [],
          workPrices: [],
          initialPrices: {},
          error: null,
          lotValid: null,
          houseModelDrawerVisible: false,
          houseModelEditId: null,
          houseModelFormNonce: 0,
          isBid: false, // Por defecto, el checkbox no está marcado, lo que significa "Contract"
          event: null,
          // Backend Contract.type choices are Rough|Trim strings only (not Category FK).
          jobTypeOptions: [
              { label: 'Rough', value: 'Rough' },
              { label: 'Trim', value: 'Trim' },
          ],
          validationErrors: {},
          _syncingFromWorkAccount: false,
          /** From public.tenants_tenant.client_type via /api/auth/me/ */
          tenantClientType: null,
      };
  },

  computed: {
      showLightingCircuits() {
          return this.tenantClientType === 'electric';
      },
      filteredContractDetails() {
          if (!this.newContract.type) return [];

          return this.newContract.contract_details.filter(detail => {
              if (this.newContract.type === "Trim") {
                  return detail.cdtrim > 0 || detail.cdtrim_qty > 0;
              } else if (this.newContract.type === "Rough") {
                  return detail.cdrough > 0 || detail.cdrough_qty > 0;
              }
              return false;
          });
      },
      visibleCreateOptionRows() {
          if (!this.newContract.type || !Array.isArray(this.workPrices)) return [];
          return this.workPrices
              .map((price, index) => ({ price, index }))
              .filter(({ price }) => {
                  if (this.newContract.type === 'Trim') {
                      return (price.trim > 0 && price.isEditedTrim) || price.trim_qty >= 0;
                  }
                  if (this.newContract.type === 'Rough') {
                      return (price.rough > 0 && price.isEditedRough) || price.rough_qty >= 0;
                  }
                  return false;
              });
      },
      createOptionColumns() {
          return this.splitOptionColumns(this.visibleCreateOptionRows);
      },
      visibleEditOptionRows() {
          if (!this.newContract.type || !Array.isArray(this.newContract.contract_details)) {
              return [];
          }
          return this.newContract.contract_details
              .map((detail, index) => ({ detail, index }))
              .filter(({ detail }) => {
                  if (this.newContract.type === 'Trim') {
                      return detail.isEditedTrim && !detail.isEditedRough;
                  }
                  if (this.newContract.type === 'Rough') {
                      return detail.isEditedRough && !detail.isEditedTrim;
                  }
                  return false;
              });
      },
      editOptionColumns() {
          return this.splitOptionColumns(this.visibleEditOptionRows);
      },
      isReadOnly() {
          return this.$route.name === 'contract-view';
      },
      pageTitle() {
          const doc = this.newContract.doc_type || 'Contract';
          if (this.$route.path === '/contract-form') return `New ${doc}`;
          if (this.isReadOnly) return `View ${doc}`;
          return `Edit ${doc}`;
      },
      pageDescription() {
          if (this.$route.path === '/contract-form' || !this.newContract.date_created) {
              return '';
          }
          return `Created: ${this.formatDate(this.newContract.date_created)} · Updated: ${this.formatDate(this.newContract.last_updated)}`;
      },
      lotDisplay() {
          return this.newContract.lot == null ? '' : String(this.newContract.lot);
      },
      houseModelDrawerHeader() {
          if (this.houseModelEditId) {
              return `Edit House Model #${this.houseModelEditId}`;
          }
          return 'Add House Model';
      },
      houseModelFormTitle() {
          return this.houseModelEditId ? 'Edit House Model' : 'Create House Model';
      },
      houseModelFormKey() {
          const id = this.houseModelEditId || 'new';
          return `contract-hm-${id}-${this.houseModelFormNonce}`;
      },
  },
  watch: {
      "newContract.type"(newType) {
          // console.log(`Contract type changed to: ${newType}`);
          this.updateTotalOptions();
      },
      'newContract.doc_type'(newVal) {
          this.isBid = (newVal === 'Bid');
      },
      // Watchers to recalculate totals and prices whenever certain fields change
      // Observadores para recalcular totales y precios cuando ciertos campos cambian
      'newContract.sqft': function (newVal, oldVal) {
          this.calculatePrice();
          this.lightingCircuits();
      },
      'newContract.total_options': function (newVal, oldVal) {
          this.calculateTotal();
      },
      'newContract.travel_price': function (newVal, oldVal) {
          this.calculateTotal();
      },
      'workPrices': {
          handler: 'updateTotalOptions',
          deep: true
      },
      'newContract.contract_details': {
          handler: 'updateTotalOptions',
          deep: true
      },
      'newContract.type'(newType) {
          console.log(`Contract type changed to: ${newType}`);
          this.updateTotalOptions();
          this.calculatePrice();
      },
      'newContract.builder': function (newVal, oldVal) {
          if (newVal !== oldVal) {
              // When syncing from Work Account, onWorkAccountChanged owns job/house_model
              if (this._syncingFromWorkAccount) {
                  if (newVal) {
                      this.fetchWorkPrices(newVal);
                      this.updateTravelPrice();
                  }
                  if (this.builders.length > 0) {
                      this.calculatePrice();
                  }
                  return;
              }
              this.newContract.job = ''; // Reset job selection
              this.newContract.house_model = ''; // Reset house model selection
              if (!newVal) {
                  this.newContract.travel_price = 0; // Reset travel price if builder is removed
                  this.newContract.job_price = 0; // Reset
              } else {
                  this.fetchJobs(() => {
                      // Set the job if it was previously selected during editing
                      if (this.newContract.job_id) {
                          this.newContract.job = this.newContract.job_id;
                      }
                  });
                  this.fetchWorkPrices(newVal); // Update work prices based on builder
                  this.updateTravelPrice(); // Update travel price
              }
          }
          if (this.builders.length > 0) {
              this.calculatePrice();
          }
      },
      'builders': function (newVal) {
          // Si el builder ya está definido, recalcula el precio al cargar los builders
          if (this.newContract.builder) {
              this.calculatePrice();
          }
      },
      'newContract.job': function (newVal, oldVal) {
          if (newVal !== oldVal) {
              if (this._syncingFromWorkAccount) {
                  // Keep house_model_id; options load happens in onWorkAccountChanged
                  return;
              }
              this.newContract.house_model = ''; // Reset house model selection

              this.fetchHouseModels(() => {
                  // Set the house model if it was previously selected during editing
                  if (this.newContract.house_model_id) {
                      this.newContract.house_model = this.newContract.house_model_id;
                  }
              });
          }
      },
      'newContract.house_model': function (newVal, oldVal) {
          if (newVal !== oldVal && !this._syncingFromWorkAccount) {
              this.fetchHouseModels();
          }
      },
      'newContract.job_price': function (newVal, oldVal) {
          this.calculateTotal();
      },
  },
  mounted() {
      // Fetch initial data when component is mounted
      // Obtener datos iniciales cuando el componente se monta
      this.loading = true; // Show loading state while fetching data
      this.updateTravelPrice();

      // Prefill desde un Event (Schedule) si viene event_id en query
      const prefill = this.prefillFromEvent();

      Promise.all([
          prefill,
          this.fetchContractToUpdate(),
          this.fetchBuilders(),
          this.fetchJobs(),
          this.fetchHouseModels(),
          this.loadEventFromContract(),
          this.loadJobTypeOptions(),
          this.loadTenantClientType(),
      ]).then(() => {
          this.loading = false; // Solo si todo carga bien, mostramos el formulario
      }).catch(error => {
          console.error("Error loading data:", error);
          this.errorMessage = "There was a problem loading the data. Please check your internet connection and try again.";
          this.loading = false; // No se mostrará el formulario si `errorMessage` tiene valor
      });
  },

  methods: {
      async loadTenantClientType() {
          try {
              const user = await this.getAuthenticatedUser();
              this.tenantClientType = user?.client_type || null;
          } catch (e) {
              console.error('Error loading tenant client_type:', e);
              this.tenantClientType = null;
          }
      },

      toggleDocType(value) {
          if (typeof value === 'boolean') {
              this.isBid = value;
          }
          this.newContract.doc_type = this.isBid ? 'Bid' : 'Contract';
      },

      async prefillFromEvent() {
          try {
              const eventId = this.$route.query.event_id
              if (!eventId) return

              // Leer el evento para obtener work_account, address y lot
              const { data } = await axios.get(`/api/event/${eventId}/`)
              // Guardar objeto del evento para mostrar en encabezado
              this.event = data
              // Guardar schedule para asociar el contrato al evento
              this.newContract.schedule_id = data.id

              // Si existe una Work Account, úsala para sincronizar el formulario
              if (data.work_account) {
                  this.newContract.work_account = data.work_account
                  // Esto autocargará builder, job, house_model, lot y address
                  const wa = await this.onWorkAccountChanged(data.work_account)
                  // Asegurar que house_model, lot y address queden prellenados
                  if (wa) {
                      if (wa.house_model) this.newContract.house_model = wa.house_model
                      if (wa.lot) this.newContract.lot = wa.lot
                      if (wa.address) this.newContract.address = wa.address
                  }
              } else {
                  // Fallback usando datos legacy del evento
                  this.newContract.builder = data.builder || null
                  this.newContract.job = data.job || null
                  this.newContract.house_model = data.house_model || null
              }

              // Prellenar address/lot si vienen del evento
              if (data.lot) this.newContract.lot = data.lot
              if (data.address) this.newContract.address = data.address
          } catch (e) {
              console.error('Error pre-filling contract from event:', e)
          }
      },

      async loadEventFromContract() {
          try {
              // Si estamos en modo edición o vista, cargar el evento (schedule) asociado al contrato
              const id = this.$route.params.id
              if (!id) return
              const { data: contract } = await axios.get(`/api/contract/${id}/`)
              const scheduleId = contract?.schedule
              if (!scheduleId) return
              const { data: event } = await axios.get(`/api/event/${scheduleId}/`)
              this.event = event
          } catch (e) {
              console.error('Error loading event from contract:', e)
          }
      },

      // Select all text in the input field (safe for non-input targets)
      selectText(event) {
          try {
              const input = event?.target;
              if (input && typeof input.select === 'function') {
                  input.select();
              }
          } catch (e) {
              /* ignore — focus target may not support select() */
          }
      },

      async onWorkAccountChanged(workAccountId) {
          try {
              if (!workAccountId) {
                  return;
              }
              const { data } = await axios.get(`/api/work-accounts/${workAccountId}/`);
              const hmId = this.normalizeHouseModelId(data.house_model);
              const hmName = data.house_model_name
                  || (data.house_model && typeof data.house_model === 'object'
                      ? data.house_model.name
                      : null);

              // Remember for edit-style restore paths
              this.newContract.house_model_id = hmId;

              this._syncingFromWorkAccount = true;
              try {
                  // 1) Builder (watchers skipped while syncing)
                  this.newContract.builder = data.builder || null;

                  // 2) Jobs for builder, then set job from WA
                  await this.fetchJobs();
                  this.newContract.job = data.job || null;

                  // 3) House models for job, then set HM from WA when present
                  await this.fetchHouseModels();
                  if (hmId) {
                      await this.ensureHouseModelOption(hmId, hmName);
                      this.newContract.house_model = hmId;
                  } else {
                      this.newContract.house_model = null;
                  }

                  // 4) Lot + Address (Spot Lot: empty lot → null)
                  this.newContract.lot = data.lot ? String(data.lot) : null;
                  this.newContract.address = data.address || '';

                  // 5) Pricing + options
                  this.updateTravelPrice();
                  this.calculatePrice();
                  if (data.builder) {
                      await this.fetchWorkPrices(data.builder);
                  }
              } finally {
                  this._syncingFromWorkAccount = false;
              }
              return data;
          } catch (e) {
              this._syncingFromWorkAccount = false;
              console.error('Error syncing WorkAccount into contract:', e);
          }
      },

      normalizeHouseModelId(houseModel) {
          if (houseModel == null || houseModel === '') return null;
          if (typeof houseModel === 'object') {
              return houseModel.id != null ? houseModel.id : null;
          }
          return houseModel;
      },

      async ensureHouseModelOption(hmId, hmName) {
          if (!hmId) return;
          if (this.houseModels.some((h) => h.id === hmId)) return;

          let name = hmName;
          if (!name) {
              try {
                  const { data } = await axios.get(`/api/house_model/${hmId}/`);
                  name = data?.name || `House Model #${hmId}`;
              } catch (e) {
                  name = `House Model #${hmId}`;
              }
          }
          this.houseModels = [
              ...this.houseModels,
              { id: hmId, name, jobs: this.newContract.job ? [this.newContract.job] : [] },
          ];
      },

      // Operational Enter focus chain (skips Lighting Circuits, calculated money, Comment, option name/amount)
      splitOptionColumns(rows) {
          const list = Array.isArray(rows) ? rows : [];
          if (!list.length) return [[]];
          const mid = Math.ceil(list.length / 2);
          const left = list.slice(0, mid);
          const right = list.slice(mid);
          return right.length ? [left, right] : [left];
      },

      getQtyFocusables() {
          const root = this.$el;
          if (!root) return [];
          return Array.from(root.querySelectorAll('.jr-contract-form__opt-qty')).filter((el) => {
              if (el.disabled || el.getAttribute('disabled') != null) return false;
              if (el.offsetParent === null && getComputedStyle(el).visibility === 'hidden') return false;
              return true;
          });
      },

      getFocusChainKeys() {
          return ['type', 'work_account', 'house_model', 'address', 'lot', 'sqft', 'travel_price'];
      },

      resolveFocusTarget(key) {
          const root = this.$el;
          if (!root) return null;
          const wrap = root.querySelector(`[data-jr-focus="${key}"]`);
          if (!wrap) return null;

          if (key === 'type') {
              return (
                  wrap.querySelector('.p-select') ||
                  wrap.querySelector('[data-pc-name="select"]') ||
                  wrap.querySelector('input') ||
                  wrap
              );
          }
          if (key === 'work_account' || key === 'house_model') {
              return (
                  wrap.querySelector('input.vs__search') ||
                  wrap.querySelector('.vs__search') ||
                  wrap.querySelector('input') ||
                  wrap
              );
          }
          const idMap = {
              address: 'address',
              lot: 'lot',
              sqft: 'sqft',
              travel_price: 'travelPrice',
          };
          const id = idMap[key];
          if (id) {
              const byId = document.getElementById(id);
              if (byId) return byId;
          }
          return wrap.querySelector('input') || wrap;
      },

      buildFocusChain() {
          const chain = [];
          this.getFocusChainKeys().forEach((key) => {
              const el = this.resolveFocusTarget(key);
              if (el) chain.push({ key, el });
          });
          this.getQtyFocusables().forEach((el, i) => {
              chain.push({ key: `qty:${i}`, el });
          });
          return chain;
      },

      findFocusChainIndex(target) {
          if (!target) return -1;
          const chain = this.buildFocusChain();
          for (let i = 0; i < chain.length; i += 1) {
              const el = chain[i].el;
              if (el === target || (el.contains && el.contains(target))) {
                  return i;
              }
          }
          return -1;
      },

      focusChainElement(entry) {
          if (!entry?.el) return;
          const el = entry.el;
          try {
              el.focus?.();
              if (typeof el.select === 'function') {
                  el.select();
              }
          } catch (e) {
              /* ignore */
          }
      },

      focusSaveButton() {
          const btn = this.$el?.querySelector?.('.jr-contract-form__actions button[type="submit"]');
          try {
              btn?.focus?.();
          } catch (e) {
              /* ignore */
          }
      },

      isOpenDropdownTarget(target) {
          if (!target) return false;
          if (target.closest?.('.vs--open')) return true;
          if (target.closest?.('.p-select-overlay')) return true;
          // PrimeVue select open panel is often portaled; leave Enter to the widget when expanded
          const openPanel = document.querySelector('.p-select-overlay:not([style*="display: none"])');
          if (openPanel && openPanel.offsetParent !== null) {
              const wrap = target.closest?.('[data-jr-focus="type"]');
              if (wrap) return true;
          }
          return false;
      },

      onEnterAdvance(event) {
          if (event.key !== 'Enter' || this.isReadOnly) return;

          const target = event.target;
          // Comment keeps native Enter for newlines — not in operational chain
          if (target?.id === 'comment' || target?.closest?.('#comment')) {
              return;
          }

          // Option name/amount: block accidental submit, do not advance
          if (target?.closest?.('.jr-contract-form__opt-name, .jr-contract-form__opt-amount')) {
              event.preventDefault();
              return;
          }

          // Let open dropdowns handle Enter for selection
          if (this.isOpenDropdownTarget(target)) {
              return;
          }

          const chain = this.buildFocusChain();
          const index = this.findFocusChainIndex(target);
          if (index === -1) {
              // Calculated fields / other controls: prevent surprise submit
              if (target?.closest?.('form.jr-contract-form')) {
                  const tag = (target.tagName || '').toLowerCase();
                  if (tag === 'input' || tag === 'textarea' || target.getAttribute?.('contenteditable')) {
                      event.preventDefault();
                  }
              }
              return;
          }

          event.preventDefault();
          event.stopPropagation();

          if (index >= chain.length - 1) {
              this.focusSaveButton();
              return;
          }
          this.focusChainElement(chain[index + 1]);
      },

      focusFirstInvalidField() {
          const order = [
              'work_account',
              'type',
              'house_model',
              'address',
              'lot',
              'sqft',
              'travel_price',
              'job_price',
              'total_options',
              'total',
          ];
          const firstKey = order.find((key) => this.validationErrors[key]);
          if (!firstKey) return;

          this.$nextTick(() => {
              const fromChain = this.resolveFocusTarget(firstKey);
              if (fromChain) {
                  this.focusChainElement({ key: firstKey, el: fromChain });
                  return;
              }
              const idMap = {
                  job_price: 'jobPrice',
                  total_options: 'totalOptions',
                  total: 'total',
              };
              const el = document.getElementById(idMap[firstKey] || firstKey);
              try {
                  el?.focus?.();
              } catch (e) {
                  /* ignore */
              }
          });
      },

      onTravelPriceInput(value) {
          this.newContract.travel_price = value;
          this.calculateTotal();
      },

      normalizeTravelPrice() {
          const raw = this.newContract.travel_price;
          if (raw === null || raw === undefined || raw === '') {
              this.newContract.travel_price = 0;
              return 0;
          }
          const n = Number(raw);
          if (!Number.isFinite(n)) {
              this.newContract.travel_price = 0;
              return 0;
          }
          const fixed = Number(n.toFixed(2));
          this.newContract.travel_price = fixed;
          return fixed;
      },

      trimContractStrings() {
          if (this.newContract.address != null) {
              this.newContract.address = String(this.newContract.address).trim();
          }
          if (this.newContract.comment != null) {
              this.newContract.comment = String(this.newContract.comment).trim();
          }
          // Spot Lot: empty lot → null (never send "")
          if (this.newContract.lot == null || this.newContract.lot === '') {
              this.newContract.lot = null;
          } else {
              const digits = String(this.newContract.lot).replace(/\D/g, '').slice(0, 10);
              this.newContract.lot = digits === '' ? null : digits;
          }
      },

      onJobTypeChange() {
          this.calculatePrice();
          this.updateTotalOptions();
      },
      onLotInput(value) {
          const raw = value == null ? '' : String(value);
          const digits = raw.replace(/\D/g, '').slice(0, 10);
          this.newContract.lot = digits === '' ? null : digits;
          if (this.validationErrors.lot) {
              delete this.validationErrors.lot;
          }
      },
      async loadJobTypeOptions() {
          // Contract.type is CharField choices Rough|Trim only — load matching category names for the select, submit name not id.
          const fallback = [
              { label: 'Rough', value: 'Rough' },
              { label: 'Trim', value: 'Trim' },
          ];
          try {
              const catRes = await axios.get('/api/categories/');
              const cats = catRes.data.results ?? catRes.data;
              const list = Array.isArray(cats) ? cats : [];
              const matched = list
                  .filter((c) => {
                      const name = (c.name || '').trim().toLowerCase();
                      return name === 'rough' || name === 'trim';
                  })
                  .map((c) => {
                      const name = (c.name || '').trim();
                      const canonical = name.toLowerCase() === 'rough' ? 'Rough' : 'Trim';
                      return { label: canonical, value: canonical };
                  });
              // Deduplicate Rough/Trim
              const byValue = new Map();
              matched.forEach((o) => byValue.set(o.value, o));
              this.jobTypeOptions = byValue.size ? Array.from(byValue.values()) : fallback;
          } catch (e) {
              console.error('Error loading categories for Job Type:', e);
              this.jobTypeOptions = fallback;
          }
      },

      lightingCircuits() {
          let sqft = parseFloat(this.newContract.sqft) || 0;
          let num = (sqft * 3) / 120 / 15;

          if (sqft === 0) {
              return 0;
          }

          return Math.ceil(num); // Siempre redondea hacia arriba
      },

      // Initialize prices for workPrices and contract_details
      // Inicializar precios para workPrices y contract_details
      initializePrices() {
          // Inicialización para workPrices (sin cambios)
          this.workPrices.forEach((price, index) => {
              const trimPrice = parseFloat(price.trim);
              const roughPrice = parseFloat(price.rough);

              // Verificar si trim y rough son números válidos
              if (!isNaN(trimPrice) && !isNaN(roughPrice)) {
                  this.initialPrices[`work_${index}_trim`] = trimPrice;
                  this.initialPrices[`work_${index}_rough`] = roughPrice;
              } else {
                  console.error('Precio trim o rough no válido para workPrice:', trimPrice, roughPrice);
              }
          });

          // Inicialización para contract_details
          this.newContract.contract_details.forEach((detail, index) => {
              const detailTrimPrice = parseFloat(detail.cdtrim) || 0;
              const detailRoughPrice = parseFloat(detail.cdrough) || 0;
              const trimQty = parseFloat(detail.cdtrim_qty) || 1;  // Usar 1 si la cantidad es NaN o 0 para evitar división por cero
              const roughQty = parseFloat(detail.cdrough_qty) || 1;  // Usar 1 si la cantidad es NaN o 0 para evitar división por cero

              // Verificar si cdtrim y cdrough son números válidos
              if (!isNaN(detailTrimPrice) && !isNaN(detailRoughPrice)) {
                  // Calcular los precios unitarios
                  const unitTrimPrice = detailTrimPrice / trimQty;
                  const unitRoughPrice = detailRoughPrice / roughQty;

                  this.initialPrices[`detail_${index}_cdtrim`] = unitTrimPrice;
                  this.initialPrices[`detail_${index}_cdrough`] = unitRoughPrice;
              } else {
                  console.error('Precio cdtrim o cdrough no válido para contract_detail:', detailTrimPrice, detailRoughPrice);
              }
          });

          // Ver contenido de initialPrices
          // console.log('Contenido de initialPrices:', this.initialPrices);
      },

      // Update price based on quantity in workPrices
      // Actualizar el precio según la cantidad en workPrices
      updateAmount(index) {
          // Ensure workPrices is initialized and index exists
          if (!this.workPrices || !this.workPrices[index]) {
              console.error(`workPrices[${index}] is undefined`);
              return;
          }
          // Prevent negative numbers
          if (this.workPrices[index].trim_qty < 0) {
              this.workPrices[index].trim_qty = 0;
          }

          const qty = this.newContract.type === 'Trim'
              ? parseFloat(this.workPrices[index].trim_qty) || 0
              : parseFloat(this.workPrices[index].rough_qty) || 0;
          const trimOrRough = this.newContract.type === 'Trim' ? 'trim' : 'rough';
          const initialPrice = this.initialPrices[`work_${index}_${trimOrRough}`];

          // Verificar si initialPrice es un número válido
          if (!isNaN(initialPrice) && !isNaN(qty) && qty > 0) {
              // Calcular el nuevo precio basado en el precio inicial y la cantidad
              const newPrice = initialPrice * qty;
              this.workPrices[index][trimOrRough] = newPrice.toFixed(2);
              //console.log(`Nuevo precio para work_${index}_${trimOrRough}: ${newPrice.toFixed(2)}`);
          } else {
              console.error(`Precio inicial no válido para work_${index}_${trimOrRough}`);
          }
      },

      // Update total options based on workPrices or contract_details
      // Actualizar las opciones totales en función de workPrices o contract_details
      updateDetailAmount(index) {
          const trimOrRough = this.newContract.type === 'Trim' ? 'cdtrim' : 'cdrough';
          const qtyKey = trimOrRough + '_qty';

          let qty = parseFloat(this.newContract.contract_details[index][qtyKey]) || 0;
          if (qty < 0) {
              this.newContract.contract_details[index][qtyKey] = 0;
              qty = 0;
          }

          const initialPrice = this.initialPrices[`detail_${index}_${trimOrRough}`];
          if (!isNaN(initialPrice)) {
              this.newContract.contract_details[index][trimOrRough] = qty >= 1 ? initialPrice * qty : 0;
          } else {
              this.newContract.contract_details[index][trimOrRough] = 0;
          }
      },

      // Update total options based on workPrices or contract_details
      // Actualizar las opciones totales en función de workPrices o contract_details
      updateTotalOptions() {
          const trimOrRough = this.newContract.type === 'Trim' ? 'trim' : 'rough';
          let totalOptions = 0;

          if (this.$route.path === '/contract-form') {
              totalOptions = this.workPrices.reduce((sum, price) => {
                  const value = parseFloat(price[trimOrRough]) || 0;
                  const qty = parseFloat(price[trimOrRough + '_qty']) || 0;

                  if (this.newContract.type === 'Trim') {
                      if (!price.isEditedTrim && (value >= 0 || qty > 0)) {
                          price.isEditedTrim = true;
                      }
                      price.isEditedRough = false;
                  }

                  if (this.newContract.type === 'Rough') {
                      if (!price.isEditedRough && (value >= 0 || qty > 0)) {
                          price.isEditedRough = true;
                      }
                      price.isEditedTrim = false;
                  }
                  // console.log("prices :", JSON.stringify(price, ["id", "name", "trim", "rough", "unit_price", "isEditedTrim", "isEditedRough"], 2));
                  // console.log("qty: ", qty);
                  return qty >= 1 ? sum + value : sum;
              }, 0);
          } else {
              totalOptions = this.filteredContractDetails.reduce((sum, detail) => {
                  const value = parseFloat(detail['cd' + trimOrRough]) || 0;
                  const qty = parseFloat(detail['cd' + trimOrRough + '_qty']) || 0;

                  detail.isEditedTrim = this.newContract.type === 'Trim' && (value > 0 || qty > 0);
                  detail.isEditedRough = this.newContract.type === 'Rough' && (value > 0 || qty > 0);
                  // console.log(`Type: ${this.newContract.type}, name: ${detail.cdname}, Trim: ${detail.cdtrim}, Rough: ${detail.cdrough},isEditedTrim: ${detail.isEditedTrim}, isEditedRough: ${detail.isEditedRough}`);
                  // console.log("qty: ", qty);

                  return qty >= 1 ? sum + value : sum;
              }, 0);
          }

          this.newContract.total_options = totalOptions.toFixed(2) || 0;
      },

      validateQuantity(index) {
          if (this.price[index].trim_qty < 0) {
              this.price[index].trim_qty = 0;
          }
      },


      // Calculate the total contract amount
      // Calcular el monto total del contrato
      calculateTotal() {
          const jobPrice = parseFloat(this.newContract.job_price) || 0;
          const travelPrice = parseFloat(this.newContract.travel_price) || 0;
          const totalOptions = parseFloat(this.newContract.total_options) || 0;
          const total = totalOptions + jobPrice + travelPrice;
          this.newContract.total = total.toFixed(2);
      },

      // Calculate the job price based on builder and square footage
      // Calcular el precio del trabajo según el constructor y los pies cuadrados
      calculatePrice() {
          const idToUpdate = this.$route.params.id;
          const builderId = this.newContract.builder;
          const sqft = parseFloat(this.newContract.sqft) || 0;
          let jobPrice = 0;

          // Intenta encontrar el builder en la lista cargada
          const builder = this.builders.find(b => b.id === builderId);
          if (!builder) {
              // Si no hay builder cargado y estamos editando, usa el precio existente
              if (idToUpdate) {
                  console.warn('Builder not found, using existing job_price from database.');
                  return;
              }
              this.newContract.job_price = 0;
              return;
          }


          if (this.newContract.type === 'Trim') {
              jobPrice = builder.trim_amount * sqft;
          } else if (this.newContract.type === 'Rough') {
              jobPrice = builder.rough_amount * sqft;
          }

          this.newContract.job_price = jobPrice.toFixed(2);

          if (sqft >= 3000 && !idToUpdate) {
              this.sqftConfirmMessage =
                  'SqFt is ' +
                  sqft +
                  ' (≥ 3000). Continue with this square footage? Cancel resets SqFt to 0.';
              this.sqftConfirmVisible = true;
              return;
          }
      },

      onSqftConfirmVisible(visible) {
          this.sqftConfirmVisible = visible;
          if (!visible) {
              if (this.sqftConfirmAccepted) {
                  this.sqftConfirmAccepted = false;
                  return;
              }
              if (Number(this.newContract.sqft) >= 3000) {
                  this.newContract.sqft = 0;
                  // After dialog teardown, return focus to SqFt (now 0)
                  this.$nextTick(() => {
                      this.$nextTick(() => {
                          const el = this.resolveFocusTarget('sqft');
                          this.focusChainElement({ key: 'sqft', el });
                      });
                  });
              }
          }
      },

      confirmLargeSqft() {
          this.sqftConfirmAccepted = true;
          this.sqftConfirmVisible = false;
      },

      formatDate(dateString) {
          const date = new Date(dateString);
          const options = { year: 'numeric', month: 'long', day: 'numeric' };
          return date.toLocaleDateString('en-EN', options);
      },
      onBuilderSelect(builder) {
          this.newContract.builder = builder.id;
      },
      onJobSelect(job) {
          this.newContract.job = job.id;
      },
      onHouseModelSelect(houseModel) {
          this.newContract.house_model = houseModel.id;
      },

      fetchContractToUpdate() {
          const idToUpdate = this.$route.params.id;
          if (idToUpdate) {
              axios.get(`/api/contract/${idToUpdate}/`)
                  .then(response => {
                      const editData = response.data;
                      this.newContract = {
                          id: editData.id,
                          created_by: editData.created_by,
                          date_created: editData.date_created,
                          last_updated: editData.last_updated,
                          type: editData.type,
                          doc_type: editData.doc_type,
                          work_account: editData.work_account || null,
                          builder: editData.builder.id,
                          builder_id: editData.builder.id,
                          job: editData.job.id,
                          job_id: editData.job.id,
                          house_model: editData.house_model.id,
                          house_model_id: editData.house_model.id,
                          lot: editData.lot,
                          sqft: editData.sqft,
                          address: editData.address,
                          job_price: parseFloat(editData.job_price) || 0,
                          travel_price: parseFloat(editData.travel_price) || 0,
                          total_options: parseFloat(editData.total_options) || 0,
                          total: parseFloat(editData.total) || 0,
                          comment: editData.comment,
                          file: editData.file,
                          contract_details: editData.contract_details.map(detail => ({
                              id: detail.id,
                              cdname: detail.cdname,
                              cdtrim: detail.cdtrim,
                              cdtrim_qty: detail.cdtrim_qty,
                              cdrough: detail.cdrough,
                              cdrough_qty: detail.cdrough_qty,
                              cdunit_price: detail.cdunit_price,
                              cdwork_price: detail.cdwork_price,
                              isEditedTrim: detail.isEditedTrim !== undefined ? detail.isEditedTrim : false,  // OAHP: Se agrega para evitar que se oculten detalles con 0 al inicio
                              isEditedRough: detail.isEditedRough !== undefined ? detail.isEditedRough : false  // OAHP: Se agrega para evitar que se oculten detalles con 0 al inicio
                          }))
                      };
                      // Sincroniza el checkbox con doc_type:
                      this.isBid = (this.newContract.doc_type === 'Bid')
                      // Fetch builders and ensure jobs are loaded after setting the builder
                      return this.fetchBuilders();
                  })
                  .then(() => {
                      return this.fetchJobs(() => {
                          if (this.newContract.job_id) {
                              this.newContract.job = this.newContract.job_id;
                          }
                      });
                  })
                  .then(() => {
                      this.fetchHouseModels(() => {
                          if (this.newContract.house_model_id) {
                              this.newContract.house_model = this.newContract.house_model_id;
                          }
                      });
                      this.calculatePrice();
                      this.initializePrices();
                  })
                  .catch(error => {
                      console.error('Error fetching data for editing:', error);
                  });
          }
      },

      fetchWorkPrices(builderId) {
          const idToUpdate = this.$route.params.id;
          if (idToUpdate || !builderId) {
              return Promise.resolve([]);
          }
          return axios.get(`/api/workprice/?builder=${builderId}`)
              .then(response => {
                  this.workPrices = response.data.map(price => ({
                      ...price,
                      isEditedTrim: false,  // Properly initializing flags for each price
                      isEditedRough: false
                  }));
                  this.initializePrices();  // Call after setting initial values
                  return this.workPrices;
              })
              .catch(error => {
                  console.error('Error fetching work prices:', error);
                  throw error;
              });
      },

      // Fetch available builders from the server
      // Obtener builders disponibles del servidor
      fetchBuilders() {
          return new Promise((resolve, reject) => {
              axios.get('/api/builder/')
                  .then(response => {
                      this.builders = response.data;
                      resolve(); // Resuelve la promesa indicando que terminó correctamente
                      this.updateTravelPrice();
                      this.newContract.job = '';
                      this.newContract.house_model = '';
                  })
                  .catch(error => {
                      console.error('Error fetching builders:', error);
                      reject(error); // Rechaza la promesa si ocurre un error
                  });
          });
      },

      // Fetch available Job from the server
      // Obtener Job de casas disponibles del servidor
      fetchJobs(callback = null) {
          const builderId = this.newContract.builder;
          if (!builderId) {
              if (callback) callback();
              return Promise.resolve([]);
          }

          return axios.get(`/api/job/jobs_by_builder/`, { params: { builder_id: builderId } })
              .then(response => {
                  this.jobs = response.data.map(job => ({
                      id: job.id,
                      name: job.name,
                      builder: job.builder // Ensure the builder property is included
                  }));
                  if (callback) callback();
                  return this.jobs;
              })
              .catch(error => {
                  console.error("Error fetching jobs:", error);
                  throw error;
              });
      },

      openModal(action, houseIdModel) {
          if (action === 'edit' && houseIdModel) {
              this.houseModelEditId = houseIdModel;
          } else {
              this.houseModelEditId = null;
          }
          this.houseModelFormNonce += 1;
          this.houseModelDrawerVisible = true;
      },

      onHouseModelDrawerVisible(visible) {
          this.houseModelDrawerVisible = visible;
          if (!visible) this.houseModelEditId = null;
      },

      closeHouseModelDrawer() {
          this.houseModelDrawerVisible = false;
          this.houseModelEditId = null;
      },

      async onHouseModelSaved() {
          await this.fetchHouseModels();
          this.closeHouseModelDrawer();
      },

      // Fetch available house models from the server
      fetchHouseModels(callback = null) {
          const jobId = this.newContract.job;
          if (!jobId) {
              if (callback) callback();
              return Promise.resolve([]);
          }

          return axios.get('/api/house_models_by_job/', { params: { job_id: jobId } })
              .then(response => {
                  this.houseModels = response.data.map(houseModel => ({
                      id: houseModel.id,
                      name: houseModel.name,
                      jobs: houseModel.jobs
                  }));
                  if (callback) callback();
                  return this.houseModels;
              })
              .catch(error => {
                  console.error('Error fetching house models:', error);
                  throw error;
              });
      },

      closeModal() {
          this.closeHouseModelDrawer();
      },

      // Update travel price based on builder and job location
      // Actualizar el precio del viaje según el constructor y la ubicación del trabajo
      updateTravelPrice() {
          const builderId = this.newContract.builder;
          if (!builderId) {
              this.newContract.travel_price = 0; // Set to 0 if no builder is selected
              return;
          }

          const selectedBuilder = this.builders.find(builder => builder.id === builderId);
          if (selectedBuilder) {
              this.newContract.travel_price = selectedBuilder.travel_price_amount || 0;
              this.calculateTotal(); // Recalculate total
          }
      },

      // Validate contract details before saving
      validateLot() {
          const idToUpdate = this.$route.params.id;
          return new Promise((resolve, reject) => {
              const { lot, type, job, address } = this.newContract;
              let lotValue = lot ? lot : null; // Convertir a null si está vacío
              let jobValue = String(job).startsWith('S/L') ? null : job;
              if (lotValue !== null && lotValue !== '') {
                  if (!/^[0-9]{1,10}$/.test(String(lotValue))) {
                      reject('Lot must be digits only (up to 10) or empty for Spot Lot.');
                      return;
                  }
              }
              if ((lotValue !== null || address) && type) {
                  axios.get('/api/contract/validate-lot/', {
                      params: {
                          lot: lotValue,
                          type: type,
                          job: jobValue,
                          address: lotValue === null ? address : null
                      }
                  })
                      .then(response => {
                          if (response.data.exists && !idToUpdate) {
                              this.lotValid = false;
                              const message =
                                  response.data.message ||
                                  ('There is already a contract with this lot or address in ' +
                                      this.newContract.type);
                              this.notifyError?.(message);
                              reject(message);
                          } else {
                              this.lotValid = true;
                              resolve();
                          }
                      })
                      .catch(error => {
                          console.error('Error validating lot:', error);
                          this.lotValid = false;
                          reject('Error validating lot.');
                      });
              } else {
                  resolve();
              }
          });
      },

      hasPermission(permission) {
          const userPermissions = JSON.parse(localStorage.getItem('userPermissions'));
          return userPermissions && userPermissions.permissions.includes(permission);
      },

      createOrUpdateContract() {
          const idToUpdate = this.$route.params.id;
          this.loading_text = 'Saving contract';
          this.getAuthenticatedUser().then(user => {
              if (user && !idToUpdate) {
                  this.newContract.created_by = user.id;
              }
          });
          const url = idToUpdate ? `/api/contract/${idToUpdate}/` : '/api/contract/';
          const method = idToUpdate ? 'put' : 'post';

          this.trimContractStrings();
          this.normalizeTravelPrice();

          this.newContract.builder_id = this.newContract.builder;
          this.newContract.house_model_id = this.newContract.house_model;
          this.newContract.job_id = this.newContract.job;
          // Asociaciones nuevas
          if (this.newContract.work_account) {
              this.newContract.work_account_id = this.newContract.work_account
          }
          if (this.$route.query.event_id) {
              this.newContract.schedule_id = parseInt(this.$route.query.event_id)
          }
          // console.log("this.newContract=> ", this.newContract)

          if (!this.validateContractFields()) {
              return;
          }

          if (idToUpdate) {
              // Añadir esta validación antes de enviar los datos
              this.newContract.contract_details = this.newContract.contract_details.map(detail => ({
                  ...detail,
                  cdtrim: detail.cdtrim || "0.00",
                  cdrough: detail.cdrough || "0.00",
                  cdtrim_qty: detail.cdtrim_qty || "0.00",
                  cdrough_qty: detail.cdrough_qty || "0.00"
              }));
          } else {
              const contractDetails = [];
              this.workPrices.forEach((price, index) => {
                  const name = price.name;
                  let trim = price.trim;
                  let rough = price.rough;
                  let trim_qty = price.trim_qty;
                  let rough_qty = price.rough_qty;
                  const unitPrice = price.unit_price;
                  let workPriceId = price.id;

                  trim = parseFloat(trim) || 0;
                  rough = parseFloat(rough) || 0;
                  trim_qty = parseFloat(trim_qty) || 0;
                  rough_qty = parseFloat(rough_qty) || 0;
                  workPriceId = parseFloat(workPriceId);
                  const details = {
                      cdname: name,
                      cdtrim: trim,
                      cdrough: rough,
                      cdunit_price: unitPrice,
                      cdwork_price: workPriceId,
                      cdtrim_qty: trim_qty,
                      cdrough_qty: rough_qty,
                  };
                  contractDetails.push(details);
              });
              this.newContract.contract_details = contractDetails;
          }
          if (this.newContract.contract_details.length === 0) {
              this.notifyError?.("Please enter at least one contract detail.");
              return;
          }
          this.loading = true;
          this.validateLot()
              .then(() => {
                  axios({
                      method: method,
                      url: url,
                      data: this.newContract,
                      headers: {
                          'Content-Type': 'application/json'
                      }
                  })
                      .then(response => {
                          // console.log('Contrato guardado con éxito:', response.data);
                          this.savedContractId = response.data.id;
                          this.savedNeedsReprint = response.data.needs_reprint;
                          this.loading = false; // Desactivar loading
                          
                          if (!idToUpdate) {
                              // No resetear el formulario inmediatamente, solo después de manejar el PDF
                              // this.resetForm();
                          }
                          
                          if (this.savedNeedsReprint === false) {
                              this.downloadContract(this.savedContractId)
                          } else {
                              // Mostrar alerta informativa de que el contrato necesita revisión
                              this.notifyToastSuccess?.(
                                  `Contract ${this.savedContractId} needs review before printing.`
                              );
                              this.$router.push('/contracts');
                          }
                      })
                      .catch(error => {
                          this.error = error;
                          this.loading = false; // Asegurar que el loading se desactive
                          if (error.response) {
                              console.error('Error de servidor:', error.response.data);
                              let errorMessage = 'Error saving contract. ';
                              if (error.response.data) {
                                  if (typeof error.response.data === 'string') {
                                      errorMessage += error.response.data;
                                  } else if (error.response.data.detail) {
                                      errorMessage += error.response.data.detail;
                                  } else if (error.response.data.message) {
                                      errorMessage += error.response.data.message;
                                  } else {
                                      errorMessage += JSON.stringify(error.response.data);
                                  }
                              }
                              this.notifyError?.(errorMessage);
                          } else if (error.request) {
                              console.error('Error de solicitud:', error.request);
                              this.notifyError?.('Could not connect to the server. Please check your connection.');
                          } else {
                              console.error('Error:', error.message);
                              this.notifyError?.(error.message);
                          }
                      });
              })
              .catch(errorMessage => {
                  this.notifyError?.(String(errorMessage));
                  this.loading = false;
              });

      },

      resetForm() {
          // Preservar work_account y schedule_id si vienen de un evento
          const preserveWorkAccount = this.$route.query.event_id && this.newContract.work_account;
          const preserveScheduleId = this.newContract.schedule_id;
          
          this.newContract = {
              house_model: '',
              builder: '',
              job: '',
              type: 'Rough',
              lot: null,
              sqft: null,
              address: '',
              job_price: null,
              travel_price: null,
              total_options: null,
              total: null,
              comment: 'Required to finish at 100%',
              created_by: null,
              work_account: preserveWorkAccount ? this.newContract.work_account : null,
              schedule_id: preserveScheduleId || null,
          };
          
          // Si hay un evento, recargar los datos
          if (preserveWorkAccount && this.$route.query.event_id) {
              this.prefillFromEvent();
          }
      },

      onFileChange(event) {
          this.newContract.file = event.target.files[0];
      },

      validateContractFields() {
          this.validationErrors = {};
          this.trimContractStrings();
          this.normalizeTravelPrice();

          const requiredFields = {
              type: "Job Type is required",
              builder: "Builder is required",
              job: "Community (Job) is required",
              house_model: "House Model is required",
              address: "Address is required",
              sqft: "SqFt is required and must be greater than 0",
              job_price: "Job Price is required",
              travel_price: "Travel Price is required",
              total_options: "Total Options is required",
              total: "Total is required and must be greater than 1",
          };

          // Spot Lot: lot may be empty when address is present (backend lot null=True; validate-lot uses address).
          // Require at least address; do not block solely for empty lot.

          let isValid = true;

          // Form identity is Work Account–first; Builder/Job are derived and not shown as separate fields.
          const hasWorkAccount = Boolean(this.newContract.work_account);
          if (!hasWorkAccount) {
              this.validationErrors.work_account = "Work Account is required";
              isValid = false;
          }

          // Skip Builder/Job messages when WA is missing (covered above) or present (derived from WA).
          const skipBuilderJob = new Set(['builder', 'job']);

          Object.keys(requiredFields).forEach(field => {
              if (skipBuilderJob.has(field)) {
                  return;
              }
              let value = this.newContract[field];

              if (value === null || value === undefined || value === "") {
                  this.validationErrors[field] = requiredFields[field];
                  isValid = false;
                  return;
              }

              if (field === "total" && parseFloat(value) <= 1) {
                  this.validationErrors[field] = requiredFields[field];
                  isValid = false;
              }
          });

          // SqFt must be a sensible number > 0
          const sqftNum = parseFloat(this.newContract.sqft);
          if (!Number.isFinite(sqftNum) || sqftNum <= 0) {
              this.validationErrors.sqft = "SqFt is required and must be greater than 0";
              isValid = false;
          }

          // Travel Price: allow 0; reject negative / non-numeric
          const travelNum = Number(this.newContract.travel_price);
          if (!Number.isFinite(travelNum)) {
              this.validationErrors.travel_price = "Travel Price must be a valid amount (use 0.00 if none)";
              isValid = false;
          } else if (travelNum < 0) {
              this.validationErrors.travel_price = "Travel Price cannot be negative";
              isValid = false;
          }

          // Lot: whole numbers (digits) only when provided
          const lot = this.newContract.lot;
          if (lot !== null && lot !== undefined && String(lot).trim() !== "") {
              if (!/^[0-9]{1,10}$/.test(String(lot).trim())) {
                  this.validationErrors.lot = "Lot must be a whole number (digits only, max 10)";
                  isValid = false;
              }
          } else if (!this.newContract.address || String(this.newContract.address).trim() === "") {
              // Spot Lot / standard: address is required when lot is empty
              this.validationErrors.address = "Address is required when Lot is empty (Spot Lot)";
              isValid = false;
          }

          if (!isValid) {
              this.notifyValidationErrors(this.validationErrors);
              this.focusFirstInvalidField();
          }

          return isValid;
      },

      notifyValidationErrors(errors = {}) {
          const messages = Object.values(errors).filter(Boolean);
          if (!messages.length) {
              this.notifyError?.("Please fix the highlighted fields before saving.");
              return;
          }
          if (messages.length === 1) {
              this.notifyError?.(messages[0]);
              return;
          }
          const html =
              '<p style="margin:0 0 0.5rem;text-align:left">Please fix the following:</p>' +
              '<ul style="text-align:left;margin:0;padding-left:1.25rem;line-height:1.45">' +
              messages.map((m) => `<li>${this.escapeHtml(m)}</li>`).join('') +
              '</ul>';
          import('sweetalert2').then((Swal) => {
              Swal.default.fire({
                  icon: 'error',
                  title: 'Validation Error',
                  html,
                  confirmButtonText: 'OK',
              });
          }).catch(() => {
              this.notifyError?.(messages.join('\n'));
          });
      },

      escapeHtml(text) {
          return String(text)
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;');
      },

      downloadContract(id) {
          this.loading = true; // Activa el spinner
          this.loading_text = `Downloading contract ${id} as PDF`;
          axios.get(`/api/contract-pdf/${id}/`)
              .then((response) => {
                  openPdf(response.data);
                  this.loading = false;
                  // Resetear formulario solo después de que el PDF se abra correctamente
                  const idToUpdate = this.$route.params.id;
                  if (!idToUpdate) {
                      this.resetForm();
                  }
                  setTimeout(() => {
                      this.$router.push('/contracts');
                  }, 210); // Asegúrate de que el PDF se abra antes de redirigir
              })
              .catch(error => {
                  console.error('Error fetching contract PDF:', error);
                  this.loading = false; // Asegúrate de que el spinner se desactive si hay un error
                  
                  // Mostrar mensaje al usuario pero no bloquear - el contrato ya se guardó
                  this.notifyError?.(
                      `Contract ${id} was saved, but the PDF could not be generated. Open it from the contracts list.`
                  );
                  const idToUpdate = this.$route.params.id;
                  if (!idToUpdate) {
                      this.resetForm();
                  }
                  this.$router.push('/contracts');
              });
      }
  }
};
</script>

<style scoped>
.jr-contract-form__loading {
  margin: 0.5rem 0;
  color: var(--color-jr-muted);
  font-size: 0.8125rem;
}

.jr-contract-form__event {
  margin: 0 0 0.5rem;
  padding: 0.4rem 0.65rem;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface-muted);
  font-size: 0.75rem;
  color: var(--color-jr-text);
}

.jr-form-banner {
  margin: 0 0 0.5rem;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-danger-subtle);
  color: var(--color-jr-danger-text);
  font-size: 0.8125rem;
}

.jr-contract-form__split {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (min-width: 1024px) {
  .jr-contract-form__split {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 0.65rem 1rem;
    align-items: start;
  }
}

.jr-form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.5rem 0.75rem;
}

.jr-contract-form__identity {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  min-width: 0;
}

/* Fill path: Job Type → Work Account → House Model → Address|Lot */
.jr-contract-form__grid--identity {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.45rem 0.75rem;
}

.jr-contract-form__grid--pricing {
  gap: 0.45rem 0.75rem;
}

@media (min-width: 640px) {
  .jr-contract-form__grid--identity {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jr-contract-form__field--type {
    grid-column: 1 / 2;
    max-width: 100%;
  }

  .jr-contract-form__field--wa,
  .jr-contract-form__field--hm {
    grid-column: 1 / -1;
  }

  .jr-contract-form__grid--pricing {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.jr-contract-form__location {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.45rem 0.75rem;
  min-width: 0;
}

@media (min-width: 640px) {
  .jr-contract-form__location {
    grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr);
    align-items: start;
  }
}

.jr-contract-form__comment-field {
  grid-column: 1 / -1;
}

/* Override global `.jr-pilot textarea.jr-control { min-height: 5.5rem }` for this Comment only */
.jr-contract-form__comment-field :deep(textarea.jr-control) {
  min-height: 2.75rem;
}

.jr-contract-form__wa {
  min-width: 0;
}

/* Informational metric — not part of the Enter fill chain */
.jr-contract-form__lighting {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0;
  padding: 0.4rem 0.65rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-surface-muted);
}

.jr-contract-form__lighting-label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

.jr-contract-form__lighting-value {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--color-jr-text);
}

.jr-contract-form__readout {
  margin: 0;
  min-height: 2rem;
  display: flex;
  align-items: center;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-contract-form__options-split {
  display: flex;
  flex-direction: column;
  gap: 0.75rem 1.25rem;
  margin-top: 0.15rem;
}

@media (min-width: 900px) {
  .jr-contract-form__options-split {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    align-items: start;
  }
}

.jr-contract-form__options {
  margin-top: 0;
  max-width: none;
  min-width: 0;
}

.jr-contract-form__options-head,
.jr-contract-form__options-row {
  display: grid;
  grid-template-columns: 3.75rem minmax(0, 1fr) 5.5rem;
  gap: 0.35rem;
  align-items: center;
  margin-bottom: 0.2rem;
}

.jr-contract-form__options-head {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
  margin-bottom: 0.3rem;
}

.jr-contract-form__options-title {
  font-size: 0.75rem;
  text-transform: none;
  letter-spacing: 0;
  font-weight: 600;
}

.jr-contract-form__opt-input {
  width: 100%;
  min-height: 1.85rem;
  padding: 0.2rem 0.4rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-surface);
  color: var(--color-jr-text);
  font-size: 0.8125rem;
}

.jr-contract-form__opt-name {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
  background: var(--color-jr-surface-muted, var(--color-jr-surface));
  border-color: transparent;
  min-height: 1.7rem;
  padding: 0.15rem 0.35rem;
}

.jr-contract-form__opt-qty,
.jr-contract-form__opt-amount {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-jr-text);
}

/* Match JR form focus contract: primary border only (no ring) */
.jr-contract-form__opt-qty:focus,
.jr-contract-form__opt-qty:focus-visible,
.jr-contract-form__opt-amount:focus,
.jr-contract-form__opt-amount:focus-visible {
  border-color: var(--color-jr-primary);
  outline: none;
  box-shadow: none;
}

.jr-contract-form__opt-input:disabled {
  opacity: 0.55;
}

@media (max-width: 390px) {
  .jr-contract-form__options-head,
  .jr-contract-form__options-row {
    grid-template-columns: 3.5rem minmax(0, 1fr) 5rem;
    gap: 0.25rem;
  }

  .jr-contract-form__opt-qty,
  .jr-contract-form__opt-amount {
    min-height: 2rem;
  }
}

.jr-contract-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.55rem 0 0.2rem;
  margin-top: 0.55rem;
  background: var(--color-jr-page);
  border-top: 1px solid var(--color-jr-border);
}

.jr-contract-form__bid {
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0;
  border: none;
  background: transparent;
}

.jr-contract-form__bid-label {
  margin: 0;
  line-height: 1.2;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text);
  cursor: pointer;
  user-select: none;
}

/* Keep Bid checkbox + label optically centered in the header actions */
.jr-contract-form__bid :deep(.p-checkbox),
.jr-contract-form__bid :deep(.jr-checkbox) {
  display: inline-flex;
  align-items: center;
}

.jr-contract-form :deep(.jr-section) {
  margin-bottom: 0.35rem;
}

.jr-contract-form :deep(.jr-field) {
  margin-bottom: 0;
}

.jr-contract-form :deep(.jr-field__hint) {
  font-size: 0.75rem;
  margin-top: 0.15rem;
}
</style>
