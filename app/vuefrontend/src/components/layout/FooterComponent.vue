<template>
  <footer class="app-footer border-top">
    <div class="container py-4 py-md-4">
      <div class="row align-items-start gy-4 text-center text-lg-start">
        <!-- Marca: logo tenant o JobRhythm por defecto -->
        <div class="col-12 col-lg-3">
          <div
            class="d-flex flex-column align-items-center align-items-lg-start gap-2">
            <router-link
              to="/"
              class="footer-brand-link d-inline-block"
              :aria-label="footerLogoAlt">
              <img
                :src="footerLogoSrc"
                :alt="footerLogoAlt"
                class="footer-brand-logo"
                height="44"
                width="180"
                loading="lazy"
                @error="onTenantLogoError" />
            </router-link>
            <span
              v-if="tenantName && tenantLogoUrl && !tenantLogoFailed"
              class="small text-muted text-truncate"
              style="max-width: 280px">
              {{ tenantName }}
            </span>
          </div>
        </div>

        <!-- Operational Flow: tarjetas con hover (solo con barra de navegación) -->
        <div class="col-12 col-lg-9">
          <nav
            v-if="!$route.meta.hideNavbar"
            class="footer-operational-flow"
            aria-label="Operational flow">
            <h2 class="footer-flow-title text-uppercase">Operational Flow</h2>
            <div
              class="d-flex flex-column flex-lg-row align-items-center justify-content-center flex-wrap gap-2 gap-lg-1">
              <template
                v-for="(step, idx) in operationalFlowSteps"
                :key="step.route">
                <router-link
                  :to="step.route"
                  class="footer-flow-card"
                  active-class="footer-flow-card--active">
                  <div class="footer-flow-card-inner">
                    <i
                      class="bi footer-flow-icon"
                      :class="step.icon"
                      aria-hidden="true" />
                    <span class="footer-flow-label">{{ step.label }}</span>
                  </div>
                </router-link>
                <span
                  v-if="idx < operationalFlowSteps.length - 1"
                  class="footer-flow-sep text-muted flex-shrink-0"
                  aria-hidden="true">
                  <i class="bi bi-chevron-right d-none d-lg-inline fs-5" />
                  <i class="bi bi-chevron-down d-lg-none fs-6" />
                </span>
              </template>
            </div>
          </nav>
          <p
            v-else
            class="my-3 small text-muted mb-0 mx-auto mx-lg-5"
            style="max-width: auto">
            Operations platform for residential trade contractors. Sign in to
            access your workspace.
          </p>
        </div>
      </div>

      <div
        class="row mt-4 pt-3 border-top border-secondary-subtle footer-meta text-center text-muted small">
        <div
          class="col-12 d-flex flex-column flex-sm-row flex-wrap align-items-center justify-content-center gap-2 gap-sm-3">
          <span>
            © {{ currentYear }}
            <strong class="text-body-secondary">JobRhythm</strong>
            . All rights reserved.
          </span>
          <span
            class="footer-meta-sep d-none d-sm-inline opacity-50"
            aria-hidden="true">
            ·
          </span>
          <span class="font-monospace">v{{ appVersion }}</span>
          <span
            class="footer-meta-sep d-none d-sm-inline opacity-50"
            aria-hidden="true">
            ·
          </span>
          <span>
            <span class="text-muted">Support:</span>
            <a
              href="mailto:team@jobrhythm.net"
              class="footer-support-email ms-1">
              team@jobrhythm.net
            </a>
          </span>
          <span
            class="footer-meta-sep d-none d-sm-inline opacity-50"
            aria-hidden="true">
            ·
          </span>
          <span
            class="d-inline-flex align-items-center gap-1 justify-content-center">
            <i
              class="bi bi-telephone-fill footer-contact-icon"
              aria-hidden="true" />
            <span>+1 (239) 240-0016</span>
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: "FooterComponent",
  data() {
    return {
      currentYear: new Date().getFullYear(),
      appVersion: "2.0.1",
      tenantLogoUrl: null,
      tenantName: null,
      tenantLogoFailed: false,
      /** Secuencia del flujo operativo (orden de uso) */
      operationalFlowSteps: [
        {
          label: "Schedule",
          route: "/schedule",
          icon: "bi-calendar-week",
        },
        {
          label: "Prepare Material Packing",
          route: "/transactions",
          icon: "bi-box-seam",
        },
        {
          label: "Piece Work Contract",
          route: "/contracts",
          icon: "bi-file-earmark-richtext",
        },
        {
          label: "Track Job Communication",
          route: "/chat-general",
          icon: "bi-chat-left-text",
        },
        {
          label: "Measure the Operation",
          route: "/inventory-dashboard",
          icon: "bi-speedometer2",
        },
      ],
    };
  },
  computed: {
    jobrhythmLogoUrl() {
      const base = process.env.BASE_URL || "/";
      return `${base}img/jobrhythm-logo.png`;
    },
    footerLogoSrc() {
      if (this.tenantLogoFailed) {
        return this.jobrhythmLogoUrl;
      }
      return this.tenantLogoUrl || this.jobrhythmLogoUrl;
    },
    footerLogoAlt() {
      return this.tenantName || "JobRhythm";
    },
  },
  mounted() {
    this.loadFooterBranding();
  },
  watch: {
    $route() {
      this.loadFooterBranding();
    },
  },
  methods: {
    loadFooterBranding() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        this.tenantLogoUrl = null;
        this.tenantName = null;
        this.tenantLogoFailed = false;
        return;
      }
      this.getAuthenticatedUser().then((user) => {
        if (user) {
          this.tenantLogoUrl = user.tenant_logo_url || null;
          this.tenantName = user.tenant_name || null;
          this.tenantLogoFailed = false;
        }
      });
    },
    onTenantLogoError() {
      if (this.tenantLogoUrl) {
        this.tenantLogoFailed = true;
      }
    },
  },
};
</script>

