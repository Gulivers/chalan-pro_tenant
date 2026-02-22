Implementar Transfer Engine + 2 Menús (Warehouse Transfer / Assign Tools to Truck)

Necesito implementar en Chalan-Pro un sistema de transferencia de inventario entre warehouses que soporte ta
productos normales (por canti
como tools/equipment serializados (SerializedI
La idea es usar un solo motor/flujo de transferencia, pero exponerlo en el UI con dos opciones de m
✅ Modo A (Inventory): “Warehouse Transfer” (genér
Pensado para el encargado de inventa
Permite mover inventario entre cualquier wareho
✅ Modo B (Crews and Fleet): “Assign Tools to Truck” (frien
Pensado para la gerente de fl
Permite seleccionar una Truck y mover serialized items hacia el warehouse móvil de esa tr
No requiere que el usuario piense en “To Warehouse” manualmente.

Backend:
Crear/usar un endpoint único (idempotente y auditado) para ejecutar transferenc
Reglas de negocio (muy important
Validar from*warehouse_id != to_warehouse*
Validar que todos los serialized_item_ids pertenezcan al from_warehouse_id (su current_warehouse debe coincidir).

Para quantity ite
crear movimientos OUT del from y IN del
actualizar Stock correspondiente (si ya existe lógica, reusa
Para serialized items
crear movimientos OUT/IN (1 unidad por item, o como esté modelado
actualizar SerializedItem.current_warehouse = to_warehouse (esto es obligatorio
Responder con un resumen
transferred_coun
transferred_serialized_items (opcional
errors si aplica.

Frontend: Core reusable + 2 vistas
2.1 Componente core reusable

Crear componente:
InventoryTransferCore.vue
Responsabilidades del core:
manejar selección de origen/destino (según modo)
cargar data (warehouses, trucks, serialized items, products si aplica)
permitir seleccionar items (checkboxes para serialized, qty inputs para productos normales)
ejecutar POST /api/inventory/transfers/
mostrar confirmación (SweetAlert) y resultados (toast)
emitir eventos:
transfer:success
transfer:cancel
transfer:error

2.2 Vista Modo A: Warehouse Transfer

Crear view:
WarehouseTransferView.vue (menú Inventory)

UI:
From Warehouse (select)
To Warehouse (select)
Tabs o selector:
“Quantity Products”
“Serialized Tools”
Pra serialized:

tabla listando serialized items disponibles en From
filtros: status, condition, search
selección múltiple
Botón: “Transfer Selected”
Debe usar InventoryTransferCore con:
mode="warehouse_transfer"

2.3 Vista Modo B: Assign Tools to Truck

Crear view:
AssignToolsToTruckView.vue (menú Crews and Fleet)

UI:
Truck (select searchable)
al seleccionar truck, obtener su warehouse móvil asociado (to_warehouse)
mostrar “Truck Warehouse: <name>” readonly
(opcional) mostrar “Current Assigned Crew” solo informativo
From Warehouse (select)
Tabla de serialized items en From
Botón: “Assign to Truck” (transfer)
Debe usar InventoryTransferCore con:
mode="assign_to_truck"

lockToWarehouse=true
defaultReason="Assign to Truck"
o similar.

Rutas y menú

Agregar rutas:
/inventory/warehouse-transfer
/crews-fleet/assign-tools-to-truck
Agregar al navbar:
Inventory → Warehouse Transfer
Crews and Fleet → Assign Tools to Truck
Agregar en cada vista un link pequeño:
“Switch to Warehouse Transfer”
“Switch to Assign to Truck”
Definition of done
Modo A funciona (warehouse→warehouse) para serialized y qty.
Modo B funciona (warehouse→truck) para serialized.
Current Warehouse en SerializedItems se actualiza correctamente tras la transferencia.
No hay duplicación de lógica: el core se reusa.
UI consistente con el resto de Chalan-Pro.
