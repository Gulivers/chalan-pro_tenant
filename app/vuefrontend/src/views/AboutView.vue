<template>
  <JRPage>
    <div class="jr-about">
      <div class="jr-about__toolbar">
        <div
          class="jr-about__lang"
          role="group"
          :aria-label="copy[currentLang].langToggleLabel">
          <button
            type="button"
            class="jr-about__lang-btn"
            :class="{ 'jr-about__lang-btn--active': currentLang === 'es' }"
            :aria-pressed="currentLang === 'es'"
            @click="currentLang = 'es'">
            ES
          </button>
          <button
            type="button"
            class="jr-about__lang-btn"
            :class="{ 'jr-about__lang-btn--active': currentLang === 'en' }"
            :aria-pressed="currentLang === 'en'"
            @click="currentLang = 'en'">
            EN
          </button>
        </div>
      </div>

      <section class="jr-about__hero" aria-labelledby="about-hero-title">
        <div class="jr-about__hero-main">
          <img
            :src="jobrhythmLogoUrl"
            alt="JobRhythm"
            class="jr-about__logo"
            width="240"
            height="60" />
          <span class="jr-about__kicker">{{ copy[currentLang].kicker }}</span>
          <h1 id="about-hero-title" class="jr-about__title">
            {{ copy[currentLang].heroTitle }}
          </h1>
          <p class="jr-about__lead">
            {{ copy[currentLang].heroText }}
          </p>
        </div>
        <aside class="jr-about__hero-meta" aria-labelledby="about-meta-title">
          <h2 id="about-meta-title" class="jr-about__meta-title">
            {{ copy[currentLang].metaTitle }}
          </h2>
          <ul class="jr-about__meta-list">
            <li v-for="item in copy[currentLang].metaItems" :key="item">
              {{ item }}
            </li>
          </ul>
        </aside>
      </section>

      <JRSection :title="copy[currentLang].modulesTitle">
        <p class="jr-about__intro">
          {{ copy[currentLang].modulesIntro }}
        </p>
        <div class="jr-about__module-grid">
          <article
            v-for="module in copy[currentLang].modules"
            :key="module.title"
            class="jr-about__module-card">
            <h3 class="jr-about__card-title">{{ module.title }}</h3>
            <p class="jr-about__card-copy">{{ module.description }}</p>
          </article>
        </div>
      </JRSection>

      <JRSection :title="copy[currentLang].flowTitle">
        <p class="jr-about__intro">
          {{ copy[currentLang].flowIntro }}
        </p>
        <ol class="jr-about__flow">
          <li
            v-for="(step, index) in copy[currentLang].operationalFlow"
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

      <JRSection :title="copy[currentLang].valueTitle">
        <div class="jr-about__value-grid">
          <article
            v-for="point in copy[currentLang].valuePoints"
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
import { ref } from "vue";
import { JRPage, JRSection } from "@ui";

const currentLang = ref("en");
const base = process.env.BASE_URL || "/";
const jobrhythmLogoUrl = `${base}img/jobrhythm-logo.png`;

