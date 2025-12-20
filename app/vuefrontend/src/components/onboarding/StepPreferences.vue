<template>
  <div class="step-preferences">
    <div class="step-header mb-4">
      <h3 class="fw-bold mb-2">System Preferences</h3>
      <p class="text-muted mb-0">Select the modules you want to activate in your workspace</p>
    </div>

    <div class="step-content">
      <div class="row g-3">
        <div
          v-for="module in modules"
          :key="module.id"
          class="col-md-6"
        >
          <div
            class="module-card card h-100"
            :class="{ 'selected': isSelected(module.id), 'border-primary': isSelected(module.id) }"
            @click="toggleModule(module.id)"
            role="button"
            tabindex="0"
            @keyup.enter="toggleModule(module.id)"
            :aria-pressed="isSelected(module.id)"
            :aria-label="`${module.name} - ${isSelected(module.id) ? 'Selected' : 'Not selected'}`"
          >
            <div class="card-body d-flex flex-column">
              <div class="d-flex align-items-start mb-3">
                <div class="module-icon me-3">
                  <i :class="module.icon" class="fa-2x" :style="{ color: isSelected(module.id) ? 'var(--bs-primary)' : 'var(--bs-secondary)' }"></i>
                </div>
                <div class="flex-grow-1">
                  <h5 class="card-title mb-2 fw-semibold">
                    {{ module.name }}
                  </h5>
                  <p class="card-text text-muted small mb-0">
                    {{ module.description }}
                  </p>
                </div>
              </div>
              <div class="mt-auto">
                <div class="form-check form-switch" @click.stop>
                  <input
                    class="form-check-input"
                    type="checkbox"
                    role="switch"
                    :checked="isSelected(module.id)"
                    @change="toggleModule(module.id)"
                    @click.stop
                    :id="`module-${module.id}`"
                    tabindex="0"
                  />
                  <label class="form-check-label" :for="`module-${module.id}`" @click.stop>
                    <span v-if="isSelected(module.id)" class="text-success fw-semibold">Enabled</span>
                    <span v-else class="text-muted">Disabled</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="errors.preferences" class="alert alert-danger mt-3 mb-0" role="alert">
        <i class="fas fa-exclamation-circle me-2"></i>
        {{ errors.preferences }}
      </div>

      <div v-if="selectedCount > 0" class="mt-4 text-center">
        <small class="text-muted">
          <i class="fas fa-info-circle me-1"></i>
          {{ selectedCount }} module{{ selectedCount !== 1 ? 's' : '' }} selected
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const modules = [
  {
    id: 'inventory',
    name: 'Inventory',
    icon: 'fas fa-boxes',
    description: 'Manage products, warehouses, categories, and real-time stock control.'
  },
  {
    id: 'contracts',
    name: 'Contracts',
    icon: 'fas fa-file-contract',
    description: 'Create contracts with work prices and pay sheets for crews to complete assigned jobs.'
  },
  {
    id: 'schedule',
    name: 'Schedule',
    icon: 'fas fa-calendar-alt',
    description: 'Organize events, appointments, and work calendar for your team.'
  },
  {
    id: 'crews',
    name: 'Crews',
    icon: 'fas fa-users',
    description: 'Manage work crews, assignments, and human resources.'
  },
  {
    id: 'notes',
    name: 'Notes',
    icon: 'fas fa-sticky-note',
    description: 'Take notes, comments, and document important information.'
  }
]

const isSelected = (moduleId) => {
  return props.modelValue.includes(moduleId)
}

const toggleModule = (moduleId) => {
  const current = [...props.modelValue]
  const index = current.indexOf(moduleId)
  
  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(moduleId)
  }
  
  emit('update:modelValue', current)
}

const selectedCount = computed(() => props.modelValue.length)
</script>

<style scoped>
.step-header {
  text-align: center;
}

.step-header h3 {
  color: var(--bs-dark);
  font-size: 1.75rem;
}

.step-content {
  max-width: 900px;
  margin: 0 auto;
}

.module-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid var(--bs-border-color);
  background-color: white;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--bs-primary);
}

.module-card.selected {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.05);
  box-shadow: 0 2px 8px rgba(var(--bs-primary-rgb), 0.2);
}

.module-card:focus {
  outline: 2px solid var(--bs-primary);
  outline-offset: 2px;
}

.module-icon {
  transition: transform 0.2s ease;
}

.module-card:hover .module-icon {
  transform: scale(1.1);
}

.form-check-input {
  cursor: pointer;
  margin-top: 0.25rem;
}

.form-check-label {
  cursor: pointer;
  user-select: none;
}
</style>

