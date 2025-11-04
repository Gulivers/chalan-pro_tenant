from rest_framework import serializers
from appinventory.models import (
    Warehouse, ProductCategory, ProductBrand, Product, UnitOfMeasure, 
    UnitCategory, PriceType, ProductPrice
)
from django.db import transaction

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
            key = (item.get('price_type'), item.get('unit'), item.get('valid_from'), item.get('valid_until'))
            if key in seen:
                raise serializers.ValidationError(f"Duplicate price for type/unit/period: {key}")
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
                ProductPrice.objects.create(product=product, **price_data)

        return product

    def update(self, instance, validated_data):
        prices_data = validated_data.pop('prices', [])
        brands_data = validated_data.pop('brands_data', None)

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

        # Elimina precios anteriores y guarda nuevos
        instance.prices.all().delete()
        for price_data in prices_data:
            ProductPrice.objects.create(product=instance, **price_data)

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
