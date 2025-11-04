# 📊 Análisis del Sistema de Stock de Inventario

> **🎉 SOLUCIÓN IMPLEMENTADA - Ver [IMPLEMENTACION_STOCK_V2.md](IMPLEMENTACION_STOCK_V2.md) para instrucciones de prueba**

## 🔍 ¿Cómo funciona actualmente el sistema?

### Flujo de Actualización de Stock

```
1. Usuario crea/edita una transacción (DocumentLine)
   ↓
2. Se ejecuta DocumentLine.save() 
   ↓
3. Se dispara la señal post_save → create_inventory_movement()
   ↓
4. Se crea/actualiza un InventoryMovement
   ↓
5. InventoryMovement.save() convierte cantidad y ACTUALIZA STOCK automáticamente
   ↓
6. Stock se actualiza en la tabla Stock
```

## ✅ El sistema SÍ actualiza el stock automáticamente

**Ubicación del código:** `appinventory/models.py`, líneas 223-228

```python
# Ajustar el stock
stock, _ = Stock.objects.get_or_create(product=self.product, warehouse=self.warehouse)
old_qty = stock.quantity
stock.quantity += self.quantity * self.movement_type
stock.save()
```

## ❌ Problemas Identificados

### Problema 1: Actualización de InventoryMovement existente

**Ubicación:** `apptransactions/signals.py`, líneas 40-49

Cuando se actualiza un `DocumentLine` existente:
- Se busca el `InventoryMovement` asociado
- Se actualizan los valores (cantidad, producto, almacén, etc.)
- **⚠️ NO se revierte el cambio anterior en el Stock**
- Se guarda el movimiento (que suma al stock nuevamente)
- **Resultado:** El stock queda mal calculado (se suma dos veces)

### Problema 2: Conversión de cantidad doble

**Ubicación:** `appinventory/models.py`, línea 205

```python
self.quantity = converted_qty  # ⚠️ Sobrescribe la cantidad original
```

Cuando se actualiza un `InventoryMovement`:
1. La cantidad original ya fue convertida en el primer `save()`
2. Al actualizar, se intenta convertir nuevamente
3. Esto causa inconsistencias en las cantidades

### Problema 3: Datos históricos sin stock

Si ya existen transacciones antes de implementar las señales:
- No tienen `InventoryMovement` asociados
- El stock no se actualiza para esas transacciones
- **Solución:** Ejecutar `recalculate_stock` una vez

## 🔧 Soluciones Propuestas

### Solución 1: Mejorar el signal de actualización ⭐ RECOMENDADA

Modificar `apptransactions/signals.py` para:

1. **Detectar si es creación o actualización**
2. **Si es actualización:** 
   - Revertir el cambio anterior en el stock
   - Aplicar el nuevo cambio
3. **Si es creación:**
   - Solo crear el movimiento nuevo

### Solución 2: Separar la cantidad convertida

Crear un campo nuevo en `InventoryMovement`:
- `quantity`: Cantidad original (sin convertir)
- `converted_quantity`: Cantidad en unidad de referencia (calculada)

Esto evita sobrescribir la cantidad original y permite recalcular correctamente.

### Solución 3: Usar el comando recalculate_stock (Solución actual)

**Cuándo usar:**
- Después de importar datos históricos
- Cuando el stock está desincronizado
- Para corregir inconsistencias

**Limitaciones:**
- Requiere intervención manual
- No es automático
- Puede causar tiempo de inactividad

## 📝 Recomendación Final

### Para actualización inmediata y automática:

**Implementar Solución 1** modificando el signal para manejar correctamente las actualizaciones:

```python
@receiver(post_save, sender=DocumentLine, dispatch_uid="docline_create_inventory_movement")
def create_inventory_movement(sender, instance, created, **kwargs):
    def handle_movement():
        try:
            warehouse = instance.warehouse
            doc_type = instance.document.document_type
            movement_type = doc_type.stock_movement

            if not warehouse or movement_type == 0:
                return

            # Buscar movimiento existente
            movement = InventoryMovement.objects.filter(line_id=instance.id).first()

            if movement:
                # ✅ ACTUALIZACIÓN: Revertir cambio anterior
                old_stock, _ = Stock.objects.get_or_create(
                    product=movement.product, 
                    warehouse=movement.warehouse
                )
                old_stock.quantity -= movement.quantity * movement.movement_type
                old_stock.save()
                
                # Actualizar movimiento con nuevos valores
                movement.product = instance.product
                movement.warehouse = warehouse
                movement.quantity = instance.quantity  # Cantidad original
                movement.movement_type = movement_type
                movement.unit = instance.unit
                movement.reason = f"{doc_type.description} #{instance.document.id}"
                movement.document = str(instance.document.id)
                movement.created_by = instance.document.created_by
            else:
                # ✅ CREACIÓN: Nuevo movimiento
                movement = InventoryMovement(
                    line_id=instance.id,
                    product=instance.product,
                    warehouse=warehouse,
                    quantity=instance.quantity,
                    movement_type=movement_type,
                    unit=instance.unit,
                    reason=f"{doc_type.description} #{instance.document.id}",
                    document=str(instance.document.id),
                    created_by=instance.document.created_by
                )

            movement.save()  # Esto aplicará el nuevo cambio al stock

        except Exception as e:
            print(f"❌ Error en handle_movement(): {e}")
            import traceback
            traceback.print_exc()

    transaction.on_commit(handle_movement)
```

### Ventajas de esta solución:

✅ Stock se actualiza automáticamente en tiempo real
✅ No requiere ejecutar comandos manualmente
✅ Maneja correctamente creaciones y actualizaciones
✅ Mantiene consistencia en el stock
✅ Los usuarios ven el stock actualizado inmediatamente

### Pasos para implementar:

1. ✅ Ejecutar `recalculate_stock` una vez (para corregir datos históricos)
2. ✅ Aplicar la solución propuesta en `signals.py`
3. ✅ Agregar campo `converted_quantity` en `InventoryMovement` (opcional pero recomendado)
4. ✅ Probar con transacciones nuevas
5. ✅ Verificar que el stock se actualiza correctamente

## 🎯 Momento de actualización del stock

Con la solución implementada, el stock se actualizará:

- ✅ **Inmediatamente** al crear una nueva transacción
- ✅ **Inmediatamente** al editar una transacción existente
- ✅ **Inmediatamente** al eliminar una transacción
- ✅ **Sin necesidad de ejecutar comandos manuales**
- ✅ **En tiempo real para el usuario**

## 🚀 Beneficios para el usuario

- Ver stock actualizado en tiempo real
- No esperar a procesos batch o comandos manuales
- Mejor experiencia de usuario
- Mayor confiabilidad del sistema
- Menos errores de inventario

