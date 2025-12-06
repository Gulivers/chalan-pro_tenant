# 🔍 Diagnóstico: URLs que no funcionan

## ✅ URLs que SÍ funcionan:
- ✅ `https://www.api.chalanpro.net/api/` → API Root (funciona)
- ✅ `https://www.chalanpro.net/login` → Login Frontend (funciona)

## ❌ URLs que NO funcionan:

### 1. Frontend: `https://www.chalanpro.net/onboarding`
**Problema**: La ruta `/onboarding` no está definida en el router de Vue.js.

**Solución**: ✅ **CORREGIDO** - Se agregó la ruta en `vuefrontend/src/router/index.js`:
```javascript
{
  path: '/onboarding',
  name: 'onboarding',
  component: OnboardingView,
  meta: { hideNavbar: true, requiresAuth: false },
}
```

**Estado**: Requiere rebuild del frontend en Render.

---

### 2. Backend: `https://www.api.chalanpro.net/admin/`
**Problema**: El middleware `TenantMainMiddleware` de django-tenants busca un tenant asociado al dominio `www.api.chalanpro.net`, pero no existe en la base de datos.

**Causa**: django-tenants requiere que cada dominio tenga un tenant asociado. Para acceder al admin global (schema `public`), necesitas crear un dominio asociado al tenant del schema `public`.

**Solución**: Crear un dominio para el schema `public` con `www.api.chalanpro.net` y `api.chalanpro.net`.

**Pasos para corregir**:

1. **Acceder a la shell de Render**:
   ```bash
   # En Render Dashboard → chalan-backend → Shell
   ```

2. **Ejecutar el siguiente script en la shell de Django**:
   ```python
   python manage.py shell
   ```

3. **Crear el dominio para el schema public**:
   ```python
   from tenants.models import Tenant, Domain
   from django_tenants.utils import get_public_schema_name
   
   # Obtener el tenant del schema public
   public_schema = get_public_schema_name()  # Retorna 'public'
   tenant = Tenant.objects.get(schema_name=public_schema)
   
   # Crear dominio www.api.chalanpro.net
   domain1, created1 = Domain.objects.get_or_create(
       domain='www.api.chalanpro.net',
       defaults={
           'tenant': tenant,
           'is_primary': True
       }
   )
   print(f"Dominio www.api.chalanpro.net: {'Creado' if created1 else 'Ya existía'}")
   
   # Crear dominio api.chalanpro.net (redirige a www.api.chalanpro.net)
   domain2, created2 = Domain.objects.get_or_create(
       domain='api.chalanpro.net',
       defaults={
           'tenant': tenant,
           'is_primary': False
       }
   )
   print(f"Dominio api.chalanpro.net: {'Creado' if created2 else 'Ya existía'}")
   
   # Verificar
   print("\nDominios configurados para schema public:")
   for d in Domain.objects.filter(tenant=tenant):
       print(f"  - {d.domain} (primary: {d.is_primary})")
   ```

4. **Verificar que funciona**:
   - Acceder a: `https://www.api.chalanpro.net/admin/`
   - Debería mostrar el login del admin de Django

---

## 📋 Resumen de Acciones Requeridas

### ✅ Completado:
1. ✅ Agregada ruta `/onboarding` al router de Vue.js
2. ✅ Documentación creada

### ⏳ Pendiente (requiere acción manual):
1. ⏳ **Rebuild del frontend en Render** para que la ruta `/onboarding` esté disponible
2. ⏳ **Crear dominios en la base de datos** para `www.api.chalanpro.net` y `api.chalanpro.net` asociados al schema `public`

---

## 🔧 Comandos para Ejecutar en Render Shell

### Opción 1: Script Python directo
```bash
python manage.py shell << EOF
from tenants.models import Tenant, Domain
from django_tenants.utils import get_public_schema_name

public_schema = get_public_schema_name()
tenant = Tenant.objects.get(schema_name=public_schema)

# Crear www.api.chalanpro.net
domain1, created1 = Domain.objects.get_or_create(
    domain='www.api.chalanpro.net',
    defaults={'tenant': tenant, 'is_primary': True}
)
print(f"www.api.chalanpro.net: {'Creado' if created1 else 'Ya existía'}")

# Crear api.chalanpro.net
domain2, created2 = Domain.objects.get_or_create(
    domain='api.chalanpro.net',
    defaults={'tenant': tenant, 'is_primary': False}
)
print(f"api.chalanpro.net: {'Creado' if created2 else 'Ya existía'}")

# Verificar
print("\nDominios para schema public:")
for d in Domain.objects.filter(tenant=tenant):
    print(f"  - {d.domain} (primary: {d.is_primary})")
EOF
```

### Opción 2: Usar el management command (RECOMENDADO) ✅
Ya existe un comando de gestión creado: `tenants/management/commands/setup_public_domains.py`

**Ejecutar en Render Shell**:
```bash
python manage.py setup_public_domains
```

Este comando:
- ✅ Crea automáticamente los dominios `www.api.chalanpro.net` y `api.chalanpro.net`
- ✅ Los asocia al schema `public`
- ✅ Marca `www.api.chalanpro.net` como dominio primario
- ✅ Muestra un resumen de los dominios configurados

**Ejemplo de salida**:
```
📋 Configurando dominios para schema "public" (tenant: Public Schema)

  ✅ ⭐ www.api.chalanpro.net: Creado (primary: True)
  ✅    api.chalanpro.net: Creado (primary: False)

📊 Resumen: 2 creados, 0 ya existían

🌐 Dominios configurados para schema public:
   - www.api.chalanpro.net ⭐ (PRIMARY)
   - api.chalanpro.net
```

---

## 🎯 Verificación Final

Después de completar las acciones pendientes:

1. ✅ `https://www.chalanpro.net/onboarding` → Debe mostrar el formulario de onboarding
2. ✅ `https://www.api.chalanpro.net/admin/` → Debe mostrar el login del admin de Django
3. ✅ `https://api.chalanpro.net/admin/` → Debe redirigir a `www.api.chalanpro.net/admin/`

---

**Fecha**: 2025-12-05  
**Estado**: Diagnóstico completado, soluciones documentadas

