from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from appinventory.models import (
    Warehouse, ProductCategory, ProductBrand, Product, UnitOfMeasure,
    UnitCategory, PriceType, ProductPrice, ProductImage, SerializedItem,
    InventoryTransfer, InventoryMovement,
)
from django.db import transaction, IntegrityError
import logging
logger = logging.getLogger(__name__)

# Serializador para almacenes
class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

# Serializador para categorías de productos
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

# Serializador para categorías de unidades
class UnitCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitCategory
        fields = '__all__'

# Serializador para marcas de productos
class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = '__all__'

# Serializador para precios de productos
class ProductPriceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = ProductPrice
        fields = [
            'id', 'price_type', 'unit', 'price',
            'is_default', 'valid_from', 'valid_until',
            'is_active', 'is_purchase', 'is_sale'
        ]


# Serializador principal para productos, incluye relación con precios y unidades
class ProductSerializer(serializers.ModelSerializer):
    prices = ProductPriceSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'

    def validate_prices(self, value):
        seen = set()
        for item in value:
            price_type_id = item.get('price_type')
            unit_id = item.get('unit')
            is_purchase = bool(item.get('is_purchase'))
            is_sale = bool(item.get('is_sale'))
            valid_from = item.get('valid_from') or None
            valid_until = item.get('valid_until') or None

            key = (
                price_type_id,
                unit_id,
                is_purchase,
                is_sale,
                valid_from,
                valid_until,
            )
            if key in seen:
                raise serializers.ValidationError(
                    "Duplicate price combination (unit, price type, flags, dates)."
                )
            seen.add(key)

        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('brand'):
            raise serializers.ValidationError({
                'brand': 'Debe proporcionar una marca para el producto.'
            })
        if self.instance is not None and 'brand' in attrs and not attrs.get('brand'):
            raise serializers.ValidationError({
                'brand': 'El producto debe tener una marca asignada.'
            })
        return super().validate(attrs)

    def create(self, validated_data):
        prices_data = validated_data.pop('prices', [])

        with transaction.atomic():
            product = super().create(validated_data)
            for price_data in prices_data:
                payload = price_data.copy()
                payload.pop('id', None)
                ProductPrice.objects.create(product=product, **payload)

        return product

    def update(self, instance, validated_data):
        prices_data = validated_data.pop('prices', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if prices_data is not None:
                existing_prices = {price.id: price for price in instance.prices.all()}
                seen_ids = set()

                for price_data in prices_data:
                    payload = price_data.copy()
                    price_id = payload.pop('id', None)

                    if payload.get('valid_from') in ('', None):
                        payload['valid_from'] = None
                    if payload.get('valid_until') in ('', None):
                        payload['valid_until'] = None

                    try:
                        if price_id and price_id in existing_prices:
                            price_obj = existing_prices[price_id]
                            for attr, value in payload.items():
                                setattr(price_obj, attr, value)
                            price_obj.full_clean()
                            price_obj.save()
                            seen_ids.add(price_id)
                        else:
                            new_price = ProductPrice.objects.create(product=instance, **payload)
                            seen_ids.add(new_price.id)
                    except IntegrityError as exc:
                        raise serializers.ValidationError({
                            'prices': [f'Duplicate price combination (unit, price type, flags, dates). DB says: {exc}']
                        }) from exc

                for price_id, price_obj in existing_prices.items():
                    if price_id not in seen_ids:
                        price_obj.delete()

        return instance

# Serializador para unidades de medida
class UnitOfMeasureSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = UnitOfMeasure
        fields = [
            'id', 'name', 'code', 'category', 'category_name',
            'reference_unit', 'conversion_sign', 'conversion_factor', 'is_active'
        ]

# Serializador para tipos de precio
class PriceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceType
        fields = ['id', 'name', 'description', 'is_active', 'pricing_method', 'margin_percent']

# Serializador compacto para listados
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', default='', read_only=True)
    default_brand = serializers.SerializerMethodField()
    brand_name = serializers.CharField(source='brand.name', default='', read_only=True)
    unit_name = serializers.CharField(source='unit_default.name', default='', read_only=True)
    unit_default_code = serializers.CharField(source='unit_default.code', default='', read_only=True)
    image = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'model_number', 'category_name', 'brand', 'brand_name',
            'default_brand', 'reorder_level', 'unit_name', 'unit_default_code',
            'tracking_mode', 'is_active', 'image', 'total_stock',
        ]

    def get_image(self, obj):
        """Thumbnail for list views: primary image, else first available."""
        images = list(obj.images.all())
        if not images:
            return None

        def image_url(image):
            return image.image.url if image.image else None

        for image in images:
            if image.is_primary:
                url = image_url(image)
                if url:
                    return url

        for image in images:
            url = image_url(image)
            if url:
                return url

        return None

    def get_total_stock(self, obj):
        """On-hand quantity across warehouses when the queryset annotates total_stock."""
        value = getattr(obj, 'total_stock', None)
        if value is None:
            return None
        return float(value)

    def get_default_brand(self, obj):
        """Compat: marca del producto."""
        brand = obj.brand
        return {
            'id': brand.id if brand else None,
            'name': brand.name if brand else None,
        }

