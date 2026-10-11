<template>
  <div class="jr-bjh jr-bjh-grid" :class="{ 'jr-bjh--stacked': stacked }">
    <JRField
      v-slot="{ describedby, invalid }"
      label="Builder"
      required
      inputId="bjh-builder">
      <JRSelectAddon
        inputId="bjh-builder"
        v-model="builderValue"
        :options="builders"
        optionLabel="name"
        optionValue="id"
        placeholder="Select Builder"
        filter
        showClear
        :disabled="!isEditing"
        :invalid="invalid"
        :ariaDescribedby="describedby"
        :showAdd="isEditing"
        :showEdit="isEditing && !!builderValue"
        :addDisabled="!isEditing"
        :editDisabled="!isEditing || !builderValue"
        addLabel="Add a new party to the system"
        editLabel="Edit the currently selected party"
        @add="openBuilderDialog('add')"
        @edit="openBuilderDialog('edit')" />
    </JRField>

    <JRField
      v-slot="{ describedby, invalid }"
      label="Community"
      required
      inputId="bjh-job">
      <JRSelectAddon
        inputId="bjh-job"
        v-model="jobValue"
        :options="filteredJobs"
        optionLabel="name"
        optionValue="id"
        placeholder="Select Community"
        filter
        showClear
        :disabled="!isEditing || !builderValue"
        :invalid="invalid"
        :ariaDescribedby="describedby"
        :showAdd="isEditing"
        :showEdit="isEditing && !!jobValue"
        :addDisabled="!isEditing"
        :editDisabled="!isEditing || !jobValue"
        addLabel="Add a new community"
        editLabel="Edit the currently selected community"
        @add="openJobDialog('add')"
        @edit="openJobDialog('edit')" />
    </JRField>

    <JRField
      v-slot="{ describedby, invalid }"
      label="House Model"
      inputId="bjh-house-model"
      :hint="
        isEditing && jobValue
          ? 'Filtered by the selected Community.'
          : ''
      ">
      <JRSelectAddon
        inputId="bjh-house-model"
        v-model="houseModelValue"
        :options="filteredHouses"
        optionLabel="name"
        optionValue="id"
        placeholder="Select House Model"
        filter
        showClear
        :disabled="!isEditing || !jobValue"
        :invalid="invalid"
        :ariaDescribedby="describedby"
        :showAdd="isEditing"
        :showEdit="isEditing && !!houseModelValue"
        :addDisabled="!isEditing"
        :editDisabled="!isEditing || !houseModelValue"
        addLabel="Add a new house model"
        editLabel="Edit the currently selected house model"
        @add="openHouseDialog('add')"
        @edit="openHouseDialog('edit')" />
    </JRField>

    <JRDrawer
      class="jr-catalog-drawer jr-catalog-drawer--stack"
      :visible="catalogDrawerVisible"
      :header="catalogDrawerHeader"
      position="right"
      @update:visible="onCatalogDrawerVisible">
      <DynamicForm
        v-if="catalogDrawerVisible && catalogType"
        :key="catalogFormKey"
        :schema-endpoint="catalogSchemaEndpoint"
        :api-endpoint="catalogApiEndpoint"
        :object-id="catalogObjectId"
        :form-title="catalogFormTitle"
        :is-modal="true"
        :sections="catalogSections"
        @saved="onCatalogSaved"
        @cancel="closeCatalogDrawer" />
    </JRDrawer>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import axios from 'axios';
import { JRField, JRSelectAddon, JRDrawer } from '@ui';
import DynamicForm from '@/components/parties/DynamicForm.vue';
import { BUILDER_FORM_SECTIONS } from '@/components/parties/builderFormSections';

const props = defineProps({
  modelValue: Object,
  isEditing: Boolean,
  isAbsence: Boolean,
  /** Single-column field stack for catalog drawers */
  stacked: { type: Boolean, default: false },
});

const emit = defineEmits([
  'update:modelValue',
  'update:builder',
  'update:job',
  'update:houseModel',
]);

const builderValue = ref(props.modelValue?.builder || null);
const jobValue = ref(props.modelValue?.job || null);
const houseModelValue = ref(props.modelValue?.house_model || null);

const builders = ref([]);
const jobs = ref([]);
const houses = ref([]);

const catalogDrawerVisible = ref(false);
const catalogType = ref(null);
const catalogAction = ref('add');
const catalogFormNonce = ref(0);

const CATALOG_CONFIG = {
  builder: {
    schemaEndpoint: '/api/schema/builder/',
    apiEndpoint: '/api/builder/',
    sections: BUILDER_FORM_SECTIONS,
    addHeader: 'Add Party',
    editHeader: (id) => `Edit Party #${id}`,
    addFormTitle: 'Create Party',
    editFormTitle: 'Edit Party',
  },
  job: {
    schemaEndpoint: '/api/schema/job/',
    apiEndpoint: '/api/job/',
    sections: undefined,
    addHeader: 'Add Community',
    editHeader: (id) => `Edit Community #${id}`,
    addFormTitle: 'Create Community',
    editFormTitle: 'Edit Community',
  },
  houseModel: {
    schemaEndpoint: '/api/schema/house-model/',
    apiEndpoint: '/api/house_model/',
    sections: undefined,
    addHeader: 'Add House Model',
    editHeader: (id) => `Edit House Model #${id}`,
    addFormTitle: 'Create House Model',
    editFormTitle: 'Edit House Model',
  },
};

const filteredJobs = computed(() =>
  builderValue.value
    ? jobs.value.filter(
        (j) =>
          j.builder === builderValue.value ||
          j.builder_id === builderValue.value
      )
    : []
);

