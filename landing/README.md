# Chalan-Pro – Web de marketing (Landing)

Sitio estático, orientado a SEO y conversión, para **chalanpro.com**. Presenta Chalan-Pro como plataforma de operaciones de construcción para contratistas, supervisores y equipos de campo.

**No es la app interna.** Es la web pública que explica el producto, capta leads (demo, contacto, precios) y soporta el crecimiento orgánico.

Arrancar servidor: npm start  
Construir cambios: npm run build

## Stack

- **HTML** estático
- **Tailwind CSS** compilado con npm (CLI)
- **JavaScript** vanilla mínimo (solo cuando haga falta)
- Sin Vue, React, Alpine ni jQuery en la landing

## Estructura de archivos

```
landing/
├── dist/                      # Build de producción (generado, no editar)
│   ├── output.css             # CSS compilado y minificado
│   ├── index.html
│   ├── pricing.html
│   ├── contact.html
│   ├── sitemap.xml
│   ├── robots.txt
│   └── img/                   # Imágenes copiadas desde src/img
│
├── src/                       # Fuentes (editar aquí)
│   ├── input.css              # Entrada Tailwind
│   ├── index.html             # Página principal
│   ├── pricing.html           # Precios
│   ├── contact.html           # Contacto
│   ├── sitemap.xml
│   ├── robots.txt
│   └── img/                   # Imágenes (opcional)
│
├── docs/
│   └── ai-guidelines.md       # Estándares para IA y desarrolladores
│
├── package.json
├── tailwind.config.js         # Config Tailwind (colores, fuentes)
├── README.md                  # Este archivo
└── AGENTS.md                  # Contexto para agentes de IA
```

## Comandos

| Comando         | Descripción                                        |
| --------------- | -------------------------------------------------- |
| `npm install`   | Instalar dependencias (Tailwind)                   |
| `npm run build` | Generar `dist/` (CSS + copiar HTML, sitemap, etc.) |
| `npm run dev`   | Watch Tailwind (regenera CSS al guardar)           |
| `npm start`     | Servir `dist/` en http://localhost:3000            |

## Desarrollo local

**Terminal 1** — Watch CSS:

```bash
npm run dev
```

**Terminal 2** — Servir archivos:

```bash
npm start
```

Abrir http://localhost:3000 en el navegador. Tras editar estilos o HTML, recargar la página (F5).

## Diseño y conversión

- **Diseño:** B2B SaaS moderno (referencias: Stripe, Linear, Notion; sector: Buildertrend, Procore, ServiceTitan). Limpio, profesional, con jerarquía clara y CTAs visibles.
- **Conversión:** Cada página debe incluir value proposition, indicador de confianza (o placeholder) y CTA above the fold + CTA cerca del final. Objetivos principales: reservar demo, contactar ventas, ver precios.

Detalle en **`docs/ai-guidelines.md`**.

## Deploy (chalanpro.com)

1. **Build:** `npm run build`
2. **Nginx:** Configurado en `../nginx/default.conf` para chalanpro.com y www.chalanpro.com
3. **Docker:** El volumen `./landing/dist` se monta en el contenedor nginx
4. **SSL:** Obtener certificado Let's Encrypt cuando corresponda
5. **Reiniciar nginx:** `docker compose restart nginx` (en el entorno de producción)

## Documentación

- **Estándares y guías:** `docs/ai-guidelines.md`
- **Agentes IA:** `AGENTS.md`
- **Proyecto principal (app):** `../AGENTS.md` (raíz del repo)
