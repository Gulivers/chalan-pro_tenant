<template>
  <!-- Price Type: purchase-cost pricing guide (presentational only) -->
  <div class="jr-catalog-note" role="note">
    <p class="jr-catalog-note__title">Pricing from purchase cost</p>
    <p>
      On sales documents, when a line uses this price type, JobRhythm can set the
      unit sale price from the product’s purchase unit cost (the active purchase
      price for the line’s unit). Choose None to use list/catalog prices without
      deriving from cost.
    </p>
    <p>
      <strong>Markup or Margin:</strong>
      JobRhythm uses inventory prices marked as purchase prices. That unit cost
      feeds the sale price formula.
    </p>
    <p>
      <strong>None (list price only):</strong>
      JobRhythm does not use purchase cost. It uses catalog prices marked for sale.
    </p>
    <ul class="jr-catalog-note__list">
      <li>
        <strong>None</strong> — No markup/margin formula; sale price from
        sale-flagged catalog rows.
      </li>
      <li>
        <strong>Markup % on cost</strong> — Sale = cost × (1 + p/100). Example: cost
        100, p = 25% → 125.
      </li>
      <li>
        <strong>Margin % on cost</strong> — Sale = cost ÷ (1 − p/100), with p &lt; 100.
        Same numbers: cost 100, p = 25% → ≈ 133.33. Margin is profit as a share of
        sale price, so the same p yields a higher price than markup.
      </li>
    </ul>
    <p>
      <strong>Markup / margin % (0–100)</strong>
      — Required when Markup or Margin is selected. Enter percentage p (non-negative;
      margin must be &lt; 100). Not used when None is selected.
    </p>
  </div>
</template>

<script>
export default {
  name: "PriceTypePricingGuide",
};
</script>

<style scoped>
.jr-catalog-note {
  margin: 0;
  padding: 0.65rem 0.75rem;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-jr-text, #111827);
  background: var(--color-jr-surface-muted, #f9fafb);
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

.jr-catalog-note__title {
  margin: 0 0 0.35rem;
  font-size: 0.8125rem;
  font-weight: 600;
}

.jr-catalog-note p {
  margin: 0 0 0.35rem;
}

.jr-catalog-note p:last-child {
  margin-bottom: 0;
}

.jr-catalog-note__list {
  margin: 0 0 0.35rem;
  padding-left: 1.1rem;
}

.jr-catalog-note__list li {
  margin-bottom: 0.25rem;
  line-height: 1.45;
}

.jr-catalog-note__list li:last-child {
  margin-bottom: 0;
}
</style>
