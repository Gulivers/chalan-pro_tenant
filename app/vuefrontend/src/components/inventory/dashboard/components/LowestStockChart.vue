<template>
  <div class="jr-chart-block">
    <div v-if="loading" class="jr-dash-state" aria-live="polite">Loading…</div>

    <JREmptyState
      v-else-if="products.length === 0"
      title="No stock data available"
      description="There is no stock data to chart right now."
    />

    <div v-else>
      <div class="jr-chart-controls">
        <p class="jr-chart-controls__hint">
          Lowest {{ displayCount }} products by on-hand quantity
        </p>
        <JRButton variant="secondary" size="sm" type="button" @click="refreshChart">
          Refresh
        </JRButton>
      </div>

      <div class="jr-chart-container">
        <canvas
          ref="chartCanvas"
          role="img"
          :aria-label="`Bar chart of the ${displayCount} products with the lowest on-hand stock`"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, watch, computed } from 'vue';
import { Chart, registerables } from 'chart.js';
import { JRButton, JREmptyState } from '@ui';
import { useDashboardChart } from './useDashboardChart';
import { getStockQty, getReorderLevel, getStockStatus, stockStatusLabel } from './stockStatus';

Chart.register(...registerables);

const STATUS_COLOR = {
  critical: 'rgba(185, 28, 28, 0.85)',
  out: 'rgba(185, 28, 28, 0.7)',
  low: 'rgba(180, 83, 9, 0.8)',
  healthy: 'rgba(21, 128, 61, 0.8)',
};

const STATUS_BORDER = {
  critical: 'rgba(185, 28, 28, 1)',
  out: 'rgba(185, 28, 28, 1)',
  low: 'rgba(180, 83, 9, 1)',
  healthy: 'rgba(21, 128, 61, 1)',
};

export default defineComponent({
  components: { JRButton, JREmptyState },
  name: 'LowestStockChart',
  props: {
    products: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['refresh', 'product-clicked'],
  setup(props, { emit }) {
    const chartCanvas = ref(null);

    const displayCount = computed(() => Math.min(props.products.length, 25));

    const { scheduleRender } = useDashboardChart({
      isLoading: () => props.loading,
      hasData: () => Array.isArray(props.products) && props.products.length > 0,
      getCanvas: () => chartCanvas.value,
      buildChart: (canvas) => {
        const topProducts = props.products.slice(0, 25);
        const labels = topProducts.map((p) =>
          p.name.length > 25 ? `${p.name.substring(0, 25)}…` : p.name
        );
        const data = topProducts.map((p) => getStockQty(p));
        const backgroundColors = topProducts.map((p) => STATUS_COLOR[getStockStatus(p)]);
        const borderColors = topProducts.map((p) => STATUS_BORDER[getStockStatus(p)]);

        return new Chart(canvas, {
          type: 'bar',
          data: {
            labels,
            datasets: [
              {
                label: 'On hand',
                data,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            animation: { duration: 0 },
            plugins: {
              title: { display: false },
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label(context) {
                    const product = topProducts[context.dataIndex];
                    const status = getStockStatus(product);
                    return [
                      `SKU: ${product.sku}`,
                      `On hand: ${getStockQty(product)}`,
                      `Reorder: ${getReorderLevel(product)}`,
                      `Status: ${stockStatusLabel(status)}`,
                    ];
                  },
                },
              },
            },
            scales: {
              x: {
                beginAtZero: true,
                title: { display: true, text: 'On hand' },
              },
              y: {
                title: { display: true, text: 'Products' },
              },
            },
            onClick(_event, elements) {
              if (elements.length > 0) {
                emit('product-clicked', topProducts[elements[0].index]);
              }
            },
          },
        });
      },
    });

    watch(
      () => props.products,
      () => scheduleRender(),
      { deep: true }
    );

    const refreshChart = () => {
      emit('refresh');
      scheduleRender();
    };

    return {
      chartCanvas,
      displayCount,
      refreshChart,
    };
  },
});
</script>

<style scoped>
.jr-chart-block {
  min-height: 0;
}

.jr-dash-state {
  padding: 0.75rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-chart-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.jr-chart-controls__hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-chart-container {
  position: relative;
  height: 360px;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  padding: 0.85rem;
}

.jr-chart-container canvas {
  display: block;
  max-width: 100%;
}

@media (max-width: 767.98px) {
  .jr-chart-container {
    height: 280px;
    padding: 0.65rem;
  }
}
</style>