const copy = {
  en: {
    langToggleLabel: "Language switch",
    kicker: "ABOUT JOBRHYTHM",
    heroTitle:
      "Construction Operations Platform for Residential Trade Contractors",
    heroText:
      "JobRhythm helps residential trade contractors centralize contracts, field operations, scheduling, inventory, and billing in one secure web platform.",
    metaTitle: "Built for teams that need control",
    metaItems: [
      "Office + field alignment",
      "Real-time operational visibility",
      "Standardized workflows",
      "Role-based security",
    ],
    modulesTitle: "Core platform modules",
    modulesIntro:
      "The platform is organized around the operational needs of residential trade contractors. Each module is connected, so your team can move faster with fewer manual handoffs.",
    modules: [
      {
        title: "Contract Management",
        description:
          "Manage bids, contract documents, revisions, and approvals with full traceability.",
      },
      {
        title: "Work Pricing",
        description:
          "Define and maintain trade pricing by builder, scope, and house model.",
      },
      {
        title: "Crew & Supervisor Scheduling",
        description:
          "Schedule field teams and supervisors using a visual calendar for faster coordination.",
      },
      {
        title: "Inventory Control",
        description:
          "Track stock, material movements, and warehouse balances in real time.",
      },
      {
        title: "Field Communication",
        description:
          "Coordinate office and field teams through contextual task communication.",
      },
      {
        title: "Notes & Job Documents",
        description:
          "Attach notes, photos, PDFs, and drawings to jobs and schedule events.",
      },
      {
        title: "Billing & Collections",
        description:
          "Connect completed work, contract scope, and billing records in one flow.",
      },
      {
        title: "Roles & Permissions",
        description:
          "Secure sensitive operations with role-based access by user and team.",
      },
    ],
    flowTitle: "Operational flow",
    flowIntro:
      "A clear sequence from planning to closeout gives your office and field teams a repeatable process.",
    operationalFlow: [
      {
        title: "Plan",
        description:
          "Create contract scope, define pricing, and prepare job documentation.",
      },
      {
        title: "Schedule",
        description:
          "Assign crews, supervisors, and equipment based on project priorities.",
      },
      {
        title: "Execute",
        description:
          "Run field activities with task context, notes, and real-time communication.",
      },
      {
        title: "Control",
        description:
          "Monitor inventory usage, progress status, and operational bottlenecks.",
      },
      {
        title: "Bill & Close",
        description:
          "Generate billing records and close jobs with complete operational history.",
      },
    ],
    valueTitle: "Why teams choose JobRhythm",
    valuePoints: [
      {
        title: "Single source of truth",
        description:
          "Contracts, schedules, inventory, and billing data stay synchronized.",
      },
      {
        title: "Faster decisions",
        description:
          "Operational visibility helps managers resolve issues before they impact delivery.",
      },
      {
        title: "Scalable operations",
        description:
          "Standardized workflows make it easier to grow teams without losing control.",
      },
    ],
  },
  es: {
    langToggleLabel: "Cambio de idioma",
    kicker: "ACERCA DE JOBRHYTHM",
    heroTitle:
      "Plataforma de Operaciones de Construccion para Contratistas Residenciales",
    heroText:
      "JobRhythm ayuda a los contratistas residenciales a centralizar contratos, operaciones de campo, programacion, inventario y facturacion en una sola plataforma web segura.",
    metaTitle: "Diseñado para equipos que necesitan control",
    metaItems: [
      "Alineacion entre oficina y campo",
      "Visibilidad operativa en tiempo real",
      "Flujos de trabajo estandarizados",
      "Seguridad basada en roles",
    ],
    modulesTitle: "Modulos principales de la plataforma",
    modulesIntro:
      "La plataforma esta organizada para las necesidades operativas de los contratistas residenciales. Cada modulo se conecta con los demas para que tu equipo avance mas rapido y con menos reprocesos.",
    modules: [
      {
        title: "Gestion de contratos",
        description:
          "Administra ofertas, documentos contractuales, revisiones y aprobaciones con trazabilidad total.",
      },
      {
        title: "Gestion de precios de trabajo",
        description:
          "Define y mantiene precios por builder, alcance y modelo de casa.",
      },
      {
        title: "Programacion de cuadrillas y supervisores",
        description:
          "Programa equipos de campo y supervisores con un calendario visual para coordinar mejor.",
      },
      {
        title: "Control de inventario",
        description:
          "Monitorea existencias, movimientos de materiales y saldos por almacen en tiempo real.",
      },
      {
        title: "Comunicacion de campo",
        description:
          "Coordina oficina y campo con comunicacion contextual por tarea.",
      },
      {
        title: "Notas y documentos de obra",
        description:
          "Adjunta notas, fotos, PDFs y planos a trabajos y eventos programados.",
      },
      {
        title: "Facturacion y cobros",
        description:
          "Conecta trabajo ejecutado, alcance contractual y registros de facturacion en un solo flujo.",
      },
      {
        title: "Roles y permisos",
        description:
          "Protege operaciones sensibles con control de acceso por rol y por usuario.",
      },
    ],
    flowTitle: "Flujo operativo",
    flowIntro:
      "Una secuencia clara desde la planeacion hasta el cierre permite a oficina y campo trabajar con un proceso repetible.",
    operationalFlow: [
      {
        title: "Planificar",
        description:
          "Define alcance contractual, precios y documentacion inicial del trabajo.",
      },
      {
        title: "Programar",
        description:
          "Asigna cuadrillas, supervisores y equipos segun prioridades del proyecto.",
      },
      {
        title: "Ejecutar",
        description:
          "Gestiona actividades de campo con contexto de tarea, notas y comunicacion en tiempo real.",
      },
      {
        title: "Controlar",
        description:
          "Monitorea uso de inventario, avance y cuellos de botella operativos.",
      },
      {
        title: "Facturar y cerrar",
        description:
          "Genera registros de facturacion y cierra trabajos con historial operativo completo.",
      },
    ],
    valueTitle: "Por que los equipos eligen JobRhythm",
    valuePoints: [
      {
        title: "Una sola fuente de verdad",
        description:
          "Contratos, programacion, inventario y facturacion permanecen sincronizados.",
      },
      {
        title: "Decisiones mas rapidas",
        description:
          "La visibilidad operativa ayuda a resolver problemas antes de impactar la entrega.",
      },
      {
        title: "Operacion escalable",
        description:
          "Los flujos estandarizados facilitan crecer el equipo sin perder control.",
      },
    ],
  },
};
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

