<template>
  <JRPage>
    <div class="jr-about">
      <div class="jr-about__toolbar">
        <LocaleToggle />
      </div>

      <section class="jr-about__hero" aria-labelledby="about-hero-title">
        <div class="jr-about__hero-main">
          <img
            :src="jobrhythmLogoUrl"
            alt="JobRhythm"
            class="jr-about__logo"
            width="240"
            height="60" />
          <span class="jr-about__kicker">{{ t("about.kicker") }}</span>
          <h1 id="about-hero-title" class="jr-about__title">
            {{ t("about.heroTitle") }}
          </h1>
          <p class="jr-about__lead">
            {{ t("about.heroText") }}
          </p>
        </div>
        <aside class="jr-about__hero-meta" aria-labelledby="about-meta-title">
          <h2 id="about-meta-title" class="jr-about__meta-title">
            {{ t("about.metaTitle") }}
          </h2>
          <ul class="jr-about__meta-list">
            <li v-for="item in metaItems" :key="item">
              {{ item }}
            </li>
          </ul>
        </aside>
      </section>

      <JRSection :title="t('about.modulesTitle')">
        <p class="jr-about__intro">
          {{ t("about.modulesIntro") }}
        </p>
        <div class="jr-about__module-grid">
          <article
            v-for="module in modules"
            :key="module.title"
            class="jr-about__module-card">
            <h3 class="jr-about__card-title">{{ module.title }}</h3>
            <p class="jr-about__card-copy">{{ module.description }}</p>
          </article>
        </div>
      </JRSection>

      <JRSection :title="t('about.flowTitle')">
        <p class="jr-about__intro">
          {{ t("about.flowIntro") }}
        </p>
        <ol class="jr-about__flow">
          <li
            v-for="(step, index) in operationalFlow"
            :key="step.title"
            class="jr-about__flow-step">
            <span class="jr-about__flow-index" aria-hidden="true">
              {{ index + 1 }}
            </span>
            <div class="jr-about__flow-body">
              <h3 class="jr-about__card-title">{{ step.title }}</h3>
              <p class="jr-about__card-copy">{{ step.description }}</p>
            </div>
          </li>
        </ol>
      </JRSection>

      <JRSection :title="t('about.valueTitle')">
        <div class="jr-about__value-grid">
          <article
            v-for="point in valuePoints"
            :key="point.title"
            class="jr-about__value-card">
            <h3 class="jr-about__card-title">{{ point.title }}</h3>
            <p class="jr-about__card-copy">{{ point.description }}</p>
          </article>
        </div>
      </JRSection>
    </div>
  </JRPage>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { JRPage, JRSection } from "@ui";
import LocaleToggle from "@/components/LocaleToggle.vue";

const { t, tm, locale } = useI18n({ useScope: "global" });
const base = import.meta.env.BASE_URL || "/";
const jobrhythmLogoUrl = `${base}img/jobrhythm-logo.png`;

const metaItems = computed(() => {
  void locale.value;
  return tm("about.metaItems") || [];
});
const modules = computed(() => {
  void locale.value;
  return tm("about.modules") || [];
});
const operationalFlow = computed(() => {
  void locale.value;
  return tm("about.operationalFlow") || [];
});
const valuePoints = computed(() => {
  void locale.value;
  return tm("about.valuePoints") || [];
});
</script>

<style scoped>
.jr-about {
  max-width: 71.25rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  text-align: left;
}

.jr-about__toolbar {
  display: flex;
  justify-content: flex-end;
}

.jr-about__hero {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

@media (min-width: 1024px) {
  .jr-about__hero {
    grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
    align-items: start;
    gap: 1.5rem;
  }
}

.jr-about__logo {
  display: block;
  max-width: 15rem;
  height: auto;
  margin-bottom: 0.75rem;
}

.jr-about__kicker {
  display: block;
  margin: 0 0 0.35rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

.jr-about__title {
  margin: 0 0 0.5rem;
  font-size: clamp(1.35rem, 2.2vw, 1.85rem);
  font-weight: 700;
  line-height: 1.25;
  color: var(--color-jr-text);
}

.jr-about__lead {
  margin: 0;
  max-width: 48ch;
  font-size: 1rem;
  line-height: 1.55;
  color: var(--color-jr-muted);
}

.jr-about__hero-meta {
  padding: 1rem;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

.jr-about__meta-title {
  margin: 0 0 0.65rem;
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-jr-text);
}

.jr-about__meta-list {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--color-jr-muted);
  font-size: 0.875rem;
  line-height: 1.5;
}

.jr-about__meta-list li + li {
  margin-top: 0.35rem;
}

.jr-about__intro {
  margin: 0 0 1rem;
  max-width: 62ch;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--color-jr-muted);
}

.jr-about__module-grid,
.jr-about__value-grid {
  display: grid;
  gap: 0.75rem;
}

@media (min-width: 768px) {
  .jr-about__module-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jr-about__value-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-about__module-card,
.jr-about__value-card {
  padding: 1rem;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

.jr-about__card-title {
  margin: 0 0 0.35rem;
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-jr-text);
}

.jr-about__card-copy {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-jr-muted);
}

.jr-about__flow {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.jr-about__flow-step {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.75rem;
  align-items: start;
  padding: 1rem;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

.jr-about__flow-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 999px;
  background: var(--color-jr-primary);
  color: #fff;
  font-size: 0.8125rem;
  font-weight: 700;
}

.jr-about__flow-body {
  min-width: 0;
}
</style>
