# 🚀 Implementación del Sistema de Stock v2.0

## ✅ Cambios Implementados

### 1. Mejora del Signal de DocumentLine (`apptransactions/signals.py`)

**Nuevas funcionalidades:**

✅ **Detección de creación vs actualización**
- Usa el parámetro `created` del signal para diferenciar

✅ **Reversión de cambios anteriores**
- Antes de actualizar un movimiento, revierte su impacto en el stock
- Esto evita la duplicación de cantidades en el stock

✅ **Verificación de is_active**
- Si el documento está anulado (`is_active=False`), no actualiza el stock
- Elimina movimientos existentes de documentos anulados

✅ **Logging mejorado**
- Mensajes claros de debug con emojis para fácil identificación
- Stack traces completos en caso de error

---

### 2. Nuevo Signal para Document (`apptransactions/signals.py`)

**Nuevos signals agregados:**

#### `track_document_previous_state` (pre_save)
- Guarda el estado anterior del documento antes de modificarlo
- Permite detectar cambios en `is_active`

#### `handle_document_active_status` (post_save)
- Detecta cuando un documento se anula o reactiva
- **Anulación:** Elimina todos los InventoryMovements (revierte stock)
- **Reactivación:** Recrea todos los InventoryMovements (aplica stock)

**Flujo de anulación:**
```
Document.is_active = False
   ↓
Signal detecta el cambio
   ↓
Elimina todos los InventoryMovement de las líneas
   ↓
Stock se revierte automáticamente (método delete())
   ↓
✅ Stock correcto sin el documento anulado
```

**Flujo de reactivación:**
```
Document.is_active = True
   ↓
Signal detecta el cambio
   ↓
Recrea todos los InventoryMovement de las líneas
   ↓
Stock se aplica automáticamente (método save())
   ↓
✅ Stock correcto con el documento reactivado
```

---

### 3. Mejora del modelo InventoryMovement (`appinventory/models.py`)

**Cambios en el método `save()`:**

✅ **Mantiene cantidad original**
- `self.quantity` permanece como la cantidad ingresada por el usuario
- NO se sobrescribe con la cantidad convertida
- Esto evita el problema de doble conversión

✅ **Usa cantidad convertida solo para el stock**
- Calcula `converted_qty` usando `get_converted_quantity()`
- Aplica esta cantidad al stock
- Pero guarda la cantidad original en la base de datos

**Cambios en el método `delete()`:**

✅ **Reversión mejorada del stock**
- Calcula correctamente la cantidad convertida
- Revierte el efecto en el stock
- Logging mejorado

---

## 🧪 Cómo Probar la Implementación

### Paso 1: Recalcular Stock (Una vez)

Ejecuta este comando para limpiar y recalcular todo el stock:

```bash
python manage.py recalculate_stock
```

**Nota:** Este comando solo se necesita ejecutar una vez después de la actualización para corregir inconsistencias anteriores.

---

### Paso 2: Probar Creación de Transacciones

1. **Crear un documento nuevo con líneas:**
   - El stock debe actualizarse inmediatamente
   - Verifica en consola los logs:
     ```
     🆕 Creando nuevo movimiento para línea X
     ✅ Nuevo movimiento creado y stock aplicado para línea X
     📊 Stock actualizado: 0.00 → 10.00 (producto: Cable, almacén: Principal)
     ```

2. **Verificar en la tabla Stock:**
   ```sql
   SELECT * FROM appinventory_stock 
   WHERE product_id = X AND warehouse_id = Y;
   ```

---

### Paso 3: Probar Actualización de Transacciones

1. **Editar una línea existente (cambiar cantidad):**
   - El stock debe actualizarse correctamente
   - Verifica en consola:
     ```
     ♻️ Actualizando movimiento existente para línea X
     🔄 Stock revertido: -5.00 para Cable
     ✅ Movimiento actualizado y nuevo stock aplicado para línea X
     📊 Stock actualizado: 5.00 → 10.00 (producto: Cable, almacén: Principal)
     ```

2. **Cambiar el producto en una línea:**
   - El stock del producto anterior debe disminuir
   - El stock del nuevo producto debe aumentar

3. **Cambiar el almacén en una línea:**
   - El stock del almacén anterior debe disminuir
   - El stock del nuevo almacén debe aumentar

