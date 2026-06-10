# Semantic Search — JobRhythm (`appsearch`)

Capa desacoplada por tenant: **`SearchIndex`** (índice consultable) + **`IndexOutbox`** (cola de indexación).

| Modelo | Función |
|--------|---------|
| `SearchIndex` | Embeddings, FTS y metadata de cada `DocumentLine` indexada |
| `IndexOutbox` | Trabajos pendientes cuando cambian transacciones (upsert/delete) |

Variables en `envs/backend.dev.env` / `envs/backend.env` (plantilla: `backend.dev.example.env`):

- `OPENAI_API_KEY` — clave API OpenAI (no incluida en ChatGPT Pro)
- `SEARCH_EMBEDDING_MODEL=text-embedding-3-small`
- `SEARCH_EMBEDDING_DIMENSIONS=1536`
- `SEARCH_INDEXING_ENABLED=True`

PostgreSQL requiere imagen **`pgvector/pgvector:pg15`** y extensión `vector`.

---

## Comandos

En **ubuntu-house** usar `-f docker-compose.dev.yml`. En **VPS** usar `docker compose` (producción).

### `migrate_schemas`

Aplica migraciones Django en **todos** los schemas (public + tenants), incluyendo tablas `appsearch_searchindex` y `appsearch_indexoutbox`.

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate_schemas
```

Ejecutar tras desplegar cambios en modelos de `appsearch` o al activar pgvector por primera vez.

---

### `reindex_document_lines`

Reconstruye el **SearchIndex completo** para las líneas de documento activas de un tenant: compone `chunk_text`, llama a OpenAI, guarda embeddings y actualiza FTS.

```bash
# Backfill inicial o tras cambiar el modelo de embedding
docker compose -f docker-compose.dev.yml exec backend python manage.py reindex_document_lines --schema TU_SCHEMA

# Solo chunk + FTS, sin OpenAI (prueba local)
docker compose -f docker-compose.dev.yml exec backend python manage.py reindex_document_lines --schema TU_SCHEMA --no-embed

# Un solo documento
docker compose -f docker-compose.dev.yml exec backend python manage.py reindex_document_lines --schema TU_SCHEMA --document-id 123
```

---

### `process_index_outbox`

Procesa filas **pendientes** de `IndexOutbox` (creadas por señales al guardar/borrar `DocumentLine`, `Document` o renombrar `Builder`). Genera embeddings y upsert en `SearchIndex`.

```bash
# Tras crear/editar transacciones en la app (indexación incremental)
docker compose -f docker-compose.dev.yml exec backend python manage.py process_index_outbox --schema TU_SCHEMA

# Procesar hasta N entradas por ejecución (default 100)
docker compose -f docker-compose.dev.yml exec backend python manage.py process_index_outbox --schema TU_SCHEMA --limit 200
```

Tras lotes de importación o pruebas manuales en un solo tenant.

---

### `process_index_outbox_all`

Procesa la cola pendiente en **todos los tenants activos** (excluye `public`). Punto de entrada para **cron en el host** (Fase A).

```bash
# Manual (todos los tenants)
docker compose -f docker-compose.dev.yml exec backend python manage.py process_index_outbox_all

# Hasta N entradas por tenant (default 200)
docker compose -f docker-compose.dev.yml exec backend python manage.py process_index_outbox_all --limit 200
```

**Cron (host, no dentro del contenedor):**

```bash
# ubuntu-house — prueba manual
./scripts/process_search_outbox_cron.sh --dev

# VPS — crontab (cada 3 min)
# */3 * * * * root /opt/chalanpro/scripts/process_search_outbox_cron.sh
```

Log: `/var/log/chalanpro/search-outbox.log` (VPS) o `logs/search-outbox.log` (modo `--dev`). El script usa `flock` para evitar ejecuciones solapadas.

---

## Fase 2 — Transaction Search

### API

`POST /api/search/transactions/`

```json
{
  "query": "Harbor Freight purchases over $500 this month",
  "limit": 50
}
```

**Respuesta:** `document_ids`, `results[]` (snippet, score, metadata), `applied_filters`, `resolved_entities`.

Pipeline: parser de intents (montos, fechas, compras/ventas) → resolución de entidades (`DocumentType`, `Builder`, `WorkAccount`) → filtros SQL en metadata → similitud vectorial + FTS en `SearchIndex`.

**Fase 2.5 — filtros estructurados:**

| Filtro | Cuándo |
|--------|--------|
| `document_type_id` | Código (`PINV`) o descripción fuzzy (`Purchase Invoice`). Frases compuestas (`sales order`, `purchase return`, …) no se descomponen en filtros `is_sales`/`is_purchase` para evitar conflictos. |
| `document_total_gte` | Monto «over $X» sin texto de producto (p. ej. compras por party) |
| `line_final_price_gte` | Monto «over $X» con texto semántico de producto/concepto |

**Relevancia (Fase 3.1):**

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SEARCH_MIN_RELEVANCE_SCORE` | `0.12` | Descarta coincidencias híbridas por debajo de este score |

Si la consulta parece un **tipo de transacción** (p. ej. «missing material») y ningún `DocumentType` del tenant coincide, la API devuelve **0 resultados** con `notice` en lugar de buscar semánticamente «material» en productos/categorías.

Tras cambiar metadata del chunk (`document_total_amount`), ejecutar `reindex_document_lines` por tenant (opcional para total de documento: el filtro usa `Document.total_amount` en BD).

### UI

Checkbox **Smart search (AI)** en `/transactions` (Vue). Requiere permiso `apptransactions.view_document`.

Botón **Similar** por fila → `POST /api/search/transactions/similar/`.

---

## Fase 3 — Advanced Retrieval

### Transacciones similares

`POST /api/search/transactions/similar/`

```json
{ "document_id": 75, "limit": 20 }
```

Opcional: `document_line_id` en lugar de `document_id`. Excluye el documento origen; k-NN sobre embeddings de `SearchIndex`.

### Rank fusion (híbrido)

Variables en `envs/backend*.env`:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SEARCH_FUSION_MODE` | `weighted` | `weighted` o `rrf` |
| `SEARCH_FUSION_VECTOR_WEIGHT` | `0.6` | Peso similitud vectorial |
| `SEARCH_FUSION_FTS_WEIGHT` | `0.4` | Peso FTS (BM25-like via SearchRank) |
| `SEARCH_FUSION_RRF_K` | `60` | Constante k para RRF |

### Aliases de Builder

Modelo **`BuilderAlias`** (admin por tenant): alias → `ctrctsapp.Builder`. Usado en resolución de party (`matched_alias` en respuesta API).

### Outbox robusto

| Variable | Default |
|----------|---------|
| `SEARCH_OUTBOX_MAX_ATTEMPTS` | `5` |

Tras agotar reintentos → `dead_letter_at`. Comandos:

```bash
docker compose exec backend python manage.py outbox_status
docker compose exec backend python manage.py requeue_dead_letter_outbox --schema TU_SCHEMA
```

### Métricas

Telemetría ligera en **`SearchTelemetry`** (latencia y recuento por request):

```bash
docker compose exec backend python manage.py search_metrics --schema TU_SCHEMA --days 7
docker compose exec backend python manage.py search_eval --schema TU_SCHEMA --queries-file /path/eval.json
```

`search_eval` espera JSON: `[{"query":"...", "expected_document_ids":[1,2]}]`.

Tras desplegar Fase 3: **`migrate_schemas`**.

---

## Admin

Por tenant: **Search index entries** e **Index outbox entries**.
