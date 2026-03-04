# AI Guidelines – Estándares del frontend del Proyecto

Clasificación por tipo de componente.

## Índice

- [Form](#form)
- [Tooltips en campos (v-tt)](#tooltips-en-campos-v-tt)
- [Selects: usar v-select (vue-select)](#selects-usar-v-select-vue-select)
- [Campos requeridos](#campos-requeridos)
- [Toast al guardar (crear/editar)](#toast-al-guardar-creareditar)
- [ViewList (b-table)](#viewlist-b-table)
- [Botón agregar registro (btn-success)](#botón-agregar-registro-btn-success)
- [Botones de acción (View, Edit, Delete)](#botones-de-acción-view-edit-delete)
- [Columna de estado (Status / Active)](#columna-de-estado-status--active)
- [Columna de acciones (Actions)](#columna-de-acciones-actions)
- [Alineación de columnas (labels y celdas)](#alineación-de-columnas-labels-y-celdas)
- [Lazy load (carga diferida) para listas transaccionales](#lazy-load-carga-diferida-para-listas-transaccionales)
- [Búsqueda por múltiples palabras (search)](#búsqueda-por-múltiples-palabras-search)
- [Ordenamiento local de los datos cargados](#ordenamiento-local-de-los-datos-cargados)
- [Encabezado de ListView (título, barra de estadísticas, filtros)](#encabezado-de-listview-título-barra-de-estadísticas-filtros)
- [Backend (Django)](#backend-django)
- [Migraciones tras cambios en modelos](#migraciones-tras-cambios-en-modelos)
- [Layout](#layout)
- [Buttons](#buttons)
- [Onboarding](#onboarding)

---

## Form

### Tooltips en campos (v-tt)

- Usar la directiva **`v-tt`** (tooltip) del proyecto para campos que necesiten ayuda contextual.
- En formularios de **DocumentType** (si existen en el frontend), el campo `creates_serialized_items` debe llevar **`v-tt`** y **`data-title`** en el control (p. ej. "Document type that creates/registers serialized items; opens the asset tag assignment modal when the document has serialized items (e.g. GRN)").
- El texto del tooltip va en **`data-title`**, en inglés.
- **Colocar `v-tt` y `data-title` en el propio control** (input, textarea, v-select o select), no en un icono `<i>`.
- **El label debe llevar solo texto**; no añadir icono de ayuda junto al label.

```html
<!-- Correcto: tooltip en el input -->
<label class="form-label" for="description">Description</label>
<input
  id="description"
  v-model.trim="form.description"
  type="text"
  class="form-control"
  v-tt
  data-title="Optional description or reference for this transfer" />

<!-- Correcto: tooltip en el v-select -->
<label class="form-label" for="from_warehouse">
  From Warehouse
  <span class="text-danger">*</span>
</label>
<v-select
  id="from_warehouse"
  v-model="form.from_warehouse"
  :options="warehousesOptions"
  :reduce="o => o.value"
  label="label"
  placeholder="Select warehouse..."
  v-tt
  data-title="Origin warehouse for the transfer" />

<!-- Para títulos de sección sin control: v-tt en el elemento de texto -->
<h6
  class="text-primary mb-2"
  v-tt
  data-title="Each line creates an OUT and an IN movement.">
  Lines (one line = two movements: OUT + IN)
</h6>
```

**No usar:** icono `<i v-tt ...></i>` junto al label para el tooltip del campo; el tooltip debe mostrarse al pasar el ratón o enfocar el input/select.

Referencia: `src/directives/tooltip.js`, `InventoryTransferForm.vue`, `SerializedItemForm.vue` (inputs con v-tt en el control).

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
  <span class="text-danger">*</span>
  Indicates required fields.
</p>
```

### Toast al guardar (crear/editar)

- Usar **`notifyToastSuccess`** del appMixin cuando se guarde un registro con éxito (crear o editar), en lugar de `Swal.fire('Success!', ...)`.
- Patrón: toast discreto + redirección a la lista.

```javascript
proxy?.notifyToastSuccess?.(id ? "Item updated." : "Item created.");
router.push({ name: "list-route" });
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
  class="btn btn-success">
  + New Category
</router-link>
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
  class="btn btn-outline-success me-1">
  View
</router-link>
<router-link
  v-if="hasPermission('crewsapp.change_category')"
  :to="`/crews/categories/edit/${data.item.id}`"
  class="btn btn-outline-primary me-1">
  Edit
</router-link>
<button
  v-if="hasPermission('crewsapp.delete_category')"
  @click="deleteItem(data.item.id)"
  class="btn btn-outline-danger">
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

### Lazy load (carga diferida) para listas transaccionales

- Usar **provider pattern** con BTable para listas con muchos registros (productos, contratos, ítems serializados, etc.).
- Endpoint backend tipo: `GET /api/xxx-provider/?page=1&per_page=25&search=&ordering=-id`. Respuesta: `{ items: [...], totalRows: N }`.
- En el BTable: `:provider="provider"`, `:filter="filter"`, `:per-page="perPage"`, `:current-page="currentPage"`.
- La función `provider(context)` recibe `context` con `currentPage`, `perPage`, `filter`, `sortBy` y devuelve la página de datos.

```html
<BTable
  ref="tableRef"
  :provider="provider"
  :fields="fields"
  :filter="filter"
  :per-page="perPage"
  :current-page="currentPage"
  no-provider-sorting
  bordered
  hover
  responsive
  striped />
```

Referencia: `ProductListView.vue`, `ContractListView.vue`, `SerializedItemListView.vue`.

### Búsqueda por múltiples palabras (search)

- El campo de búsqueda debe enviar el texto tal cual al backend en el parámetro **`search`** (p. ej. `context.filter` en el provider). El backend interpreta **varias palabras** separadas por espacios.
- **Backend (provider API):** partir `search` por espacios (`words = search.split()`). Para **cada palabra**, aplicar un filtro con un `Q` que haga **OR** entre los campos correspondientes a las columnas de la lista (nombre, SKU, categoría, etc.). Encadenar los filtros de todas las palabras (todas deben coincidir en algún campo). Si hay relaciones M2M o JOINs que puedan duplicar filas, usar **`.distinct()`**.
- **Frontend:** usar un único input de búsqueda; el placeholder puede indicar que se admiten varias palabras y enumerar los campos/columnas por los que se busca (p. ej. "Search by name, SKU, category... (multiple words)").

```python
# Backend (Django) – ejemplo en el endpoint provider
if search:
    words = search.split()
    for w in words:
        q = (
            Q(name__icontains=w) |
            Q(sku__icontains=w) |
            Q(category__name__icontains=w)
            # ... más campos según columnas de la lista
        )
        if w.isdigit():
            q = q | Q(id=w)
        queryset = queryset.filter(q).distinct()
```

```javascript
// Frontend – el provider pasa context.filter como search
const params = new URLSearchParams({
  page: context.currentPage || 1,
  per_page: context.perPage || 25,
  search: context.filter || "",
  ordering: getOrderingFromSortBy(context.sortBy) || "-id",
});
const response = await axios.get(`${ENDPOINT}?${params}`);
```

Referencia: `ProductListProviderAPIView` (appinventory/views.py), `ContractViewSet.contracts_provider` (ctrctsapp/views.py), `ProductListView.vue`, `ContractListView.vue`.

### Ordenamiento local de los datos cargados

- Usar **`no-provider-sorting`** en el BTable cuando se usa provider. Así, al hacer clic en un encabezado de columna se ordenan **localmente** los registros de la página actual, sin volver a llamar al provider ni al servidor.
- Evita peticiones extra al API y errores por formatos de `sortBy` incompatibles (ej. array vs objeto).
- Si el provider se llama tras un refresh (ej. botón "Refresh List"), `getOrderingFromSortBy` debe manejar el formato array de BTable: `[{key: 'id', order: 'desc'}]`.

```javascript
const getOrderingFromSortBy = (sortBy) => {
  if (!sortBy) return "-id";
  if (Array.isArray(sortBy) && sortBy.length > 0) {
    const first = sortBy[0];
    const field = first.key ?? first.field;
    const desc = (first.order ?? "asc") === "desc";
    return field ? (desc ? `-${field}` : field) : "-id";
  }
  const field = Object.keys(sortBy)[0];
  return sortBy[field] === "desc" ? `-${field}` : field;
};
```

### Encabezado de ListView (título, barra de estadísticas, filtros)

- **Título:** Usar `h5` con clases `text-primary mb-0 fw-semibold listview-title` (tamaño ~1.1rem). El botón de creación en el header debe ser `btn btn-success btn-sm` ("+ New …"). El contenedor del header: `d-flex flex-wrap justify-content-between align-items-center w-100 gap-2` para que en móvil título y botón se reacomoden.
- **Barra de estadísticas (toolbar):** Una sola barra con clase `listview-toolbar`: fondo suave (`background-color: rgba(13, 110, 253, 0.06)`), borde discreto, `padding: 0.5rem 0.75rem`, `border-radius: 0.375rem`. Contenido:
  - **Badges de estadísticas:** `badge bg-primary stats-badge`, `bg-success`, `bg-secondary` con texto breve (ej. "X Total", "X Active", "X Inactive"). Clase `.stats-badge`: `font-size: 0.7rem`, `font-weight: 500`, `padding: 0.25rem 0.5rem`.
  - **Separador:** `<span class="listview-toolbar-divider d-none d-sm-inline">` (línea vertical entre badges y botón, oculta en móvil).
  - **Botón Refresh:** `btn btn-outline-success btn-sm listview-refresh-btn` con texto "Refresh List". Clase `.listview-refresh-btn`: `padding: 0.2rem 0.6rem`, `font-size: 0.8rem`.
  - **Comportamiento al refrescar:** Al hacer clic en "Refresh List", mostrar un **overlay** sobre la tabla (sin recargar la página) con `BOverlay` (`:show="isLoading"`), texto "Loading…" (o "Loading [entidad]...") y `BSpinner` en el slot `#overlay`. El estado `isLoading` se pone a `true` al iniciar el fetch y a `false` en `finally`. Referencia: ContractListView.
- **Fila de filtros:** Contenedor `listview-filters row g-2 g-md-3 mb-3 align-items-end`. "entries per page" en `col-12 col-sm-6 col-lg-4 col-xl-3`, Search en `col-12 col-sm-6 col-lg-5 col-xl-4 ms-lg-auto`. Labels con `label-size="sm"` y estilo `.listview-filter-group label`: `font-size: 0.8rem`, `color: var(--bs-secondary-color)`. Inputs con `form-control-sm` / `form-select-sm`.

```html
<!-- Header del card -->
<template #header>
  <div
    class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
    <h5 class="text-primary mb-0 fw-semibold listview-title">Products</h5>
    <button
      v-if="hasPermission('appinventory.add_product')"
      class="btn btn-success btn-sm"
      @click="goToCreateForm">
      + New Product
    </button>
  </div>
</template>

<div class="card-body">
  <!-- Toolbar: stats + refresh -->
  <div class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
    <span class="badge bg-primary stats-badge">{{ stats.total }} Total</span>
    <span class="badge bg-success stats-badge">{{ stats.active }} Active</span>
    <span class="badge bg-secondary stats-badge">
      {{ stats.inactive }} Inactive
    </span>
    <span
      class="listview-toolbar-divider d-none d-sm-inline"
      aria-hidden="true"></span>
    <button
      type="button"
      class="btn btn-outline-success btn-sm listview-refresh-btn"
      @click="refreshTable">
      Refresh List
    </button>
  </div>

  <!-- Filters -->
  <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
    <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
      <BFormGroup
        label="entries per page:"
        label-for="per-page-select"
        label-size="sm"
        class="mb-0 listview-filter-group">
        <BFormSelect
          id="per-page-select"
          v-model="perPage"
          :options="pageOptions"
          size="sm"
          class="form-select form-select-sm" />
      </BFormGroup>
    </div>
    <div class="col-12 col-sm-6 col-lg-5 col-xl-4 ms-lg-auto">
      <BFormGroup
        label="Search:"
        label-for="filter-input"
        label-size="sm"
        class="mb-0 listview-filter-group">
        <BFormInput
          id="filter-input"
          v-model="filter"
          type="search"
          placeholder="Search..."
          size="sm"
          class="form-control form-control-sm" />
      </BFormGroup>
    </div>
  </div>
  <!-- BTable / tabla -->
</div>
```

**Estilos scoped recomendados** (incluir en la vista o en un CSS compartido):

```css
.listview-title {
  font-size: 1.1rem;
  letter-spacing: -0.01em;
}
.listview-toolbar {
  padding: 0.5rem 0.75rem;
  background-color: rgba(13, 110, 253, 0.06);
  border: 1px solid rgba(13, 110, 253, 0.12);
  border-radius: 0.375rem;
}
.listview-toolbar .stats-badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  line-height: 1.2;
}
.listview-toolbar-divider {
  width: 1px;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0.12);
  margin: 0 0.15rem;
}
.listview-refresh-btn {
  padding: 0.2rem 0.6rem;
  font-size: 0.8rem;
}
.listview-filters .listview-filter-group label {
  font-size: 0.8rem;
  color: var(--bs-secondary-color);
}
```

Referencia: `ProductListView.vue`, `ContractListView.vue`, `TransactionListView.vue`, `WorkAccountListView.vue`, `SerializedItemListView.vue`.

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

- **DocumentType (tipos de documento):** si se agrega, elimina o cambia algún campo en el modelo `apptransactions.DocumentType`, después de aplicar las migraciones hay que **regenerar el fixture maestro** que usan los tenants nuevos:

```bash
docker compose exec backend python manage.py generate_masters_inventory_fixture --schema test_dominio_local --output /app/appinventory/fixtures/masters_inventory.json
```

- Sin ejecutar `migrate_schemas`, los cambios no se reflejan en las empresas (tenants) y pueden aparecer errores como `column does not exist` o `no such column`.

---

## Layout

_(Estándares específicos de componentes de layout, ej. TxCard, headers, footers.)_

---

## Buttons

_(Estándares de botones: variantes, tamaños, iconos.)_

---

## Onboarding

_(Estándares del flujo de onboarding.)_
