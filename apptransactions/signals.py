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
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from apptransactions.models import DocumentLine, Document
from appinventory.models import InventoryMovement, Stock


@receiver(post_save, sender=DocumentLine, dispatch_uid="docline_create_inventory_movement")
def create_inventory_movement(sender, instance, created, **kwargs):
    """
    Crea o actualiza movimientos de inventario cuando se guarda una línea de documento.
    
    Mejoras v2.0:
    - Detecta si es creación o actualización
    - Revierte cambios anteriores en el stock antes de aplicar nuevos cambios
    - Verifica el estado is_active del documento padre
    """
    print("2 🧼 apptransactions\\signals.py -> create_inventory_movement()")
    
    def handle_movement():
        try:
            # ✅ Verificar si el documento está activo
            if not instance.document.is_active:
                print(f"⏭️ Documento {instance.document.id} está anulado - No actualizar stock")
                # Si el documento está anulado, eliminar movimientos existentes
                InventoryMovement.objects.filter(line_id=instance.id).delete()
                return
            
            warehouse = instance.warehouse
            doc_type = instance.document.document_type
            movement_type = doc_type.stock_movement

            if not warehouse or movement_type == 0:
                print(f"⏭️ Sin almacén o movimiento neutro para línea {instance.id}")
                return

            # Buscar si ya existe un movimiento para esta línea
            movement = InventoryMovement.objects.filter(line_id=instance.id).first()

            if movement:
                print(f"♻️ Actualizando movimiento existente para línea {instance.id}")
                
                # ✅ PASO 1: Revertir el impacto anterior en el stock
                # Obtener el stock actual
                old_stock, _ = Stock.objects.get_or_create(
                    product=movement.product,
                    warehouse=movement.warehouse,
                    defaults={'quantity': Decimal('0.00')}
                )
                
                # Calcular cantidad convertida del movimiento anterior
                from appinventory.helpers import convert_to_reference_unit
                old_converted_qty = convert_to_reference_unit(
                    movement.product, 
                    movement.unit, 
                    movement.quantity
                )
                
                # Revertir el cambio anterior
                old_stock.quantity -= old_converted_qty * movement.movement_type
                old_stock.save()
                print(f"🔄 Stock revertido: -{old_converted_qty * movement.movement_type} para {movement.product.name}")
                
                # ✅ PASO 2: Actualizar el movimiento con los nuevos valores
                movement.product = instance.product
                movement.warehouse = warehouse
                movement.quantity = instance.quantity  # Cantidad original sin convertir
                movement.movement_type = movement_type
                movement.unit = instance.unit
                movement.reason = f"{doc_type.description} #{instance.document.id}"
                movement.document = str(instance.document.id)
                movement.created_by = instance.document.created_by
                
                # El save() del InventoryMovement aplicará el nuevo cambio al stock
                movement.save()
                print(f"✅ Movimiento actualizado y nuevo stock aplicado para línea {instance.id}")
                
            else:
                print(f"🆕 Creando nuevo movimiento para línea {instance.id}")
                movement = InventoryMovement(
                    line_id=instance.id,
                    product=instance.product,
                    warehouse=warehouse,
                    quantity=instance.quantity,  # Cantidad original sin convertir
                    movement_type=movement_type,
                    unit=instance.unit,
                    reason=f"{doc_type.description} #{instance.document.id}",
                    document=str(instance.document.id),
                    created_by=instance.document.created_by
                )
                movement.save()
                print(f"✅ Nuevo movimiento creado y stock aplicado para línea {instance.id}")

        except Exception as e:
            print(f"❌ Error en handle_movement(): {e}")
            import traceback
            traceback.print_exc()

    transaction.on_commit(handle_movement)


@receiver(post_delete, sender=DocumentLine, dispatch_uid="docline_delete_inventory_movement")
def delete_inventory_movement(sender, instance, **kwargs):
    """
    Elimina movimientos de inventario cuando se elimina una línea de documento.
    El delete() del InventoryMovement automáticamente revertirá el stock.
    """
    def handle_deletion():
        try:
            InventoryMovement.objects.filter(line_id=instance.id).delete()
            print(f"🗑️ Movimiento eliminado para línea {instance.id}")
        except Exception as e:
            print(f"❌ Error al eliminar movimiento para línea {instance.id}: {e}")
            import traceback
            traceback.print_exc()

    transaction.on_commit(handle_deletion)


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
                # 🗑️ DOCUMENTO ANULADO: Eliminar todos los movimientos
                print(f"📄 Anulando documento {instance.id} - Revirtiendo stock de todas las líneas")
                
                for line in instance.lines.all():
                    movements = InventoryMovement.objects.filter(line_id=line.id)
                    count = movements.count()
                    if count > 0:
                        # El delete() automáticamente revierte el stock
                        movements.delete()
                        print(f"   🗑️ Eliminados {count} movimiento(s) de línea {line.id}")
                
                print(f"✅ Documento {instance.id} anulado - Stock revertido correctamente")
                
            else:
                # ✅ DOCUMENTO REACTIVADO: Recrear todos los movimientos
                print(f"📄 Reactivando documento {instance.id} - Aplicando stock de todas las líneas")
                
                for line in instance.lines.all():
                    warehouse = line.warehouse
                    doc_type = instance.document_type
                    movement_type = doc_type.stock_movement
                    
                    if warehouse and movement_type != 0:
                        # Verificar si ya existe un movimiento (por seguridad)
                        existing = InventoryMovement.objects.filter(line_id=line.id).first()
                        if existing:
                            print(f"   ⚠️ Ya existe movimiento para línea {line.id}, omitiendo")
                            continue
                        
                        movement = InventoryMovement(
                            line_id=line.id,
                            product=line.product,
                            warehouse=warehouse,
                            quantity=line.quantity,
                            movement_type=movement_type,
                            unit=line.unit,
                            reason=f"{doc_type.description} #{instance.id} (Reactivado)",
                            document=str(instance.id),
                            created_by=instance.created_by
                        )
                        movement.save()  # Esto actualiza el stock automáticamente
                        print(f"   ✅ Movimiento recreado para línea {line.id}")
                
                print(f"✅ Documento {instance.id} reactivado - Stock aplicado correctamente")
                
        except Exception as e:
            print(f"❌ Error al manejar cambio de estado del documento {instance.id}: {e}")
            import traceback
            traceback.print_exc()
    
    transaction.on_commit(handle_status_change)
