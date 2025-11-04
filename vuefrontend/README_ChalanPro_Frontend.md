# Proyecto Chalan-Pro - Estructura Frontend Vue.js

Bienvenido al sistema **Chalan-Pro** – un sistema robusto y modular para gestionar contratos, comunidades, cuadrillas, cronogramas y notas de obra. Este archivo te guiará sobre cómo está organizado el **frontend** con Vue.js para que puedas entrar al código con confianza y estilo. 

---

## 📁 Estructura del Proyecto

```bash
src/
│
├── assets/                  # Estilos globales, imágenes, íconos
│   ├── css/                 # Archivos CSS base
│   ├── scss/                # Estilos personalizados (ej: Bootstrap override)
│   └── img/                 # Logos, íconos, gráficos
│
├── components/              # Componentes Vue reutilizables y modulares
│   ├── layout/              # Navbar, Footer, Sidebar
│   ├── contracts/           # Formulario, charts, modales de contrato
│   ├── houses/              # Vista de mapa, notas, etc.
│   ├── schedule/            # Calendario, chats, discusiones
│   ├── inventory/           # Componentes de inventario, productos, precios
│   ├── transactions/        # Formularios de transacciones, party types, document types
│   └── buttons/             # Botones reutilizables del sistema
│
├── views/                   # Vistas principales del sistema (Login, Home, etc.)
│    │   AboutView.vue
│    │   HomeView.vue
│    │   LoginView.vue
│    ├── contract/            # Subvistas de contratos (WorkPrices, etc.)
│    ├── inventory/           # Vistas de inventario (productos, categorías, etc.)
│    └── transactions/        # Vistas de transacciones y party types
│
├── auth/                    # Servicios y lógica de autenticación (login, tokens)
├── router/                  # Configuración de rutas Vue Router
├── store/                   # Vuex (o Pinia) para manejo del estado global
├── utils/                   # Axios configs, helpers, funciones utilitarias
├── helpers/                 # Otros helpers y funciones personalizadas
├── mixins/                  # Mixins globales para reusar lógica (ej: authMixin)
├── types/                   # Archivos de definición de tipos (ej: vue-select.d.ts)
│
├── App.vue                 # Componente raíz
└── main.js                 # Punto de entrada principal de la app
```

---

## 🚀 Tips para Desarrolladores Nuevos

1. **Alias Everywhere!**
   - Usa alias como `@components`, `@views`, `@contracts`, etc.
   - ¡No más `../../../../../components/contracts` en tus imports!

   ```js
   import Navbar from '@components/layout/NavbarComponent.vue';
   import ContractForm from '@contracts/ContractFormComponent.vue';
   ```

2. **Separa por feature, no por tipo**
   - Cada módulo (como `contracts`, `schedule`) tiene sus propios componentes.
   - Más fácil escalar y mantener.

3. **Mantén tus imports limpios**
   - Prefiere PascalCase para componentes `.vue`
   - Usa helpers o mixins para lógica repetida

4. **No temas preguntar 🧠**
   - Si algo no está documentado, ¡pregunta o documenta tú mismo!

---

## 💬 Estándares del equipo

- Componentes `.vue`: PascalCase (ej: `ContractFormComponent.vue`)
- Vistas: `LoginView.vue`, `HomeView.vue`, etc.
- Estado global: por ahora se usa Vuex (en `store/`)

---

## 🧩 Recursos útiles

