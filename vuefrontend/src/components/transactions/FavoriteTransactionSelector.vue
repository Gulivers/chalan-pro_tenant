<template>
  <div class="favorite-transaction-selector">
    <label class="form-label d-flex align-items-center gap-1 text-primary">
      <i class="fas fa-star me-1"></i>
      Import favorite
    </label>

    <div class="position-relative">
      <!-- Dropdown personalizado para favoritos -->
      <div class="dropdown">
        <button 
          class="btn btn-outline-secondary dropdown-toggle w-100 d-flex justify-content-between align-items-center"
          type="button" 
          :disabled="isEditMode"
          @click="toggleDropdown"
          :class="{ 'show': isDropdownOpen }">
          <span v-if="selectedFavoriteName" class="text-truncate">
            {{ selectedFavoriteName }}
          </span>
          <span v-else class="text-muted text-truncate">
            <span class="d-none d-sm-inline">
              {{ isEditMode ? 'Cannot import favorites in edit mode' : 'Select a favorite transaction to import...' }}
            </span>
            <span class="d-sm-none">
              {{ isEditMode ? 'Cannot import in edit mode' : 'Select favorite...' }}
            </span>
          </span>
        </button>
        
        <ul 
          class="dropdown-menu w-100" 
          :class="{ 'show': isDropdownOpen }"
          @click.stop>
           <!-- Buscador -->
           <li class="px-2 pt-2" v-if="favoritesOptions.length > 0">
             <input
               type="text"
               class="form-control form-control-sm"
               v-model.trim="searchQuery"
               ref="searchInputRef"
               placeholder="Search favorite..." />
           </li>
           <li v-if="favoritesOptions.length > 0"><hr class="dropdown-divider" /></li>
          <li v-if="favoritesOptions.length === 0">
            <span class="dropdown-item-text text-muted">
              <i class="fas fa-info-circle me-2"></i>
              No favorites available
            </span>
          </li>
           <li v-for="favorite in filteredFavorites" :key="favorite.id">
            <div class="dropdown-item d-flex justify-content-between align-items-center">
              <div class="flex-grow-1" @click="selectFavorite(favorite.id)">
                <div class="fw-semibold">{{ favorite.display_name || favorite.name }}</div>
                <small class="text-muted">{{ formatDate(favorite.created_at) }}</small>
              </div>
              <div class="dropdown-item-actions">
                <button 
                  class="btn btn-outline-secondary "
                  @click="editFavorite(favorite)"
                  v-tt="'Edit the favorite.'">
                  <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15" />
                </button>
              </div>
            </div>
          </li>
        </ul>
      </div>


      <!-- Indicador de error -->
      <div class="invalid-feedback" v-if="error">
        {{ error }}
      </div>
    </div>

  </div>
</template>

