# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Office and field operations staff** at residential trade contractors: schedulers, project managers, office admins, crew leads, and supervisors who run daily operations from desktop and mobile browsers.
- **Tenant administrators** who configure modules, users, permissions, and company-specific workflows per organization (multi-tenant SaaS).

## Product Purpose

JobRhythm is an operational platform for residential trade contractors. It centralizes scheduling, contracts, inventory, purchases, crews, documents, and field communication so teams can see work, materials, and job status without relying on calls, texts, and paper notes.

Success means teams complete daily operational tasks faster, with fewer errors, clearer accountability, and reliable visibility across jobs and tenants.

## Positioning

JobRhythm sits in the space between generic field-service tools and enterprise construction PM: **operations for residential trade contractors** — scheduling, piece-work contracts, inventory, purchases, and crew coordination in one multi-tenant system.

## Operating Context

- Multi-tenant SaaS: each customer organization runs in an isolated schema; users access their tenant via subdomain.
- Primary interface is a **Vue.js SPA** (administrative, data-dense) backed by Django/DRF APIs.
- Users work in long sessions with tables, filters, forms, schedules, and document workflows.
- Development runs on ubuntu-house; production runs on VPS (outside agent scope for deploy).
- Visible product name: **JobRhythm**. Internal repo/infra may still use Chalan-Pro naming.

## Capabilities and Constraints

- Confirmed modules include scheduling, contracts, inventory, transactions/purchases, crews, documents, reports, onboarding, and billing-related admin flows.
- Backend is authoritative for permissions, tenant isolation, business rules, calculations, and API contracts.
- Frontend must preserve existing API semantics during visual modernization.
- Bilingual marketing landing exists separately (`landing/`); the operational app UI is the primary design surface for this harness.

## Brand Commitments

- Commercial and user-visible name: **JobRhythm**.
- Domains: SaaS `jobrhythm.net` (tenant subdomains); landing `getjobrhythm.com`. Legacy domains may remain during transition.
- Professional, trustworthy, construction-technology character — not consumer marketing gloss inside the app shell.

## Evidence on Hand

- Repository instructions: `AGENTS.md`, `app/readme/README_RESUMEN_GENERAL_LOCAL.md`.
- Incumbent Vue frontend: `app/vuefrontend/` (Vue 3, Vue CLI, Bootstrap 5, operational modules).
- Marketing positioning reference: `landing/AGENTS.md` (niche: residential trade contractor operations).
- Do not fabricate customer logos, testimonials, benchmarks, or pricing not present in repo assets.

## Product Principles

1. **Operational clarity over decoration** — dense work surfaces must remain scannable and fast to use.
2. **Backend truth** — permissions, money, dates, and business rules come from Django; the UI reflects them accurately.
3. **Tenant safety** — never blur organization boundaries in UI or navigation.
4. **Incremental modernization** — improve presentation and interaction without breaking contracts or workflows.
5. **Consistent JobRhythm identity** — one professional admin experience across modules.

## Accessibility & Inclusion

- Target baseline: keyboard reachability, visible focus, meaningful labels, contrast for operational reading, and responsive usability for field/office contexts.
- No product-specific WCAG certification recorded in repo; treat accessibility as a required baseline for frontend upgrades.