<style scoped>
.app-footer {
  background: linear-gradient(180deg, #f8f9fb 0%, #eef1f5 100%);
  color: #374151;
}

.footer-brand-link {
  text-decoration: none;
  line-height: 0;
}

.footer-brand-logo {
  height: auto;
  max-height: 44px;
  width: auto;
  max-width: min(200px, 70vw);
  display: block;
  object-fit: contain;
}

.footer-support-email {
  color: #c08500;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.15s ease, text-decoration 0.15s ease;
}

.footer-support-email:hover {
  color: #92400e;
  text-decoration: underline;
}

.footer-operational-flow {
  width: 100%;
}

.footer-flow-title {
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #c08500;
  margin-bottom: 0.875rem;
  text-align: center;
}

.footer-flow-card {
  flex: 1 1 118px;
  max-width: 220px;
  min-width: min(118px, 100%);
  text-decoration: none;
  color: inherit;
  border-radius: 0.65rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease,
    background-color 0.2s ease;
}

.footer-flow-card:focus-visible {
  outline: 2px solid #1e40af;
  outline-offset: 2px;
}

.footer-flow-card-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem;
  padding: 0.65rem 0.6rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.65rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
  min-height: 5.5rem;
}

.footer-flow-card:hover .footer-flow-card-inner {
  border-color: #93c5fd;
  box-shadow: 0 8px 20px rgba(30, 64, 175, 0.12),
    0 2px 6px rgba(15, 23, 42, 0.08);
  transform: translateY(-3px);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.footer-flow-card--active .footer-flow-card-inner {
  border-color: #c08500;
  background: linear-gradient(180deg, #fffbeb 0%, #fef3c7 100%);
  box-shadow: 0 2px 8px rgba(180, 83, 9, 0.15);
}

.footer-flow-icon {
  font-size: 1.35rem;
  color: #1e40af;
}

.footer-flow-card--active .footer-flow-icon {
  color: #b45309;
}

.footer-flow-label {
  font-size: 0.7rem;
  font-weight: 600;
  line-height: 1.25;
  text-align: center;
  color: #334155;
}

.footer-flow-card:hover .footer-flow-label {
  color: #1e3a8a;
}

.footer-flow-sep {
  opacity: 0.45;
  padding: 0.15rem 0;
}

@media (min-width: 992px) {
  .footer-flow-sep {
    padding: 0 0.15rem;
  }
}

/* Móvil: flujo como lista de enlaces de texto (sin tarjeta ni iconos) */
@media (max-width: 767.98px) {
  .footer-flow-title {
    margin-bottom: 0.5rem;
    font-size: 0.625rem;
  }

  .footer-flow-card {
    flex: 1 1 auto !important;
    max-width: none !important;
    min-width: 0 !important;
    width: 100%;
  }

  .footer-flow-card-inner {
    flex-direction: row !important;
    justify-content: center !important;
    align-items: center !important;
    min-height: 0 !important;
    padding: 0.2rem 0.25rem !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    gap: 0 !important;
  }

  .footer-flow-icon {
    display: none !important;
  }

  .footer-flow-label {
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    text-align: center !important;
    line-height: 1.3 !important;
  }

  .footer-flow-card:hover .footer-flow-card-inner {
    transform: none !important;
    box-shadow: none !important;
    background: transparent !important;
  }

  .footer-flow-card:hover .footer-flow-label {
    color: #1e40af !important;
    text-decoration: underline;
  }

  .footer-flow-card--active .footer-flow-card-inner {
    background: transparent !important;
    box-shadow: none !important;
  }

  .footer-flow-card--active .footer-flow-label {
    color: #b45309 !important;
    font-weight: 700 !important;
  }

  .footer-flow-sep {
    padding: 0.05rem 0 !important;
    opacity: 0.35;
  }

  .footer-meta {
    font-size: 0.75rem !important;
    line-height: 1.45;
  }

  .footer-meta .footer-meta-sep {
    display: none !important;
  }
}

.footer-contact-icon {
  color: #c08500;
  font-size: 1rem;
}

.footer-meta {
  font-size: 0.8125rem;
}
</style>
