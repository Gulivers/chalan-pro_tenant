# Configuración DNS en Hostinger (JobRhythm)

## IP del Servidor VPS
```
72.60.168.62
```

## Estado del cambio de dominio

- **Dominio principal actual de la web app:** `jobrhythm.net`
- **Dominio API/admin actual:** `api.jobrhythm.net`
- **Wildcard tenants actual:** `*.jobrhythm.net`
- **Landing marketing:** `getjobrhythm.com`, `www.getjobrhythm.com`
- **Dominios anteriores (paralelo 7–14 días):** `jobrithm.net`, `getjobrithm.com`, `chalanpro.net`

## Registros DNS requeridos (actual)

### 1. Registro A - Dominio Raíz (@)
**Tipo:** A  
**Nombre:** @  
**Points to:** 72.60.168.62  
**TTL:** 300 (migración) / 14400 (estable)

Este registro apunta el dominio principal `jobrhythm.net` al servidor.

### 2. Registro A - Subdominio API
**Tipo:** A  
**Nombre:** api  
**Points to:** 72.60.168.62  
**TTL:** 300 / 14400

Este registro apunta `api.jobrhythm.net` al servidor para el API REST y Admin de Django.

### 3. Registro A - Wildcard tenants (*)
**Tipo:** A  
**Nombre:** *  
**Points to:** 72.60.168.62  
**TTL:** 300 / 14400

Permite que cualquier subdominio tenant (ej: `phoenix.jobrhythm.net`) resuelva al VPS.

### 4. Registro CNAME - www
**Tipo:** CNAME  
**Nombre:** www  
**Points to:** jobrhythm.net  
**TTL:** 300 / 14400

### Landing (`getjobrhythm.com`)

| Tipo | Name | Points to | TTL |
|------|------|-----------|-----|
| **A** | @ | 72.60.168.62 | 300 |
| **CNAME** | www | getjobrhythm.com | 300 |

Los registros de correo (MX, SPF, DKIM) en `jobrhythm.net` se mantienen en Hostinger para `noreply@jobrhythm.net` y `team@jobrhythm.net`.

## Pasos para Configurar en Hostinger

1. **Panel DNS SaaS:** https://hpanel.hostinger.com/domain/jobrhythm.net/dns  
2. **Panel DNS landing:** https://hpanel.hostinger.com/domain/getjobrhythm.com/dns  
3. Añadir registros A (@, api, *) y CNAME www como en la tabla anterior.

## Verificación

```bash
nslookup jobrhythm.net
nslookup api.jobrhythm.net
nslookup phoenix.jobrhythm.net
nslookup getjobrhythm.com
nslookup www.getjobrhythm.com
```

Las consultas A deberían devolver **72.60.168.62**.

## URLs Finales

- **Frontend:** https://jobrhythm.net
- **Onboarding:** https://www.jobrhythm.net/onboarding
- **API REST:** https://api.jobrhythm.net/api/
- **Admin Django:** https://api.jobrhythm.net/admin/
- **Tenant Login:** https://{tenant}.jobrhythm.net/login/
- **Landing:** https://getjobrhythm.com

## Post-migración y retiro de dominios legacy

**Ventana de transición:** 7–14 días con ambos dominios activos (`jobrhythm` + `jobrithm`).

Checklist:
- [ ] Confirmar login, API, tenants y onboarding en `jobrhythm.net` / `getjobrhythm.com`.
- [ ] Verificar dominios primarios en `tenants_domain` (`*.jobrhythm.net`).
- [ ] Aplicar redirecciones 301 desde `jobrithm.net` y `getjobrithm.com` cuando el tráfico legacy sea bajo.
- [ ] Renovar wildcard SSL: `renew_wildcard_certbot_auto_domain.sh --domain jobrhythm.net --email admin@jobrhythm.net` (requiere `HOSTINGER_API_TOKEN` en el VPS).
- [ ] Retirar gradualmente `chalanpro.net` cuando no haya tráfico relevante.

```bash
HOSTINGER_API_TOKEN=$(cat /root/.hostinger-api-token) /opt/chalanpro/scripts/renew_wildcard_certbot_auto_domain.sh --domain jobrhythm.net --email admin@jobrhythm.net
```
