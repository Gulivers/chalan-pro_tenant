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

    def validate(self, attrs):
        instance = self.instance
        name = (attrs.get('name') or (instance.name if instance else '') or '').strip()
        category = attrs.get('category') if 'category' in attrs else (instance.category if instance else None)

        if name:
            qs = Crew.objects.filter(name__iexact=name, category=category)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                cat_str = category.name if category else 'without category'
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"A crew with name '{name}' already exists in category '{cat_str}'."
                    ]
                })
        return attrs

    class Meta:
        model = Crew
        fields = [
            'id', 'name', 'category', 'category_name', 'status',
            'members', 'jobs', 'permission_create_event'
        ]
        read_only_fields = ['category_name']


def _periods_overlap(a1, u1, a2, u2):
    """Check if two time periods overlap. None end means ongoing."""
    from datetime import datetime
    tz = a1.tzinfo if getattr(a1, 'tzinfo', None) else None
    far_future = datetime(9999, 12, 31, 23, 59, 59, tzinfo=tz)
    end1 = u1 if u1 is not None else far_future
    end2 = u2 if u2 is not None else far_future
    return a1 < end2 and end1 > a2


class TruckAssignmentSerializer(serializers.ModelSerializer):
    crew_name = serializers.SerializerMethodField()
    trucks_display = serializers.SerializerMethodField()

    def get_crew_name(self, obj):
        return obj.crew.name if obj.crew else None

    def get_trucks_display(self, obj):
        trucks = obj.trucks.all()
        return [f"{t.plate_number} - {t.model}" for t in trucks] if trucks else []

    def validate_trucks(self, value):
        """No duplicate trucks in the list."""
        if not value:
            return value
        seen = set()
        for item in value:
            tid = item.id if hasattr(item, 'id') else item
            if tid in seen:
                raise serializers.ValidationError("Duplicate trucks are not allowed.")
            seen.add(tid)
        return value

    def validate(self, attrs):
        instance = self.instance
        crew = attrs.get('crew') or (instance.crew if instance else None)
        trucks = attrs.get('trucks')
        if trucks is None and instance:
            trucks = list(instance.trucks.values_list('id', flat=True))
        trucks = trucks or []
        assigned_at = attrs.get('assigned_at') or (instance.assigned_at if instance else None)
        unassigned_at = attrs.get('unassigned_at')
        if unassigned_at is None and instance:
            unassigned_at = instance.unassigned_at

        if not crew or not assigned_at:
            return attrs

        # No overlapping assignments for the same crew
        crew_qs = TruckAssignment.objects.filter(crew=crew).exclude(pk=instance.pk if instance else 0)
        for other in crew_qs:
            if _periods_overlap(assigned_at, unassigned_at, other.assigned_at, other.unassigned_at):
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"Crew '{crew.name}' already has an overlapping assignment ({other.assigned_at} - {other.unassigned_at or 'ongoing'})."
                    ]
                })

        # No overlapping assignments for the same truck (different crews)
        for item in trucks:
            tid = item.id if hasattr(item, 'id') else item
            truck_assignments = TruckAssignment.objects.filter(trucks__id=tid).exclude(pk=instance.pk if instance else 0)
            for other in truck_assignments:
                if _periods_overlap(assigned_at, unassigned_at, other.assigned_at, other.unassigned_at):
                    truck = Truck.objects.filter(pk=tid).first()
                    truck_str = str(truck) if truck else f"ID {tid}"
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            f"Truck '{truck_str}' is already assigned to another crew during this period."
                        ]
                    })

        return attrs

    def create(self, validated_data):
        trucks = validated_data.pop('trucks', [])
        instance = TruckAssignment.objects.create(**validated_data)
        if trucks:
            instance.trucks.set(trucks)
        return instance

    def update(self, instance, validated_data):
        trucks = validated_data.pop('trucks', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if trucks is not None:
            instance.trucks.set(trucks)
        return instance

    class Meta:
        model = TruckAssignment
        fields = ['id', 'crew', 'crew_name', 'trucks', 'trucks_display', 'assigned_at', 'unassigned_at']
        read_only_fields = ['crew_name', 'trucks_display']
