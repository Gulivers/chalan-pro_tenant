"""
Sistema de Señales para Gestión Automática de Inventario

Este módulo implementa señales de Django que automatizan la sincronización
entre transacciones de documentos y movimientos de inventario.

Funcionalidades:
- Crear/actualizar movimientos de inventario al guardar líneas de documento
- Eliminar movimientos de inventario al eliminar líneas de documento
- Manejo automático de entradas/salidas de productos en almacenes
- Soporte para anulación/reactivación de documentos (is_active)
- Consistencia de datos mediante transacciones atómicas

Autor: Sistema Chalan-Pro
Versión: 2.0 - Con soporte para actualizaciones correctas de stock
"""

from decimal import Decimal
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
from apptransactions.models import DocumentLine, Document
from appinventory.models import InventoryMovement, Stock, SerializedItem, Warehouse, Product


MOBILE_WAREHOUSE_NAME = "Mobile Warehouse"


def get_or_create_mobile_warehouse():
    """Obtiene o crea el almacén 'Mobile Warehouse' para ítems serializados."""
    wh, created = Warehouse.objects.get_or_create(
        name=MOBILE_WAREHOUSE_NAME,
        defaults={'location': '', 'is_active': True, 'is_default': False}
    )
    return wh


@receiver(post_save, sender=DocumentLine, dispatch_uid="docline_create_inventory_movement")
def create_inventory_movement(sender, instance, created, **kwargs):
    """
    Crea o actualiza movimientos de inventario cuando se guarda una línea de documento.
    Para productos SERIALIZED en compras (entrada): crea N SerializedItems y N movimientos
    (uno por unidad) sin tocar Stock. Para el resto, un movimiento por cantidad.
    """
    print("2 🧼 apptransactions\\signals.py -> create_inventory_movement()")

    def handle_movement():
        try:
            if not instance.document.is_active:
                print(f"⏭️ Documento {instance.document.id} está anulado - No actualizar stock")
                InventoryMovement.objects.filter(line_id=instance.id).delete()
                SerializedItem.objects.filter(document_line_id=instance.id).delete()
                return

            warehouse = instance.warehouse or get_or_create_mobile_warehouse()
            doc_type = instance.document.document_type
            movement_type = doc_type.stock_movement

            if not warehouse or movement_type == 0:
                print(f"⏭️ Sin almacén o movimiento neutro para línea {instance.id}")
                return

            # --- Compra de producto SERIALIZED: N SerializedItems + N movimientos (quantity=1 cada uno)
            if (
                doc_type.is_purchase
                and movement_type == 1
                and instance.product.tracking_mode == Product.TRACKING_SERIALIZED
            ):
                InventoryMovement.objects.filter(line_id=instance.id).delete()
                SerializedItem.objects.filter(document_line_id=instance.id).delete()
                n = int(instance.quantity)
                if n < 1:
                    return
                purchase_date = instance.document.date
                for _ in range(n):
                    item = SerializedItem.objects.create(
                        product=instance.product,
                        document=instance.document,
                        document_line=instance,
                        current_warehouse=warehouse,
                        status=SerializedItem.STATUS_ACTIVE,
                        condition=SerializedItem.CONDITION_OK,
                        purchase_date=purchase_date,
                        asset_tag=None,
                    )
                    mov = InventoryMovement(
                        line_id=instance.id,
                        product=instance.product,
                        warehouse=warehouse,
                        quantity=Decimal('1'),
                        movement_type=1,
                        serialized_item=item,
                        unit=instance.unit,
                        reason=f"{doc_type.description} #{instance.document.id}",
                        document=str(instance.document.id),
                        created_by=instance.document.created_by,
                    )
                    mov.save()
                print(f"✅ Creados {n} SerializedItem(s) y movimientos para línea {instance.id}")
                return

            # --- Movimiento normal por cantidad
            movement = InventoryMovement.objects.filter(line_id=instance.id).first()

            if movement:
                print(f"♻️ Actualizando movimiento existente para línea {instance.id}")
                from appinventory.helpers import convert_to_reference_unit
                old_stock, _ = Stock.objects.get_or_create(
                    product=movement.product,
                    warehouse=movement.warehouse,
                    defaults={'quantity': Decimal('0.00')}
                )
                old_converted_qty = convert_to_reference_unit(
                    movement.product, movement.unit, movement.quantity
                )
                old_stock.quantity -= old_converted_qty * movement.movement_type
                old_stock.save()
                movement.product = instance.product
                movement.warehouse = warehouse
                movement.quantity = instance.quantity
                movement.movement_type = movement_type
                movement.unit = instance.unit
                movement.reason = f"{doc_type.description} #{instance.document.id}"
                movement.document = str(instance.document.id)
                movement.created_by = instance.document.created_by
                movement.save()
                print(f"✅ Movimiento actualizado para línea {instance.id}")
            else:
                print(f"🆕 Creando nuevo movimiento para línea {instance.id}")
                movement = InventoryMovement(
                    line_id=instance.id,
                    product=instance.product,
                    warehouse=warehouse,
                    quantity=instance.quantity,
                    movement_type=movement_type,
                    unit=instance.unit,
                    reason=f"{doc_type.description} #{instance.document.id}",
                    document=str(instance.document.id),
                    created_by=instance.document.created_by,
                )
                movement.save()
                print(f"✅ Nuevo movimiento creado para línea {instance.id}")

        except Exception as e:
            print(f"❌ Error en handle_movement(): {e}")
            import traceback
            traceback.print_exc()

    transaction.on_commit(handle_movement)


