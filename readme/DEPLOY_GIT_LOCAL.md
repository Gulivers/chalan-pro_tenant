# Sincronización local con Git (chalanpro)

Guía para **sincronizar tus cambios locales** con el repositorio Git. El despliegue en el VPS Hostinger lo haces tú por tu cuenta.

---

## 1. Resumen de ramas (junio 2026)

| Rama | Uso |
|------|-----|
| **`dev_local_status`** | Desarrollo activo en **ubuntu-house** |
| **`main_deploy`** | **Producción VPS** — la que usan `deploy-vps.sh` y `deploy-landing-vps.sh` |
| **`main`**, **`develop`**, **`dev_local_inv-img`** | **Históricas** (incluyen búsqueda semántica archivada; **no desplegar**) |
| **`backup-dev_local_inv-img-semantic-search-*`** | Snapshot con semántica por si se necesita recuperar |

- **Repositorio:** https://github.com/Gulivers/chalan-pro_tenant.git  
- **Local:** `~/shared/projects/chalanpro`

---

## 2. Flujo recomendado (ubuntu-house → VPS)

1. **Commitear** en `dev_local_status`.
2. **Probar** en ubuntu-house (`docker-compose.dev.yml`).
3. **Integrar en despliegue:**
   ```bash
   git checkout main_deploy
   git pull origin main_deploy
   git merge dev_local_status --no-ff -m "Merge dev_local_status: descripción breve"
   git push origin main_deploy
   ```
4. **Subir desarrollo** (opcional, en paralelo):
   ```bash
   git push origin dev_local_status
   ```
5. **Despliegue VPS:** `sudo /opt/chalanpro/scripts/deploy-vps.sh` (hace `git pull origin main_deploy`).

---

## 3. Comandos habituales

```bash
cd /home/oliver/shared/projects/chalanpro

git checkout dev_local_status
git status
git branch -a
```

**Nuevo cambio:**

```bash
git add -A
git status   # Revisar que no entren envs/*.env ni postgres_data/
git commit -m "feat(modulo): descripción breve"
git push origin dev_local_status
```

**Listo para producción:**

```bash
git checkout main_deploy
git pull origin main_deploy
git merge dev_local_status --no-ff -m "Merge dev_local_status: listo para VPS"
git push origin main_deploy
# En el VPS: sudo /opt/chalanpro/scripts/deploy-vps.sh
```

---

## 4. Antes de push a `main_deploy`

- [ ] No incluir `envs/*.env` ni `postgres_data/` (deben estar en `.gitignore`).
- [ ] Probar en local (backend, frontend, migraciones si las hay).
- [ ] Mensaje de commit claro (`feat:`, `fix:`, `chore:`, etc.).
- [ ] **No** hacer merge a `main` / `develop` / `dev_local_inv-img` para desplegar (ramas históricas).

---

## 5. Scripts útiles

| Script | Uso |
|--------|-----|
| `./scripts/deploy-vps.sh` | Deploy completo en VPS (`main_deploy`) |
| `./scripts/deploy-landing-vps.sh` | Solo landing en VPS (`main_deploy`) |
| `./scripts/git-workflow.sh status` | Estado de ramas (puede referir nombres legacy) |
| `./scripts/backup_local.sh` | Backup local código + BD |

Los scripts `prepare-deploy` / `sync_local_prepare_deploy.sh` siguen orientados al flujo antiguo (`dev_local_inv-img` → `main`). Para el flujo actual, usar merge manual a **`main_deploy`** (sección 2).

---

## 6. Problemas frecuentes (local)

- **Conflictos al merge a `main_deploy`:** resolver en local, `git add`, commit de merge, `git push origin main_deploy`.
- **Rama equivocada:** `git checkout dev_local_status` o `main_deploy` según corresponda.
- **Recuperar búsqueda semántica:** rama `backup-dev_local_inv-img-semantic-search-2026-06-17` o backup tar en `~/shared/projects/backups/`.

---

**Nota:** El despliegue en el VPS (pull, build, migraciones) lo ejecutas tú con `deploy-vps.sh`; los agentes no deben desplegar en Hostinger automáticamente.
