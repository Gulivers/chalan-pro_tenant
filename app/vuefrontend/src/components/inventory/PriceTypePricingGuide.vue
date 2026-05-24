<template>
  <!-- Price Type: purchase-cost pricing guide (presentational only) -->
  <div class="alert alert-light border shadow-sm mt-4 price-type-pricing-guide" role="note">
    <div class="d-flex gap-2 gap-md-3">
      <i class="bi bi-calculator flex-shrink-0 mt-1 text-primary fs-5" aria-hidden="true"></i>
      <div class="min-w-0">
        <div class="fw-semibold text-body mb-2">Pricing from purchase cost</div>
        <p class="text-secondary small mb-2 mb-md-3">
          On sales documents, when a line uses this price type, JobRhythm can set the
          <strong>unit sale price</strong> from the product’s
          <strong>purchase unit cost</strong>
          (from the active purchase <code class="small">ProductPrice</code> for the line’s unit). Choose
          <strong>None</strong> to use list/catalog prices without deriving from cost.
        </p>
        <div class="border-start border-3 border-primary-subtle ps-3 mb-3 mb-md-4 small">
          <strong class="text-body d-block mb-2">Which product price does JobRhythm use?</strong>
          <p class="mb-2 text-body-secondary">
            <strong class="text-body">If you use Markup or Margin (cost-based):</strong>
            JobRhythm looks up prices in your inventory marked as <strong>purchase</strong> prices
            (<code class="small">is_purchase=True</code> on <code class="small">ProductPrice</code>). That
            <strong>unit cost</strong> is what the sale price formula uses.
          </p>
          <p class="mb-0 text-body-secondary">
            <strong class="text-body">If you choose None (list price only):</strong>
            JobRhythm does <strong>not</strong> use what you paid for the item (purchase cost) to set the price
            under the cost-based rule. Instead, it uses prices marked <strong>for sale</strong>
            (<code class="small">is_sale=True</code>) from your <strong>catalog</strong>.
          </p>
        </div>
        <ul class="small text-body-secondary mb-3 mb-md-4 ps-3 pricing-rules-list">
          <li class="mb-2">
            <strong class="text-body">None (list price only)</strong> — No markup/margin formula on purchase cost;
            sale price comes from catalog rows flagged for sale (<code class="small">is_sale=True</code>).
          </li>
          <li class="mb-2">
            <strong class="text-body">Markup % on cost</strong> — Sale price = cost × (1 + <em>p</em>/100).
            Example: cost <strong>100</strong>, <em>p</em> = <strong>25%</strong> → <strong>125</strong>.
          </li>
          <li class="mb-2">
            <strong class="text-body">Margin % on cost</strong> — Sale price = cost ÷ (1 − <em>p</em>/100), with
            <em>p</em> &lt; 100. Same numbers for comparison: cost <strong>100</strong>,
            <em>p</em> = <strong>25%</strong> → <strong>≈ 133.33</strong> (100 ÷ 0.75).
            <span class="d-block text-body-secondary mt-1">
              <em>Why higher than markup?</em> With the same <em>p</em>, margin is the percentage of the
              <strong>sale price</strong> that is profit—not of cost—so the formula backs cost out of that
              revenue share and yields a higher price than adding <em>p</em>% on top of cost.
            </span>
          </li>
        </ul>
        <div class="border-top pt-2 pt-md-3 mt-2">
          <div class="fw-semibold text-body small mb-1">Markup / margin % (0–100)</div>
          <p class="small text-secondary mb-0">
            Required when <strong>Markup</strong> or <strong>Margin</strong> is selected. Enter the percentage
            <em>p</em> used in the formula above (non‑negative; margin must be &lt; 100). Not used when
            <strong>None</strong> is selected.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PriceTypePricingGuide'
}
</script>

<style scoped>
.pricing-rules-list li {
  line-height: 1.45;
}
</style>
