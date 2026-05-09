<template>
  <div class="step-preferences">
    <div class="step-header mb-4">
      <h3 class="fw-bold mb-2">Modules for your trial</h3>
      <p class="text-muted mb-0">
        These operational areas mirror the Jobrithm app menu—you get them during
        your trial while module toggles are simplified.
      </p>
    </div>

    <div class="step-content">
      <div class="alert alert-info border-0 mb-4" role="status">
        <i class="fas fa-layer-group me-2"></i>
        <strong class="d-inline">Included in trial.</strong>
        All sections below ship with full access during your trial. You can tune
        access later where your plan allows it.
      </div>

      <div class="row g-3">
        <div v-for="module in modules" :key="module.id" class="col-md-6">
          <div class="module-card module-card-static card h-100">
            <div class="card-body d-flex flex-column">
              <div class="d-flex align-items-start">
                <div class="module-icon me-3">
                  <i :class="module.icon" class="fa-2x text-primary"></i>
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

              <!-- Switches temporarily hidden (trial = all modules on; aligns with Navbar menu)
              <div class="mt-auto pt-3">
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
                    <span v-if="isSelected(module.id)" class="text-success fw-semibold">On</span>
                    <span v-else class="text-muted">Off</span>
                  </label>
                </div>
              </div>
              -->
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="errors.preferences"
        class="alert alert-danger mt-3 mb-0"
        role="alert">
        <i class="fas fa-exclamation-circle me-2"></i>
        {{ errors.preferences }}
      </div>

      <div class="mt-4 text-center">
        <small class="text-muted">
          <i class="fas fa-info-circle me-1"></i>
          {{ modules.length }} Jobrithm areas included with your workspace
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { ONBOARDING_MODULE_IDS } from "./onboardingModuleDefaults.js";

/** Display copy aligned with `NavbarComponent.vue` top-level menu (Dashboard excluded — home route). */
const MODULE_DEFS = {
  operations: {
    name: "Operations",
    icon: "fas fa-gears",
    description:
      "Schedule, Work Order Viewer, Transactions, Work Accounts—the day-to-day field and office rhythm.",
  },
  inventory: {
    name: "Inventory",
    icon: "fas fa-boxes",
    description:
      "Products, warehouses, transfers, dashboards, serialization, pricing units—everything under Inventory in the menu.",
  },
  contracts_pricing: {
    name: "Contracts & Pricing",
    icon: "fas fa-file-signature",
    description:
      "Piece work contracts and unit pricing for crews—not the prime agreement between you and the builder.",
  },
  entities: {
    name: "Entities",
    icon: "fas fa-building",
    description:
      "Builders & Parties, Party Types, Party Categories—master data that ties builders and parties together.",
  },
  crews_fleet: {
    name: "Crews and Fleet",
    icon: "fas fa-truck",
    description:
      "Categories, crews, trucks, truck assignments—the people and fleet you send to jobs.",
  },
  communities: {
    name: "Communities",
    icon: "fas fa-map-marked-alt",
    description:
      "Communities Map and Supervisor Communities—where jobs and subdivisions live on the map.",
  },
};

defineProps({
  errors: {
    type: Object,
    default: () => ({}),
  },
});

const modules = computed(() =>
  ONBOARDING_MODULE_IDS.map((id) => ({
    id,
    ...(MODULE_DEFS[id] || {
      name: id,
      icon: "fas fa-folder",
      description: "",
    }),
  }))
);
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

.module-card-static {
  cursor: default;
  border: 2px solid var(--bs-border-color);
  background-color: white;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.module-card-static:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--bs-primary);
}

.module-icon {
  flex-shrink: 0;
}
</style>
