from rest_framework import serializers
from appinventory.models import ProductCategory

class ProductCategorySchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'