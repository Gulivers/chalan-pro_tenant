import { shallowRef, watch, nextTick, onUnmounted } from 'vue';

/**
 * Renders a Chart.js instance only when:
 * - not loading (canvas is in the DOM; charts use v-if="loading")
 * - data is available
 * - the canvas container has a non-zero layout size (avoids blank charts in hidden tabs)
 *
 * Also observes container size so charts recover when a tab/details becomes visible
 * after the initial render window (e.g. Suppliers tab behind v-show).
 */
export function useDashboardChart({ isLoading, hasData, getCanvas, buildChart }) {
  const chartInstance = shallowRef(null);
  let retryTimer = null;
  let renderGeneration = 0;
  let resizeObserver = null;
  let observedEl = null;
  let lastObservedWidth = 0;
  let lastObservedHeight = 0;

  const destroyChart = () => {
    if (chartInstance.value) {
      try {
        chartInstance.value.destroy();
      } catch (_) {
        /* ignore */
      }
      chartInstance.value = null;
    }
  };

  const clearRetry = () => {
    if (retryTimer != null) {
      clearTimeout(retryTimer);
      retryTimer = null;
    }
  };

  const disconnectObserver = () => {
    if (resizeObserver) {
      try {
        resizeObserver.disconnect();
      } catch (_) {
        /* ignore */
      }
      resizeObserver = null;
      observedEl = null;
      lastObservedWidth = 0;
      lastObservedHeight = 0;
    }
  };

  const ensureObserver = () => {
    if (typeof ResizeObserver === 'undefined') return;
    const canvas = getCanvas();
    const el = canvas?.parentElement;
    if (!el) return;
    if (observedEl === el) return;

    disconnectObserver();
    observedEl = el;
    lastObservedWidth = el.clientWidth ?? 0;
    lastObservedHeight = el.clientHeight ?? 0;
    resizeObserver = new ResizeObserver(() => {
      const width = el.clientWidth ?? 0;
      const height = el.clientHeight ?? 0;
      const wasHidden = lastObservedWidth < 2 || lastObservedHeight < 2;
      const isVisible = width >= 2 && height >= 2;
      lastObservedWidth = width;
      lastObservedHeight = height;

      if (!isVisible) return;

      if (wasHidden || !chartInstance.value) {
        scheduleRender();
        return;
      }

      try {
        chartInstance.value.resize();
      } catch (_) {
        scheduleRender();
      }
    });
    resizeObserver.observe(el);
  };

  const scheduleRender = (retryCount = 0) => {
    clearRetry();
    const generation = ++renderGeneration;

    const run = async () => {
      if (generation !== renderGeneration) return;

      if (isLoading()) {
        destroyChart();
        return;
      }

      if (!hasData()) {
        destroyChart();
        return;
      }

      await nextTick();
      if (generation !== renderGeneration) return;

      const canvas = getCanvas();
      if (!canvas) {
        if (retryCount < 15) {
          retryTimer = setTimeout(() => scheduleRender(retryCount + 1), 50);
        }
        return;
      }

      ensureObserver();

      const container = canvas.parentElement;
      const width = container?.clientWidth ?? 0;
      const height = container?.clientHeight ?? 0;
      if (width < 2 || height < 2) {
        // Keep retrying briefly; ResizeObserver covers late visibility.
        if (retryCount < 25) {
          retryTimer = setTimeout(() => scheduleRender(retryCount + 1), 100);
        }
        return;
      }

      destroyChart();
      try {
        chartInstance.value = buildChart(canvas);
        requestAnimationFrame(() => {
          if (generation !== renderGeneration) return;
          try {
            chartInstance.value?.resize();
          } catch (_) {
            /* ignore */
          }
        });
      } catch (error) {
        destroyChart();
        if (retryCount < 5) {
          retryTimer = setTimeout(() => scheduleRender(retryCount + 1), 200);
        } else {
          console.warn('Dashboard chart render failed:', error);
        }
      }
    };

    retryTimer = setTimeout(run, 0);
  };

  watch(
    () => [isLoading(), hasData()],
    () => scheduleRender(),
    { immediate: true }
  );

  onUnmounted(() => {
    renderGeneration += 1;
    clearRetry();
    disconnectObserver();
    destroyChart();
  });

  return {
    chartInstance,
    scheduleRender,
    destroyChart,
  };
}