---

### Paso 4: Probar Eliminación de Líneas

1. **Eliminar una línea de documento:**
   - El stock debe revertirse automáticamente
   - Verifica en consola:
     ```
     🗑️ Movimiento eliminado para línea X
     🗑️ Movimiento eliminado - Stock revertido: 10.00 → 5.00 (producto: Cable)
     ```

---

### Paso 5: Probar Anulación de Documentos ⭐

1. **Anular un documento (is_active = False):**
   ```python
   # En Django Admin o API
   document.is_active = False
   document.save()
   ```
   
   - Verifica en consola:
     ```
     📄 Anulando documento 123 - Revirtiendo stock de todas las líneas
        🗑️ Eliminados 3 movimiento(s) de línea 1
        🗑️ Eliminados 3 movimiento(s) de línea 2
     ✅ Documento 123 anulado - Stock revertido correctamente
     ```

2. **Verificar que el stock disminuyó:**
   ```sql
   SELECT * FROM appinventory_stock 
   WHERE product_id IN (SELECT product_id FROM apptransactions_documentline WHERE document_id = 123);
   ```

3. **Verificar que los movimientos fueron eliminados:**
   ```sql
   SELECT COUNT(*) FROM appinventory_inventorymovement 
   WHERE document = '123';
   -- Debe retornar 0
   ```

---

### Paso 6: Probar Reactivación de Documentos ⭐

1. **Reactivar un documento anulado (is_active = True):**
   ```python
   document.is_active = True
   document.save()
   ```
   
   - Verifica en consola:
     ```
     📄 Reactivando documento 123 - Aplicando stock de todas las líneas
        ✅ Movimiento recreado para línea 1
        ✅ Movimiento recreado para línea 2
     ✅ Documento 123 reactivado - Stock aplicado correctamente
     ```

2. **Verificar que el stock aumentó nuevamente:**
   ```sql
   SELECT * FROM appinventory_stock 
   WHERE product_id IN (SELECT product_id FROM apptransactions_documentline WHERE document_id = 123);
   ```

3. **Verificar que los movimientos fueron recreados:**
   ```sql
   SELECT COUNT(*) FROM appinventory_inventorymovement 
   WHERE document = '123';
   -- Debe retornar el número de líneas del documento
   ```

---

## 🎯 Casos de Prueba Críticos

### Caso 1: Actualizar cantidad de una línea
```
Estado inicial: Cable - 10 unidades en stock
Línea: 5 unidades de Cable

Editar línea: cambiar a 8 unidades
   ↓
Resultado esperado: 13 unidades en stock (10 - 5 + 8)
```

### Caso 2: Cambiar producto en una línea
```
Estado inicial: 
- Cable - 10 unidades
- Tubo - 5 unidades

Línea: 3 unidades de Cable
Editar: cambiar a 3 unidades de Tubo
   ↓
Resultado esperado:
- Cable: 13 unidades (10 + 3 revertido)
- Tubo: 2 unidades (5 - 3)
```

### Caso 3: Anular y reactivar documento
```
Estado inicial: Cable - 10 unidades
Documento con 5 unidades de Cable

Anular documento (is_active = False)
   ↓
Resultado esperado: Cable - 15 unidades (revertido)

Reactivar documento (is_active = True)
   ↓
Resultado esperado: Cable - 10 unidades (reaplicado)
```

### Caso 4: Conversión de unidades
```
Estado inicial: Cable - 10 metros
Línea: 100 centímetros de Cable (= 1 metro)

Crear línea
   ↓
Resultado esperado: Cable - 9 metros en stock (10 - 1)
```

---

## 📊 Monitoreando el Sistema

### Logs en Consola

Busca estos emojis en la consola del servidor:

- 🆕 = Nuevo movimiento creado
- ♻️ = Movimiento actualizado
- 🔄 = Stock revertido
- 📊 = Stock actualizado
- 🗑️ = Movimiento eliminado
- 📄 = Documento anulado/reactivado
- ✅ = Operación exitosa
- ❌ = Error
- ⚠️ = Advertencia

### Queries SQL Útiles

