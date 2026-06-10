# Golden queries y afinación de búsqueda semántica

Archivos en este directorio para **evaluar y mantener** Smart search sin adivinar.

## Archivos JSON (`app/appsearch/eval/`)

JSON estándar no admite comentarios `//`. Cada archivo incluye un bloque **`_meta`** al inicio que documenta para qué sirve; los comandos leen solo `cases` o `aliases`.

| Archivo | Para qué es |
|---------|-------------|
| **`golden_queries.<schema>.json`** | Baseline de **regresión** Smart search para un tenant: lista de consultas con resultados esperados (`expected_document_ids`, `min_count`, `forbidden_document_ids`, etc.). Usado por `search_eval` y `./scripts/run_search_eval.sh`. Plantilla: `golden_queries.test_dominio_local.json`. |
| **`builder_aliases.recommended.json`** | Plantilla de **alias de party** (nombre alternativo → `Builder` del tenant). Usado por `seed_builder_aliases`; el admin del tenant sigue siendo la fuente de verdad en producción. |

Campos útiles en **`_meta`**: `purpose`, `used_by`, `tenant_schema` (golden), `refresh_baseline`, `row_fields` (aliases).

## Golden queries (`golden_queries.<schema>.json`)

Lista de ~26 consultas de referencia para el tenant `test_dominio_local` (plantilla para otros tenants).

Cada caso puede incluir:

| Campo | Uso |
|-------|-----|
| `query` | Texto que escribe el usuario |
| `expected_document_ids` | Documentos que deben aparecer (recall@k) |
| `min_count` | Mínimo de resultados |
| `forbidden_document_ids` | IDs que **no** deben salir (anti falsos positivos) |
| `expect_notice` | Debe devolver `notice` (p. ej. tipo inexistente) |

### Ejecutar evaluación

```bash
# ubuntu-house
./scripts/run_search_eval.sh --dev test_dominio_local

# Con umbral de recall (falla el script si no llega)
./scripts/run_search_eval.sh --dev test_dominio_local --fail-under 0.95

# Dentro del contenedor
docker compose -f docker-compose.dev.yml exec backend \
  python manage.py search_eval --schema test_dominio_local
```

### Actualizar baseline (tras cambio de datos o lógica aprobado)

```bash
./scripts/run_search_eval.sh --dev test_dominio_local --update-baseline
```

Revisa el diff del JSON antes de commitear.

### Nuevo tenant

```bash
cp app/appsearch/eval/golden_queries.test_dominio_local.json \
   app/appsearch/eval/golden_queries.TU_SCHEMA.json
# Editar expected_document_ids con --update-baseline o a mano
```

---

## Builder aliases (`builder_aliases.recommended.json`)

Plantilla de alias → party. Admin del tenant: **Builder search aliases**.

```bash
docker compose -f docker-compose.dev.yml exec backend \
  python manage.py seed_builder_aliases --schema test_dominio_local

# Simular
docker compose -f docker-compose.dev.yml exec backend \
  python manage.py seed_builder_aliases --schema test_dominio_local --dry-run
```

Ajusta `builder_name` a parties reales de cada tenant antes de ejecutar.

---

## Cron outbox (indexación incremental)

Tras crear/editar transacciones, la cola `IndexOutbox` debe procesarse:

```bash
# Manual
./scripts/process_search_outbox_cron.sh --dev

# Cron ubuntu-house (cada 3 min)
*/3 * * * * oliver cd /home/oliver/shared/projects/chalanpro && ./scripts/process_search_outbox_cron.sh --dev
```

---

## Reindex tras cambios en `chunk.py`

Cuando cambie qué texto o metadata se indexa:

```bash
./scripts/reindex_search_after_chunk_change.sh --dev --schema test_dominio_local
# o todos los tenants:
./scripts/reindex_search_after_chunk_change.sh --dev --all-tenants
```

Orden: outbox pendiente → `reindex_document_lines` (embeddings OpenAI).

---

## `SEARCH_MIN_RELEVANCE_SCORE`

En `envs/backend.dev.env` (no versionado):

```env
SEARCH_MIN_RELEVANCE_SCORE=0.12
```

- **Subir** (0.15–0.20): menos ruido, más estricto.
- **Bajar** (0.08–0.10): más resultados, más falsos positivos.

Tras cambiar: `docker compose -f docker-compose.dev.yml up -d --force-recreate backend` y volver a correr `run_search_eval.sh`.
