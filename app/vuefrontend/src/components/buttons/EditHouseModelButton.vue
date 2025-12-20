<template>
  <div class="d-inline-block">
    <button
      class="btn btn-outline-secondary btn-sm ms-1"
      type="button"
      @click="openModal"
      :disabled="isDisabled"
      v-tt="'Edit the house model.'">
      <img src="@assets/img/icon-changelink.svg" alt="Edit House Model" width="15" height="15" />
    </button>

    <HouseModelModal
      ref="houseModelModal"
      :action="'edit'"
      :houseModelId="modelData?.id"
      :builderId="props.builderId"
      @refresh="handleSaved"
      @close="closeModal" />
  </div>
</template>

<script setup>
  import { ref, defineProps, defineEmits, watch } from 'vue';
  import HouseModelModal from '@components/contracts/HouseModelModalComponent.vue';
  import axios from 'axios';

  const props = defineProps({
    houseModel: Object,
    isDisabled: Boolean,
    jobId: { type: [Number, String, Array, null], default: null },
    builderId: { type: [Number, String, null], default: null },
  });

  const emit = defineEmits(['housemodel-updated']);

  const houseModelModal = ref(null);
  const modelData = ref({ ...props.houseModel });

  watch(
    () => props.houseModel,
    newVal => {
      modelData.value = { ...newVal };
    }
  );

  function openModal() {
    houseModelModal.value?.showModal();
  }

  function closeModal() {
    houseModelModal.value?.hideModal();
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  }

  async function handleSaved() {
    try {
      const listRes = await axios.get('/api/house_model/');
      const houseList = listRes.data || [];

      // Rebuscamos el actualizado por ID
      const updated = houseList.find(h => h.id === modelData.value?.id) || null;

      emit('housemodel-updated', { houseModel: updated, list: houseList });
    } catch (error) {
      console.error('Error updating house models:', error);
    }
  }
</script>
