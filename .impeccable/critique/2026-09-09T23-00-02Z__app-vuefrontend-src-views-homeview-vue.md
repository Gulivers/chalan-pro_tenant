---
target: app/vuefrontend/src/views/HomeView.vue
total_score: 25
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-09-09T23-00-02Z
slug: app-vuefrontend-src-views-homeview-vue
---
# Critique — Home Dashboard (`HomeView.vue`)

**Target:** `app/vuefrontend/src/views/HomeView.vue` (+ AreaChart, BarChart, WeeklySupervisorChart; CustomersSuppliersComparison shared)  
**Mode:** Operate — Construction Operations / ERP home  
**Contract:** DESIGN.md → Target State (Pilot). English. JRPage. Square chart containers.

## Design Health Score

| # | Heurística | Score | Hallazgo clave |
|---|-----------|-------|----------------|
| 1 | Visibilidad del estado | 3 | Loading/empty/Retry por chart; sin status de página |
| 2 | Correspondencia mundo real | 3 | Trim/Rough OK; “Dashboard” genérico; márgenes extremos |
| 3 | Control y libertad | 3 | Refresh, filtros, export |
| 4 | Consistencia y estándares | 2 | Sales sin título JRSection; Swal Excel; colores chart mixtos |
| 5 | Prevención de errores | 2 | KPIs txn estimados; margin % cuando sales≈0 |
| 6 | Reconocer antes que recordar | 3 | Hints; canvas limitado para SR |
| 7 | Flexibilidad y eficiencia | 2 | Refresh repetido; sin rangos de fecha |
| 8 | Estético y minimalista | 2 | Stack de peso igual; supervisor vacío ocupa espacio |
| 9 | Recuperación de errores | 3 | Retry en charts principales |
| 10 | Ayuda y documentación | 2 | Micro-hints; poco guidance empty |
| **Total** | | **25/40** | **Acceptable** |

## Design Specificity

Pilot shell sólido (sin Bootstrap cards, contenedores cuadrados). IA aún es “dashboard de charts apilados”, no consola matutina de obra.

## What's Working

1. JRPage / JRSection / charts con a11y `role=img`.
2. Estados loading/empty/error en contracts + supervisor.
3. Espaciado entre secciones (2rem); `border-radius: 0` en `.jr-chart-container`.

## Priority Issues

### [P1] Sin jerarquía de “morning console”
Charts históricos de peso igual; no responde “qué corro hoy”.

### [P1] Confianza — KPIs txn / margin % en comparison
Conteos estimados y % explosivos cuando sales≈0 (shared `CustomersSuppliersComparison`).

### [P1] Sales section IA
`JRSection` sin título + título interno del shared.

### [P2] Supervisor vacío con toolbar completa
### [P2] Comparison ilegible cuando purchases dominan

## Smoke (esta corrida)

- Login OK; `/` muestra Weekly/Monthly charts; supervisor empty OK; comparison chart+tabla OK.
- Login log POST registrado.
- Contenedores `border-radius: 0`; margin-bottom sección `32px`.
- Intro “Morning console…” eliminada.

## Detector

CLI: limpio. Browser overlay: hallazgos mayormente footer/shell (FP para este target).
