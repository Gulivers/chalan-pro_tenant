<template>
  <div class="jr-favorite-selector">
    <JRSelectAddon
      :inputId="inputId"
      :modelValue="selectedFavorite"
      :options="favoritesOptions"
      optionLabel="label"
      optionValue="id"
      filter
      showClear
      :disabled="isEditMode || loading"
      :placeholder="
        isEditMode
          ? 'Cannot import in edit mode'
          : 'Select a favorite transaction…'
      "
      :showEdit="true"
      :editDisabled="!selectedFavorite"
      editLabel="Edit the selected favorite"
      @update:modelValue="selectFavorite"
      @show="() => loadFavorites(false)"
      @edit="editSelectedFavorite" />
    <p v-if="error" class="jr-favorite-selector__error" role="alert">
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import axios from "axios";
import { JRSelectAddon } from "@ui";

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: null,
  },
  isEditMode: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
  inputId: {
    type: String,
    default: "favorite-transaction-select",
  },
});

const emit = defineEmits([
  "update:modelValue",
  "favorite-selected",
  "edit-favorite",
]);

const loading = ref(false);
const favoritesOptions = ref([]);
const selectedFavorite = ref(props.modelValue);

watch(
  () => props.modelValue,
  (newValue) => {
    selectedFavorite.value = newValue;
  }
);

async function loadFavorites(forceReload = false) {
  if (favoritesOptions.value.length > 0 && !forceReload) return;
  loading.value = true;
  try {
    const response = await axios.get("/api/transaction-favorites/", {
      params: { is_active: true, ordering: "-created_at" },
    });
    const favorites = Array.isArray(response.data)
      ? response.data
      : response.data.results || [];
    favoritesOptions.value = favorites.map((favorite) => ({
      id: favorite.id,
      name: favorite.name,
      label: favorite.display_name || favorite.name,
      description: favorite.description,
      created_at: favorite.created_at,
      display_name: favorite.display_name,
      document_data: favorite.document_data,
      lines_data: favorite.lines_data,
      lines_count: favorite.lines_data ? favorite.lines_data.length : 0,
    }));
  } catch (error) {
    console.error("Error loading favorites:", error);
    favoritesOptions.value = [];
  } finally {
    loading.value = false;
  }
}

async function selectFavorite(favoriteId) {
  selectedFavorite.value = favoriteId;
  emit("update:modelValue", favoriteId);
  await onFavoriteSelected(favoriteId);
}

async function onFavoriteSelected(favoriteId) {
  if (!favoriteId) {
    emit("favorite-selected", null);
    return;
  }
  try {
    const response = await axios.get(
      `/api/transaction-favorites/${favoriteId}/import/`
    );
    const favoriteData = response.data;
    emit("favorite-selected", {
      id: favoriteData.id,
      name: favoriteData.name,
      description: favoriteData.description,
      document_data: favoriteData.document_data,
      lines_data: favoriteData.lines_data,
      created_at: favoriteData.created_at,
    });
  } catch (error) {
    console.error("Error loading favorite details:", error);
    selectedFavorite.value = null;
    emit("update:modelValue", null);
    emit("favorite-selected", null);
  }
}

function editSelectedFavorite() {
  const favorite = favoritesOptions.value.find(
    (f) => f.id === selectedFavorite.value
  );
  if (!favorite) return;
  emit("edit-favorite", favorite);
}

onMounted(() => {
  loadFavorites();
});

defineExpose({ loadFavorites });
</script>

<style scoped>
.jr-favorite-selector__error {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
}
</style>
