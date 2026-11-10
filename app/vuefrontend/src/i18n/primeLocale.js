/**
 * Sync PrimeVue built-in labels / date formats with app locale.
 * Always deep-merge over PrimeVue defaults — a shallow replace of `aria`
 * drops keys like `pageLabel` and crashes Paginator/DataTable (URL changes,
 * view freezes).
 */
import { defaultOptions } from '@primevue/core/config'

function deepMerge(target, source) {
  const out = { ...target }
  for (const [key, value] of Object.entries(source || {})) {
    if (
      value &&
      typeof value === 'object' &&
      !Array.isArray(value) &&
      target?.[key] &&
      typeof target[key] === 'object' &&
      !Array.isArray(target[key])
    ) {
      out[key] = deepMerge(target[key], value)
    } else {
      out[key] = value
    }
  }
  return out
}

const BASE = defaultOptions.locale

const EN_OVERLAY = {
  // Keep US date conventions; rest inherits PrimeVue English defaults.
  firstDayOfWeek: 0,
  dateFormat: 'mm/dd/yy',
}

const ES_OVERLAY = {
  startsWith: 'Comienza con',
  contains: 'Contiene',
  notContains: 'No contiene',
  endsWith: 'Termina con',
  equals: 'Igual a',
  notEquals: 'Diferente de',
  noFilter: 'Sin filtro',
  lt: 'Menor que',
  lte: 'Menor o igual que',
  gt: 'Mayor que',
  gte: 'Mayor o igual que',
  dateIs: 'Fecha es',
  dateIsNot: 'Fecha no es',
  dateBefore: 'Fecha es anterior',
  dateAfter: 'Fecha es posterior',
  clear: 'Limpiar',
  apply: 'Aplicar',
  matchAll: 'Coincidir todo',
  matchAny: 'Coincidir cualquiera',
  addRule: 'Agregar regla',
  removeRule: 'Quitar regla',
  accept: 'Sí',
  reject: 'No',
  choose: 'Elegir',
  upload: 'Subir',
  cancel: 'Cancelar',
  completed: 'Completado',
  pending: 'Pendiente',
  dayNames: [
    'Domingo',
    'Lunes',
    'Martes',
    'Miércoles',
    'Jueves',
    'Viernes',
    'Sábado',
  ],
  dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
  dayNamesMin: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'],
  monthNames: [
    'Enero',
    'Febrero',
    'Marzo',
    'Abril',
    'Mayo',
    'Junio',
    'Julio',
    'Agosto',
    'Septiembre',
    'Octubre',
    'Noviembre',
    'Diciembre',
  ],
  monthNamesShort: [
    'Ene',
    'Feb',
    'Mar',
    'Abr',
    'May',
    'Jun',
    'Jul',
    'Ago',
    'Sep',
    'Oct',
    'Nov',
    'Dic',
  ],
  chooseYear: 'Elegir año',
  chooseMonth: 'Elegir mes',
  chooseDate: 'Elegir fecha',
  prevDecade: 'Década anterior',
  nextDecade: 'Década siguiente',
  prevYear: 'Año anterior',
  nextYear: 'Año siguiente',
  prevMonth: 'Mes anterior',
  nextMonth: 'Mes siguiente',
  prevHour: 'Hora anterior',
  nextHour: 'Hora siguiente',
  prevMinute: 'Minuto anterior',
  nextMinute: 'Minuto siguiente',
  prevSecond: 'Segundo anterior',
  nextSecond: 'Segundo siguiente',
  am: 'am',
  pm: 'pm',
  today: 'Hoy',
  weekHeader: 'Sem',
  firstDayOfWeek: 1,
  dateFormat: 'dd/mm/yy',
  weak: 'Débil',
  medium: 'Media',
  strong: 'Fuerte',
  passwordPrompt: 'Ingrese una contraseña',
  emptyFilterMessage: 'Sin resultados',
  searchMessage: '{0} resultados disponibles',
  selectionMessage: '{0} elementos seleccionados',
  emptySelectionMessage: 'Ningún elemento seleccionado',
  emptySearchMessage: 'Sin resultados',
  emptyMessage: 'Sin opciones disponibles',
  fileChosenMessage: '{0} archivos',
  noFileChosenMessage: 'Ningún archivo elegido',
  aria: {
    trueLabel: 'Verdadero',
    falseLabel: 'Falso',
    nullLabel: 'No seleccionado',
    star: '1 estrella',
    stars: '{star} estrellas',
    selectAll: 'Todos los elementos seleccionados',
    unselectAll: 'Ningún elemento seleccionado',
    close: 'Cerrar',
    previous: 'Anterior',
    next: 'Siguiente',
    navigation: 'Navegación',
    scrollTop: 'Ir arriba',
    moveTop: 'Mover al inicio',
    moveUp: 'Mover arriba',
    moveDown: 'Mover abajo',
    moveBottom: 'Mover al final',
    moveToTarget: 'Mover al destino',
    moveToSource: 'Mover al origen',
    moveAllToTarget: 'Mover todo al destino',
    moveAllToSource: 'Mover todo al origen',
    pageLabel: 'Página {page}',
    firstPageLabel: 'Primera página',
    lastPageLabel: 'Última página',
    nextPageLabel: 'Página siguiente',
    prevPageLabel: 'Página anterior',
    rowsPerPageLabel: 'Filas por página',
    jumpToPageDropdownLabel: 'Ir a página (lista)',
    jumpToPageInputLabel: 'Ir a página (entrada)',
    selectRow: 'Fila seleccionada',
    unselectRow: 'Fila deseleccionada',
    expandRow: 'Fila expandida',
    collapseRow: 'Fila contraída',
    showFilterMenu: 'Mostrar menú de filtro',
    hideFilterMenu: 'Ocultar menú de filtro',
    filterOperator: 'Operador de filtro',
    filterConstraint: 'Restricción de filtro',
    editRow: 'Editar fila',
    saveEdit: 'Guardar edición',
    cancelEdit: 'Cancelar edición',
    listView: 'Vista de lista',
    gridView: 'Vista de cuadrícula',
    slide: 'Diapositiva',
    slideNumber: '{slideNumber}',
    zoomImage: 'Ampliar imagen',
    zoomIn: 'Acercar',
    zoomOut: 'Alejar',
    rotateRight: 'Rotar a la derecha',
    rotateLeft: 'Rotar a la izquierda',
    listLabel: 'Lista de opciones',
  },
}

export function primeLocaleFor(lang) {
  const overlay = lang === 'es' ? ES_OVERLAY : EN_OVERLAY
  return deepMerge(BASE, overlay)
}

export function applyPrimeVueLocale(primevue, lang) {
  if (!primevue?.config) return
  const next = primeLocaleFor(lang)
  // Replace with a fresh deep-merged object so nested `aria` keeps every key.
  primevue.config.locale = next
}
