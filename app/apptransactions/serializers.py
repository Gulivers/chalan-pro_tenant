
from decimal import Decimal
import logging
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from apptransactions.models import (
    DocumentType, PartyType, PartyCategory, Party, Document, DocumentLine,
    WorkAccount, TransactionFavorite
)
from appinventory.models import Stock, PriceType

logger = logging.getLogger(__name__)

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'
        
class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyType
        fields = '__all__'
        
class PartyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyCategory
        fields = '__all__'
        

class WorkAccountSerializer(serializers.ModelSerializer):
    builder_name = serializers.CharField(source="builder.name", read_only=True)
    job_name = serializers.CharField(source="job.name", read_only=True)
    house_model_name = serializers.CharField(source="house_model.name", read_only=True)
    display = serializers.SerializerMethodField()

    class Meta:
        model = WorkAccount
        fields = "__all__"

    def get_display(self, obj):
        # Etiqueta compacta para el v-select
        parts = [obj.title]
        ctx = []
        if obj.builder:
            ctx.append(obj.builder.name)
        if obj.job:
            ctx.append(obj.job.name)
        if obj.house_model:
            ctx.append(obj.house_model.name)
        if obj.lot: 
            ctx.append(f"Lot {obj.lot}")
        ctx = [p for p in ctx if p]
        if ctx: 
            parts.append("• " + " • ".join(ctx))
        return " ".join(parts)
            

