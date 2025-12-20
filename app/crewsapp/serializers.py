from rest_framework import serializers
from .models import Crew, Truck, TruckAssignment, Category
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# Serializador para Truck
class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = '__all__'


# Serializador para Crew
class CrewSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    class Meta:
        model = Crew
        fields = ['id', 'name', 'category_name', 'status']
        # depth = 1  # Para incluir las relaciones (Job, Members y Truck)


class TruckAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckAssignment
        fields = '__all__'