# Serializador para detalle completo de producto (usado en modo edición o vista)
class ProductDetailSerializer(ProductSerializer):
    prices = ProductPriceSerializer(many=True, read_only=True)
    brand_detail = ProductBrandSerializer(source='brand', read_only=True)
    default_brand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_default_brand(self, obj):
        brand = obj.brand
        return {
            'id': brand.id if brand else None,
            'name': brand.name if brand else None,
        }

# Serializador para ítems serializados (equipos/herramientas)
class SerializedItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    current_warehouse_name = serializers.CharField(source='current_warehouse.name', read_only=True)
    warehouse_crew_name = serializers.SerializerMethodField()
    document_id = serializers.SerializerMethodField()
    document_display = serializers.SerializerMethodField()
    document_line_display = serializers.SerializerMethodField()

    class Meta:
        model = SerializedItem
        fields = [
            'id', 'product', 'product_name', 'asset_tag', 'status', 'condition',
            'purchase_date', 'current_warehouse', 'current_warehouse_name', 'warehouse_crew_name',
            'document', 'document_id', 'document_display',
            'document_line', 'document_line_display', 'notes', 'created_at',
        ]

    def get_warehouse_crew_name(self, obj):
        wh = getattr(obj, 'current_warehouse', None)
        return _get_current_crew_name_for_truck(wh.truck if wh else None)
        read_only_fields = ['created_at']

    def get_document_id(self, obj):
        return obj.document_id if obj.document_id else None

    def get_document_display(self, obj):
        doc = getattr(obj, 'document', None)
        if not doc:
            return None
        try:
            return str(doc)
        except Exception:
            return f"Document #{doc.id}"

    def get_document_line_display(self, obj):
        line = getattr(obj, 'document_line', None)
        if not line:
            return None
        try:
            product_name = getattr(line.product, 'name', '') if getattr(line, 'product', None) else ''
            qty = getattr(line, 'quantity', '')
            return f"{product_name} (qty: {qty})" if product_name else str(line)
        except Exception:
            return f"Line #{line.id}"


# Serializador para imágenes de productos
class ProductImageSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True, allow_null=True)

    class Meta:
        model = ProductImage
        fields = [
            'id', 'product', 'product_name',
            'image', 'image_url', 'is_primary', 'uploaded_at',
            'uploaded_by', 'uploaded_by_username', 'description',
        ]
        read_only_fields = ['uploaded_at', 'uploaded_by']

    def get_image_url(self, obj):
        """Returns the image URL (relative path for frontend proxy compatibility)"""
        if obj.image:
            return obj.image.url
        return None

    def validate(self, attrs):
        product = attrs.get('product') or (self.instance.product if self.instance else None)
        if not product:
            raise serializers.ValidationError({'product': 'La imagen debe pertenecer a un producto.'})
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user

        if validated_data.get('is_primary'):
            product = validated_data.get('product')
            if product:
                ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_primary', False) and instance.product_id:
            ProductImage.objects.filter(
                product_id=instance.product_id,
                is_primary=True,
            ).exclude(pk=instance.pk).update(is_primary=False)

        return super().update(instance, validated_data)


def _get_current_crew_name_for_truck(truck):
    """Return the name of the crew that currently has this truck assigned, or None."""
    if not truck:
        return None
    from crewsapp.models import TruckAssignment
    now = timezone.now()
    assignment = (
        TruckAssignment.objects.filter(trucks=truck)
        .filter(Q(unassigned_at__isnull=True) | Q(unassigned_at__gt=now))
        .order_by('-assigned_at')
        .select_related('crew')
        .first()
    )
    return assignment.crew.name if assignment and assignment.crew else None


# Serializador para líneas de transferencia (una línea = 2 movimientos OUT+IN)
class InventoryTransferLineSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    unit_id = serializers.IntegerField(required=False, allow_null=True)
    serialized_item_id = serializers.IntegerField(required=False, allow_null=True)


