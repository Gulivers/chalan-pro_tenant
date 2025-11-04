// Tooltip global para Chalan-Pro
// Uso en templates:
//   v-tt="'Texto'"
//   v-tt:right="'Texto'"
//   v-tt:bottom="'Texto'"
//   v-tt:left="'Texto'"

const CLASS = 'cp-tt'
const ARROW = 'cp-tt-arrow'

// ÚNICO tooltip global reutilizable
const Tip = {
  el: null,
  currentEl: null,
  placement: 'top',

  ensure() {
    if (this.el) return this.el
    const t = document.createElement('div')
    t.className = CLASS
    // ------- estilos inline de respaldo (por si el CSS global no cargó) -------
    Object.assign(t.style, {
      position: 'absolute',
      background: '#000',
      color: '#fff',
      padding: '2px 4px',
      borderRadius: '4px',
      fontSize: '12px',
      lineHeight: '1.2',
      pointerEvents: 'none',
      zIndex: '2000',
      opacity: '0',
      transition: 'opacity .12s ease',
      boxShadow: '0 4px 16px rgba(0,0,0,.2)',
    })
    // --------------------------------------------------------------------------
    const textNode = document.createTextNode('')   // primer hijo siempre texto
    t.appendChild(textNode)
    const arrow = document.createElement('div')
    arrow.className = ARROW
    // estilos inline básicos del arrow (respaldo)
    Object.assign(arrow.style, {
      position: 'absolute',
      width: '0', height: '0',
      border: '6px solid transparent',
    })
    t.appendChild(arrow)

    document.body.appendChild(t)
    this.el = t
    return t
  },

  setText(text) {
    if (!this.el) return
    // el primer hijo es SIEMPRE el nodo de texto
    this.el.firstChild.nodeValue = text ?? ''
  },

  setArrow() {
    if (!this.el) return
    const arrow = this.el.lastChild
    // limpiar
    arrow.style.borderTopColor = 'transparent'
    arrow.style.borderBottomColor = 'transparent'
    arrow.style.borderLeftColor = 'transparent'
    arrow.style.borderRightColor = 'transparent'
    // colocar según placement
    if (this.placement === 'top') {
      Object.assign(arrow.style, {
        bottom: '-12px', left: '50%', transform: 'translateX(-50%)',
        borderTopColor: '#000', borderBottomWidth: '0',
      })
    } else if (this.placement === 'bottom') {
      Object.assign(arrow.style, {
        top: '-12px', left: '50%', transform: 'translateX(-50%)',
        borderBottomColor: '#000', borderTopWidth: '0',
      })
    } else if (this.placement === 'left') {
      Object.assign(arrow.style, {
        top: '50%', right: '-12px', transform: 'translateY(-50%)',
        borderLeftColor: '#000', borderRightWidth: '0',
      })
    } else { // right
      Object.assign(arrow.style, {
        top: '50%', left: '-12px', transform: 'translateY(-50%)',
        borderRightColor: '#000', borderLeftWidth: '0',
      })
    }
  },

  showFor(el, text, placement = 'top') {
    const tip = this.ensure()
    this.currentEl = el
    this.placement = placement
    this.setText(text)
    tip.dataset.placement = placement
    this.setArrow()
    this.position(el)
    // mostrar
    tip.style.opacity = '1'
  },

  hide(el = null) {
    if (!this.el) return
    if (el && el !== this.currentEl) return
    this.el.style.opacity = '0'
    this.currentEl = null
  },

  position(el) {
    if (!this.el) return
    const tip = this.el
    const rect = el.getBoundingClientRect()
    const tipRect = tip.getBoundingClientRect()
    const gap = 8
    let top = 0, left = 0, transform = ''

    switch (this.placement) {
      case 'bottom':
        top  = rect.bottom + gap + window.scrollY
        left = rect.left + rect.width / 2 + window.scrollX
        transform = 'translate(-50%, 8px)'
        break
      case 'left':
        top  = rect.top + rect.height / 2 + window.scrollY
        left = rect.left - gap + window.scrollX
        transform = 'translate(-100%, -50%)'
        break
      case 'right':
        top  = rect.top + rect.height / 2 + window.scrollY
        left = rect.right + gap + window.scrollX
        transform = 'translate(0, -50%)'
        break
      default: // top
        top  = rect.top - gap + window.scrollY
        left = rect.left + rect.width / 2 + window.scrollX
        transform = 'translate(-50%, -8px)'
    }

    // clamp horizontal
    const vw = document.documentElement.clientWidth
    const maxLeft = vw - tipRect.width - 8
    const minLeft = 8
    left = Math.max(minLeft, Math.min(left, maxLeft))

    tip.style.top = `${Math.round(top)}px`
    tip.style.left = `${Math.round(left)}px`
    tip.style.transform = transform
  }
}

function onGlobalScrollOrResize() {
  if (Tip.currentEl && Tip.el && Tip.el.style.opacity === '1') {
    Tip.position(Tip.currentEl)
  }
}

function onGlobalKeydown(e) {
  if (e.key === 'Escape' || e.key === 'Esc' || e.key === 'Tab') {
    Tip.hide()
  }
}

const directive = {
  mounted(el, binding) {
    const text = binding?.value || el.getAttribute('data-title') || el.getAttribute('title')
    if (!text) return
    el.setAttribute('data-title', text)
    el.removeAttribute('title') // evitar nativo

    const placement = binding?.arg || el.getAttribute('data-placement') || 'top'

    // Abrir SIEMPRE reemplazando el actual
    const open = () => {
      Tip.showFor(el, el.getAttribute('data-title'), placement)
    }
    const close = () => Tip.hide(el)

    const onEnter = open
    const onLeave = close
    const onFocus = open
    const onBlur  = close
    const onClick = open

    const onDocClick = (e) => {
      if (!Tip.el || Tip.el.style.opacity !== '1') return
      if (el.contains(e.target)) return
      Tip.hide()
    }

    el.addEventListener('mouseenter', onEnter)
    el.addEventListener('mouseleave', onLeave)
    el.addEventListener('focus', onFocus, true)
    el.addEventListener('blur', onBlur, true)
    el.addEventListener('click', onClick)
    document.addEventListener('click', onDocClick)
    window.addEventListener('scroll', onGlobalScrollOrResize, true)
    window.addEventListener('resize', onGlobalScrollOrResize)
    document.addEventListener('keydown', onGlobalKeydown)

    el._ttHandlers = { onEnter, onLeave, onFocus, onBlur, onClick, onDocClick }
  },

  updated(el, binding) {
    const newText = binding?.value
    if (typeof newText === 'string' && newText.length) {
      el.setAttribute('data-title', newText)
      if (Tip.currentEl === el && Tip.el && Tip.el.style.opacity === '1') {
        Tip.setText(newText)
        Tip.position(el)
      }
    }
  },

  unmounted(el) {
    const h = el._ttHandlers
    if (h) {
      el.removeEventListener('mouseenter', h.onEnter)
      el.removeEventListener('mouseleave', h.onLeave)
      el.removeEventListener('focus', h.onFocus, true)
      el.removeEventListener('blur', h.onBlur, true)
      el.removeEventListener('click', h.onClick)
      document.removeEventListener('click', h.onDocClick)
      el._ttHandlers = null
    }
    if (Tip.currentEl === el) Tip.hide()
  },
}

export default {
  install(app) {
    app.directive('tt', directive)
  }
}