class PartySerializer(serializers.ModelSerializer):
    # IDs de relaciones (simple y performante para list/create/update)
    types = serializers.PrimaryKeyRelatedField(
        queryset=PartyType.objects.all(), many=True
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=PartyCategory.objects.all(), allow_null=True, required=False
    )
    default_price_type = serializers.PrimaryKeyRelatedField(
        queryset=PriceType.objects.all(), allow_null=True, required=False
    )

    # Unicidad por nombre (case-insensitive)
    name = serializers.CharField(
        max_length=255,
        validators=[
            UniqueValidator(
                queryset=Party.objects.all(),
                lookup='iexact',
                message='A party with this name already exists.'
            )
        ]
    )

    class Meta:
        model = Party
        fields = [
            'id', 'name', 'rfc', 'street', 'floor_office', 'city', 'state',
            'zipcode', 'country', 'phone', 'email',
            'types', 'category', 'default_price_type',
            'customer_rank', 'supplier_rank', 'is_active'
        ]

    # Validaciones y normalización
    def validate(self, attrs):
        # trim strings
        for k in ['name','rfc','street','floor_office','city','state','zipcode','country','phone','email']:
            if k in attrs and isinstance(attrs[k], str):
                attrs[k] = attrs[k].strip()

        # email en minúsculas
        if attrs.get('email'):
            attrs['email'] = attrs['email'].lower()

        # (Opcional) política: al menos un rol cliente/proveedor
        # if attrs.get('customer_rank', 0) == 0 and attrs.get('supplier_rank', 0) == 0:
        #     raise serializers.ValidationError({'customer_rank': 'Must be > 0 if not supplier.', 'supplier_rank': 'Must be > 0 if not customer.'})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        types = validated_data.pop('types', [])
        instance = Party.objects.create(**validated_data)
        if types:
            instance.types.set(types)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        types = validated_data.pop('types', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if types is not None:
            instance.types.set(types)
        return instance

# ---- Aux: validación de disponibilidad (solo para salidas) ------------------
def _validate_stock_out(line: "DocumentLine"):
    doc = line.document
    if not doc or not doc.document_type:
        return
    if doc.document_type.stock_movement != -1:
        return  # sólo salidas

    warehouse = line.warehouse or doc.warehouse
    if not warehouse:
        raise serializers.ValidationError({"warehouse": "Se requiere almacén para validar stock."})
    
    # Stock disponible en referencia (Stock ya está en unidad de referencia)
    from django.db.models import Sum
    available = (
        Stock.objects
        .filter(product=line.product, warehouse=warehouse)
        .aggregate(total=Sum("quantity"))["total"] or Decimal("0")
    )

    if line.quantity is None or line.quantity <= 0:
        raise serializers.ValidationError({"quantity": "La cantidad debe ser > 0."})

    # Convertir solicitado a unidad de referencia
    try:
        from appinventory.helpers import convert_to_reference_unit
        requested_ref = convert_to_reference_unit(line.product, line.unit, line.quantity) if line.unit else line.quantity
    except Exception as e:
        raise serializers.ValidationError({"unit": f"Error al convertir la cantidad: {e}"})

    # Verificar si se permite venta negativa
    if Decimal(available) < Decimal(requested_ref):
        # Si el documento permite ventas negativas, solo mostrar advertencia
        if doc.document_type.allow_negative_sales:
            return  # Permitir la transacción
            
        # Si no permite ventas negativas, rechazar la transacción
        raise serializers.ValidationError({
            "quantity": {
                "error_type": "insufficient_stock",
                "product_name": line.product.name,
                "available": str(available),
                "requested": str(requested_ref),
                "document_type": doc.document_type.type_code,
                "message": f"{line.product.name}: Stock insuficiente. Disponible: {available}, solicitado(ref): {requested_ref}. El tipo de documento '{doc.document_type.type_code}' no permite ventas sin stock."
            }
        })

# DocumentLine
class DocumentLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_code = serializers.CharField(source="unit.code", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = DocumentLine
        fields = [
            "id", "document", "product", "product_name",
            "quantity", "unit", "unit_code",
            "unit_price", "discount_percentage", "final_price",
            "warehouse", "warehouse_name", "price_type", "brand"
        ]
        read_only_fields = ["final_price"]

    def validate(self, attrs):
        # quantity > 0 y product obligatorio ya se valida en clean(), pero reforzamos acá para 400 consistente
        if "quantity" in attrs and (attrs["quantity"] is None or attrs["quantity"] <= 0):
            raise serializers.ValidationError({"quantity": "The quantity must be greater than 0."})
        if "product" in attrs and attrs["product"] is None:
            raise serializers.ValidationError({"product": "You must select a product."})
        # unit es opcional según la estructura de la tabla (unit_id DEFAULT NULL)
        doc = attrs.get("document") or getattr(self.instance, "document", None)
        warehouse = attrs.get("warehouse") if "warehouse" in attrs else getattr(self.instance, "warehouse", None)
        
        if doc and doc.document_type and doc.document_type.warehouse_required and not warehouse:
            raise serializers.ValidationError({"warehouse": "This document type requires a warehouse in each line."})
        
        return attrs

    def create(self, validated_data):
        instance = DocumentLine(**validated_data)
        
        # Nota: La validación de stock se hace a nivel de DocumentSerializer para todas las líneas juntas
        
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # Aplicamos cambios temporales para validar stock
        for k, v in validated_data.items():
            setattr(instance, k, v)
        _validate_stock_out(instance)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        instance.save()
        return instance


# Document (con soporte opcional de líneas anidadas)
class DocumentLineInlineSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    # Campos de solo lectura para mostrar información adicional
    unit_code = serializers.CharField(source="unit.code", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = DocumentLine
        fields = [
            "id", "product", "product_name", "quantity", "unit", "unit_code",
            "unit_price", "discount_percentage", "final_price", "warehouse",
            "price_type", "brand"
        ]
        read_only_fields = ["final_price", "unit_code", "product_name"]


class DocumentSerializer(serializers.ModelSerializer):
    document_type_code = serializers.CharField(source="document_type.type_code", read_only=True)
    builder_name = serializers.CharField(source="builder.name", read_only=True)
    work_account_display = serializers.CharField(source="work_account.__str__", read_only=True)

    # Opcional: manejo anidado (lines) en create/update si se envía `lines`
    lines = DocumentLineInlineSerializer(many=True, required=False)

    class Meta:
        model = Document
        fields = [
            "id", "document_type", "document_type_code",
            "date", "builder", "builder_name",
            "work_account", "work_account_display",
            "created_by", "notes",
            "total_discount", "total_amount", "is_active",
            "lines",
        ]
        read_only_fields = ["date", "total_discount", "total_amount"]

    def validate(self, attrs):
        doc_type = attrs.get("document_type") or getattr(self.instance, "document_type", None)
        builder = attrs.get("builder") or getattr(self.instance, "builder", None)
        work_account = attrs.get("work_account") or getattr(self.instance, "work_account", None)

        if doc_type is None:
            raise serializers.ValidationError({"document_type": "You must select a document type."})
        
        # Para documentos operacionales, el builder se obtiene del work_account
        if doc_type.is_operational:
            if work_account is None:
                raise serializers.ValidationError({"work_account": "You must select a work account for operational documents."})
            # Si no hay builder pero hay work_account, el builder se obtendrá del work_account en save()
        else:
            # Para documentos no operacionales, builder es requerido para ventas/compras
            if doc_type.is_sales or doc_type.is_purchase:
                if builder is None:
                    raise serializers.ValidationError({"builder": "You must select a builder for sales or purchase documents."})
                
                # Chequeos de cliente/proveedor usando clean() del modelo
                # (re-ejecutamos después en save(), pero aquí damos 400 temprano)
                if doc_type.is_sales and not builder.is_customer():
                    raise serializers.ValidationError({"builder": "The builder is not a customer for sales documents."})
                if doc_type.is_purchase and not builder.is_supplier():
                    raise serializers.ValidationError({"builder": "The builder is not a supplier for purchase documents."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop("lines", None)
        
        # Normalizar work_account: siempre guardar como ID (int)
        work_account_id = None
        if validated_data.get('work_account'):
            work_account = validated_data.pop('work_account')  # Remover de validated_data para manejarlo por separado
            # Si work_account es un ID (int), usarlo directamente
            if isinstance(work_account, int):
                work_account_id = work_account
            # Si work_account es un objeto, extraer el ID
            elif hasattr(work_account, 'id'):
                work_account_id = work_account.id
            else:
                # Si es None o cualquier otro valor, mantenerlo como None
                work_account_id = None
            
        # Obtener el objeto WorkAccount si tenemos el ID (para obtener builder si es necesario)
        work_account_obj = None
        if work_account_id is not None:
            try:
                work_account_obj = WorkAccount.objects.get(id=work_account_id)
                logger.info(f"WorkAccount object retrieved: {work_account_obj}")
                
                # Obtener builder del work_account si no está presente (para cualquier tipo de documento)
                # Esto es importante porque algunos documentos pueden requerir builder aunque no sean operacionales
                # IMPORTANTE: Pasar el objeto Builder completo, no solo el ID
                if not validated_data.get('builder') and work_account_obj.builder_id:
                    # Obtener el objeto Builder explícitamente usando el ID para asegurar que es un objeto
                    from ctrctsapp.models import Builder as BuilderModel
                    builder_id = work_account_obj.builder_id
                    try:
                        builder_obj = BuilderModel.objects.get(id=builder_id)
                        validated_data['builder'] = builder_obj  # Asignar el objeto Builder completo
                        logger.info(f"Auto-assigned builder object from work_account: {builder_obj} (id: {builder_obj.id}, type: {type(builder_obj).__name__})")
                    except BuilderModel.DoesNotExist:
                        logger.warning(f"Builder with id {builder_id} from work_account does not exist")
            except WorkAccount.DoesNotExist:
                logger.error(f"WorkAccount with id {work_account_id} does not exist")
                raise serializers.ValidationError({'work_account': f'WorkAccount with id {work_account_id} does not exist'})
        
        # Debug: Log para verificar que work_account esté presente
        logger.info(f"Creating Document - validated_data keys: {list(validated_data.keys())}")
        logger.info(f"Creating Document with work_account_id: {work_account_id}")
        if validated_data.get('builder'):
            builder_value = validated_data['builder']
            logger.info(f"Builder in validated_data: {builder_value} (type: {type(builder_value).__name__}, is instance: {hasattr(builder_value, 'id')})")
        
        # Crear el documento paso a paso para evitar problemas con ForeignKeys
        # Primero, extraer los valores que necesitamos
        document_type = validated_data.pop('document_type')
        date = validated_data.pop('date', None)
        builder = validated_data.pop('builder', None)
        notes = validated_data.pop('notes', '')
        is_active = validated_data.pop('is_active', True)
        
        # Crear el documento con los campos básicos
        doc = Document(
            document_type=document_type,
            date=date,
            notes=notes,
            is_active=is_active
        )
        
        # Asignar builder si está presente (debe ser un objeto Builder, no un ID)
        if builder:
            if isinstance(builder, int):
                # Si es un ID, obtener el objeto Builder
                from ctrctsapp.models import Builder as BuilderModel
                try:
                    builder_obj = BuilderModel.objects.get(id=builder)
                    doc.builder = builder_obj
                    logger.info(f"Builder ID {builder} converted to Builder object: {builder_obj}")
                except BuilderModel.DoesNotExist:
                    logger.error(f"Builder with id {builder} does not exist")
                    raise serializers.ValidationError({'builder': f'Builder with id {builder} does not exist'})
            else:
                # Ya es un objeto Builder
                doc.builder = builder
                logger.info(f"Builder object assigned: {builder} (id: {builder.id})")
        
        # Asignar work_account_id
        if work_account_id is not None:
            doc.work_account_id = work_account_id
            logger.info(f"Set doc.work_account_id = {work_account_id}")
        
        # Asignar automáticamente el usuario actual
        doc.created_by = self.context['request'].user
        
        logger.info(f"Document object created successfully with work_account_id: {doc.work_account_id}, builder_id: {doc.builder_id if doc.builder else None}")

        try:
            doc.full_clean()
            logger.info(f"Document validation passed")
        except DjangoValidationError as e:
            logger.error(f"Validation error: {e.message_dict}")
            raise serializers.ValidationError(e.message_dict)
        except Exception as e:
            logger.error(f"Unexpected error during full_clean: {e}", exc_info=True)
            raise serializers.ValidationError({'non_field_errors': [f'Validation error: {str(e)}']})
        
        try:
            doc.save()
            logger.info(f"Document saved successfully")
        except Exception as e:
            logger.error(f"Error saving Document: {e}", exc_info=True)
            raise serializers.ValidationError({'non_field_errors': [f'Error saving document: {str(e)}']})
        
        # Verificar que se guardó correctamente
        doc.refresh_from_db()  # Recargar desde la BD para obtener el valor real
        logger.info(f"Document {doc.id} created - work_account_id in DB: {doc.work_account_id}")
        if doc.work_account_id is None:
            logger.warning(f"⚠️ WARNING: Document {doc.id} was saved but work_account_id is NULL!")

        # Crear líneas si vinieron anidadas
        if lines_data:
            # Primero validar TODAS las líneas (sin validación de stock aún)
            all_line_errors = []
            for idx, ld in enumerate(lines_data):
                # Convertir objetos a IDs antes de validar la línea
                line_data = {
                    'id': ld.get('id'),
                    'product': ld.get('product').id if hasattr(ld.get('product'), 'id') else ld.get('product'),
                    'quantity': ld.get('quantity'),
                    'unit': ld.get('unit').id if hasattr(ld.get('unit'), 'id') else ld.get('unit'),
                    'unit_price': ld.get('unit_price'),
                    'discount_percentage': ld.get('discount_percentage'),
                    'warehouse': ld.get('warehouse').id if hasattr(ld.get('warehouse'), 'id') else ld.get('warehouse'),
                    'price_type': ld.get('price_type').id if hasattr(ld.get('price_type'), 'id') else ld.get('price_type'),
                    'brand': ld.get('brand').id if hasattr(ld.get('brand'), 'id') else ld.get('brand'),
                    'document': doc.id,  # Usar el ID del documento, no el objeto
                }
                line_ser = DocumentLineSerializer(data=line_data)
                if not line_ser.is_valid():
                    all_line_errors.append(line_ser.errors)
                else:
                    all_line_errors.append({})  # Línea válida
            
            # Si hay errores en cualquier línea, lanzar todos los errores juntos
            if any(all_line_errors):
                raise serializers.ValidationError({"lines": all_line_errors})
            
            # Ahora validar stock para TODAS las líneas después de que el documento esté creado
            stock_errors = []
            for idx, ld in enumerate(lines_data):
                try:
                    # Crear una instancia temporal para validar stock
                    temp_line = DocumentLine(
                        document=doc,
                        product=ld.get('product'),
                        quantity=ld.get('quantity'),
                        unit=ld.get('unit'),
                        warehouse=ld.get('warehouse')
                    )
                    _validate_stock_out(temp_line)
                except Exception as e:
                    stock_errors.append(str(e))
            
            # Si hay errores de stock, lanzar todos los errores juntos
            if stock_errors:
                raise serializers.ValidationError({"lines": stock_errors})
            
            # Si todas las líneas son válidas, crear todas las líneas
            for idx, ld in enumerate(lines_data):
                line_data = {
                    'id': ld.get('id'),
                    'product': ld.get('product').id if hasattr(ld.get('product'), 'id') else ld.get('product'),
                    'quantity': ld.get('quantity'),
                    'unit': ld.get('unit').id if hasattr(ld.get('unit'), 'id') else ld.get('unit'),
                    'unit_price': ld.get('unit_price'),
                    'discount_percentage': ld.get('discount_percentage'),
                    'warehouse': ld.get('warehouse').id if hasattr(ld.get('warehouse'), 'id') else ld.get('warehouse'),
                    'price_type': ld.get('price_type').id if hasattr(ld.get('price_type'), 'id') else ld.get('price_type'),
                    'brand': ld.get('brand').id if hasattr(ld.get('brand'), 'id') else ld.get('brand'),
                    'document': doc.id,
                }
                line_ser = DocumentLineSerializer(data=line_data)
                line_ser.is_valid(raise_exception=True)  # ✅ Validar antes de guardar
                line_instance = line_ser.save()

        # Recalcular totales
        doc.calculate_totals()
        return doc

    @transaction.atomic
    def update(self, instance, validated_data):
        lines_data = validated_data.pop("lines", None)

        # Normalizar work_account: siempre guardar como ID (int)
        work_account_id = None
        if validated_data.get('work_account'):
            work_account = validated_data.pop('work_account')  # Remover de validated_data para manejarlo por separado
            # Si work_account es un ID (int), usarlo directamente
            if isinstance(work_account, int):
                work_account_id = work_account
            # Si work_account es un objeto, extraer el ID
            elif hasattr(work_account, 'id'):
                work_account_id = work_account.id
            else:
                # Si es None o cualquier otro valor, mantenerlo como None
                work_account_id = None
            
            # Para documentos operacionales, obtener builder del work_account si no está presente
            if work_account_id and not validated_data.get('builder'):
                try:
                    work_account_obj = WorkAccount.objects.get(id=work_account_id)
                    if work_account_obj.builder:
                        validated_data['builder'] = work_account_obj.builder.id if hasattr(work_account_obj.builder, 'id') else work_account_obj.builder
                except WorkAccount.DoesNotExist:
                    logger.warning(f"WorkAccount with id {work_account_id} does not exist")
                    pass  # Si no existe, continuar sin builder

        # Debug: Log para verificar que work_account esté presente
        logger.info(f"Updating Document {instance.id} - validated_data keys: {list(validated_data.keys())}")
        logger.info(f"Updating Document {instance.id} with work_account_id: {work_account_id}")

        # Actualizamos campos del documento
        for k, v in validated_data.items():
            setattr(instance, k, v)
        
        # Asignar explícitamente work_account_id (usar _id para ForeignKey)
        if work_account_id is not None:
            instance.work_account_id = work_account_id
            logger.info(f"Explicitly set instance.work_account_id = {work_account_id}")
        
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            logger.error(f"Validation error: {e.message_dict}")
            raise serializers.ValidationError(e.message_dict)
        instance.save()
        
        # Verificar que se guardó correctamente
        instance.refresh_from_db()  # Recargar desde la BD para obtener el valor real
        logger.info(f"Document {instance.id} updated - work_account_id in DB: {instance.work_account_id}")
        if instance.work_account_id is None and 'work_account' in validated_data and validated_data['work_account'] is not None:
            logger.warning(f"⚠️ WARNING: Document {instance.id} was updated but work_account_id is NULL!")

        # Manejo de líneas anidadas (UPSERT + delete implícito si el front lo decide)
        if lines_data is not None:
            # Index actual por id
            existing = {l.id: l for l in instance.lines.all()}
            seen_ids = set()

            # Primero validar TODAS las líneas antes de crear/actualizar ninguna
            all_line_errors = []
            for idx, ld in enumerate(lines_data):
                line_id = ld.get("id")
                
                # Convertir objetos a IDs antes de validar la línea (igual que en create)
                line_data = {
                    'id': ld.get('id'),
                    'product': ld.get('product').id if hasattr(ld.get('product'), 'id') else ld.get('product'),
                    'quantity': ld.get('quantity'),
                    'unit': ld.get('unit').id if hasattr(ld.get('unit'), 'id') else ld.get('unit'),
                    'unit_price': ld.get('unit_price'),
                    'discount_percentage': ld.get('discount_percentage'),
                    'warehouse': ld.get('warehouse').id if hasattr(ld.get('warehouse'), 'id') else ld.get('warehouse'),
                    'price_type': ld.get('price_type').id if hasattr(ld.get('price_type'), 'id') else ld.get('price_type'),
                    'brand': ld.get('brand').id if hasattr(ld.get('brand'), 'id') else ld.get('brand'),
                    'document': instance.id,  # Usar el ID del documento, no el objeto
                }
                
                if line_id and line_id in existing:
                    # update
                    line = existing[line_id]
                    ser = DocumentLineSerializer(line, data=line_data, partial=True)
                    if not ser.is_valid():
                        all_line_errors.append(ser.errors)
                    else:
                        all_line_errors.append({})
                else:
                    # create - el document ya está en line_data como ID
                    ser = DocumentLineSerializer(data=line_data)
                    if not ser.is_valid():
                        all_line_errors.append(ser.errors)
                    else:
                        all_line_errors.append({})
            
            # Si hay errores en cualquier línea, lanzar todos los errores juntos
            if any(all_line_errors):
                raise serializers.ValidationError({"lines": all_line_errors})

            # Si todas las líneas son válidas, crear/actualizar todas las líneas
            for ld in lines_data:
                line_id = ld.get("id")
                
                # Convertir objetos a IDs antes de crear/actualizar (igual que en create)
                line_data = {
                    'id': ld.get('id'),
                    'product': ld.get('product').id if hasattr(ld.get('product'), 'id') else ld.get('product'),
                    'quantity': ld.get('quantity'),
                    'unit': ld.get('unit').id if hasattr(ld.get('unit'), 'id') else ld.get('unit'),
                    'unit_price': ld.get('unit_price'),
                    'discount_percentage': ld.get('discount_percentage'),
                    'warehouse': ld.get('warehouse').id if hasattr(ld.get('warehouse'), 'id') else ld.get('warehouse'),
                    'price_type': ld.get('price_type').id if hasattr(ld.get('price_type'), 'id') else ld.get('price_type'),
                    'brand': ld.get('brand').id if hasattr(ld.get('brand'), 'id') else ld.get('brand'),
                    'document': instance.id,  # Usar el ID del documento, no el objeto
                }
                
                if line_id and line_id in existing:
                    # update
                    line = existing[line_id]
                    ser = DocumentLineSerializer(line, data=line_data, partial=True)
                    ser.is_valid(raise_exception=True)
                    ser.save()
                    seen_ids.add(line_id)
                else:
                    # create - el document ya está en line_data como ID
                    ser = DocumentLineSerializer(data=line_data)
                    ser.is_valid(raise_exception=True)
                    ser.save()
                    seen_ids.add(ser.instance.id)

            # Opcional: eliminar líneas que no vinieron (comportamiento “replace”)
            to_delete = [lid for lid in existing.keys() if lid not in seen_ids]
            if to_delete:
                DocumentLine.objects.filter(id__in=to_delete).delete()

        # Recalcular totales
        instance.calculate_totals()
        return instance


class TransactionFavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer para TransactionFavorite con funcionalidades especiales para importar/exportar datos.
    """
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = TransactionFavorite
        fields = [
            'id', 'name', 'description', 'document_data', 'lines_data',
            'created_by', 'created_by_username', 'created_at', 'updated_at',
            'is_active', 'display_name'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validación de nombre único por usuario"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es requerido.")
        
        # Verificar unicidad case-insensitive para el usuario actual
        user = self.context['request'].user
        existing = TransactionFavorite.objects.filter(
            name__iexact=value.strip(),
            created_by=user,
            is_active=True
        )
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("Ya existe un favorito con este nombre.")
        
        return value.strip()
    
    def validate_document_data(self, value):
        """Validación de estructura de datos del documento"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("document_data debe ser un objeto JSON.")
        
        # Campos requeridos básicos
        required_fields = ['document_type']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"document_data debe contener el campo '{field}'.")
        
        return value
    
    def validate_lines_data(self, value):
        """Validación de estructura de líneas"""
        if not isinstance(value, list):
            raise serializers.ValidationError("lines_data debe ser un array JSON.")
        
        # Validar que cada línea tenga los campos básicos
        for idx, line in enumerate(value):
            if not isinstance(line, dict):
                raise serializers.ValidationError(f"Línea {idx} debe ser un objeto JSON.")
            
            required_line_fields = ['product', 'quantity']
            for field in required_line_fields:
                if field not in line:
                    raise serializers.ValidationError(f"Línea {idx} debe contener el campo '{field}'.")
        
        return value
    
    def create(self, validated_data):
        """Crear favorito asignando automáticamente el usuario actual"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Personalizar representación para diferentes contextos"""
        data = super().to_representation(instance)
        
        # Si se solicita para importar, incluir datos estructurados
        if self.context.get('for_import', False):
            data['import_data'] = {
                'document': instance.document_data,
                'lines': instance.lines_data
            }
        
        return data


class TransactionFavoriteImportSerializer(serializers.Serializer):
    """
    Serializer especializado para importar datos de un favorito.
    Retorna los datos estructurados listos para usar en el formulario.
    """
    favorite_id = serializers.IntegerField()
    
    def validate_favorite_id(self, value):
        """Validar que el favorito existe y pertenece al usuario"""
        user = self.context['request'].user
        try:
            favorite = TransactionFavorite.objects.get(
                id=value,
                created_by=user,
                is_active=True
            )
            return favorite
        except TransactionFavorite.DoesNotExist:
            raise serializers.ValidationError("Favorito no encontrado o no tienes permisos para accederlo.")
    
    def to_representation(self, instance):
        """Retornar datos estructurados para importar"""
        favorite = instance
        return {
            'id': favorite.id,
            'name': favorite.name,
            'description': favorite.description,
            'document_data': favorite.document_data,
            'lines_data': favorite.lines_data,
            'created_at': favorite.created_at
        }