const filteredHouses = computed(() =>
  jobValue.value
    ? houses.value.filter(
        (h) => Array.isArray(h.jobs) && h.jobs.includes(jobValue.value)
      )
    : []
);

const catalogConfig = computed(() =>
  catalogType.value ? CATALOG_CONFIG[catalogType.value] : null
);

const catalogObjectId = computed(() => {
  if (catalogAction.value !== 'edit') return null;
  if (catalogType.value === 'builder') return builderValue.value;
  if (catalogType.value === 'job') return jobValue.value;
  if (catalogType.value === 'houseModel') return houseModelValue.value;
  return null;
});

const catalogSchemaEndpoint = computed(
  () => catalogConfig.value?.schemaEndpoint || ''
);
const catalogApiEndpoint = computed(
  () => catalogConfig.value?.apiEndpoint || ''
);
const catalogSections = computed(() => catalogConfig.value?.sections);

const catalogDrawerHeader = computed(() => {
  const config = catalogConfig.value;
  if (!config) return '';
  if (catalogAction.value === 'edit' && catalogObjectId.value) {
    return config.editHeader(catalogObjectId.value);
  }
  return config.addHeader;
});

const catalogFormTitle = computed(() => {
  const config = catalogConfig.value;
  if (!config) return '';
  return catalogAction.value === 'edit'
    ? config.editFormTitle
    : config.addFormTitle;
});

const catalogFormKey = computed(() => {
  const id = catalogObjectId.value || 'new';
  return `bjh-${catalogType.value}-${catalogAction.value}-${id}-${catalogFormNonce.value}`;
});

function emitModel() {
  emit('update:modelValue', {
    builder: builderValue.value,
    job: jobValue.value,
    house_model: houseModelValue.value,
  });
}

async function getBuilders() {
  try {
    const { data } = await axios.get('/api/builders/');
    builders.value = Array.isArray(data) ? data : data?.results || [];
  } catch (e) {
    console.error('Error fetching builders:', e);
  }
}

async function getJobs() {
  try {
    const { data } = await axios.get('/api/jobs/');
    jobs.value = Array.isArray(data) ? data : data?.results || [];
  } catch (e) {
    console.error('Error fetching jobs:', e);
  }
}

async function getHouses() {
  try {
    const { data } = await axios.get('/api/house_model/');
    houses.value = Array.isArray(data) ? data : data?.results || [];
  } catch (e) {
    console.error('Error fetching house models:', e);
  }
}

async function fetchData() {
  await Promise.all([getBuilders(), getJobs(), getHouses()]);
}

fetchData();

function openCatalogDrawer(type, mode) {
  catalogType.value = type;
  catalogAction.value = mode;
  catalogFormNonce.value += 1;
  catalogDrawerVisible.value = true;
}

function openBuilderDialog(mode) {
  openCatalogDrawer('builder', mode);
}

function openJobDialog(mode) {
  openCatalogDrawer('job', mode);
}

function openHouseDialog(mode) {
  openCatalogDrawer('houseModel', mode);
}

function closeCatalogDrawer() {
  catalogDrawerVisible.value = false;
}

function onCatalogDrawerVisible(visible) {
  catalogDrawerVisible.value = visible;
  if (!visible) catalogType.value = null;
}

async function onCatalogSaved(saved) {
  if (catalogType.value === 'builder') {
    await onBuilderSaved(saved);
  } else if (catalogType.value === 'job') {
    await onJobSaved(saved);
  } else if (catalogType.value === 'houseModel') {
    await onHouseSaved(saved);
  }
  closeCatalogDrawer();
}

async function onBuilderSaved(saved) {
  await getBuilders();
  if (saved?.id) {
    builderValue.value = saved.id;
    emit('update:builder', saved.id);
    emitModel();
  }
}

async function onJobSaved(saved) {
  await getJobs();
  if (saved?.id) {
    jobValue.value = saved.id;
    emit('update:job', saved.id);
    emitModel();
  } else if (builderValue.value) {
    // refresh path without payload: pick newest for this builder
    const list = filteredJobs.value;
    if (list.length) {
      const newest = list.reduce((a, b) => (a.id > b.id ? a : b));
      jobValue.value = newest.id;
      emit('update:job', newest.id);
      emitModel();
    }
  }
}

async function onHouseSaved(saved) {
  await getHouses();
  if (saved?.id) {
    houseModelValue.value = saved.id;
    emit('update:houseModel', saved.id);
    emitModel();
  }
}

watch(builderValue, (newValue, oldValue) => {
  emit('update:builder', newValue);
  if (oldValue && !newValue) {
    jobValue.value = null;
    houseModelValue.value = null;
  }
  emitModel();
});

watch(jobValue, (newValue, oldValue) => {
  emit('update:job', newValue);
  if (oldValue && !newValue) {
    houseModelValue.value = null;
  }
  emitModel();
});

watch(houseModelValue, (newValue) => {
  emit('update:houseModel', newValue);
  emitModel();
});

watch(
  () => props.modelValue,
  (newValue) => {
    if (!newValue) return;
    builderValue.value = newValue.builder || null;
    jobValue.value = newValue.job || null;
    houseModelValue.value = newValue.house_model || null;
  },
  { deep: true }
);
</script>

<style scoped>
.jr-bjh {
  min-width: 0;
}

.jr-bjh-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .jr-bjh-grid:not(.jr-bjh--stacked) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .jr-bjh-grid:not(.jr-bjh--stacked) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-bjh--stacked.jr-bjh-grid {
  gap: 0.85rem;
  grid-template-columns: minmax(0, 1fr);
}
</style>
