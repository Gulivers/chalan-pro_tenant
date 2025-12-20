<template>
  <div class="d-inline-block">
    <button
      class="btn btn-outline-secondary btn-sm ms-1"
      type="button"
      @click="openModal"
      :disabled="isDisabled"
      v-tt="'Add a new house model to the system.'">
      <img src="@assets/img/icon-addlink.svg" alt="Add House Model" width="15" height="15" />
    </button>

    <HouseModelModal
      ref="houseModelModal"
      :action="'add'"
      :builderId="props.builderId"
      @saved="handleSaved"
      @refresh="handleSaved"
      @close="closeModal" />
  </div>
</template>

<script setup>
  import { ref, defineProps, defineEmits } from 'vue';
  import HouseModelModal from '@components/contracts/HouseModelModalComponent.vue';
  import axios from 'axios';

  const props = defineProps({
    isDisabled: Boolean,
    jobId: { type: [Number, String, Array, null], default: null },
    builderId: { type: [Number, String, null], default: null },
  });

  const emit = defineEmits(['housemodel-added']);

  const houseModelModal = ref(null);
  const action = ref('add');

  async function openModal() {
    action.value = 'add';
    await houseModelModal.value?.showModal();
  }

  function closeModal() {
    houseModelModal.value?.hideModal();
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  }

  function handleSaved(saved) {
    // Si backend devolvió el objeto guardado, seleccionamos por ID exacto
    const savedId = saved?.id ? Number(saved.id) : null;
    axios
      .get('/api/house_model/')
      .then(response => {
        const houseList = response.data || [];
        let selected = null;
        if (savedId != null) {
          selected = houseList.find(h => Number(h.id) === savedId) || null;
        }
        // Fallback: si no se encontró por id, tomar el más reciente
        if (!selected && houseList.length) {
          selected = houseList.reduce((a, b) => (a.id > b.id ? a : b));
        }
        emit('housemodel-added', { houseModel: selected, list: houseList });
      })
      .catch(error => {
        console.error('Error fetching house models:', error);
      });
  }

  async function handleRefresh() {
    /* noop o reusar handleSaved si quieres */
  }
</script>
