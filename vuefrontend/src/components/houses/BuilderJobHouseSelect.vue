<template>
  <div>
    <!-- Builder Field -->
    <div class="row mb-2">
      <label class="col-sm-2 col-form-label">Builder</label>
      <div class="col col-sm-10 d-flex align-items-start gap-1">
        <v-select
          id="builder"
          :options="builders"
          v-model="builderValue"
          :reduce="b => b.id"
          label="name"
          :disabled="!isEditing"
          :loading="loadingBuilders"
          :clearable="true"
          placeholder="Select Builder"
          class="flex-grow-1"
          @change="resetJob"
          @keydown.enter="focusNext($event, 'job')"
          @focus="selectText"
          v-tt="'Select the Builder for this work account. Builder is required to enable Lot and Address fields.'" />
        <AddBuilderButton v-if="isEditing" @builder-added="reloadBuilders" />
        <EditBuilderButton
          v-if="isEditing && builderValue && selectedBuilder"
          :builder="selectedBuilder"
          @builder-updated="onBuilderUpdated" />
      </div>
    </div>

    <!-- Job Field -->
    <div class="row mb-2">
      <label class="col-sm-2 col-form-label">Job</label>
      <div class="col col-sm-10 d-flex align-items-start gap-1">
        <v-select
          id="job"
          :options="filteredJobs"
          v-model="jobValue"
          :reduce="j => j.id"
          label="name"
          :disabled="!isEditing"
          :loading="loadingJobs"
          :clearable="true"
          placeholder="Select Job"
          class="flex-grow-1"
          @change="resetHouse"
          @keydown.enter="focusNext($event, 'houseModel')"
          @focus="selectText"
          v-tt="'Select the Job for this work account. Job is required to enable House Model field.'" />
        <AddJobButton v-if="isEditing" :builder-id="builderValue" :builders="builders" @job-added="reloadJobs" />
        <EditJobButton
          v-if="isEditing && jobValue && selectedJob"
          :job="selectedJob"
          :builders="builders"
          @job-updated="reloadJobs" />
      </div>
    </div>

    <!-- House Model Field -->
    <div class="row align-items-center mb-3">
      <label class="col-sm-2 col-form-label">House Model</label>
      <div class="col col-sm-10 d-flex align-items-start gap-1">
        <v-select
          id="houseModel"
          :options="filteredHouses"
          v-model="houseModelValue"
          :reduce="h => h.id"
          label="name"
          :disabled="!isEditing"
          :loading="loadingHouses"
          :clearable="true"
          placeholder="Select House Model"
          class="flex-grow-1"
          ref="houseModel"
          @keydown.enter="focusNext($event, 'lot')"
          @focus="selectText"
          v-tt="
            'This field is for selecting the House Model associated with the work account. This field is optional.'
          " />
        <AddHouseModelButton :job-id="jobValue" :builder-id="builderValue" @housemodel-added="reloadHouseModels" />
        <EditHouseModelButton
          v-if="isEditing && houseModelValue && selectedHouseModel"
          :house-model="selectedHouseModel"
          :builder-id="builderValue"
          @housemodel-updated="reloadHouseModels" />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, watch, computed, defineProps, defineEmits, nextTick } from 'vue';
  import VSelect from 'vue-select';
  import AddBuilderButton from '@/components/buttons/AddBuilderButton.vue';
  import EditBuilderButton from '@/components/buttons/EditBuilderButton.vue';
  import AddJobButton from '@/components/buttons/AddJobButton.vue';
  import EditJobButton from '@/components/buttons/EditJobButton.vue';
  import AddHouseModelButton from '@/components/buttons/AddHouseModelButton.vue';
  import EditHouseModelButton from '@/components/buttons/EditHouseModelButton.vue';
  import axios from 'axios';

  const props = defineProps({
    modelValue: Object,
    isEditing: Boolean,
    isAbsence: Boolean,
  });

  const emit = defineEmits(['update:modelValue', 'update:builder', 'update:job', 'update:houseModel']);

  // Form values as props
  const builderValue = ref(props.modelValue?.builder || null);
  const jobValue = ref(props.modelValue?.job || null);
  const houseModelValue = ref(props.modelValue?.house_model || null);
  const loadingBuilders = ref(false);
  const loadingJobs = ref(false);
  const loadingHouses = ref(false);

  // Local data
  const builders = ref([]);
  const jobs = ref([]);
  const houses = ref([]);

  // Load initial data
  fetchData();

  async function fetchData() {
    await getBuilders();
    await getJobs();
    await getHouses();
  }

  async function getBuilders() {
    loadingBuilders.value = true;
    try {
      const response = await axios.get('/api/builders/');
      builders.value = response.data;
    } catch (error) {
      console.error('Error fetching builders:', error);
    } finally {
      loadingBuilders.value = false;
    }
  }

  async function getJobs() {
    loadingJobs.value = true;
    try {
      const response = await axios.get('/api/jobs/');
      jobs.value = response.data;
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      loadingJobs.value = false;
    }

  }

