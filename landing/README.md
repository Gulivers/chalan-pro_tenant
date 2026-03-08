# Chalan-Pro – Web de marketing (Landing)

**Inspiración (nicho y segmento):**

> **Construction operations platform for residential trade contractors.**

En SaaS aplica la regla: *The riches are in the niches.* Cuanto más específico sea el problema que resuelves, más fácil es vender.

**Dónde entra el sistema (nicho de negocio):**

El producto está exactamente aquí:

```
              Enterprise Construction
                    |
                    |
    Builder PM ---- | ---- Field Service
                    |
                    |
           ⭐ CHALAN-PRO ZONE ⭐
   Residential trade contractors operations
                    |
                    |
                Small contractors
```

Ese espacio tiene:
- millones de empresas
- baja digitalización
- mucho dolor operativo

---

Sitio estático, orientado a SEO y conversión, para **chalanpro.com**. Presenta Chalan-Pro como plataforma de operaciones de construcción para contratistas residenciales, supervisores y equipos de campo.


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

| Comando              | Descripción                                        |
| -------------------- | -------------------------------------------------- |
| `npm install`        | Instalar dependencias (Tailwind, chokidar-cli)     |
| `npm run build`      | Generar `dist/` (CSS + copiar HTML, sitemap, etc.) |
| `npm run dev`        | Watch Tailwind (regenera solo CSS al guardar)      |
| `npm run build:watch`| Watch `src/`: ejecuta build completo al guardar   |
| `npm start`          | Servir `dist/` en http://localhost:3000            |

## Desarrollo local

**Opción A — Build completo al guardar (HTML + CSS + assets):**

**Terminal 1** — Watch y rebuild al guardar cualquier archivo en `src/`:

```bash
npm run build:watch
```

**Terminal 2** — Servir archivos:

```bash
npm start
```

**Opción B — Solo CSS en watch (más rápido si solo tocas estilos):**

**Terminal 1:** `npm run dev`  
**Terminal 2:** `npm start`

Abrir http://localhost:3000 en el navegador. Tras editar, recargar la página (F5).

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
