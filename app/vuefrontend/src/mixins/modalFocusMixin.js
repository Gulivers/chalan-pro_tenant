export default {
  methods: {
    /**
     * Maneja el foco al mostrar un modal
     * @param {HTMLElement} modalElement - Elemento del modal
     * @param {string} selector - Selector para el primer elemento a enfocar
     */
    handleModalShow(modalElement, selector = 'input[type="text"], input[type="date"]') {
      if (!modalElement) return
      
      // Enfocar el primer campo después de que el modal se muestre
      this.$nextTick(() => {
        const firstInput = modalElement.querySelector(selector)
        if (firstInput) {
          firstInput.focus()
        }
      })
    },

    /**
     * Maneja el foco al ocultar un modal
     * @param {HTMLElement} modalElement - Elemento del modal
     */
    handleModalHide(modalElement) {
      // Quitar el foco antes de ocultar el modal
      if (document.activeElement) {
        document.activeElement.blur()
      }
      
      // Verificar si hay elementos con foco dentro del modal
      if (modalElement) {
        const focusedElement = modalElement.querySelector(':focus')
        if (focusedElement) {
          focusedElement.blur()
        }
      }
    },

    /**
     * Configura event listeners para manejo de foco en modales
     * @param {HTMLElement} modalElement - Elemento del modal
     */
    setupModalFocusHandling(modalElement) {
      if (!modalElement) return
      
      // Agregar event listener para manejar el foco cuando se oculta el modal
      modalElement.addEventListener('hidden.bs.modal', () => {
        this.handleModalHide(modalElement)
      })
    }
  }
}