.jr-about__lang {
  display: inline-flex;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
}

.jr-about__lang-btn {
  border: 0;
  background: transparent;
  color: var(--color-jr-primary);
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.3;
  padding: 0.4rem 0.7rem;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.jr-about__lang-btn:hover {
  background: var(--color-jr-surface-muted);
}

.jr-about__lang-btn:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
  z-index: 1;
}

.jr-about__lang-btn--active {
  background: var(--color-jr-primary);
  color: #ffffff;
}

.jr-about__lang-btn--active:hover {
  background: var(--color-jr-primary-hover);
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
    padding: 1.5rem 1.75rem;
  }
}

.jr-about__logo {
  display: block;
  width: min(100%, 15rem);
  max-width: 15rem;
  height: auto;
  object-fit: contain;
}

.jr-about__kicker {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  font-weight: 600;
  color: var(--color-jr-primary);
}

.jr-about__title {
  margin: 0.5rem 0 0.75rem;
  font-size: 1.3125rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--color-jr-text);
}

@media (min-width: 768px) {
  .jr-about__title {
    font-size: 1.75rem;
  }
}

.jr-about__lead {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-about__hero-meta {
  padding: 1rem 1.25rem;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
}

.jr-about__meta-title {
  margin: 0 0 0.75rem;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-about__meta-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.jr-about__meta-list li {
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-jr-muted);
}

.jr-about__intro {
  margin: 0 0 1rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-about__module-grid {
  display: grid;
  gap: 0.75rem;
}

@media (min-width: 768px) {
  .jr-about__module-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
}

@media (min-width: 1200px) {
  .jr-about__module-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-about__module-card,
.jr-about__value-card {
  padding: 1rem 1.25rem;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
}

.jr-about__card-title {
  margin: 0 0 0.35rem;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-about__card-copy {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-about__flow {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.75rem;
}

.jr-about__flow-step {
  display: grid;
  grid-template-columns: 2rem 1fr;
  align-items: start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
}

.jr-about__flow-index {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-jr-primary);
  color: #ffffff;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1;
}

.jr-about__flow-body {
  min-width: 0;
}

.jr-about__value-grid {
  display: grid;
  gap: 0.75rem;
}

@media (min-width: 768px) {
  .jr-about__value-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
  }
}

@media (max-width: 767px) {
  .jr-about__logo {
    margin-inline: auto;
  }

  .jr-about__kicker,
  .jr-about__title,
  .jr-about__lead {
    text-align: center;
  }
}
</style>
