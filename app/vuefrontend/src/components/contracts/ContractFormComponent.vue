<template>
  <div class="container position-relative">

      <p v-if="errorMessage" class="alert alert-danger py-3">
          {{ errorMessage }}
      </p>
      <h3 v-show="!loading && !errorMessage" class="pt-2">
          <p>{{ newContract.doc_type }}</p>
      </h3>
      <div class="card shadow mb-4">
          <!-- Checkbox para Doc Type en la esquina superior derecha -->
          <div v-if="this.hasPermission('ctrctsapp.add_contract')" v-show="!loading && !errorMessage"
              class="position-absolute" style="top: 10px; right: 10px;">
              <div class="form-check">
                  <!-- El checkbox se vincula con la propiedad isBid -->
                  <input type="checkbox" class="form-check-input" id="docTypeCheckbox" v-model="isBid"
                      @change="toggleDocType" :disabled="isReadOnly">
                  <label class="form-check-label" for="docTypeCheckbox">
                      Bid
                  </label>
              </div>
          </div>
          <div v-show="!loading && !errorMessage" class="card-header">
              <div v-if="$route.path === '/contract-form'">
                  <h6 class="m-0 font-weight-bold text-primary">Create {{ newContract.doc_type }}</h6>
              </div>
              <div v-else>
                  <h6 class="m-0 font-weight-bold text-primary">Edit {{ newContract.doc_type }}</h6>
                  <p class="text-center">
                      Created: {{ formatDate(newContract.date_created) }}
                      <strong class="d-block d-md-inline">Updated: {{ formatDate(newContract.last_updated) }}</strong>
                  </p>
              </div>
              <div class="mt-3 text-primary-emphasis small" v-if="event">
                <strong>Event:</strong> {{ event.title }}
                <span class="mx-2">|</span>
                <strong>Crew:</strong> {{ event.crew_title }}
              </div>
          </div>
          <div class="card-body">
              <div v-if="loading" class="spinner-container my-5">
                  {{ loading_text }} ...&nbsp;
                  <div class="spinner-border" style="width: 4rem; height: 4rem;" role="status"></div>
                  <div class="spinner-grow" style="width: 3rem; height: 3rem;" role="status"></div>
                  <div class="spinner-grow" style="width: 2rem; height: 2rem;" role="status"></div>
                  <div class="spinner-grow" style="width: 1rem; height: 1rem;" role="status"></div>
              </div>

              <form v-show="!loading && !errorMessage">
                  <div class="row">
                      <div class="col-md-6">
                          <div class="form-group row align-items-center mb-3">
                              <label for="type" class="col-12 col-sm-4 col-form-label text-start text-sm-end">Job
                                  Type</label>
                              <div class="col-sm-8">
                                  <select class="form-select column-input" id="type" v-model="newContract.type"
                                      :disabled="isReadOnly" @change="calculatePrice" ref="type"
                                      @keydown.enter="focusNext($event, 'builder')" required>
                                      <option value="">Select type</option>
                                      <option value="Rough">Rough</option>
                                      <option value="Trim">Trim</option>
                                  </select>
                              </div>
                          </div>

                          <!-- Selector para Builder -->
                          <!-- Work Account selector -->
                          <div class="form-group row align-items-center mb-3">
                              <label class="col-12 col-sm-4 col-form-label text-start text-sm-end">Work Account</label>
                              <div class="col-sm-8">
                                  <WorkAccountSelector
                                      v-model="newContract.work_account"
                                      @change="onWorkAccountChanged"
                                      :show-label="false"
                                  />
                              </div>
                          </div>

                          <!-- Selector para Builder (hidden - replaced by WorkAccountSelector) -->
                          <div class="form-group row align-items-center mb-3" v-if="false">
                              <label for="builder-select"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">Builder</label>
                              <!-- If user has permission to add or edit builder -->
                              <div v-if="this.hasPermission('ctrctsapp.add_builder') || this.hasPermission('ctrctsapp.change_builder')"
                                  class="col-sm-8 d-flex align-items-center">
                                  <!-- Vue-select component -->
                                  <v-select id="builder-select" :options="builders" v-model="newContract.builder"
                                      :reduce="builder => builder.id" label="name" placeholder="Select Builder"
                                      ref="builder" class="flex-grow-1" @input="fetchHouseModels"
                                      @keydown.enter="focusNext($event, 'job')" @focus="selectText"
                                      :disabled="isReadOnly">
                                  </v-select>
                                  <!-- Add button with permission check -->
                                  <button class="btn btn-outline-secondary btn-sm ms-1" type="button"
                                      @click="openBuilderModal('add')" :disabled="isReadOnly">
                                      <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15">
                                  </button>
                                  <!-- Edit button with permission check -->
                                  <button v-if="newContract.builder" class="btn btn-outline-secondary btn-sm ms-1"
                                      type="button" @click="editBuilderModal('edit', newContract.builder)"
                                      :disabled="isReadOnly">
                                      <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15">
                                  </button>
                              </div>
                              <!-- If user doesn't have permission, show this simpler layout -->
                              <div v-else class="col-sm-8">
                                  <!-- Vue-select component without buttons -->
                                  <v-select :options="builders" v-model="newContract.builder"
                                      :reduce="builder => builder.id" label="name" placeholder="Select Builder"
                                      ref="builder" @input="fetchHouseModels"
                                      @keydown.enter="focusNext($event, 'job')" @focus="selectText"
                                      :disabled="isReadOnly">
                                  </v-select>
                              </div>
                          </div>

                          <!-- Selector for Job (hidden - replaced by WorkAccountSelector) -->
                          <div class="form-group row align-items-center mb-3" v-if="false">
                              <label for="job-select"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">Job</label>
                              <!-- If user has permission to add or edit Job -->
                              <div v-if="this.hasPermission('ctrctsapp.add_job') || this.hasPermission('ctrctsapp.change_job')"
                                  class="col-sm-8 d-flex align-items-center">
                                  <!-- Job selection using vue-select -->
                                  <v-select id="job-select" :options="jobs" v-model="newContract.job"
                                      :reduce="job => job.id" label="name" class="flex-grow-1"
                                      placeholder="Select Job" @input="fetchHouseModels" ref="job"
                                      @keydown.enter="focusNext($event, 'houseModel')" @focus="selectText"
                                      :disabled="isReadOnly">
                                  </v-select>
                                  <!-- Add button for opening the job modal in add mode -->
                                  <button type="button" class="btn btn-outline-secondary btn-sm ms-1"
                                      @click="openJobModal('add')" :disabled="isReadOnly">
                                      <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15">
                                  </button>
                                  <!-- Edit button for opening the job modal in edit mode -->
                                  <button v-if="newContract.job" type="button"
                                      class="btn btn-outline-secondary btn-sm ms-1"
                                      @click="editJobModal('edit', newContract.job)" :disabled="isReadOnly">
                                      <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15">
                                  </button>
                              </div>
                              <div v-else class="col-sm-8">
                                  <!-- Vue-select component without buttons -->
                                  <v-select :options="jobs" v-model="newContract.job" :reduce="job => job.id"
                                      label="name" placeholder="Select Job" @input="fetchHouseModels" ref="job"
                                      @keydown.enter="focusNext($event, 'houseModel')" @focus="selectText"
                                      :disabled="isReadOnly">
                                  </v-select>
                              </div>
                          </div>

                          <!-- Selector for House Model (hidden - replaced by WorkAccountSelector) -->
                          <div class="form-group row align-items-center mb-3" v-if="true">
                              <label for="houseModel"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">House Model</label>
                              <!-- If user has permission to add or edit Job -->
                              <div v-if="this.hasPermission('ctrctsapp.add_housemodel') || this.hasPermission('ctrctsapp.change_housemodel')"
                                  class="col-sm-8 d-flex align-items-center">
                                  <v-select :options="houseModels" v-model="newContract.house_model"
                                      :reduce="houseModel => houseModel.id" label="name"
                                      placeholder="Select House Model" ref="houseModel" class="flex-grow-1"
                                      @keydown.enter="focusNext($event, 'address')" @focus="selectText"
                                      :disabled="isReadOnly">
                                  </v-select>
                                  <button type="button" class="btn btn-outline-secondary btn-sm ms-1"
                                      @click="openModal('add')" :disabled="isReadOnly">
                                      <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15">
                                  </button>
                                  <button v-if="newContract.house_model" type="button"
                                      class="btn btn-outline-secondary btn-sm ms-1"
                                      @click="openModal('edit', newContract.house_model)" :disabled="isReadOnly">
                                      <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15">
                                  </button>
                              </div>
                              <div v-else class="col-sm-8">
                                  <v-select :options="houseModels" v-model="newContract.house_model"
                                      :reduce="houseModel => houseModel.id" label="name"
                                      placeholder="Select House Model" ref="houseModel"
                                      @keydown.enter="focusNext($event, 'address')" @focus="selectText"
                                      :disabled="isReadOnly">
                                  </v-select>
                              </div>
                          </div>

                          <div class="form-group row align-items-center mb-3">
                              <label for="address"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">Address</label>
                              <div class="col-sm-8">
                                  <input type="text" class="form-control column-input" id="address" ref="address"
                                      v-model="newContract.address" @keydown.enter="focusNext($event, 'lot')"
                                      @focus="selectText" :disabled="isReadOnly">
                              </div>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <label for="lot"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">Lot</label>
                              <div class="col-sm-8">
                                  <input type="text" class="form-control column-input" id="lot"
                                      v-model="newContract.lot" ref="lot" @keydown.enter="focusNext($event, 'sqft')"
                                      @focus="selectText" :disabled="isReadOnly">
                              </div>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <label for="lot" class="col-12 col-sm-4 col-form-label text-start text-sm-end">Lighting
                                  Circuits:</label>
                              <h5 class="col-sm-4 col-form-label text-start"><strong>{{ lightingCircuits() }}
                                  </strong></h5>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <div class="col-sm-4"></div>
                              <div class="col-sm-8">
                                  <input class="form-control" hidden type="file" id="file" @change="onFileChange"
                                      @focus="selectText">
                              </div>
                          </div>
                      </div>
                      <div class="col-md-6">
                          <div class="form-group row align-items-center mb-3">
                              <label for="sqft"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">SqFt</label>
                              <div class="col-sm-8">
                                  <input type="number" class="form-control column-input" id="sqft" ref="sqft"
                                      v-model="newContract.sqft" @input="calculatePrice"
                                      @keydown.enter="focusNext($event, 'travelPrice')" @focus="selectText"
                                      :disabled="isReadOnly">
                              </div>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <label for="jobPrice" class="col-12 col-sm-4 col-form-label text-start text-sm-end">Job
                                  Price</label>
                              <div class="col-sm-8">
                                  <input type="number" step="0.01" class="form-control column-input" id="jobPrice"
                                      ref="jobPrice" v-model.number="newContract.job_price" @input="calculateTotal"
                                      @blur.enter="focusNext($event, 'travelPrice')" @focus="selectText"
                                      :disabled="isReadOnly">
                              </div>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <label for="travelPrice"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">Travel Price</label>
                              <div class="col-sm-8">
                                  <input type="number" step="0.01" class="form-control column-input" id="travelPrice"
                                      ref="travelPrice" v-model.number="newContract.travel_price"
                                      @input="calculateTotal" @keydown.enter="focusNext($event, 'comment')"
                                      @focus="selectText" :disabled="isReadOnly">
                              </div>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <label for="totalOptions"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">Total Options</label>
                              <div class="col-sm-8">
                                  <input type="number" step="0.01" class="form-control column-input" id="totalOptions"
                                      ref="totalOptions" v-model.number="newContract.total_options"
                                      @input="calculateTotal" @keydown.enter="focusNext($event, 'comment')"
                                      @focus="selectText" :disabled="isReadOnly">
                              </div>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <label for="total"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end">Total</label>
                              <div class="col-sm-8">
                                  <input type="number" step="0.01" class="form-control column-input" id="total"
                                      ref="total" v-model.number="newContract.total"
                                      @keydown.enter="focusNext($event, 'comment')" @focus="selectText"
                                      :disabled="isReadOnly">
                              </div>
                          </div>
                          <div class="form-group row align-items-center mb-3">
                              <label for="comment"
                                  class="col-12 col-sm-4 col-form-label text-start text-sm-end column-input"
                                  @keydown.enter="focusNext($event)">Comment</label>
                              <div class="col-sm-8">
                                  <textarea class="form-control" id="comment" ref="comment" rows="3"
                                      v-model="newContract.comment" @keydown.enter="focusNextDetail($event)"
                                      @focus="selectText" :disabled="isReadOnly"></textarea>
                              </div>
                          </div>
                      </div>
                  </div>
                  <div class="row justify-content-center align-items-center">
                      <div class="col-12 col-sm-auto">
                          <div class="mb-6" v-if="$route.path == '/contract-form'">
                              <div class="form-group row align-items-center" v-if="newContract.work_account || newContract.builder">
                                  <div class="col col-sm-2">
                                      <label>Qty</label>
                                  </div>
                                  <div class="col-6 col-sm-6">
                                      <label>Options: {{ newContract.type }}</label>
                                  </div>
                                  <div class="col col-sm-4">
                                      <label>Amount</label>
                                  </div>
                              </div>
                              <div v-if="newContract.work_account || newContract.builder">
                                  <div v-for="(price, index) in workPrices" :key="index">
                                      <div class="form-group row align-items-center">
                                          <div class="col col-sm-2"
                                              v-if="newContract.type === 'Trim' && ((price.trim > 0 && price.isEditedTrim) || price.trim_qty >= 0)">
                                              <input type="number" min="0" :id="'trim_qty' + index"
                                                  class="form-control form-control-sm column-input"
                                                  v-model.number="price.trim_qty" @keydown.enter="focusNextDetail($event)"
                                                  @focus="selectText" @input="updateAmount(index)">
                                          </div>
                                          <div class="col col-sm-2"
                                              v-if="newContract.type === 'Rough' && ((price.rough > 0 && price.isEditedRough) || price.rough_qty >= 0)">
                                              <input type="number" min="0" :id="'rough_qty' + index"
                                                  class="form-control form-control-sm column-input"
                                                  v-model.number="price.rough_qty"
                                                  @keydown.enter="focusNextDetail($event)" @focus="selectText"
                                                  @input="updateAmount(index)">
                                          </div>
                                          <div class="col-6 col-sm-6">
                                              <input type="text" class="form-control form-control-sm"
                                                  v-if="(newContract.type === 'Trim' && ((price.trim > 0 && price.isEditedTrim) || price.trim_qty >= 0)) ||
                                                      (newContract.type === 'Rough' && ((price.rough > 0 && price.isEditedRough) || price.rough_qty >= 0))"
                                                  v-model="price.name" v-bind:placeholder="price.name">
                                          </div>
                                          <input type="hidden" class="form-control" v-model="price.id">
                                          <div class="col col-sm-4"
                                              v-if="newContract.type === 'Trim' && ((price.trim > 0 && price.isEditedTrim) || price.trim_qty >= 0)">
                                              <label hidden class="form-label">Trim {{ index }}</label>
                                              <input type="number" class="form-control form-control-sm"
                                                  v-model.number="price.trim" @input="updateTotalOptions"
                                                  @focus="selectText" :disabled="!price.trim_qty">
                                          </div>
                                          <div class="col col-sm-4"
                                              v-if="newContract.type === 'Rough' && ((price.rough > 0 && price.isEditedRough) || price.rough_qty >= 0)">
                                              <label hidden class="form-label">Rough {{ index }}</label>
                                              <input type="number" class="form-control form-control-sm"
                                                  v-model.number="price.rough" @input="updateTotalOptions"
                                                  @focus="selectText" :disabled="!price.rough_qty">
                                          </div>
                                      </div>
                                  </div>
                              </div>
                          </div>

                          <div class="mb-6" v-if="$route.path !== '/contract-form'">
                              <div class="form-group row align-items-center">
                                  <div class="col col-sm-2">
                                      <label>Qty</label>
                                  </div>
                                  <div class="col-6 col-sm-6">
                                      <label>Opciones: {{ newContract.type }}</label>
                                  </div>
                                  <div class="col col-sm-4">
                                      <label>Amount</label>
                                  </div>
                              </div>
                              <div v-for="(detail, index) in newContract.contract_details" :key="index">
                                  <div class="form-group row align-items-center">
                                      <div class="col col-sm-2"
                                          v-if="newContract.type === 'Trim' && detail.isEditedTrim && !detail.isEditedRough">
                                          <input type="number" min="0" :id="'detail_qty' + index"
                                              ref="'detail_qty' + index"
                                              class="form-control form-control-sm column-input"
                                              v-model="detail.cdtrim_qty" @keydown.enter="focusNextDetail($event)"
                                              @focus="selectText" @input="updateDetailAmount(index)"
                                              :disabled="isReadOnly">
                                      </div>
                                      <div class="col col-sm-2"
                                          v-if="newContract.type === 'Rough' && detail.isEditedRough && !detail.isEditedTrim">
                                          <input type="number" min="0" :id="'detail_qty' + index"
                                              class="form-control form-control-sm column-input"
                                              v-model="detail.cdrough_qty" @keydown.enter="focusNextDetail($event)"
                                              @focus="selectText" @input="updateDetailAmount(index)"
                                              :disabled="isReadOnly">
                                      </div>
                                      <div class="col-6 col-sm-6">
                                          <input type="text" class="form-control form-control-sm"
                                              v-if="(newContract.type === 'Trim' && detail.isEditedTrim && !detail.isEditedRough) ||
                                                  (newContract.type === 'Rough' && detail.isEditedRough && !detail.isEditedTrim)" v-model="detail.cdname"
                                              v-bind:placeholder="detail.cdname" :disabled="isReadOnly">
                                      </div>
                                      <div class="col col-sm-4"
                                          v-if="newContract.type === 'Trim' && detail.isEditedTrim && !detail.isEditedRough">
                                          <label hidden class="form-label">Trim {{ index }}</label>
                                          <input type="number" class="form-control form-control-sm"
                                              v-model.number="detail.cdtrim" @input="updateTotalOptions"
                                              @focus="selectText" :disabled="detail.cdtrim_qty <= 0.00 || isReadOnly">
                                      </div>
                                      <div class="col col-sm-4"
                                          v-if="newContract.type === 'Rough' && detail.isEditedRough && !detail.isEditedTrim">
                                          <label hidden class="form-label">Rough {{ index }}</label>
                                          <input type="number" class="form-control form-control-sm"
                                              v-model.number="detail.cdrough" @input="updateTotalOptions"
                                              @focus="selectText"
                                              :disabled="detail.cdrough_qty <= 0.00 || isReadOnly">
                                      </div>
                                  </div>
                              </div>
                          </div>
                      </div>
                  </div>
                  <div class="container p-2" v-if="!isReadOnly">
                      <button class="btn btn-primary column-input" @click.prevent="createOrUpdateContract">Save
                          Contract</button>
                  </div>
              </form>
          </div>
      </div>
      <!-- Modals for CRUD (Builder, Job, and HouseModel) -->
      <BuilderModal ref="builderModal" :action="action" :builder="selectedBuilders" @saved="fetchBuilders"
          @close="closeModal" @clearBuilderSelect="clearBuilderSelection" />
      <JobModal ref="jobModal" :action="action" :job="selectedJob" :builders="builders" @refresh="fetchJobs"
          @close="closeModal" @clearJobSelect="clearJobSelection" />
      <HouseModelModal ref="houseModelModal" :action="action" :houseModelId="houseModelId" :jobs="jobs"
          @refresh="fetchHouseModels" @close="closeModal" />
  </div>
