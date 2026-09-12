<template>
  <footer class="jr-footer">
    <div class="jr-footer__inner">
      <div class="jr-footer__main">
        <div class="jr-footer__brand">
          <router-link
            to="/"
            class="jr-footer__brand-link"
            :aria-label="footerLogoAlt">
            <img
              :src="footerLogoSrc"
              :alt="footerLogoAlt"
              class="jr-footer__brand-logo"
              height="36"
              width="148"
              loading="lazy"
              @error="onTenantLogoError" />
          </router-link>
          <p
            v-if="tenantName && tenantLogoUrl && !tenantLogoFailed"
            class="jr-footer__tenant-name">
            {{ tenantName }}
          </p>
        </div>

        <div class="jr-footer__content">
          <nav
            v-if="!$route.meta.hideNavbar"
            class="jr-footer__flow"
            aria-label="Operational flow">
            <header class="jr-footer__flow-header">
              <h2 class="jr-footer__flow-title">Operational flow</h2>
              <p class="jr-footer__flow-lead">
                Follow these steps in order.
              </p>
            </header>

            <ol class="jr-footer__steps">
              <li
                v-for="(step, index) in operationalFlowSteps"
                :key="step.route"
                class="jr-footer__step">
                <router-link
                  :to="step.route"
                  class="jr-footer__step-link"
                  active-class="jr-footer__step-link--active"
                  :aria-label="`Step ${index + 1}: ${step.label}`"
                  :aria-current="
                    isActiveRoute(step.route) ? 'page' : undefined
                  ">
                  <span class="jr-footer__step-index" aria-hidden="true">
                    {{ index + 1 }}
                  </span>
                  <span class="jr-footer__step-icon-wrap" aria-hidden="true">
                    <component :is="step.icon" class="jr-footer__step-icon" />
                  </span>
                  <span class="jr-footer__step-label">{{ step.label }}</span>
                </router-link>
                <span
                  v-if="index < operationalFlowSteps.length - 1"
                  class="jr-footer__step-connector"
                  aria-hidden="true">
                  <svg
                    class="jr-footer__connector-icon"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M3 8h10M9 4l4 4-4 4"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round" />
                  </svg>
                </span>
              </li>
            </ol>
          </nav>

          <p v-else class="jr-footer__guest-copy">
            Operations platform for residential trade contractors. Sign in to
            access your workspace.
          </p>
        </div>
      </div>

      <div class="jr-footer__meta">
        <p class="jr-footer__meta-line">
          <span>
            © {{ currentYear }}
            <strong class="jr-footer__meta-brand">JobRhythm</strong>
            . All rights reserved.
          </span>
          <span class="jr-footer__meta-dot" aria-hidden="true">·</span>
          <span class="jr-footer__meta-version">v{{ appVersion }}</span>
        </p>
        <p class="jr-footer__meta-line">
          <span>
            <span class="jr-footer__meta-label">Support:</span>
            <a href="mailto:team@jobrhythm.net" class="jr-footer__support-link">
              team@jobrhythm.net
            </a>
          </span>
          <span class="jr-footer__meta-dot" aria-hidden="true">·</span>
          <span class="jr-footer__meta-phone">
            <svg
              class="jr-footer__phone-icon"
              viewBox="0 0 16 16"
              fill="currentColor"
              aria-hidden="true">
              <path
                d="M3.654 1.328a.678.678 0 0 1 .737-.061l2.79 1.395c.329.165.445.534.246.86l-1.12 1.933a.678.678 0 0 0 .178.884l1.12 1.12a.678.678 0 0 0 .884.178l1.933-1.12c.326-.199.695-.083.86.246l1.395 2.79a.678.678 0 0 1-.061.737l-1.385 1.385a1.75 1.75 0 0 1-1.85.41 12.84 12.84 0 0 1-5.52-3.37 12.84 12.84 0 0 1-3.37-5.52 1.75 1.75 0 0 1 .41-1.85L3.654 1.328z" />
            </svg>
            <a href="tel:+12392400016" class="jr-footer__phone-link"
              >+1 (239) 240-0016</a
            >
          </span>
        </p>
      </div>
    </div>
  </footer>
</template>

<script>
import { h } from "vue";

const stroke = {
  stroke: "currentColor",
  "stroke-width": "1.5",
  "stroke-linecap": "round",
  "stroke-linejoin": "round",
};

function createFlowIcon(nodes) {
  return {
    render() {
      return h(
        "svg",
        {
          class: "jr-footer__step-icon",
          viewBox: "0 0 24 24",
          fill: "none",
          xmlns: "http://www.w3.org/2000/svg",
          "aria-hidden": "true",
        },
        nodes
      );
    },
  };
}

const FlowIconCalendar = createFlowIcon([
  h("rect", { x: 3, y: 4, width: 18, height: 18, rx: 2, ...stroke }),
  h("path", { d: "M16 2v4M8 2v4M3 10h18", ...stroke }),
]);

