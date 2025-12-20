<template>
  <div class="d-inline-block">
    <button
      class="btn btn-outline-secondary btn-sm ms-1"
      type="button"
      @click="openJobModal"
      :disabled="isDisabled"
      v-tt="'Edit the job.'">
      <img src="@assets/img/icon-changelink.svg" alt="Edit Job" width="15" height="15" />
    </button>

    <JobModalComponent
      ref="jobModal"
      :action="'edit'"
      :job="jobData"
      :builders="builders"
      @refresh="handleSaved"
      @close="closeModal" />
  </div>
</template>

<script setup>
  import { ref, defineProps, defineEmits, watch } from 'vue';
  import JobModalComponent from '@components/contracts/JobModalComponent.vue';
  import axios from 'axios';

  const props = defineProps({
    job: Object,
    builders: Array,
    isDisabled: Boolean,
  });

  const emit = defineEmits(['job-updated']);

  const jobModal = ref(null);
  const jobData = ref({ ...props.job });

  watch(
    () => props.job,
    newVal => {
      jobData.value = { ...newVal };
    }
  );

  function openJobModal() {
    jobData.value = { ...props.job };
    jobModal.value?.showModal();
  }

  function closeModal() {
    jobModal.value?.hideModal();
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  }

  function handleSaved() {
    const builderId = props.job.builder;
    if (!builderId) return;

    axios
      .get(`/api/job/jobs_by_builder/`, {
        params: { builder_id: builderId },
      })
      .then(response => {
        const updatedList = response.data;
        const updatedJob = updatedList.find(j => j.id === props.job.id);
        emit('job-updated', { job: updatedJob, list: updatedList });
      })
      .catch(error => {
        console.error('Error fetching jobs after edit:', error);
      });
  }
</script>
