import { computed } from 'vue';
import { useRoute } from 'vue-router';

/**
 * Derive a minimal Assistant context from the current vue-router route.
 * Sends canonical IDs only — never DOM text or invented paths.
 *
 * @returns {{ context: import('vue').ComputedRef<object>, contextLabel: import('vue').ComputedRef<string> }}
 */
export function useAssistantContext() {
  const route = useRoute();

  const context = computed(() => {
    const routeName = typeof route.name === 'string' ? route.name : null;
    const view = routeName || (route.path ? route.path.replace(/^\//, '').split('/')[0] || null : null);

    let entityType = null;
    let entityId = null;

    if (routeName === 'transactions-form' || route.path.startsWith('/transactions/form')) {
      const rawId = route.query?.id ?? route.params?.id;
      const parsed = parsePositiveInt(rawId);
      if (parsed != null) {
        entityType = 'document';
        entityId = parsed;
      }
    } else if (routeName === 'builder-view' || /^\/builder\/view\//.test(route.path)) {
      const parsed = parsePositiveInt(route.params?.id);
      if (parsed != null) {
        entityType = 'builder';
        entityId = parsed;
      }
    }

    return {
      view: view || null,
      route_name: routeName,
      entity_type: entityType,
      entity_id: entityId,
    };
  });

  const contextLabel = computed(() => {
    const ctx = context.value;
    const parts = [];
    if (ctx.route_name) parts.push(ctx.route_name);
    else if (ctx.view) parts.push(ctx.view);
    if (ctx.entity_type && ctx.entity_id) {
      parts.push(`${ctx.entity_type} #${ctx.entity_id}`);
    }
    return parts.length ? parts.join(' · ') : 'No page entity';
  });

  return { context, contextLabel };
}

function parsePositiveInt(value) {
  if (value == null || value === '') return null;
  const n = Number.parseInt(String(value), 10);
  if (!Number.isFinite(n) || n < 1) return null;
  return n;
}
