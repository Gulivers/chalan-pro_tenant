export const dataTableMixin = {
  data() {
    return {
      dataTable: null,
    };
  },
  beforeUnmount() {
    // Limpiar DataTable antes de desmontar el componente
    this.destroyDataTable();
  },
  methods: {
    destroyDataTable() {
      if (this.dataTable && $.fn.dataTable && this.$refs && this.$refs[this.tableRef]) {
        const table = this.$refs[this.tableRef];
        if (table && $.fn.dataTable.isDataTable(table)) {
          try {
            this.dataTable.destroy();
            this.dataTable = null;
          } catch (error) {
            console.warn('Error destroying DataTable:', error);
          }
        }
      }
    },
    initDataTable(options = {}) {
      const table = this.$refs[this.tableRef];
      if (!table || !$.fn.dataTable) {
        return;
      }

      try {
        // Destruir DataTable existente si existe
        this.destroyDataTable();

        // Configuración por defecto
        const defaultOptions = {
          destroy: true,
          responsive: true,
          pageLength: 50,
          order: [[0, "desc"]],
          language: {
            search: "_INPUT_",
            searchPlaceholder: "Search...",
          },
        };

        // Combinar opciones por defecto con opciones personalizadas
        const finalOptions = { ...defaultOptions, ...options };

        // Inicializar nuevo DataTable
        this.dataTable = $(table).DataTable(finalOptions);
      } catch (error) {
        console.error('Error initializing DataTable:', error);
      }
    },
    safeInitDataTable(options = {}) {
      // Usar setTimeout para asegurar que el DOM esté completamente renderizado
      setTimeout(() => {
        if (this.items && this.items.length && this.$refs[this.tableRef]) {
          this.initDataTable(options);
        }
      }, 100);
    },
  },
}; 