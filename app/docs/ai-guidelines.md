# AI Guidelines – Estándares del frontend del Proyecto

Clasificación por tipo de componente.

---

## Form

### Tooltips en campos (v-tt)

- Usar la directiva **`v-tt`** (tooltip) del proyecto para campos que necesiten ayuda contextual.
- El texto del tooltip va en **`data-title`**, en inglés.
- En inputs: añadir `v-tt` y `data-title` al elemento.
- En labels: usar un icono `<i v-tt class="fas fa-info-circle text-muted" data-title="..."></i>` junto al label.

```html
<!-- En input (como ProductForm) -->
<input
  v-model.trim="product.name"
  type="text"
  class="form-control"
  v-tt
  data-title="Product name for identification and display purposes" />

<!-- En label con icono -->
<label class="form-label d-flex align-items-center gap-2">
  Category
  <i
    v-tt
    class="fas fa-info-circle text-muted"
    data-title="Group products for filtering"></i>
</label>
```

Referencia: `src/directives/tooltip.js`

### Selects: usar v-select (vue-select)

- Usar **`v-select`** en lugar de `<select>` nativo para listas desplegables con opciones dinámicas.
- Importar: `import vSelect from 'vue-select'` y `import 'vue-select/dist/vue-select.css'`.
- Usar `:reduce` para vincular el valor (ej. `id`), `label` para mostrar el texto (propiedad o función).
- Añadir `v-tt` y `data-title` para tooltips contextuales.

```html
<v-select
  :options="categories"
  v-model="product.category"
  :reduce="cat => cat.id"
  label="name"
  placeholder="Select Category"
  :disabled="isReadOnly"
  v-tt
  data-title="Required field for product categorization" />
```

Referencia: `ProductForm.vue`, `CrewForm.vue`, `TruckAssignmentForm.vue`.

### Campos requeridos

- Usar `<span class="text-danger">*</span>` junto al label de los campos obligatorios.
- Incluir un mensaje pequeño debajo del formulario explicando el significado del asterisco.

```html
<p class="small text-muted mt-3 mb-0">
  <span class="text-danger">*</span> Indicates required fields.
</p>
```

### Toast al guardar (crear/editar)

- Usar **`notifyToastSuccess`** del appMixin cuando se guarde un registro con éxito (crear o editar), en lugar de `Swal.fire('Success!', ...)`.
- Patrón: toast discreto + redirección a la lista.

```javascript
proxy?.notifyToastSuccess?.(id ? 'Item updated.' : 'Item created.');
router.push({ name: 'list-route' });
```

---

## ViewList (b-table)

### Botón agregar registro (btn-success)

- Usar el texto **"+ New"** (no "+ Add") para el botón que abre el formulario de creación.
- Proteger con `v-if="hasPermission('app_label.add_model')"` usando el permiso de Django correspondiente.

```html
<router-link
  v-if="hasPermission('crewsapp.add_category')"
  to="/crews/categories/form"
  class="btn btn-success"
  >+ New Category</router-link
>
```

Referencia: `CategoryListView.vue`, `CrewListView.vue`, `TruckListView.vue`, `TruckAssignmentListView.vue`.

### Botones de acción (View, Edit, Delete)

- Proteger cada botón con `v-if="hasPermission('app_label.permission')"` según la acción:
  - View: `view_model`
  - Edit: `change_model`
  - Delete: `delete_model`

```html
<router-link
  v-if="hasPermission('crewsapp.view_category')"
  :to="`/crews/categories/view/${data.item.id}`"
  class="btn btn-outline-success me-1"
  >View</router-link
>
<router-link
  v-if="hasPermission('crewsapp.change_category')"
  :to="`/crews/categories/edit/${data.item.id}`"
  class="btn btn-outline-primary me-1"
  >Edit</router-link
>
<button
  v-if="hasPermission('crewsapp.delete_category')"
  @click="deleteItem(data.item.id)"
  class="btn btn-outline-danger"
>
  Delete
</button>
```

`hasPermission()` está disponible globalmente vía `appMixin.js`. Permisos por entidad: ver `router/index.js`.

### Columna de estado (Status / Active)

- Usar siempre el label **"Status"** en lugar de "Active" para columnas de estado (`is_active`, `status`, etc.).

```javascript
{ key: 'is_active', label: 'Status', thClass: 'text-center', tdClass: 'text-center', ... }
{ key: 'status', label: 'Status', thClass: 'text-center', tdClass: 'text-center', ... }
```

### Columna de acciones (Actions)

- Añadir `thStyle` y `tdStyle` a la columna de acciones para un ancho consistente y evitar saltos de línea en los botones:

```javascript
{
  key: 'actions',
  label: 'Actions',
  thClass: 'text-center',
  tdClass: 'text-center',
  thStyle: { width: '12%', whiteSpace: 'nowrap' },
  tdStyle: { whiteSpace: 'nowrap' },
},
```

### Alineación de columnas (labels y celdas)

- **Centradas** (`thClass: 'text-center'`, `tdClass: 'text-center'`): ID, Status, Actions, fechas, números, badges.
- **Alineadas a la izquierda** (`thClass: 'text-start'`, `tdClass: 'text-start'`): `name`, `description` y columnas de tipo texto (títulos, emails, direcciones, etc.).

```javascript
// Centradas
{ key: 'id', label: 'ID', thClass: 'text-center', tdClass: 'text-center' },
{ key: 'is_active', label: 'Status', thClass: 'text-center', tdClass: 'text-center' },

// Texto (izquierda)
{ key: 'name', label: 'Name', thClass: 'text-start', tdClass: 'text-start' },
{ key: 'description', label: 'Description', thClass: 'text-start', tdClass: 'text-start' },
```

---

## Backend (Django)

### Migraciones tras cambios en modelos

- Tras modificar modelos de Django, **crear las migraciones** y **ejecutarlas en todos los tenant schemas**.
- El proyecto es multi-tenant; usar `migrate_schemas` en lugar de `migrate` para aplicar cambios en cada schema.

```bash
# 1. Crear migraciones (desde el directorio app/ o con docker)
docker compose exec backend python manage.py makemigrations <app_name>

# 2. Aplicar en todos los tenant schemas
docker compose exec backend python manage.py migrate_schemas
```

- Sin ejecutar `migrate_schemas`, los cambios no se reflejan en las empresas (tenants) y pueden aparecer errores como `column does not exist` o `no such column`.

---

## Layout

*(Estándares específicos de componentes de layout, ej. TxCard, headers, footers.)*

---

## Buttons

*(Estándares de botones: variantes, tamaños, iconos.)*

---

## Onboarding

*(Estándares del flujo de onboarding.)*
