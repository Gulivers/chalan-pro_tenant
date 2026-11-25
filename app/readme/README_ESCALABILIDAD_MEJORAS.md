# JobRhythm — Escalabilidad y Mejoras Pendientes

Documento vivo de backlog técnico: mejoras de capacidad, resiliencia y rendimiento.
Clasificado por **tipo de escalabilidad** y ordenado por **prioridad**.

**Relacionado:** [README_RESUMEN_GENERAL.md](./README_RESUMEN_GENERAL.md) (§1 arquitectura VPS), [DEVOPS.md](../../DEVOPS.md), regla [pdf-async-jobs.mdc](../../.cursor/rules/pdf-async-jobs.mdc).

---

## Índice

- [1. Cómo usar este documento](#1-cómo-usar-este-documento)
- [2. Tipos de escalabilidad (glosario)](#2-tipos-de-escalabilidad-glosario)
- [3. Matriz de prioridades](#3-matriz-de-prioridades)
- [4. Backlog por tipo](#4-backlog-por-tipo)
  - [4.1 Horizontal scaling (réplicas / LB)](#41-horizontal-scaling-réplicas--lb)
  - [4.2 Escala de trabajo async (offload del request)](#42-escala-de-trabajo-async-offload-del-request)
  - [4.3 Optimización vertical / código](#43-optimización-vertical--código)
  - [4.4 Datos y almacenamiento](#44-datos-y-almacenamiento)
  - [4.5 Observabilidad y límites](#45-observabilidad-y-límites)
- [5. Hecho (referencia)](#5-hecho-referencia)
- [6. Notas de entorno (VPS vs ubuntu-house)](#6-notas-de-entorno-vps-vs-ubuntu-house)
- [7. Historial de entradas](#7-historial-de-entradas)

---

## 1. Cómo usar este documento

| Campo | Significado |
|-------|-------------|
| **P0 / P1 / P2 / P3** | Urgencia: P0 = riesgo de caída percibida; P3 = nice-to-have |
| **Tipo** | Ver §2 |
| **Estado** | `pendiente` · `en curso` · `hecho` · `descartado` |
| **Entorno** | `prod` · `dev` · `ambos` |

Al completar un ítem: mover a [§5](#5-hecho-referencia) con fecha y enlace a commit/PR si aplica.

---

## 2. Tipos de escalabilidad (glosario)

| Tipo | Qué implica en JobRhythm |
|------|---------------------------|
| **H — Horizontal** | Más réplicas del mismo servicio detrás de Nginx (p. ej. Daphne ×N). Misma DB/media. |
| **A — Async / offload** | Sacar trabajo pesado del request HTTP (jobs Redis, colas, workers dedicados). |
| **V — Vertical / código** | Más CPU/RAM **o** menos trabajo por request (queries, N+1, índices, templates). |
| **D — Datos** | Postgres (conexiones, réplicas read, partición), media, Redis. |
| **O — Observabilidad** | Métricas, timeouts, rate limits, alertas — para saber *cuándo* escalar. |

---

## 3. Matriz de prioridades

Orden sugerido de ataque (no escalar cajas a ciegas):

| Pri | ID | Título | Tipo | Estado | Entorno |
|-----|-----|--------|------|--------|---------|
| P0 | A-01 | Offload create/update de documentos pesados (líneas + movimientos) | A | pendiente | ambos |
| P1 | A-02 | Workers dedicados a WeasyPrint (separar de Daphne) | A / H | pendiente | prod |
| P1 | V-01 | Optimizar `DocumentSerializer.create/update` (bulk, menos logs, menos round-trips) | V | pendiente | ambos |
| P1 | O-01 | Métricas Daphne/Redis/Postgres + alertas de cola PDF | O | pendiente | prod |
| P2 | O-02 | Autoheal de contenedores `unhealthy` (opcional; Compose no reinicia solo por unhealthy) | O | pendiente | prod |
| P2 | D-01 | Auditoría índices y `EXPLAIN` en tenants demo (docs 50+ líneas) | D / V | pendiente | ambos |
| P2 | H-01 | Evaluar Daphne ×3 solo si VPS ≥4 vCPU y métricas lo justifican | H | pendiente | prod |
| P2 | D-02 | Política de limpieza `media/pdf_jobs/` (TTL disco) | D | pendiente | ambos |
| P3 | D-03 | Réplica Postgres read-only (solo si read traffic lo exige) | D / H | pendiente | prod |
| P3 | A-03 | Excel schedule / exports pesados al mismo patrón jobs | A | pendiente | ambos |

---

## 4. Backlog por tipo

### 4.1 Horizontal scaling (réplicas / LB)

#### H-01 — Más réplicas Daphne (condicional)
- **Prioridad:** P2  
- **Estado:** pendiente  
- **Contexto:** Hoy `backend` ×2 + Nginx round-robin. VPS ~2 vCPU: ×3 suele empeorar contención.  
- **Criterio de go:** p95 API alto *y* CPU no saturada en un solo worker; VPS con ≥4 vCPU.  
- **No hacer:** escalar frontend/nginx/landing.

---

### 4.2 Escala de trabajo async (offload del request)

#### A-01 — Documentos pesados fuera del request (futuro cercano)
- **Prioridad:** P0  
- **Estado:** pendiente  
- **Problema:** Un `POST/PATCH` de documento con muchas líneas + movimientos de inventario sigue bloqueando **un** Daphne; ×2 solo mitiga el blast radius.  
- **Dirección:** patrón similar a PDF jobs (`enqueue` + poll/websocket de progreso), o pipeline por lotes, **sin** rediseñar el modelo de inventario.  
- **Relacionado:** incidente demos (doc ~50 líneas + PDF).  
- **Nota agentes:** no confundir con PDF async (ya hecho); esto es el **save**.

#### A-02 — Workers PDF dedicados
- **Prioridad:** P1  
- **Estado:** pendiente  
- **Hoy:** WeasyPrint corre en hilo daemon dentro de Daphne.  
- **Futuro:** proceso/cola solo para PDF si schedules/contratos saturan CPU de API.  
- **Mantener:** contrato `POST …/jobs/` + poll `/api/pdf/jobs/<id>/` (regla `pdf-async-jobs.mdc`).

#### A-03 — Exports Excel / reportes largos
- **Prioridad:** P3  
- **Estado:** pendiente  
- **Ejemplo:** `schedule-excel` sync. Mismo patrón jobs si empieza a molestar.

---

### 4.3 Optimización vertical / código

#### V-01 — Serializer de documentos
- **Prioridad:** P1  
- **Estado:** pendiente  
- **Ideas:** bulk create líneas, menos `logger.info` por línea, prefetch, transacciones más cortas donde sea seguro.  
- **Complementa** A-01 (a veces basta optimizar sin cola).

---

### 4.4 Datos y almacenamiento

#### D-01 — Índices / queries en demos
- **Prioridad:** P2  
- **Estado:** pendiente  

#### D-02 — Limpieza `media/pdf_jobs/`
- **Prioridad:** P2  
- **Estado:** pendiente  
- **Hoy:** TTL Redis ~10 min; archivos en disco pueden quedar. Cron o purge en deploy.

#### D-03 — Réplica Postgres
- **Prioridad:** P3  
- **Estado:** pendiente  
- **Solo** con evidencia de read-heavy; no antes de D-01/V-01.

---

### 4.5 Observabilidad y límites

#### O-01 — Telemetría mínima
- **Prioridad:** P1  
- **Estado:** pendiente  
- **Qué medir:** duración PDF jobs, cola Redis, latencia `/api/documents/`, saturación Daphne, conexiones Postgres.  
- **Base ya hecha:** timeouts Nginx API 120s / PDF sync 180s / WS 86400; healthchecks Docker + Better Stack Uptime (email).

#### O-02 — Autoheal opcional
- **Prioridad:** P2  
- **Estado:** pendiente  
- **Contexto:** `restart: unless-stopped` cubre crash; Compose no recrea por `unhealthy`. Sidecar liviano (`willfarrell/autoheal`) solo si hay hung reales sin crash.

---

## 5. Hecho (referencia)

| Fecha | ID | Qué | Tipo |
|-------|-----|-----|------|
| 2026-11 | H-00 | Daphne ×2 (`--scale backend=2`) + Redis Channels | H |
| 2026-11 | A-00 | PDF async (transacciones, MR, schedule, contratos) + CSS sin CDN | A |
| 2026-11 | O-00 | Timeouts Nginx API/PDF; cron wildcard `jobrhythm.net` | O |
| 2026-11 | O-00b | `GET /api/health/` + healthcheck backend/nginx; docs Better Stack Uptime (§1.4) | O |
| 2026-11 | DOC-00 | Diagrama §1.1 README_RESUMEN_GENERAL + regla `pdf-async-jobs.mdc` | — |

Detalle operativo: `docker-compose.yml`, `scripts/deploy-vps.sh`, `apptransactions/pdf_jobs.py`, `vuefrontend/src/utils/downloadPdfJob.js`.

---

## 6. Notas de entorno (VPS vs ubuntu-house)

| Aspecto | VPS (`docker-compose.yml` / `main_deploy`) | ubuntu-house (`docker-compose.dev.yml` / `dev_local_primevue`) |
|---------|--------------------------------------------|------------------------------------------------------------------|
| Daphne | ×2 (scale) | ×1 (suficiente para desarrollo) |
| Redis | Obligatorio | Obligatorio si se usan PDF jobs / Channels Redis |
| `REDIS_URL` | `redis://redis:6379/0` | Igual en `backend.dev.env` / example |
| Deploy | `deploy-vps.sh` | compose local; **no** desplegar `develop` histórico al VPS |

**Git (evitar solapes):**

1. Integrar este trabajo primero en **`dev_local_primevue`** (ubuntu-house) y probar con Redis.  
2. Merge a **`main_deploy`** para VPS.  
3. Propagar a **`develop`** / **`wilson-developments`** cuando se quiera alinear esas líneas, sin usarlas como fuente de deploy VPS.

---

## 7. Historial de entradas

| Fecha | Cambio |
|-------|--------|
| 2026-11-23 | Creación del documento; backlog inicial post Daphne×2 + PDF async |
