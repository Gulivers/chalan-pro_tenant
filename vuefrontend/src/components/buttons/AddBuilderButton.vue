<template>
  <div class="d-inline-block">
    <button
      class="btn btn-outline-secondary btn-sm ms-1"
      type="button"
      @click="openBuilderModal"
      :disabled="isDisabled"
      v-tt="'Add a new party to the system.'">
      <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
    </button>

    <BuilderModal
      ref="builderModal"
      :action="action"
      :builder="builderData"
      @saved="handleSaved"
      @close="closeModal" />
  </div>
</template>

<script setup>
  import { ref, defineProps, defineEmits } from 'vue';
  import BuilderModal from '@/components/contracts/BuilderModalComponent.vue';
  import axios from 'axios';

  const props = defineProps({
    isDisabled: {
      type: Boolean,
      default: false,
    },
  });

  const emit = defineEmits(['builder-added']);

  const action = ref('add');
  const builderData = ref(null); // DynamicForm maneja los datos internamente

  const builderModal = ref(null);

  function openBuilderModal() {
    action.value = 'add';
    builderData.value = null; // DynamicForm inicializa los datos
    builderModal.value?.showModal();
  }

  function closeModal() {
    builderModal.value?.hideModal();
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  }

  function handleSaved(savedBuilder) {
    // El DynamicForm ya nos pasa el builder guardado
    emit('builder-added', {
      builder: savedBuilder,
      list: null, // Se puede recargar externamente si es necesario
    });
  }
</script>