const FlowIconBox = createFlowIcon([
  h("path", { d: "M21 8.5 12 3 3 8.5v7L12 21l9-5.5v-7z", ...stroke }),
  h("path", { d: "M3.5 8.5 12 14l8.5-5.5M12 14v7", ...stroke }),
]);

const FlowIconContract = createFlowIcon([
  h("path", {
    d: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z",
    ...stroke,
  }),
  h("path", { d: "M14 2v6h6M8 13h8M8 17h5", ...stroke }),
]);

const FlowIconChat = createFlowIcon([
  h("path", {
    d: "M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z",
    ...stroke,
  }),
  h("path", { d: "M8 10h8M8 14h5", ...stroke }),
]);

const FlowIconDashboard = createFlowIcon([
  h("path", { d: "M4 19V5M4 19h16M8 19v-6M12 19V9M16 19v-3", ...stroke }),
]);

export default {
  name: "FooterComponent",
  data() {
    return {
      currentYear: new Date().getFullYear(),
      appVersion: "2.0.1",
      tenantLogoUrl: null,
      tenantName: null,
      tenantLogoFailed: false,
      operationalFlowSteps: [
        {
          label: "Schedule",
          route: "/schedule",
          icon: FlowIconCalendar,
        },
        {
          label: "Prepare Material Packing",
          route: "/transactions",
          icon: FlowIconBox,
        },
        {
          label: "Piece Work Contract",
          route: "/contracts",
          icon: FlowIconContract,
        },
        {
          label: "Track Job",
          route: "/chat-general",
          icon: FlowIconChat,
        },
        {
          label: "Measure the Operation",
          route: "/inventory-dashboard",
          icon: FlowIconDashboard,
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
    isActiveRoute(route) {
      return (
        this.$route.path === route || this.$route.path.startsWith(`${route}/`)
      );
    },
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
.jr-footer {
  --jr-footer-max: 72rem;
  --jr-footer-pad-x: 1rem;
  --jr-footer-pad-y: 0.875rem;

  border-top: 1px solid var(--color-jr-border);
  background: linear-gradient(
    180deg,
    var(--color-jr-surface) 0%,
    var(--color-jr-surface-muted) 100%
  );
  color: var(--color-jr-text);
  font-family: var(--font-jr-sans);
  font-size: 0.9375rem;
  line-height: 1.45;
  text-align: left;
}

.jr-footer ::selection {
  background: color-mix(in srgb, var(--color-jr-primary) 22%, transparent);
  color: var(--color-jr-text);
}

.jr-footer__inner {
  max-width: var(--jr-footer-max);
  margin-inline: auto;
  padding: var(--jr-footer-pad-y) var(--jr-footer-pad-x);
}

.jr-footer__main {
  display: grid;
  gap: 1rem;
}

.jr-footer__brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
}

.jr-footer__brand-link {
  display: inline-block;
  line-height: 0;
  text-decoration: none;
}

.jr-footer__brand-link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 3px;
}

.jr-footer__brand-logo {
  display: block;
  width: auto;
  max-width: min(168px, 60vw);
  height: auto;
  max-height: 36px;
  object-fit: contain;
}

.jr-footer__tenant-name {
  margin: 0;
  max-width: 17.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-footer__content {
  min-width: 0;
}

.jr-footer__flow-header {
  margin-bottom: 0.5rem;
  text-align: center;
}

.jr-footer__flow-title {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-footer__flow-lead {
  margin: 0.15rem 0 0;
  font-size: 0.75rem;
  font-weight: 400;
  line-height: 1.35;
  color: var(--color-jr-muted);
}

.jr-footer__steps {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 0.25rem;
  margin: 0;
  padding: 0 0 0.1rem;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  -webkit-overflow-scrolling: touch;
  list-style: none;
  scrollbar-width: thin;
  scrollbar-color: var(--color-jr-hover-border) transparent;
}

.jr-footer__steps:focus-within {
  scrollbar-color: var(--color-jr-primary) transparent;
}

.jr-footer__step {
  display: flex;
  flex: 0 0 auto;
  flex-direction: row;
  align-items: center;
}

.jr-footer__step-link {
  position: relative;
  display: grid;
  grid-template-columns: auto auto;
  align-items: center;
  gap: 0.35rem;
  min-height: 1.875rem;
  padding: 0.2rem 0.45rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
  color: inherit;
  text-decoration: none;
  transition: background-color 0.15s ease, border-color 0.15s ease,
    box-shadow 0.15s ease, transform 0.15s ease;
}

.jr-footer__step-link:hover {
  background: var(--color-jr-info-subtle);
  border-color: color-mix(in srgb, var(--color-jr-primary) 18%, transparent);
}

.jr-footer__step-link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-footer__step-link--active {
  background: var(--color-jr-warning-subtle);
  border-color: color-mix(in srgb, var(--color-jr-warning) 35%, transparent);
  box-shadow: 0 1px 3px
    color-mix(in srgb, var(--color-jr-warning) 12%, transparent);
}

.jr-footer__step-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-primary);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.jr-footer__step-link--active .jr-footer__step-index {
  background: var(--color-jr-warning);
}

.jr-footer__step-icon-wrap {
  display: none;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-jr-info-text);
}

.jr-footer__step-link--active .jr-footer__step-icon-wrap {
  color: var(--color-jr-warning-text);
}

.jr-footer__step-icon {
  width: 1rem;
  height: 1rem;
}

.jr-footer__step-label {
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.3;
  color: var(--color-jr-text);
  white-space: nowrap;
}

.jr-footer__step-link--active .jr-footer__step-label {
  font-weight: 600;
  color: var(--color-jr-warning-text);
}

.jr-footer__step-connector {
  display: none;
  justify-content: center;
  padding: 0.1rem 0;
  color: var(--color-jr-hover-border);
}

.jr-footer__connector-icon {
  width: 0.75rem;
  height: 0.75rem;
  transform: none;
}

.jr-footer__guest-copy {
  margin: 0 auto;
  max-width: 36rem;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-jr-muted);
  text-align: center;
  text-wrap: pretty;
}

.jr-footer__meta {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-jr-border);
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
  text-align: center;
}

.jr-footer__meta-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
}

