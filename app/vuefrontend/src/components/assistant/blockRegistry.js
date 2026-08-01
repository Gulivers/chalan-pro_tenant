import TextBlock from './blocks/TextBlock.vue';
import KpiBlock from './blocks/KpiBlock.vue';
import KpiGroupBlock from './blocks/KpiGroupBlock.vue';
import TableBlock from './blocks/TableBlock.vue';
import BarChartBlock from './blocks/BarChartBlock.vue';
import LineChartBlock from './blocks/LineChartBlock.vue';
import DonutChartBlock from './blocks/DonutChartBlock.vue';
import EntityLinkBlock from './blocks/EntityLinkBlock.vue';
import SourcesBlock from './blocks/SourcesBlock.vue';

/**
 * Fixed allowlist: block type → local Vue component.
 * Unknown types must never be rendered dynamically from payload strings.
 */
export const BLOCK_REGISTRY = Object.freeze({
  text: TextBlock,
  kpi: KpiBlock,
  kpi_group: KpiGroupBlock,
  table: TableBlock,
  bar_chart: BarChartBlock,
  line_chart: LineChartBlock,
  donut_chart: DonutChartBlock,
  entity_link: EntityLinkBlock,
  source: SourcesBlock,
});

export function resolveBlockComponent(type) {
  if (typeof type !== 'string') return null;
  return BLOCK_REGISTRY[type] || null;
}

/**
 * Lightweight edge validation before render.
 * @param {unknown} block
 * @returns {boolean}
 */
export function isValidBlockShape(block) {
  if (!block || typeof block !== 'object') return false;
  if (typeof block.type !== 'string' || !block.type) return false;
  if (typeof block.id !== 'string' || !block.id) return false;
  return true;
}