- [Documentación Vue.js](https://vuejs.org/guide/introduction.html)
- [Bootstrap 5.3 Docs](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
- [Axios](https://axios-http.com/)

---

# 🏗️ Patrón CRUD en el Sistema

Este patrón aplica a **todos los CRUD** del sistema:

- **Forms**: Bootstrap puro (sin `bootstrap-vue-next`).  
  ➡️ Éxito silencioso + redirección inmediata.  
- **Listas**: `bootstrap-vue-next` (`b-table`) para search/paginación client-side y acciones (view/edit/delete).  
- **Auth/axios**: No setear headers manualmente; la Pinia store de auth ya los inyecta.

---

## 📄 Formularios (Bootstrap only)

### 🔹 Estructura base (`script setup`)
- `id = route.query.id`
- `isViewMode = route.query.mode === 'view'`
- `isEditMode = !!id && !isViewMode`
- **onMounted**: si hay `id`, `GET /api/<resource>/:id/` y `form.value = data`

### 🔹 `handleSubmit`
- Trim + validación mínima (requeridos y longitudes).
- `POST /api/<resource>/` en **create**.
- `PUT /api/<resource>/:id/` en **edit**.
- ❌ Sin toasts ni alerts en éxito → **redirigir de una por nombre de ruta**.
- ✅ `SweetAlert` solo para errores (400/403/etc.).

### 🔹 UI
- Inputs `form-control` y `form-switch` de Bootstrap.
- Botones `btn-outline` (primary, secondary).
- **Modo view**: deshabilita todos los campos y oculta el botón **Save**.

Botón Save obligatorio:
```vue
<i v-else class="fas fa-save me-1"></i>
{{ submitting ? 'Saving...' : 'Save' }}

Redirección recomendada:

router.push({ name: 'party-types' }).catch(() => router.push('/party-types'))

📋 Listas (bootstrap-vue-next)

b-table con columns mínimas + actions (view/edit/delete).
Search client-side (b-form-input).
Entries per page (10, 25, 50, 100).
b-pagination.

🔹 Acciones

Create →
router.push({ name: 'party-types-form', query: { mode: 'create' }})
View →
router.push({ name: 'party-types-form', query: { mode: 'view', id }})
Edit →
router.push({ name: 'party-types-form', query: { mode: 'edit', id }})
Delete → con confirm de SweetAlert, luego fetch().

🧭 Rutas (patrón recomendado)

Dos rutas son suficientes:

// Lista
{ path: '/party-types', name: 'party-types', component: PartyTypeListView, meta: { requiresAuth: true } },
// Form multi-modo por query (?mode=view|edit|create&id=)
{ path: '/party-types/form', name: 'party-types-form', component: PartyTypeForm, meta: { requiresAuth: true } },

El form detecta el modo por query.
Si prefieres rutas separadas, asegúrate de mantener la misma lógica interna (trim, view mode, redirect por nombre).

🧩 Últimas 3 mejoras aplicadas a PartyTypeForm.vue

Trim antes de enviar.
Validación de longitud mínima.
Validación de requeridos antes del submit.

---
🧩 Patrón CRUD — Política de Unicidad y Validaciones (Chalan-Pro)

Usaremos unique=True en los modelos. ✅
Frontend, captura 400/403/otros y muestra Swal ✅
No usaremos validaciones a nivel de serializer ni view para tablas maestras con menos de 4 campos. ✅
Sí usaremos validaciones a nivel de serializer y view para tablas transaccionales con más de 1 campos ✅
(Opcional, recomendado): mapear errores de BD a 400 en el back cuando queramos mensajes por campo más consistentes en transaccionales.

---
<label class="col-12 col-sm-3 col-form-label text-start text-sm-end"> Este label se alinea a la derecha al input y se queda arriba en movil
<div class="row mt-4">
  <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
    <!-- botones iguales al ejemplo de arriba -->
  </div>
</div>


🔮 Clave: d-flex justify-content-center centra horizontalmente; gap-2 separa; y con la opción 2, flex-column flex-sm-row apila en pantallas chicas y alinea en fila desde sm.

---

## 🔧 Backend - Exception Handler

El sistema incluye un manejador personalizado de excepciones (`project/api/exception_handler.py`) que:

- **ProtectedError**: Captura intentos de eliminar registros que están en uso por otros modelos, devolviendo HTTP 409 con mensaje claro
- **IntegrityError**: Maneja violaciones de restricciones de base de datos (foreign keys, constraints) con el mismo patrón
- **Respuesta consistente**: Siempre devuelve `{"detail": "This record is in use and cannot be deleted. Inactivate it instead.", "code": "in_use"}` para estos casos
- **Frontend**: El frontend puede capturar estos errores 409 y mostrar mensajes apropiados al usuario

---

🔑 Notas sobre unicidad case-insensitive (MySQL vs Postgres)

MySQL 8 + utf8mb4_0900_ai_ci
ci = case-insensitive, ai = accent-insensitive.
Los índices únicos con esta collation ya impiden duplicados ignorando mayúsculas/minúsculas y acentos.
Ej.: "ACME", "acme" o "Ácme" se consideran el mismo valor → el UNIQUE falla.

Postgres
Los índices únicos son case-sensitive por defecto, la collation no cambia esto.
Necesitas usar:
CITEXT (tipo de dato case-insensitive), o
UniqueConstraint(Lower('campo'), name='uniq_lower_campo').

Django/DRF

El UniqueValidator ayuda a atrapar duplicados antes de que llegue a la BD.
En MySQL puede parecer redundante, pero mejora la UX (errores más rápidos y claros).

Para verificar case sentitive en la BD para que unique=True trabaje
  SHOW VARIABLES LIKE 'collation_%';
  SHOW FULL COLUMNS FROM apptransactions_partycategory LIKE 'name';
Si la columna name está en _ci, unique=True será case-insensitive para evitar duplicados de datos.

---

Patrón estándar de formularios (Chalan-Pro)

Encabezado principal centrado, color orange (h2.text-orange.text-center), sin fw-semibold.

Subtítulo dinámico con title = computed(() => isCreateMode ? 'Create …' : isViewMode ? 'View …' : 'Edit …') en h6.text-primary.text-center dentro del card-header.

Card base con class="card shadow mb-4" para sombra y separación vertical.

Formulario horizontal: labels a la izquierda usando grid (ej. row g-2, label.col-sm-3.col-form-label, control en col-sm-9).

Responsive: en móviles, labels alineados a la izquierda con media query:

@media (max-width: 576px){ .col-form-label{ text-align:left!important; } }


Validación de negocio mínima (cliente): longitudes, formato de email, enteros no negativos para ranks, etc. Mantener en función validateClient().

Validación de requeridos con SweetAlert2 (antes del submit):

const REQUIRED_LABELS = { name:'Name', ..., default_price_type:'Default Price Type' }
if (!validateRequiredFields()) {
  Swal.fire({ title:'Missing Required Fields', html: `<ul>${...}</ul>`, icon:'error' })
  return
}


Catálogos con auto-refresh: cargar catálogos primero y refrescar al volver/recuperar foco:

onActivated(() => refreshCatalogs(true));
window.addEventListener('focus', () => refreshCatalogs(true));


Botonera centrada al final:

<div class="mt-4 d-flex justify-content-center gap-2">
  <button class="btn btn-primary">Save</button>
  <button class="btn btn-secondary">Cancel</button>
</div>

---

### 🎯 Tooltip global `v-tt`

- Uso: `<input v-tt="'Texto del tooltip'">`  
- Posiciones: `v-tt:right`, `v-tt:left`, `v-tt:bottom`.  
- Estándar de formularios CRUD de Chalan-Pro.  
- Cierra automáticamente al cambiar de input, click fuera, `Tab` o `Esc`.

---

## 🛠️ En resumen
> Código limpio, modular
> ¡Aquí trabajamos con cariño y con buenas prácticas! 

¡Bienvenido a bordo de Chalan-Pro