async function getHouses() {
    loadingHouses.value = true;
    try {
      const response = await axios.get('/api/house_model/');
      houses.value = response.data;
    } catch (error) {
      console.error('Error fetching houses:', error);
    } finally {
      loadingHouses.value = false;
    }
  }

  function resetJob() {
    jobValue.value = null;
    houseModelValue.value = null;
  }

  function resetHouse() {
    houseModelValue.value = null;
  }

  function reloadBuilders({ builder, list }) {
    // Si recibimos una lista válida úsala, de lo contrario recarga desde el backend
    if (Array.isArray(list) && list.length > 0) {
      builders.value = list;
    } else {
      // Fallback robusto: volver a consultar para asegurar que el v-select tenga la opción
      getBuilders();
    }

    if (builder?.id) {
      builderValue.value = builder.id;
      // Asegurar que el componente resuelva la etiqueta y no muestre el ID crudo
      nextTick(() => {
        const exists = (builders.value || []).some(b => b.id === builder.id);
        if (!exists) getBuilders();
      });
    }
  }

  function onBuilderUpdated({ builder, list }) {
    if (Array.isArray(list) && list.length > 0) {
      builders.value = list;
    } else {
      getBuilders();
    }

    if (builder?.id) {
      builderValue.value = builder.id;
      nextTick(() => {
        const exists = (builders.value || []).some(b => b.id === builder.id);
        if (!exists) getBuilders();
      });
    }
  }

  function reloadJobs({ job, list }) {
    jobs.value = Array.isArray(list) ? list : [];
    if (job?.id) jobValue.value = job.id;
  }

  function reloadHouseModels({ houseModel, list }) {
    // Si no llega lista (o viene vacía), recargar desde API para que aparezca inmediatamente
    if (Array.isArray(list) && list.length > 0) {
      houses.value = list;
    } else {
      getHouses();
    }

    if (houseModel?.id) {
      houseModelValue.value = houseModel.id;
      nextTick(() => {
        const exists = (houses.value || []).some(h => h.id === houseModel.id);
        if (!exists) getHouses();
      });
    }
  }

  const filteredJobs = computed(() =>
    builderValue.value
      ? jobs.value.filter(j => j.builder === builderValue.value || j.builder_id === builderValue.value)
      : []
  );
  const filteredHouses = computed(() =>
    jobValue.value ? houses.value.filter(h => h.jobs && h.jobs.includes(jobValue.value)) : []
  );

  const selectedBuilder = computed(() => (builders.value || []).find(b => b.id === builderValue.value));
  const selectedJob = computed(() => (jobs.value || []).find(j => j.id === jobValue.value));
  const selectedHouseModel = computed(() => (houses.value || []).find(h => h.id === houseModelValue.value));

  function focusNext(event, nextField) {
    event.preventDefault();
    
    // Usar setTimeout para asegurar que el DOM esté actualizado
    setTimeout(() => {
      let targetElement = null;
      
      if (nextField === 'job') {
        // Buscar por ID
        const jobElement = document.querySelector('#job');
        if (jobElement) {
          targetElement = jobElement.querySelector('.vs__search');
        }
        // Fallback: buscar por posición
        if (!targetElement) {
          const vSelects = document.querySelectorAll('.v-select');
          if (vSelects.length >= 2) {
            targetElement = vSelects[1].querySelector('.vs__search');
          }
        }
      } else if (nextField === 'houseModel') {
        // Buscar por ID
        const houseModelElement = document.querySelector('#houseModel');
        if (houseModelElement) {
          targetElement = houseModelElement.querySelector('.vs__search');
        }
        // Fallback: buscar por posición
        if (!targetElement) {
          const vSelects = document.querySelectorAll('.v-select');
          if (vSelects.length >= 3) {
            targetElement = vSelects[2].querySelector('.vs__search');
          }
        }
        // Fallback adicional: buscar por placeholder
        if (!targetElement) {
          const houseModelSelect = Array.from(document.querySelectorAll('.v-select')).find(vs => {
            const placeholder = vs.querySelector('.vs__placeholder');
            return placeholder && placeholder.textContent.includes('House Model');
          });
          if (houseModelSelect) {
            targetElement = houseModelSelect.querySelector('.vs__search');
          }
        }
      } else if (nextField === 'lot') {
        // Buscar el campo Lot en el componente padre (WorkAccountSelect)
        targetElement = document.querySelector('#f-lot');
      }
      
      if (targetElement) {
        targetElement.focus();
        // Si es un input, seleccionar el texto
        if (targetElement.tagName === 'INPUT') {
          targetElement.select();
        }
      } else {
        console.log('No se pudo encontrar el elemento objetivo para:', nextField);
        console.log('v-selects encontrados:', document.querySelectorAll('.v-select').length);
        console.log('Todos los v-selects:', document.querySelectorAll('.v-select'));
      }
    }, 150);
  }

  function selectText(event) {
    const input = event.target;
    input.select();
  }

  // Watchers to sync values and emit events
  watch(builderValue, (newValue, oldValue) => {
    emit('update:builder', newValue);

    // Si se deselecciona el builder, limpiar job y house model
    if (oldValue && !newValue) {
      jobValue.value = null;
      houseModelValue.value = null;
    }

    emit('update:modelValue', {
      builder: newValue,
      job: jobValue.value,
      house_model: houseModelValue.value,
    });
  });

  watch(jobValue, (newValue, oldValue) => {
    emit('update:job', newValue);

    // Si se deselecciona el job, limpiar house model
    if (oldValue && !newValue) {
      houseModelValue.value = null;
    }

    emit('update:modelValue', {
      builder: builderValue.value,
      job: newValue,
      house_model: houseModelValue.value,
    });
  });

  watch(houseModelValue, newValue => {
    emit('update:houseModel', newValue);
    emit('update:modelValue', {
      builder: builderValue.value,
      job: jobValue.value,
      house_model: newValue,
    });
  });

  // Watch for external changes to modelValue
  watch(
    () => props.modelValue,
    newValue => {
      if (newValue) {
        builderValue.value = newValue.builder || null;
        jobValue.value = newValue.job || null;
        houseModelValue.value = newValue.house_model || null;
      }
    },
    { deep: true }
  );
</script>

<style scoped>
:deep(.vs__spinner) {
  border-color: #007bff transparent #007bff transparent;
}
</style>