<script setup>
  import { ref, reactive, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
  import axios from 'axios';

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
  });

  const emit = defineEmits(['update:modelValue', 'favorite-selected', 'edit-favorite']);

  const loading = ref(false);
  const favoritesOptions = ref([]);
  const selectedFavorite = ref(props.modelValue);
  const selectedFavoriteName = ref('');
  const isDropdownOpen = ref(false);
  const searchQuery = ref('');
  const searchInputRef = ref(null);

  // Watcher para sincronizar con v-model
  watch(
    () => props.modelValue,
    newValue => {
      selectedFavorite.value = newValue;
    }
  );

  watch(selectedFavorite, newValue => {
    emit('update:modelValue', newValue);
  });

   async function loadFavorites(forceReload = false) {
     if (favoritesOptions.value.length > 0 && !forceReload) return; // Ya cargados

     console.log('🔍 Loading favorites...', forceReload ? '(forced reload)' : '');
     loading.value = true;
     try {
       const response = await axios.get('/api/transaction-favorites/', {
         params: {
           is_active: true,
           ordering: '-created_at',
         },
       });

       console.log('🔍 Favorites response:', response.data);
       const favorites = Array.isArray(response.data) ? response.data : response.data.results || [];

       favoritesOptions.value = favorites.map(favorite => ({
         id: favorite.id,
         name: favorite.name,
         description: favorite.description,
         created_at: favorite.created_at,
         display_name: favorite.display_name,
         document_type_preview: getDocumentTypePreview(favorite.document_data),
         lines_count: favorite.lines_data ? favorite.lines_data.length : 0,
       }));
       
       console.log('🔍 Favorites loaded:', favoritesOptions.value.length);
     } catch (error) {
       console.error('Error loading favorites:', error);
       favoritesOptions.value = [];
     } finally {
       loading.value = false;
     }
   }

  function getDocumentTypePreview(documentData) {
    try {
      if (documentData && documentData.document_type) {
        // Aquí podrías hacer una llamada para obtener el nombre del tipo de documento
        // Por ahora retornamos el ID
        return `Type: ${documentData.document_type}`;
      }
    } catch (error) {
      console.error('Error getting document type preview:', error);
    }
    return null;
  }

  function formatDate(dateString) {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch (error) {
      return dateString;
    }
  }

  // Función para abrir/cerrar el dropdown
  function toggleDropdown() {
    if (props.isEditMode) return;
    isDropdownOpen.value = !isDropdownOpen.value;
    if (!isDropdownOpen.value) {
      searchQuery.value = '';
    }
    if (isDropdownOpen.value) {
      nextTick(() => {
        if (searchInputRef.value) {
          try { searchInputRef.value.focus(); } catch (e) {}
        }
      });
    }
  }

  // Función para seleccionar un favorito
  async function selectFavorite(favoriteId) {
    selectedFavorite.value = favoriteId;
    emit('update:modelValue', favoriteId);
    
    // Actualizar nombre mostrado
    const favorite = favoritesOptions.value.find(f => f.id === favoriteId);
    selectedFavoriteName.value = favorite ? (favorite.display_name || favorite.name) : '';
    
    // Cerrar dropdown
    isDropdownOpen.value = false;
    
    await onFavoriteSelected(favoriteId);
  }

  async function onFavoriteSelected(favoriteId) {
    if (!favoriteId) {
      selectedFavoriteName.value = '';
      emit('favorite-selected', null);
      return;
    }

    try {
      // Obtener información detallada del favorito
      const response = await axios.get(`/api/transaction-favorites/${favoriteId}/import/`);
      const favoriteData = response.data;

      // Emitir evento con los datos completos del favorito
      emit('favorite-selected', {
        id: favoriteData.id,
        name: favoriteData.name,
        description: favoriteData.description,
        document_data: favoriteData.document_data,
        lines_data: favoriteData.lines_data,
        created_at: favoriteData.created_at,
      });
    } catch (error) {
      console.error('Error loading favorite details:', error);

      // Limpiar selección en caso de error
      selectedFavorite.value = null;
      selectedFavoriteName.value = '';
      emit('favorite-selected', null);
    }
  }

  const filteredFavorites = computed(() => {
    const q = (searchQuery.value || '').toLowerCase();
    if (!q) return favoritesOptions.value;
    return favoritesOptions.value.filter(fav => {
      const name = String(fav.display_name || fav.name || '').toLowerCase();
      const desc = String(fav.description || '').toLowerCase();
      const doc  = String(fav.document_type_preview || '').toLowerCase();
      const date = String(fav.created_at || '').toLowerCase();
      return name.includes(q) || desc.includes(q) || doc.includes(q) || date.includes(q);
    });
  });

  function editFavorite(favorite) {
    // Cerrar dropdown
    isDropdownOpen.value = false;
    // Emitir evento para editar el favorito
    emit('edit-favorite', favorite);
  }

   // Cargar favoritos al montar el componente
   loadFavorites();
   
   // Debug: Log cuando el componente se monta
   console.log('🔍 FavoriteTransactionSelector mounted');

   // Cerrar dropdown cuando se hace clic fuera
   function handleClickOutside(event) {
     const dropdown = event.target.closest('.dropdown');
     if (!dropdown) {
       isDropdownOpen.value = false;
     }
   }

   // Agregar listener al montar
   document.addEventListener('click', handleClickOutside);

   // Limpiar listener al desmontar
   onUnmounted(() => {
     document.removeEventListener('click', handleClickOutside);
   });

   // Exponer funciones para el componente padre
   defineExpose({
     loadFavorites,
   });
</script>

<style scoped>
  .favorite-transaction-selector {
    position: relative;
  }

  .form-select-custom {
    min-height: 38px;
  }

  .form-select-custom.is-invalid {
    border-color: #dc3545;
  }

  .invalid-feedback {
    display: block;
  }

  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }

  .fw-semibold {
    font-weight: 600;
  }

  .card.bg-light {
    border: 1px solid #dee2e6;
  }

  /* Estilos mínimos para dropdown Bootstrap */
  .dropdown-menu {
    min-width: 100%;
  }

  .dropdown-item {
    padding: 0.5rem 1rem;
  }

  .dropdown-item-text {
    padding: 0.5rem 1rem;
  }

  /* Estilos para el botón de editar */
  .edit-btn {
    padding: 0.375rem 0.5rem;
    font-size: 0.875rem;
    min-width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .edit-btn i {
    font-size: 0.875rem;
  }

  /* Estilos para las acciones del dropdown */
  .dropdown-item-actions {
    opacity: 0;
    transition: opacity 0.4s ease;
  }

  .dropdown-item:hover .dropdown-item-actions {
    opacity: 1;
  }
</style>
