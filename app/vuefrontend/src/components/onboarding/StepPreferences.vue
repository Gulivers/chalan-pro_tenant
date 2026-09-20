<template>
  <div class="jr-onboard-step">
    <p v-if="errors.preferences" class="jr-onboard-step__error" role="alert">
      {{ errors.preferences }}
    </p>

    <ul class="jr-onboard-modules">
      <li
        v-for="mod in modules"
        :key="mod.id"
        class="jr-onboard-modules__item">
        <div class="jr-onboard-modules__icon" aria-hidden="true">
          <component :is="mod.Icon" class="jr-onboard-modules__svg" />
        </div>
        <div class="jr-onboard-modules__copy">
          <h2 class="jr-onboard-modules__name">{{ mod.name }}</h2>
          <p class="jr-onboard-modules__desc">{{ mod.description }}</p>
        </div>
        <span class="jr-onboard-modules__badge">Included</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Cog from '@primeicons/vue/cog'
import Box from '@primeicons/vue/box'
import File from '@primeicons/vue/file'
import Building from '@primeicons/vue/building'
import Truck from '@primeicons/vue/truck'
import MapMarker from '@primeicons/vue/map-marker'
import { ONBOARDING_MODULE_IDS } from './onboardingModuleDefaults.js'

const MODULE_DEFS = {
  operations: {
    name: 'Operations',
    Icon: Cog,
    description:
      'Schedule, Work Order Viewer, Transactions, Work Accounts—the day-to-day field and office rhythm.',
  },
  inventory: {
    name: 'Inventory',
    Icon: Box,
    description:
      'Products, warehouses, transfers, dashboards, serialization, pricing units—everything under Inventory in the menu.',
  },
  contracts_pricing: {
    name: 'Contracts & Pricing',
    Icon: File,
    description:
      'Piece work contracts and unit pricing for crews—not the prime agreement between you and the builder.',
  },
  entities: {
    name: 'Entities',
    Icon: Building,
    description:
      'Builders & Parties, Party Types, Party Categories—master data that ties builders and parties together.',
  },
  crews_fleet: {
    name: 'Crews and Fleet',
    Icon: Truck,
    description:
      'Categories, crews, trucks, truck assignments—the people and fleet you send to jobs.',
  },
  communities: {
    name: 'Communities',
    Icon: MapMarker,
    description:
      'Communities Map and Supervisor Communities—where jobs and subdivisions live on the map.',
  },
}

defineProps({
  errors: {
    type: Object,
    default: () => ({}),
  },
})

const modules = computed(() =>
  ONBOARDING_MODULE_IDS.map((id) => ({
    id,
    ...(MODULE_DEFS[id] || {
      name: id,
      Icon: Box,
      description: '',
    }),
  }))
)
</script>

<style scoped>
.jr-onboard-step__error {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  border: 1px solid color-mix(in srgb, var(--color-jr-danger, #dc2626) 35%, transparent);
  background: color-mix(in srgb, var(--color-jr-danger, #dc2626) 8%, #fff);
  color: var(--color-jr-danger, #dc2626);
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-onboard-modules {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.jr-onboard-modules__item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 0.75rem;
  align-items: start;
  padding: 1rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #fff);
}

.jr-onboard-modules__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  background: color-mix(in srgb, var(--color-jr-primary, #2563eb) 10%, #fff);
  color: var(--color-jr-primary, #2563eb);
}

.jr-onboard-modules__svg {
  width: 1.125rem;
  height: 1.125rem;
}

.jr-onboard-modules__name {
  margin: 0 0 0.25rem;
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-jr-text, #111827);
}

.jr-onboard-modules__desc {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--color-jr-muted, #4b5563);
}

.jr-onboard-modules__badge {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-jr-success, #16a34a);
  white-space: nowrap;
}
</style>
