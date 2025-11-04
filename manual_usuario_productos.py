#!/usr/bin/env python3
"""
Script para crear el manual de usuario de productos en el modelo ManualEntry
Ejecutar con: python manage.py shell < manual_usuario_productos.py
"""

from appcore.models import ManualCategory, ManualEntry

# Crear categoría si no existe
category, created = ManualCategory.objects.get_or_create(
    name="Inventario",
    defaults={
        'description': "Manuales relacionados con la gestión de inventario y productos",
    }
)

print(f"Categoría {'creada' if created else 'encontrada'}: {category.name}")

# Contenido del manual de usuario
manual_content = """# 📦 Manual de Usuario: Creación de Productos con Precios

## 🎯 ¿Qué aprenderás en este manual?

Este manual te enseñará paso a paso cómo crear productos en el sistema ChalanPro, configurar sus precios y realizar transacciones exitosas. Al finalizar podrás:

- ✅ Crear productos nuevos con toda su información
- ✅ Configurar precios para diferentes tipos de clientes
- ✅ Manejar diferentes unidades de medida (piezas, rollos, galones, etc.)
- ✅ Realizar ventas y compras correctamente
- ✅ Solucionar problemas comunes

---

## 🚀 Paso 1: Preparar la Información del Producto

### Antes de crear un producto, necesitas tener:

**📋 Información Básica:**
- **Nombre del producto**: Ej: "Cable THHN 12 AWG Negro"
- **Código SKU**: Ej: "THHN-12-BLK" (debe ser único)
- **Categoría**: Ej: "Cables y Alambres", "Equipos Eléctricos"
- **Marca**: Ej: "SIEMENS", "LEVITON" (opcional)

**💰 Información de Precios:**
- **Precio de lista**: Precio base del producto
- **Precio de costo**: Lo que te cuesta comprarlo
- **Precios especiales**: Para mayoristas, contratistas, etc.

**📏 Información de Medidas:**
- **Unidad principal**: ¿Se vende por pieza, por pie, por rollo, por galón?
- **Otras unidades**: ¿También se puede vender en otras presentaciones?

---

## 📝 Paso 2: Crear el Producto

### 2.1 Acceder al Módulo de Inventario

1. **Inicia sesión** en ChalanPro
2. **Navega** al menú "Inventario" → "Productos"
3. **Haz clic** en "Nuevo Producto"

### 2.2 Llenar la Información Básica

**Campos Obligatorios:**
- **Nombre**: Nombre descriptivo del producto
- **SKU**: Código único (sin espacios, usar guiones)
- **Categoría**: Selecciona de la lista desplegable
- **Unidad por Defecto**: La unidad principal de venta

**Campos Opcionales:**
- **Marca**: Si el producto tiene marca específica
- **Nivel de Reorden**: Cantidad mínima antes de reabastecer

### 2.3 Ejemplo Práctico: Cable THHN

```
Nombre: Cable THHN 12 AWG Negro
SKU: THHN-12-BLK
Categoría: Cables y Alambres
Marca: SIEMENS
Unidad por Defecto: Pie (FT)
Nivel de Reorden: 100
```

---

## 💰 Paso 3: Configurar Precios

### 3.1 Tipos de Precio Disponibles

El sistema maneja diferentes tipos de precio:

| Tipo | Descripción | Cuándo usar |
|------|-------------|-------------|
| **LIST** | Precio de lista | Precio base de referencia |
| **COST** | Precio de costo | Para calcular ganancias |
| **SALE** | Precio de venta | Precio al público general |
| **WHOLESALE** | Precio mayorista | Para compradores grandes |
| **CONTRACTOR** | Precio contratista | Para contratistas especializados |

### 3.2 Configurar Precios por Unidad

**Ejemplo: Cable THHN con múltiples presentaciones**

**Por Pie (unidad principal):**
- Precio LIST: $1.25 por pie
- Precio COST: $0.81 por pie (65% del precio lista)
- Precio WHOLESALE: $1.00 por pie (80% del precio lista)

**Por Rollo de 250 pies:**
- Precio LIST: $275.00 por rollo
- Precio COST: $178.75 por rollo

**Por Rollo de 1000 pies:**
- Precio LIST: $1,050.00 por rollo
- Precio COST: $682.50 por rollo

### 3.3 Configurar Precios Paso a Paso

1. **En la sección "Precios"** del formulario de producto
2. **Haz clic** en "Agregar Precio"
3. **Selecciona** el tipo de precio
4. **Selecciona** la unidad de medida
5. **Ingresa** el precio
6. **Marca** si es precio por defecto (solo uno por unidad)
7. **Marca** si se usa para ventas y/o compras
8. **Repite** para cada precio diferente

---

## 🏪 Paso 4: Configurar Almacén

### 4.1 Almacén Predeterminado

El sistema necesita saber en qué almacén se guarda el producto:

1. **Ve** a "Inventario" → "Almacenes"
2. **Verifica** que existe un almacén marcado como "Predeterminado"
3. **Si no existe**, crea uno y márcalo como predeterminado

**Importante**: Solo puede haber un almacén predeterminado en todo el sistema.

### 4.2 Ejemplo de Configuración

```
Nombre: Almacén Principal
Ubicación: Bodega Central - Piso 1
Predeterminado: ✓ (marcado)
Activo: ✓ (marcado)
```

---

## 🛒 Paso 5: Realizar Transacciones

### 5.1 Crear una Venta

1. **Ve** a "Transacciones" → "Nueva Venta"
2. **Selecciona** el cliente
3. **Agrega productos**:
   - Busca el producto por nombre o SKU
   - El sistema carga automáticamente:
     - Precio por defecto
     - Unidad por defecto
     - Almacén predeterminado
     - Marca del producto
4. **Ajusta** si es necesario:
   - Cambiar cantidad
   - Cambiar unidad (pie → rollo)
   - Cambiar precio
   - Cambiar almacén
5. **Guarda** la transacción

### 5.2 Ejemplo de Línea de Venta

```
Producto: Cable THHN 12 AWG Negro
Cantidad: 50
Unidad: Pie (FT)
Precio Unitario: $1.25
Descuento: 0%
Subtotal: $62.50
Almacén: Almacén Principal
Marca: SIEMENS
```

---

## 🔄 Paso 6: Conversiones Automáticas

### 6.1 ¿Cómo Funciona?

El sistema convierte automáticamente entre unidades:

**Ejemplos:**
- Vendes 1 rollo de 250FT → Sistema registra 250 pies en inventario
- Vendes 24 pulgadas → Sistema registra 2 pies en inventario
- Compras 1 galón → Sistema registra 1 galón en inventario

### 6.2 Unidades Comunes

| Producto | Compra | Venta | Inventario |
|----------|--------|-------|------------|
| **Cables** | Rollos 250FT | Por pie o rollo | En pies totales |
| **Tuberías** | Sticks 10FT | Por pie o stick | En pies totales |
| **Interruptores** | Cajas de 25 | Individual | Por pieza |
| **Líquidos** | Galones | Por galón, cuarto o pinta | En galones |

---

## ⚠️ Problemas Comunes y Soluciones

### Problema 1: "No se encuentra precio por defecto"

**¿Qué significa?** El producto no tiene un precio marcado como predeterminado.

**Solución:**
1. Ve al producto
2. En la sección precios
3. Marca uno de los precios como "Por Defecto"
4. Guarda los cambios

### Problema 2: "No hay almacén predeterminado"

**¿Qué significa?** El sistema no sabe dónde guardar el producto.

**Solución:**
1. Ve a "Inventario" → "Almacenes"
2. Crea un almacén si no existe
3. Márcalo como "Predeterminado"
4. Asegúrate que esté activo

### Problema 3: "SKU ya existe"

**¿Qué significa?** Ya hay otro producto con el mismo código.

**Solución:**
1. Cambia el SKU por uno único
2. Usa formato: MARCA-TIPO-TAMAÑO-COLOR
3. Ejemplo: "THHN-12-BLK" en lugar de "Cable Negro"

### Problema 4: "Conversión de unidades falla"

**¿Qué significa?** Las unidades no están configuradas correctamente.

**Solución:**
1. Contacta al administrador del sistema
2. Verifica que las unidades de medida estén configuradas
3. Asegúrate de usar las unidades correctas

---

## 📊 Consejos para Mejorar tu Trabajo

### ✅ Mejores Prácticas

**Para Nombres de Productos:**
- Usa nombres descriptivos y claros
- Incluye información técnica importante
- Mantén consistencia en el formato

**Para SKUs:**
- Usa códigos cortos y fáciles de recordar
- Incluye información del producto en el código
- Evita espacios y caracteres especiales

**Para Precios:**
- Configura siempre un precio por defecto
- Mantén precios actualizados
- Usa diferentes tipos según tu negocio

**Para Inventario:**
- Revisa niveles de reorden regularmente
- Mantén almacenes organizados
- Actualiza cantidades después de movimientos

### 🎯 Casos de Uso Reales

**Caso 1: Empresa Eléctrica**
- Productos: Cables, interruptores, tuberías
- Unidades: Pies, rollos, piezas
- Precios: LIST, COST, CONTRACTOR

**Caso 2: Ferretería**
- Productos: Herramientas, materiales
- Unidades: Piezas, cajas, galones
- Precios: LIST, COST, WHOLESALE

**Caso 3: Distribuidor**
- Productos: Variedad amplia
- Unidades: Múltiples por producto
- Precios: Todos los tipos disponibles

---

## 🔍 Verificar que Todo Funciona

### Checklist Final

Antes de usar el producto en transacciones, verifica:

- [ ] **Producto creado** con nombre y SKU únicos
- [ ] **Categoría asignada** correctamente
- [ ] **Marca configurada** si aplica
- [ ] **Unidad por defecto** seleccionada
- [ ] **Al menos un precio** configurado
- [ ] **Precio por defecto** marcado
- [ ] **Almacén predeterminado** configurado
- [ ] **Nivel de reorden** establecido

### Prueba Rápida

1. **Crea una venta de prueba** con el producto
2. **Verifica** que se cargan los datos automáticamente
3. **Cambia** unidad y precio si es necesario
4. **Guarda** la transacción
5. **Revisa** que el inventario se actualiza correctamente

---

## 📞 ¿Necesitas Ayuda?

### Recursos Disponibles

**En el Sistema:**
- **Ayuda contextual**: Iconos de información en cada campo
- **Validaciones**: El sistema te avisa si falta algo
- **Mensajes de error**: Te indican qué corregir

**Contacto:**
- **Administrador del sistema**: Para problemas técnicos
- **Supervisor**: Para dudas sobre procesos
- **Manual técnico**: Para información avanzada

### Actualizaciones

Este manual se actualiza regularmente. Siempre consulta la versión más reciente para obtener la información más actualizada.

---

## ✨ Resumen

Crear productos en ChalanPro es un proceso sencillo cuando sigues estos pasos:

1. **Prepara** toda la información necesaria
2. **Crea** el producto con datos básicos
3. **Configura** precios para diferentes tipos de cliente
4. **Verifica** que el almacén predeterminado esté configurado
5. **Prueba** creando una transacción de ejemplo

Con esta configuración completa, podrás realizar ventas y compras de manera eficiente y precisa.

**¡Tu sistema está listo para manejar productos de manera profesional!** 🎉
"""

# Crear el manual
manual, created = ManualEntry.objects.get_or_create(
    title="Manual de Usuario: Creación de Productos con Precios",
    defaults={
        'module': 'Inventario',
        'summary': 'Guía completa paso a paso para crear productos, configurar precios y realizar transacciones en el sistema ChalanPro. Incluye ejemplos prácticos, solución de problemas comunes y mejores prácticas.',
        'content': manual_content,
        'category': category,
        'is_active': True,
    }
)

if created:
    print(f"✅ Manual creado exitosamente: {manual.title}")
    print(f"📁 Categoría: {manual.category.name}")
    print(f"🔗 Slug: {manual.slug}")
else:
    print(f"ℹ️ Manual ya existe: {manual.title}")
    print("🔄 Actualizando contenido...")
    manual.content = manual_content
    manual.save()
    print("✅ Contenido actualizado")

print(f"\n📊 Estadísticas:")
print(f"   - Total categorías: {ManualCategory.objects.count()}")
print(f"   - Total manuales: {ManualEntry.objects.count()}")
print(f"   - Manuales activos: {ManualEntry.objects.filter(is_active=True).count()}")