.jr-footer__meta-dot {
  display: none;
}

.jr-footer__meta-brand {
  color: var(--color-jr-text);
  font-weight: 600;
}

.jr-footer__meta-version {
  font-size: 0.75rem;
  font-variant-numeric: tabular-nums;
}

.jr-footer__meta-label {
  color: var(--color-jr-muted);
}

.jr-footer__support-link {
  margin-left: 0.25rem;
  color: var(--color-jr-warning);
  font-weight: 600;
  text-decoration: none;
  transition: color 0.15s ease;
}

.jr-footer__support-link:hover {
  color: var(--color-jr-warning-text);
  text-decoration: underline;
  text-underline-offset: 0.12em;
}

.jr-footer__support-link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-footer__meta-phone {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  color: var(--color-jr-text);
}

.jr-footer__phone-link {
  color: inherit;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.15s ease;
}

.jr-footer__phone-link:hover {
  color: var(--color-jr-warning-text);
  text-decoration: underline;
  text-underline-offset: 0.12em;
}

.jr-footer__phone-link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-footer__phone-icon {
  width: 0.9rem;
  height: 0.9rem;
  color: var(--color-jr-warning);
}

@media (min-width: 576px) {
  .jr-footer__meta-line {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem 0.75rem;
  }

  .jr-footer__meta-dot {
    display: inline;
    opacity: 0.5;
  }
}

@media (min-width: 768px) {
  .jr-footer__inner {
    padding-inline: 1.5rem;
  }
}

@media (min-width: 992px) {
  .jr-footer__main {
    grid-template-columns: minmax(9rem, 11rem) minmax(0, 1fr);
    align-items: start;
    gap: 1.25rem;
  }

  .jr-footer__brand {
    align-items: flex-start;
    text-align: left;
  }

  .jr-footer__flow-header {
    margin-bottom: 0.5rem;
    text-align: left;
  }

  .jr-footer__steps {
    flex-wrap: nowrap;
    align-items: center;
    gap: 0.15rem;
    overflow-x: auto;
  }

  .jr-footer__step {
    flex: 0 0 auto;
    flex-direction: row;
    align-items: center;
    max-width: none;
  }

  .jr-footer__step-icon-wrap {
    display: inline-flex;
  }

  .jr-footer__step-link {
    flex: 0 0 auto;
    grid-template-columns: auto auto minmax(0, 1fr);
    grid-template-rows: auto;
    justify-items: start;
    gap: 0.3rem;
    min-height: 1.875rem;
    max-width: none;
    padding: 0.2rem 0.45rem;
    background: var(--color-jr-surface);
    border-color: var(--color-jr-border);
    box-shadow: none;
    text-align: left;
  }

  .jr-footer__step-link:hover {
    border-color: var(--color-jr-hover-border);
    box-shadow: 0 2px 6px
      color-mix(in srgb, var(--color-jr-primary) 8%, transparent);
    transform: none;
  }

  .jr-footer__step-label {
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.25;
    white-space: nowrap;
  }

  .jr-footer__step-connector {
    display: flex;
    align-self: center;
    flex-shrink: 0;
    padding-inline: 0.05rem;
  }

  .jr-footer__connector-icon {
    width: 0.65rem;
    height: 0.65rem;
    transform: none;
  }

  .jr-footer__guest-copy {
    margin-inline: 0;
    text-align: left;
  }

  .jr-footer__meta {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 0 0.75rem;
  }

  .jr-footer__meta-line {
    flex-direction: row;
    flex-wrap: nowrap;
    width: auto;
    gap: 0.5rem;
  }

  .jr-footer__meta-line + .jr-footer__meta-line::before {
    content: "·";
    margin-right: 0.75rem;
    opacity: 0.5;
  }
}
</style>
