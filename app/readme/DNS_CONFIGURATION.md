# Configuración DNS en Hostinger (Jobrithm)

## IP del Servidor VPS
```
72.60.168.62
```

## Estado del cambio de dominio

- **Dominio principal actual de la web app:** `jobrithm.net`
- **Dominio API/admin actual:** `api.jobrithm.net`
- **Wildcard tenants actual:** `*.jobrithm.net`
- **Dominio anterior:** `chalanpro.net` (se mantiene temporalmente por compatibilidad/rollback)

## Registros DNS requeridos (actual)

### 1. Registro A - Dominio Raíz (@)
**Tipo:** A  
**Nombre:** @  
**Points to:** 72.60.168.62  
**TTL:** 14400 (o Auto)

Este registro apunta el dominio principal `jobrithm.net` al servidor.

### 2. Registro A - Subdominio API
**Tipo:** A  
**Nombre:** api  
**Points to:** 72.60.168.62  
**TTL:** 14400 (o Auto)

Este registro apunta `api.jobrithm.net` al servidor para el API REST y Admin de Django.

### 3. Registro A - Wildcard tenants (*)
**Tipo:** A  
**Nombre:** *  
**Points to:** 72.60.168.62  
**TTL:** 300 (durante migración) / 14400 (estable)

Permite que cualquier subdominio tenant (ej: `tenant1.jobrithm.net`) resuelva al VPS.

### 4. Registro CNAME - www
**Tipo:** CNAME  
**Nombre:** www  
**Points to:** jobrithm.net  
**TTL:** 300 (durante migración) / 14400 (estable)

Opcional: `www.api` -> `api.jobrithm.net` si deseas mantener ese alias.

## Pasos para Configurar en Hostinger

1. **Accede al panel de Hostinger:**
   - Ve a: `https://hpanel.hostinger.com/domain/jobrithm.net/dns`

2. **Agrega el Registro A para el dominio raíz:**
   - Haz clic en "Add Record"
   - Tipo: **A**
   - Name: **@** (o déjalo vacío)
   - Points to: **72.60.168.62**
   - TTL: **14400** (o Auto)
   - Haz clic en "Add Record"

3. **Agrega el Registro A para api:**
   - Haz clic en "Add Record"
   - Tipo: **A**
   - Name: **api**
   - Points to: **72.60.168.62**
   - TTL: **14400** (o Auto)
   - Haz clic en "Add Record"

4. **Agrega el Registro A wildcard (`*`):**
   - Tipo: **A**
   - Name: **\***
   - Points to: **72.60.168.62**
   - TTL: **300** (migración) o **14400** (estable)

5. **Verifica los registros existentes:**
   - El CNAME para `www` apunta a `jobrithm.net`
   - Los registros CAA pueden quedarse (son para certificados SSL)

## Configuración Final Esperada

Después de agregar los registros, deberías tener:

| Tipo | Name | Points to / Content | TTL |
|------|------|---------------------|-----|
| **A** | @ | 72.60.168.62 | 300/14400 |
| **A** | api | 72.60.168.62 | 300/14400 |
| **A** | * | 72.60.168.62 | 300/14400 |
| **CNAME** | www | jobrithm.net | 300/14400 |
| **CAA** | @ | (varios registros existentes) | 14400 |

## Verificación

Después de configurar los DNS (puede tardar unos minutos en propagarse):

```bash
# Verificar que el dominio raíz apunta al servidor
nslookup jobrithm.net

# Verificar que api.jobrithm.net apunta al servidor
nslookup api.jobrithm.net

# Verificar wildcard tenant (ejemplo)
nslookup tenant-prueba.jobrithm.net
```

Las tres consultas deberían devolver: **72.60.168.62**

## URLs Finales

Una vez configurados los DNS y los certificados SSL:

- **Frontend:** https://jobrithm.net
- **API REST:** https://api.jobrithm.net/api/
- **Admin Django:** https://api.jobrithm.net/admin/
- **Tenant Login:** https://{tenant}.jobrithm.net/login/
- **pgAdmin:** http://72.60.168.62:5050 (o configurar subdominio si lo deseas)

## Nota Importante

Los cambios de DNS pueden tardar entre 5 minutos y 48 horas en propagarse completamente, aunque generalmente es mucho más rápido (5-30 minutos).

## Post-migración y retiro de `chalanpro.net`

**Fecha objetivo de apagado (editable):** `2026-05-01`

Checklist:
- [ ] Mantener ambos dominios durante transición (`jobrithm.net` principal + `chalanpro.net` compatibilidad).
- [ ] Confirmar que `api.jobrithm.net` y `*.jobrithm.net` están estables (login, API, tenants).
- [ ] Aplicar redirecciones 301 desde `chalanpro.net` hacia `jobrithm.net`.
- [ ] Actualizar/validar renovación SSL para `jobrithm.net` (`renew_wildcard_certbot_auto_domain.sh`).
- [ ] En fecha objetivo, retirar registros DNS legacy de `chalanpro.net` (si ya no hay tráfico relevante).

Comando definitivo recomendado para renovación manual:

```bash
HOSTINGER_API_TOKEN=$(cat /root/.hostinger-api-token) /opt/chalanpro/scripts/renew_wildcard_certbot_auto_domain.sh --domain jobrithm.net --email admin@jobrithm.net
```