</template>

<script>
import axios from 'axios';
import VSelect from 'vue-select';
import Swal from 'sweetalert2'
import { Modal } from 'bootstrap';
import '@assets/css/base.css';
import BuilderModal from './BuilderModalComponent.vue';
import JobModal from './JobModalComponent.vue';
import HouseModelModal from './HouseModelModalComponent.vue';
import { openPdf } from "@helpers";
import WorkAccountSelector from '@/components/transactions/WorkAccountSelector.vue'


export default {
  name: 'ContractFormComponent',
  components: {
      BuilderModal,
      JobModal,
      HouseModelModal,
      VSelect,
      WorkAccountSelector

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
          selectedBuilders: {},
          selectedJob: {},
          houseModelId: null,
          action: 'add',
          isBid: false, // Por defecto, el checkbox no está marcado, lo que significa "Contract"
          event: null,
      };
  },

  computed: {
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
      isReadOnly() {
          return this.$route.name === 'contract-view';
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
          if (newVal !== oldVal) {
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
      ]).then(() => {
          this.loading = false; // Solo si todo carga bien, mostramos el formulario
      }).catch(error => {
          console.error("Error loading data:", error);
          this.errorMessage = "There was a problem loading the data. Please check your internet connection and try again.";
          this.loading = false; // No se mostrará el formulario si `errorMessage` tiene valor
      });
  },

  methods: {
      toggleDocType() {
          // Si el checkbox está marcado, se asigna "Bid", de lo contrario "Contract"
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

      // Select all text in the input field
      // Seleccionar todo el texto en el campo de entrada
      selectText(event) {
          const input = event.target;
          input.select();
      },

      async onWorkAccountChanged(workAccountId) {
          try {
              if (!workAccountId) return
              const { data } = await axios.get(`/api/work-accounts/${workAccountId}/`)

              // 1) Builder primero (limpia dependencias por watchers)
              this.newContract.builder = data.builder || null

              // 2) Cargar jobs y setear job
              await this.fetchJobs(() => {
                  this.newContract.job = data.job || null
              })

              // 3) Cargar house models y setear house_model
              await this.fetchHouseModels(async () => {
                  // Si el house_model viene en el WA, asegúralo en opciones
                  if (data.house_model) {
                      // Confirmar que el house_model pertenece al job actual
                      const hmId = data.house_model
                      const exists = this.houseModels.some(h => h.id === hmId)
                      if (!exists) {
                          // fallback: recargar por si no estaba la relación aún en memoria
                          await this.fetchHouseModels()
                      }
                      this.newContract.house_model = hmId
                  } else {
                      this.newContract.house_model = null
                  }
              })

              // 4) Lote y Dirección
              this.newContract.lot = data.lot || ''
              this.newContract.address = data.address || ''

              // 5) Recalcular precios (travel desde builder)
              this.updateTravelPrice()
              this.calculatePrice()

              // 6) Cargar precios de opciones según builder
              if (data.builder) {
                  await this.fetchWorkPrices(data.builder)
              }
              return data
          } catch (e) {
              console.error('Error syncing WorkAccount into contract:', e)
          }
      },

      // Move to the next input field when Enter is pressed
      // Moverse al siguiente campo de entrada cuando se presiona Enter
      focusNext(event, nextField) {
          event.preventDefault();
          if (this.$refs[nextField]) {
              if (this.$refs[nextField].$el) {
                  this.$refs[nextField].$el.querySelector('input, select').focus();
              } else {
                  this.$refs[nextField].focus();
              }
          }
      },
      // Move to the next input Detail field when Enter is pressed
      // Moverse al siguiente campo de Detail de entrada cuando se presiona Enter
      focusNextDetail(event) {
          if (event.key === 'Enter') {
              event.preventDefault();
              const inputs = Array.from(document.querySelectorAll('.column-input'));
              const index = inputs.indexOf(event.target);
              if (index > -1 && index < inputs.length - 1) {
                  inputs[index + 1].focus();
              }
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
              const confirmContinue = Swal.fire({
                  title: 'Confirm?',
                  text: 'Do you want to continue with a SqFt of ' + sqft + '? The value is greater than or equal to 3000.',
                  icon: 'warning',
                  showCancelButton: true,
                  confirmButtonText: 'Yes',
                  cancelButtonText: 'No'
              });
              confirmContinue.then(result => {
                  if (!result.isConfirmed) {
                      // Si el usuario cancela, restablecer el valor a 0
                      this.newContract.sqft = 0;
                  } else {
                      this.newContract.sqft = sqft;
                  }
              });
              return;
          }
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
          if (!idToUpdate) {
              axios.get(`/api/workprice/?builder=${builderId}`)
                  .then(response => {
                      this.workPrices = response.data.map(price => ({
                          ...price,
                          isEditedTrim: false,  // Properly initializing flags for each price
                          isEditedRough: false
                      }));
                      this.initializePrices();  // Call after setting initial values
                      // console.log('fetchWorkPrices: ', JSON.stringify(this.workPrices, null, 2));
                  })
                  .catch(error => {
                      console.error('Error fetching work prices:', error);
                  });
          }
      },

      // Method to open the builder modal in edit mode with selected builder data
      editBuilderModal(action, builderId) {
          this.action = action;
          // Find the builder by its ID in the builders array
          const builderToEdit = this.builders.find((builder) => builder.id === builderId);

          if (builderToEdit) {
              this.selectedBuilders = { ...builderToEdit };
              this.$refs.builderModal?.showModal();
          } else {
              console.error(`Builder with ID ${builderId} not found.`);
          }
      },

      openBuilderModal(action) {
          this.action = action;
          this.selectedBuilders = action === 'edit' ? this.getSelectedBuilder() : {
              name: '',
              trim_amount: 0,
              rough_amount: 0,
              travel_price_amount: 0,
          };

          // Show the modal using JavaScript
          this.$refs.builderModal?.showModal();
      },

      clearBuilderSelection() {
          this.newContract.builder = null; // Clear the selected job in v-select
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

      // Open the modal to add a new job
      // Open the modal to add a new job or edit an existing one
      openJobModal(action, job = null) {
          this.action = action;
          // Reset for adding a new job
          this.selectedJob = {
              name: '',
              builder: this.newContract.builder || null, // Use the current builder from newContract if available
          };
          // show the modal
          this.$refs.jobModal?.showModal();
      },

      clearJobSelection() {
          this.selectedJob = {}; // Reset job selection
      },

      // Open the modal to edit an existing job
      editJobModal(action, jobId) {
          this.action = action;
          const jobToEdit = this.jobs.find((job) => job.id === jobId);
          if (jobToEdit) {
              // Make sure builder information is included in the selectedJob
              this.selectedJob = { ...jobToEdit };
              //this.newContract.builder = jobToEdit.builder; // Set the builder for modalJob (if necessary)
              this.fetchJobs();
              this.$refs.jobModal?.showModal();
          } else {
              console.error(`Job with ID ${jobId} not found.`);
          }
      },

      // Fetch available Jod from the server
      // Obtener Job de casas disponibles del servidor
      fetchJobs(callback = null) {
          const builderId = this.newContract.builder;
          if (!builderId) return; // Exit if no builder is selected

          axios.get(`/api/job/jobs_by_builder/`, { params: { builder_id: builderId } })
              .then(response => {
                  this.jobs = response.data.map(job => ({
                      id: job.id,
                      name: job.name,
                      builder: job.builder // Ensure the builder property is included
                  }));
                  // console.log("Jobs fetched and updated:", this.jobs);

                  // Execute callback if provided
                  if (callback) callback();
              })
              .catch(error => {
                  console.error("Error fetching jobs:", error);
              });
      },

      openModal(action, houseIdModel) {
          this.action = action;
          if (action === 'edit' && houseIdModel) {
              // Pasar el ID y los datos del modelo de casa seleccionado
              this.houseModelId = houseIdModel;
          } else {
              // Para agregar un nuevo modelo de casa
              this.houseModelId = null;
              if (this.newContract.job) {
                  this.houseModelId = [this.newContract.job]; // Asegura que sea un array
              }
          }
          // Open the modal
          const modalInstance = Modal.getOrCreateInstance(this.$refs.houseModelModal.$el);
          modalInstance.show();
      },

      // Fetch available house models from the server
      fetchHouseModels(callback = null) {
          const jobId = this.newContract.job;
          if (!jobId) return; // Exit if no job is selected

          axios.get('/api/house_models_by_job/', { params: { job_id: jobId } })
              .then(response => {
                  this.houseModels = response.data.map(houseModel => ({
                      id: houseModel.id,
                      name: houseModel.name,
                      jobs: houseModel.jobs
                  }));
                  // console.log("House models fetched and updated:", this.houseModels);

                  // Execute callback if provided
                  if (callback) callback();
              })
              .catch(error => {
                  console.error('Error fetching house models:', error);
              });
      },

      closeModal() {
          ['builderModal', 'jobModal', 'houseModelModal'].forEach(refName => {
              const modalRef = this.$refs[refName];
              modalRef?.hideModal?.(); // Llama al método elegante del hijo
          });
          // Limpiar los backdrop por si acaso
          document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
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
              /*    
                  if (lot !== NULL || lot !== '') {
                      if (!/^[0-9]{1,10}$/.test(lot)) {
                          reject('The LOT field must be a valid number of up to 10 digits or empty');
                          return;
                      }
                  }
              */
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
                              // Show alert with SweetAlert but don't reject the promise immediately
                              Swal.fire({
                                  icon: 'warning',
                                  title: 'Alert',
                                  text: 'There is already a contract with this lot or address in ' + this.newContract.type,
                              }).then(() => {
                                  // Continue the rejection after the alert is closed
                                  reject('Lot ' + this.newContract.lot + ' Address ' + this.newContract.address + ' ☺');
                              });
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
                  resolve(); // Si no hay lot o type, consideramos que la validación pasó.
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
              alert("Please enter at least one contract detail.");
              return;
          }
          this.loading = true;
          this.validateLot()
              .then(() => {
                  // console.log("this.newContract.contract_details: ", this.newContract.contract_details);
                  axios({
                      method: method,
                      url: url,
                      data: this.newContract,
                      headers: {
                          'Content-Type': 'application/json'
                      }
                  })
                      .then(response => {
                          if (!idToUpdate) {
                              this.resetForm();
                          }
                          // console.log('Contrato guardado con éxito:', response.data);
                          this.savedContractId = response.data.id;
                          this.savedNeedsReprint = response.data.needs_reprint;
                          if (this.savedNeedsReprint === false) {
                              this.downloadContract(this.savedContractId)
                          } else {
                              // Mostrar alerta informativa de que el contrato necesita revisión
                              Swal.fire({
                                  title: 'Transaction Pending Review',
                                  text: `This transaction ${this.savedContractId} will be shown in the contract list in red for review and printing.`,
                                  icon: 'info',
                                  confirmButtonText: 'OK',
                              }).then(() => {
                                  // Redirigir a ContractView.vue después de aceptar la alerta
                                  this.$router.push('/contracts');
                              });
                          }
                      })
                      .catch(error => {
                          this.error = error;
                          if (error.response) {
                              console.error('Error de servidor:', error.response.data);
                          } else if (error.request) {
                              console.error('Error de solicitud:', error.request);
                          } else {
                              console.error('Error:', error.message);
                          }
                      });
              })
              .catch(errorMessage => {
                  alert(errorMessage);
                  this.loading = false;
              });

      },

      resetForm() {
          this.newContract = {
              house_model: '',
              builder: '',
              job: '',
              type: '',
              lot: null,
              sqft: null,
              address: '',
              job_price: null,
              travel_price: null,
              total_options: null,
              total: null,
              comment: '',
              created_by: null,
          };
      },

      onFileChange(event) {
          this.newContract.file = event.target.files[0];
      },

      validateContractFields() {
          this.validationErrors = {}; // Reset previous errors

          const requiredFields = {
              builder: "Builder is required",
              job: "Community is required",
              house_model: "House Model is required",
              lot: "LOT is required",
              address: "Address is required",
              sqft: "Square Feet is required",
              job_price: "Job Price is required",
              travel_price: "Travel Price is required",
              total_options: "Total Options is required",
              total: "Total is required and must be greater than 1",

          };

          let isValid = true;

          Object.keys(requiredFields).forEach(field => {
              let value = this.newContract[field];

              // Validar si está vacío, nulo o indefinido
              if (value === null || value === undefined || value === "") {
                  this.validationErrors[field] = requiredFields[field];
                  isValid = false;
              }

              // Validaciones adicionales para valores numéricos
              if (["total"].includes(field) && parseFloat(value) <= 1) {
                  this.validationErrors[field] = requiredFields[field];
                  isValid = false;
              }
          });

          // Mostrar errores en una alerta si hay alguno
          if (!isValid) {
              Swal.fire({
                  title: "Missing Required Fields",
                  html: `<ul>${Object.values(this.validationErrors).map(error => `<li>${error}</li>`).join('')}</ul>`,
                  icon: "error",
                  confirmButtonText: "OK"
              });
          }

          return isValid;
      },

      downloadContract(id) {
          this.loading = true; // Activa el spinner
          this.loading_text = `Downloading contract ${id} as PDF`;
          axios.get('/web/contract-pdf/' + id)
              .then((response) => {
                  openPdf(response.data);
                  this.loading = false;
                  setTimeout(() => {
                      this.$router.push('/contracts');
                  }, 210); // Asegúrate de que el PDF se abra antes de redirigir
              })
              .catch(error => {
                  console.error('Error fetching contracts:', error);
                  this.loading = false; // Asegúrate de que el spinner se desactive si hay un error
              });
      }
  }
};
</script>

<style scoped>
.valid-feedback {
  display: block;
}

.invalid-feedback {
  display: block;
}

input::placeholder {
  color: #d9dde2;
}

label {
  color: rgb(var(--bs-primary-rgb));
}

p {
  color: orange;
}
</style>