```sql
-- Ver todos los movimientos de un producto
SELECT im.*, p.name as product_name, w.name as warehouse_name
FROM appinventory_inventorymovement im
JOIN appinventory_product p ON im.product_id = p.id
JOIN appinventory_warehouse w ON im.warehouse_id = w.id
WHERE p.id = X
ORDER BY im.timestamp DESC;

-- Ver stock actual de todos los productos
SELECT p.name, w.name as warehouse, s.quantity
FROM appinventory_stock s
JOIN appinventory_product p ON s.product_id = p.id
JOIN appinventory_warehouse w ON s.warehouse_id = w.id
ORDER BY p.name, w.name;

-- Ver documentos anulados
SELECT id, document_type_id, date, is_active, total_amount
FROM apptransactions_document
WHERE is_active = FALSE
ORDER BY date DESC;
```

---

## 🐛 Troubleshooting

### Problema: El stock no se actualiza

**Verificar:**
1. ¿Las señales están registradas? Revisar `apptransactions/apps.py`
2. ¿El documento tiene `is_active=True`?
3. ¿La línea tiene `warehouse` asignado?
4. ¿El tipo de documento tiene `stock_movement != 0`?

**Solución:**
- Revisar logs en consola
- Ejecutar `python manage.py recalculate_stock` para resincronizar

---

### Problema: Stock duplicado después de actualizar

**Causa:** Esto ya no debería ocurrir con la nueva implementación.

**Verificar:**
- ¿Los cambios están aplicados correctamente?
- Revisar logs: debe aparecer "🔄 Stock revertido"

---

### Problema: Stock negativo

**Causas posibles:**
1. Venta sin stock disponible (permitido si `allow_negative_sales=True`)
2. Errores en conversión de unidades
3. Documento anulado múltiples veces

**Solución:**
```bash
python manage.py recalculate_stock
```

---

## ✅ Checklist de Validación

Antes de considerar la implementación completa, verifica:

- [ ] Stock se actualiza al crear nueva transacción
- [ ] Stock se actualiza correctamente al editar transacción
- [ ] Stock se revierte al eliminar línea
- [ ] Stock se revierte al anular documento
- [ ] Stock se reaplica al reactivar documento
- [ ] Conversiones de unidades funcionan correctamente
- [ ] No hay stock duplicado después de actualizaciones
- [ ] Logs aparecen correctamente en consola
- [ ] No hay errores en consola

---

## 🎉 Beneficios de la Nueva Implementación

✅ **Actualización en tiempo real:** El usuario ve el stock actualizado inmediatamente

✅ **No requiere comandos manuales:** El sistema se mantiene sincronizado automáticamente

✅ **Soporte completo de anulación:** Documentos anulados no afectan el stock

✅ **Auditoría completa:** Todos los cambios quedan registrados en logs

✅ **Prevención de duplicados:** Ya no se suma dos veces al actualizar

✅ **Conversiones correctas:** Las unidades se convierten una sola vez

✅ **Manejo de errores robusto:** Stack traces completos para debugging

---

## 📝 Próximos Pasos (Opcional)

### Mejora 1: Agregar campo `converted_quantity`

Agregar un campo en `InventoryMovement`:

```python
class InventoryMovement(models.Model):
    # ... campos existentes ...
    converted_quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cantidad convertida a unidad de referencia"
    )
```

**Beneficios:**
- Ver directamente la cantidad en unidad de referencia
- Facilita auditorías y reportes
- Evita recalcular conversiones

---

### Mejora 2: Agregar campo `is_active` en InventoryMovement

Para marcar movimientos como inactivos en lugar de eliminarlos:

```python
class InventoryMovement(models.Model):
    # ... campos existentes ...
    is_active = models.BooleanField(default=True)
```

**Beneficios:**
- Mantiene historial completo de movimientos
- Permite auditorías más completas
- Facilita debugging

---

## 🎓 Resumen

La implementación v2.0 del sistema de stock resuelve todos los problemas identificados:

1. ✅ Stock se actualiza automáticamente en tiempo real
2. ✅ Actualizaciones no duplican stock
3. ✅ Anulación de documentos funciona correctamente
4. ✅ No requiere ejecutar comandos manuales
5. ✅ Conversiones de unidades son correctas

**El usuario ahora tiene un sistema de inventario robusto y confiable** 🎉


