from rest_framework import serializers
from appinventory.models import (
    Warehouse, ProductCategory, ProductBrand, Product, UnitOfMeasure, 
    UnitCategory, PriceType, ProductPrice, ProductImage
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
    brands_data = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'brands': {'read_only': True}  # Exclude from automatic serialization
        }
        
    def validate_prices(self, value):
        seen = set()
        for item in value:
            price_type_id = item.get('price_type')
            unit_id = item.get('unit')
            is_purchase = bool(item.get('is_purchase'))
            is_sale = bool(item.get('is_sale'))
            valid_from = item.get('valid_from') or None
            valid_until = item.get('valid_until') or None

            # Normalizar fechas: cadenas vacías → None
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

    def validate_brands_data(self, value):
        """Valida que al menos se proporcione una marca al crear producto"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("El producto debe tener al menos una marca asignada.")
        return value

    def validate(self, attrs):
        """Validación completa del serializer"""
        # Si es un nuevo producto, validar que tenga marcas
        if self.instance is None:
            brands_data = attrs.get('brands_data', [])
            if not brands_data:
                raise serializers.ValidationError({
                    'brands_data': 'Debe proporcionar al menos una marca para el producto.'
                })
        
        return super().validate(attrs)

    def create(self, validated_data):
        prices_data = validated_data.pop('prices', [])
        brands_data = validated_data.pop('brands_data', [])

        with transaction.atomic():
            product = super().create(validated_data)
            
            # Asignar marcas
            if brands_data:
                brands = ProductBrand.objects.filter(id__in=brands_data)
                product.brands.set(brands)
                
                # Asegurar que haya una marca default
                product.ensure_default_brand()

            for price_data in prices_data:
                payload = price_data.copy()
                payload.pop('id', None)
                ProductPrice.objects.create(product=product, **payload)

        return product

    def update(self, instance, validated_data):
        prices_data = validated_data.pop('prices', None)
        brands_data = validated_data.pop('brands_data', None)

        with transaction.atomic():
            # Actualizar marcas si se proporcionan
            if brands_data is not None:
                brands = ProductBrand.objects.filter(id__in=brands_data)
                instance.brands.set(brands)

                # Mantener validación: debe tener al menos una marca
                if len(brands_data) == 0:
                    raise serializers.ValidationError({
                        'brands_data': 'El producto debe tener al menos una marca asignada.'
                    })

                # Reajustar marca default si es necesario
                instance.ensure_default_brand()

            # Actualiza campos del producto
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if prices_data is not None:
                existing_prices = {price.id: price for price in instance.prices.all()}
                seen_ids = set()

                for price_data in prices_data:
                    payload = price_data.copy()
                    price_id = payload.pop('id', None)

                    # Normalizar fechas vacías a None
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

                # Eliminar precios que ya no vienen en el payload
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
        fields = ['id', 'name', 'description', 'is_active']

# Serializador compacto para listados
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', default='', read_only=True)
    default_brand = serializers.SerializerMethodField()
    brands_count = serializers.SerializerMethodField()
    unit_name = serializers.CharField(source='unit_default.name', default='', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category_name', 'default_brand', 'brands_count',
            'reorder_level', 'unit_name', 'is_active'
        ]
    
    def get_default_brand(self, obj):
        """Obtiene la marca predeterminada del producto"""
        default_brand = obj.get_default_brand()
        return {
            'id': default_brand.id if default_brand else None,
            'name': default_brand.name if default_brand else None
        }
    
    def get_brands_count(self, obj):
        """Retorna el número de marcas asociadas al producto"""
        return obj.brands.count()

# Serializador para detalle completo de producto (usado en modo edición o vista)
class ProductDetailSerializer(ProductSerializer):
    prices = ProductPriceSerializer(many=True, read_only=True)
    brands = ProductBrandSerializer(many=True, read_only=True)
    brands_data = serializers.ListField(write_only=True, required=False)
    default_brand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        extra_fields = ['prices', 'brands', 'brands_data', 'default_brand']
    
    def get_default_brand(self, obj):
        """Obtiene la marca predeterminada del producto"""
        default_brand = obj.get_default_brand()
        return {
            'id': default_brand.id if default_brand else None,
            'name': default_brand.name if default_brand else None
        }

# Serializador para imágenes de productos
class ProductImageSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='assignment.brand.name', read_only=True)
    brand_id = serializers.IntegerField(source='assignment.brand.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True, allow_null=True)

    class Meta:
        model = ProductImage
        fields = [
            'id', 'product', 'product_name', 'assignment', 'brand_id', 'brand_name',
            'image', 'image_url', 'is_primary', 'uploaded_at',
            'uploaded_by', 'uploaded_by_username', 'description'
        ]
        read_only_fields = ['uploaded_at', 'uploaded_by']

    def get_image_url(self, obj):
        """Returns the image URL (relative path for frontend proxy compatibility)"""
        if obj.image:
            # Use relative URL so it works with frontend proxy in development
            # and direct access in production
            return obj.image.url
        return None

    def validate(self, attrs):
        """Valida que la asignación pertenezca al producto"""
        product = attrs.get('product') or (self.instance.product if self.instance else None)
        assignment = attrs.get('assignment') or (self.instance.assignment if self.instance else None)
        
        if product and assignment:
            if assignment.product != product:
                raise serializers.ValidationError({
                    'assignment': f"Assignment '{assignment}' does not belong to product '{product.name}'."
                })
        
        return attrs

    def create(self, validated_data):
        """Override create para asignar el usuario actual y manejar is_primary"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
        
        # Si se marca como principal, desmarcar otras principales de la misma asignación
        if validated_data.get('is_primary'):
            ProductImage.objects.filter(
                assignment=validated_data['assignment'],
                is_primary=True
            ).update(is_primary=False)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Override update para manejar is_primary"""
        # Si se marca como principal, desmarcar otras principales de la misma asignación
        if validated_data.get('is_primary', False):
            ProductImage.objects.filter(
                assignment=instance.assignment,
                is_primary=True
            ).exclude(pk=instance.pk).update(is_primary=False)
        
        return super().update(instance, validated_data)