class InventoryTransferSerializer(serializers.ModelSerializer):
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    truck_crew_name = serializers.SerializerMethodField()
    movements_count = serializers.SerializerMethodField()
    lines = serializers.ListField(
        child=InventoryTransferLineSerializer(),
        write_only=True,
        required=False,
        allow_empty=False
    )

    class Meta:
        model = InventoryTransfer
        fields = [
            'id', 'from_warehouse', 'from_warehouse_name',
            'to_warehouse', 'to_warehouse_name',
            'description', 'status',
            'truck_crew_name',
            'created_at', 'last_updated', 'created_by', 'created_by_username',
            'movements_count', 'lines',
        ]
        read_only_fields = ['created_at', 'last_updated', 'status']

    def get_truck_crew_name(self, obj):
        from_wh = getattr(obj, 'from_warehouse', None)
        to_wh = getattr(obj, 'to_warehouse', None)
        from_crew = _get_current_crew_name_for_truck(from_wh.truck if from_wh else None)
        to_crew = _get_current_crew_name_for_truck(to_wh.truck if to_wh else None)
        if from_crew and to_crew:
            return f"{from_crew} → {to_crew}" if from_crew != to_crew else from_crew
        if from_crew:
            return from_crew
        if to_crew:
            return to_crew
        return None

    def get_movements_count(self, obj):
        return obj.movements.count() if obj.pk else 0

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.pk:
            movements = list(instance.movements.select_related('product', 'warehouse', 'unit', 'serialized_item').order_by('id'))
            lines_out = {}
            for m in movements:
                key = (m.product_id, m.serialized_item_id)
                if key not in lines_out:
                    lines_out[key] = {
                        'product_id': m.product_id,
                        'product_name': m.product.name if m.product else None,
                        'quantity': float(m.quantity),
                        'unit_id': m.unit_id,
                        'serialized_item_id': m.serialized_item_id,
                        'serialized_item_asset_tag': m.serialized_item.asset_tag if m.serialized_item else None,
                        'serialized_item_status': m.serialized_item.status if m.serialized_item else None,
                        'serialized_item_condition': m.serialized_item.condition if m.serialized_item else None,
                        'from_warehouse_id': instance.from_warehouse_id,
                        'to_warehouse_id': instance.to_warehouse_id,
                    }
            data['lines'] = list(lines_out.values())
        return data

    def create(self, validated_data):
        lines = validated_data.pop('lines', [])
        request = self.context.get('request')
        with transaction.atomic():
            transfer = InventoryTransfer.objects.create(
                **validated_data,
                created_by=request.user if request and request.user.is_authenticated else None,
            )
            _create_movements_from_lines(transfer, lines, request)
        return transfer

    def update(self, instance, validated_data):
        lines = validated_data.pop('lines', None)
        request = self.context.get('request')
        with transaction.atomic():
            if instance.status != InventoryTransfer.STATUS_REVERTED:
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                if lines is not None:
                    instance.movements.all().delete()
                    _create_movements_from_lines(instance, lines, request)
        return instance


def _create_movements_from_lines(transfer, lines, request):
    """Create 2 InventoryMovement (OUT+IN) per line from single-line format."""
    from appinventory.models import InventoryTransfer, InventoryMovement, Product, SerializedItem
    from decimal import Decimal

    for line in lines:
        product_id = line['product_id']
        quantity = Decimal(str(line['quantity']))
        unit_id = line.get('unit_id')
        serialized_item_id = line.get('serialized_item_id')

        product = Product.objects.get(pk=product_id)
        unit = product.unit_default
        if unit_id:
            unit = UnitOfMeasure.objects.filter(pk=unit_id).first() or unit
        serialized_item = None
        if serialized_item_id:
            serialized_item = SerializedItem.objects.get(pk=serialized_item_id)

        is_serialized = bool(serialized_item) or product.tracking_mode == Product.TRACKING_SERIALIZED

        if is_serialized:
            if not serialized_item:
                raise serializers.ValidationError(
                    {'lines': f'Product "{product.name}" is serialized; provide serialized_item_id.'}
                )
            quantity = Decimal('1')
            mt_out = InventoryMovement.MOVEMENT_TYPE_AJUSTE
            mt_in = InventoryMovement.MOVEMENT_TYPE_AJUSTE
        else:
            mt_out = InventoryMovement.MOVEMENT_TYPE_SALIDA
            mt_in = InventoryMovement.MOVEMENT_TYPE_ENTRADA

        reason_out = f"Inventory Transfer to {transfer.to_warehouse.name}"
        reason_in = f"Inventory Transfer from {transfer.from_warehouse.name}"

        InventoryMovement.objects.create(
            product=product,
            warehouse=transfer.from_warehouse,
            quantity=quantity,
            movement_type=mt_out,
            reason=reason_out,
            unit=unit,
            serialized_item=serialized_item,
            transfer=transfer,
            created_by=request.user if request and request.user.is_authenticated else None,
        )
        InventoryMovement.objects.create(
            product=product,
            warehouse=transfer.to_warehouse,
            quantity=quantity,
            movement_type=mt_in,
            reason=reason_in,
            unit=unit,
            serialized_item=serialized_item,
            transfer=transfer,
            created_by=request.user if request and request.user.is_authenticated else None,
        )
