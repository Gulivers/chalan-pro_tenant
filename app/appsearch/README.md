# Semantic Search — Fase 1 (Foundation)

Capa desacoplada `SearchIndex` + `IndexOutbox` por schema de tenant.

## Comandos

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate_schemas
docker compose -f docker-compose.dev.yml exec backend python manage.py reindex_document_lines --schema TU_SCHEMA
docker compose -f docker-compose.dev.yml exec backend python manage.py process_index_outbox --schema TU_SCHEMA
```

Variables en `envs/backend.dev.env` (ver `backend.dev.example.env`).