@receiver(pre_delete, sender=DocumentLine, dispatch_uid="docline_delete_inventory_movement")
def delete_inventory_movement(sender, instance, **kwargs):
    """
    Antes de borrar la línea: elimina movimientos (line_id) y SerializedItems (document_line)
    para evitar ProtectedError al hacer CASCADE desde DocumentLine.
    """
    try:
        InventoryMovement.objects.filter(line_id=instance.id).delete()
        SerializedItem.objects.filter(document_line_id=instance.id).delete()
        print(f"🗑️ Movimientos e ítems serializados eliminados para línea {instance.id}")
    except Exception as e:
        print(f"❌ Error al eliminar para línea {instance.id}: {e}")
        import traceback
        traceback.print_exc()


# Variable global para rastrear el estado anterior del documento
_document_previous_state = {}


@receiver(pre_save, sender=Document, dispatch_uid="document_track_previous_state")
def track_document_previous_state(sender, instance, **kwargs):
    """
    Guarda el estado anterior del documento antes de guardarlo.
    Esto permite detectar cambios en is_active.
    """
    if instance.pk:
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            _document_previous_state[instance.pk] = {
                'is_active': old_instance.is_active
            }
        except Document.DoesNotExist:
            pass


@receiver(post_save, sender=Document, dispatch_uid="document_handle_active_status")
def handle_document_active_status(sender, instance, created, **kwargs):
    """
    Maneja el stock cuando un documento se anula o reactiva.
    
    Casos:
    - Documento anulado (is_active=False): Elimina todos los InventoryMovements asociados
    - Documento reactivado (is_active=True): Recrea todos los InventoryMovements
    """
    if created:
        return  # Documento nuevo, las líneas se manejan en su propio signal
    
    def handle_status_change():
        try:
            # Obtener el estado anterior
            old_state = _document_previous_state.get(instance.pk, {})
            old_is_active = old_state.get('is_active', instance.is_active)
            
            # Limpiar el estado anterior
            if instance.pk in _document_previous_state:
                del _document_previous_state[instance.pk]
            
            # Si no cambió el estado is_active, no hacer nada
            if old_is_active == instance.is_active:
                return
            
            if not instance.is_active:
                # 🗑️ DOCUMENTO ANULADO: Eliminar movimientos e ítems serializados por línea
                print(f"📄 Anulando documento {instance.id} - Revirtiendo stock de todas las líneas")
                for line in instance.lines.all():
                    InventoryMovement.objects.filter(line_id=line.id).delete()
                    SerializedItem.objects.filter(document_line_id=line.id).delete()
                print(f"✅ Documento {instance.id} anulado - Stock revertido correctamente")

            else:
                # ✅ DOCUMENTO REACTIVADO: Recrear movimientos (y SerializedItems si aplica)
                print(f"📄 Reactivando documento {instance.id} - Aplicando stock de todas las líneas")
                doc_type = instance.document_type
                movement_type = doc_type.stock_movement
                for line in instance.lines.all():
                    warehouse = line.warehouse or get_or_create_mobile_warehouse()
                    if not warehouse or movement_type == 0:
                        continue
                    if InventoryMovement.objects.filter(line_id=line.id).exists():
                        continue
                    if (
                        doc_type.is_purchase
                        and movement_type == 1
                        and line.product.tracking_mode == Product.TRACKING_SERIALIZED
                    ):
                        n = int(line.quantity)
                        if n >= 1:
                            purchase_date = instance.date
                            for _ in range(n):
                                item = SerializedItem.objects.create(
                                    product=line.product,
                                    document=instance,
                                    document_line=line,
                                    current_warehouse=warehouse,
                                    status=SerializedItem.STATUS_ACTIVE,
                                    condition=SerializedItem.CONDITION_OK,
                                    purchase_date=purchase_date,
                                    asset_tag=None,
                                )
                                mov = InventoryMovement(
                                    line_id=line.id,
                                    product=line.product,
                                    warehouse=warehouse,
                                    quantity=Decimal('1'),
                                    movement_type=1,
                                    serialized_item=item,
                                    unit=line.unit,
                                    reason=f"{doc_type.description} #{instance.id} (Reactivado)",
                                    document=str(instance.id),
                                    created_by=instance.created_by,
                                )
                                mov.save()
                    else:
                        movement = InventoryMovement(
                            line_id=line.id,
                            product=line.product,
                            warehouse=warehouse,
                            quantity=line.quantity,
                            movement_type=movement_type,
                            unit=line.unit,
                            reason=f"{doc_type.description} #{instance.id} (Reactivado)",
                            document=str(instance.id),
                            created_by=instance.created_by,
                        )
                        movement.save()
                print(f"✅ Documento {instance.id} reactivado - Stock aplicado correctamente")
                
        except Exception as e:
            print(f"❌ Error al manejar cambio de estado del documento {instance.id}: {e}")
            import traceback
            traceback.print_exc()
    
    transaction.on_commit(handle_status_change)
