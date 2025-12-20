<template>
  <div class="d-inline-block">
    <button
      class="btn btn-outline-secondary btn-sm ms-1"
      type="button"
      @click="openJobModal"
      :disabled="isDisabled"
      v-tt="'Add a new job to the system.'">
      <img src="@assets/img/icon-addlink.svg" alt="Add Job" width="15" height="15" />
    </button>

    <JobModalComponent
      ref="jobModal"
      :action="action"
      :job="jobData"
      :builders="builders"
      @refresh="handleSaved"
      @close="closeModal" />
  </div>
</template>

<script setup>
  import { ref, defineProps, defineEmits } from 'vue';
  import JobModalComponent from '@components/contracts/JobModalComponent.vue';
  import axios from 'axios';

  const props = defineProps({
    isDisabled: Boolean,
    builderId: { type: [Number, String, null], default: null },
    builders: Array,
  });

  const emit = defineEmits(['job-added']);

  const jobModal = ref(null);
  const action = ref('add');
  const jobData = ref({ name: '', builder: Number(props.builderId) || null });

  function openJobModal() {
    action.value = 'add';
    jobData.value = { name: '', builder: Number(props.builderId) || null };
    jobModal.value?.showModal();
  }

  function closeModal() {
    jobModal.value?.hideModal();
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  }

  function handleSaved() {
    // Convertir a número y validar que sea válido
    const builderId = Number(props.builderId);
    if (!builderId || isNaN(builderId)) return;

    axios
      .get(`/api/job/jobs_by_builder/`, {
        params: { builder_id: builderId },
      })
      .then(response => {
        const jobList = response.data;
        const newestJob = jobList.reduce((a, b) => (a.id > b.id ? a : b));
        emit('job-added', { job: newestJob, list: jobList });
      })
      .catch(error => {
        console.error('Error fetching jobs:', error);
      });
  }
</script>
