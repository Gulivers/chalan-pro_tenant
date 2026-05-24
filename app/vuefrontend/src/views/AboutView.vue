<template>
  <section class="about-page py-">
    <div class="container">
      <div class="d-flex justify-content-end p-3">
        <div
          class="lang-toggle"
          role="group"
          :aria-label="copy[currentLang].langToggleLabel">
          <button
            type="button"
            class="lang-btn"
            :class="{ active: currentLang === 'es' }"
            @click="currentLang = 'es'">
            ES
          </button>
          <button
            type="button"
            class="lang-btn"
            :class="{ active: currentLang === 'en' }"
            @click="currentLang = 'en'">
            EN
          </button>
        </div>
      </div>

      <div class="hero-card p-4 p-md-5 mb-5">
        <div class="row align-items-center g-4">
          <div class="col-lg-8">
            <img
              :src="jobrithmLogoUrl"
              alt="JobRhythm"
              class="about-logo mb-2 mb-md-4"
              width="240"
              height="60" />
            <span class="kicker">{{ copy[currentLang].kicker }}</span>
            <h1 class="display-5 fw-bold mt-2 mb-3">
              {{ copy[currentLang].heroTitle }}
            </h1>
            <p class="lead mb-0">
              {{ copy[currentLang].heroText }}
            </p>
          </div>
          <div class="col-lg-4">
            <div class="hero-meta p-3 p-md-4">
              <h2 class="h5 fw-semibold mb-3">
                {{ copy[currentLang].metaTitle }}
              </h2>
              <ul class="meta-list mb-0">
                <li v-for="item in copy[currentLang].metaItems" :key="item">
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="content-block mb-5">
        <h2 class="section-title mb-3">{{ copy[currentLang].modulesTitle }}</h2>
        <p class="section-text mb-4">
          {{ copy[currentLang].modulesIntro }}
        </p>
        <div class="row g-3 g-md-4">
          <div
            class="col-md-6 col-xl-4"
            v-for="module in copy[currentLang].modules"
            :key="module.title">
            <article class="module-card h-100 p-4">
              <h3 class="h5 fw-semibold mb-2">{{ module.title }}</h3>
              <p class="mb-0">{{ module.description }}</p>
            </article>
          </div>
        </div>
      </div>

      <div class="content-block mb-5">
        <h2 class="section-title mb-3">{{ copy[currentLang].flowTitle }}</h2>
        <p class="section-text mb-4">
          {{ copy[currentLang].flowIntro }}
        </p>
        <div class="flow-grid">
          <article
            class="flow-step"
            v-for="(step, index) in copy[currentLang].operationalFlow"
            :key="step.title">
            <div class="flow-index">{{ index + 1 }}</div>
            <div>
              <h3 class="h6 fw-semibold mb-1">{{ step.title }}</h3>
              <p class="mb-0">{{ step.description }}</p>
            </div>
          </article>
        </div>
      </div>

      <div class="content-block">
        <h2 class="section-title mb-3">{{ copy[currentLang].valueTitle }}</h2>
        <div class="row g-3">
          <div
            class="col-md-4 p-3"
            v-for="point in copy[currentLang].valuePoints"
            :key="point.title">
            <article class="value-card h-100 p-4">
              <h3 class="h6 fw-semibold mb-2">{{ point.title }}</h3>
              <p class="mb-0">{{ point.description }}</p>
            </article>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";

const currentLang = ref("en");
const base = process.env.BASE_URL || "/";
const jobrithmLogoUrl = `${base}img/jobrithm-logo.png`;

const copy = {
  en: {
    langToggleLabel: "Language switch",
    kicker: "ABOUT JOBRITHM",
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
    kicker: "ACERCA DE JOBRITHM",
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
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap");

.about-page {
  font-family: "Montserrat", sans-serif;
  background: #f8fafc;
}

.container {
  max-width: 1140px;
}

.about-logo {
  display: block;
  width: min(100%, 240px);
  max-width: 240px;
  height: auto;
  object-fit: contain;
  margin-left: 0;
  margin-right: 0;
}

.lang-toggle {
  display: inline-flex;
  border: 1px solid #dbe5ff;
  border-radius: 10px;
  overflow: hidden;
  background: #ffffff;
}

.lang-btn {
  border: 0;
  background: transparent;
  color: #395ecb;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.4rem 0.7rem;
}

.lang-btn.active {
  background: #395ecb;
  color: #ffffff;
}

.kicker {
  display: block;
  margin-top: 0.35rem;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  font-weight: 700;
  color: #395ecb;
}

.hero-card {
  background: linear-gradient(135deg, #ffffff 0%, #f4f7ff 100%);
  border: 1px solid #dbe5ff;
  border-radius: 16px;
}

h1,
.section-title {
  color: #395ecb;
}

.lead,
.section-text {
  color: #495057;
  font-weight: 500;
}

.hero-meta {
  background: #ffffff;
  border: 1px solid #e6ecff;
  border-radius: 12px;
}

.meta-list {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.meta-list li {
  padding: 0.3rem 0;
  color: #4a4a4a;
  font-size: 0.95rem;
}

.module-card,
.value-card {
  background: #ffffff;
  border: 1px solid #e7ebf5;
  border-radius: 12px;
}

.module-card h3,
.value-card h3,
.flow-step h3 {
  color: #2f4fb2;
}

.module-card p,
.value-card p,
.flow-step p {
  color: #4a4a4a;
  font-size: 0.95rem;
}

.flow-grid {
  display: grid;
  gap: 12px;
}

.flow-step {
  display: grid;
  grid-template-columns: 40px 1fr;
  align-items: start;
  gap: 12px;
  background: #ffffff;
  border: 1px solid #e7ebf5;
  border-radius: 12px;
  padding: 14px 16px;
}

.flow-index {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #395ecb;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 700;
}

@media (max-width: 768px) {
  h1 {
    font-size: 1.9rem;
  }

  .about-logo {
    width: min(78vw, 220px);
    max-width: 220px;
    margin-left: auto;
    margin-right: auto;
  }
}
</style>
