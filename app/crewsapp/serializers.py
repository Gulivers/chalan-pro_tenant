import re
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import connection, transaction
from django_tenants.utils import get_public_schema_name

from utils.tenant_branding import _resolve_tenant
from .models import Crew, Truck, TruckAssignment, TruckAssignmentTruck, Category

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


VIN_RE = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$', re.IGNORECASE)


class TruckSerializer(serializers.ModelSerializer):
    current_mileage = serializers.SerializerMethodField()
    current_mileage_display = serializers.SerializerMethodField()

    class Meta:
        model = Truck
        fields = [
            'id',
            'unit_number',
            'plate_number',
            'vin',
            'make',
            'model',
            'year',
            'fleet_status',
            'registration_expiration',
            'insurance_expiration',
            'status',
            'current_mileage',
            'current_mileage_display',
        ]
        read_only_fields = ['current_mileage', 'current_mileage_display']

    def get_current_mileage(self, obj):
        return obj.current_mileage()

    def get_current_mileage_display(self, obj):
        miles = obj.current_mileage()
        return 'Not recorded' if miles is None else miles

    def validate_unit_number(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Unit number is required.')
        qs = Truck.objects.filter(unit_number__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Unit number must be unique.')
        return value

    def validate_vin(self, value):
        value = (value or '').strip().upper()
        if len(value) != 17 or not value.isalnum():
            raise serializers.ValidationError(
                'VIN must be exactly 17 alphanumeric characters.'
            )
        if not VIN_RE.match(value):
            # Still allow digits/letters; I and O/Q often excluded in real VIN — keep simple alnum rule.
            pass
        qs = Truck.objects.filter(vin__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('VIN must be unique.')
        return value

    def validate_make(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Make is required.')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Required on create for expiration dates
        if self.instance is None:
            if not attrs.get('registration_expiration'):
                raise serializers.ValidationError({
                    'registration_expiration': 'Registration expiration is required.',
                })
            if not attrs.get('insurance_expiration'):
                raise serializers.ValidationError({
                    'insurance_expiration': 'Insurance expiration is required.',
                })
        return attrs


# Serializador para Crew
class CrewSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def validate(self, attrs):
        instance = self.instance
        name = (attrs.get('name') or (instance.name if instance else '') or '').strip()
        category = attrs.get('category') if 'category' in attrs else (instance.category if instance else None)

        if instance is None:
            request = self.context.get('request')
            tenant = _resolve_tenant(request) if request else getattr(connection, 'tenant', None)
            if tenant and getattr(tenant, 'schema_name', None) != get_public_schema_name():
                from appbilling.services.crews import validate_crew_create
                crew_err = validate_crew_create(tenant)
                if crew_err:
                    raise serializers.ValidationError({'non_field_errors': [crew_err]})

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


class TruckReadingSerializer(serializers.Serializer):
    truck = serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all())
    starting_mileage = serializers.IntegerField(min_value=0)
    ending_mileage = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    def validate(self, attrs):
        start = attrs.get('starting_mileage')
        end = attrs.get('ending_mileage')
        if end is not None and start is not None and end < start:
            raise serializers.ValidationError({
                'ending_mileage': 'Ending mileage cannot be less than starting mileage.',
            })
        return attrs


class TruckAssignmentSerializer(serializers.ModelSerializer):
    crew_name = serializers.SerializerMethodField()
    trucks_display = serializers.SerializerMethodField()
    truck_readings = TruckReadingSerializer(many=True, required=False)
    # Keep trucks as read-only list of IDs for list views / legacy clients.
    trucks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def get_crew_name(self, obj):
        return obj.crew.name if obj.crew else None

    def get_trucks_display(self, obj):
        rows = []
        for link in obj.truck_links.select_related('truck').all():
            t = link.truck
            rows.append(
                f"{t.unit_number} · {t.plate_number} - {t.make} {t.model}"
            )
        return rows

    def to_representation(self, instance):
        data = super().to_representation(instance)
        readings = []
        for link in instance.truck_links.select_related('truck').all():
            readings.append({
                'truck': link.truck_id,
                'unit_number': link.truck.unit_number,
                'plate_number': link.truck.plate_number,
                'make': link.truck.make,
                'model': link.truck.model,
                'starting_mileage': link.starting_mileage,
                'ending_mileage': link.ending_mileage,
            })
        data['truck_readings'] = readings
        data['trucks'] = [r['truck'] for r in readings]
        return data

    def validate(self, attrs):
        instance = self.instance
        crew = attrs.get('crew') or (instance.crew if instance else None)
        assigned_at = attrs.get('assigned_at') or (instance.assigned_at if instance else None)
        unassigned_at = attrs.get('unassigned_at', serializers.empty)
        if unassigned_at is serializers.empty:
            unassigned_at = instance.unassigned_at if instance else None

        readings = attrs.get('truck_readings', serializers.empty)
        if readings is serializers.empty:
            if instance:
                readings = [
                    {
                        'truck': link.truck,
                        'starting_mileage': link.starting_mileage,
                        'ending_mileage': link.ending_mileage,
                    }
                    for link in instance.truck_links.select_related('truck')
                ]
            else:
                readings = []

        if not readings:
            raise serializers.ValidationError({
                'truck_readings': 'At least one truck with mileage is required.',
            })

        seen = set()
        for row in readings:
            truck = row['truck'] if isinstance(row, dict) else row.get('truck')
            tid = truck.id if hasattr(truck, 'id') else truck
            if tid in seen:
                raise serializers.ValidationError({
                    'truck_readings': 'Duplicate trucks are not allowed.',
                })
            seen.add(tid)
            start = row['starting_mileage'] if isinstance(row, dict) else None
            end = row.get('ending_mileage') if isinstance(row, dict) else None
            if start is None:
                raise serializers.ValidationError({
                    'truck_readings': 'Starting mileage is required for each truck.',
                })
            if unassigned_at is not None:
                if end is None:
                    raise serializers.ValidationError({
                        'truck_readings': (
                            'Ending mileage is required when registering truck return '
                            '(unassigned at is set).'
                        ),
                    })
                if end < start:
                    raise serializers.ValidationError({
                        'truck_readings': (
                            'Ending mileage cannot be less than starting mileage.'
                        ),
                    })

        attrs['truck_readings'] = readings

        if not crew or not assigned_at:
            return attrs

        # No overlapping assignments for the same crew
        crew_qs = TruckAssignment.objects.filter(crew=crew).exclude(
            pk=instance.pk if instance else 0
        )
        for other in crew_qs:
            if _periods_overlap(assigned_at, unassigned_at, other.assigned_at, other.unassigned_at):
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"Crew '{crew.name}' already has an overlapping assignment "
                        f"({other.assigned_at} - {other.unassigned_at or 'ongoing'})."
                    ]
                })

        # No overlapping assignments for the same truck
        for row in readings:
            truck = row['truck']
            tid = truck.id if hasattr(truck, 'id') else truck
            truck_assignments = TruckAssignment.objects.filter(
                trucks__id=tid
            ).exclude(pk=instance.pk if instance else 0)
            for other in truck_assignments:
                if _periods_overlap(
                    assigned_at, unassigned_at, other.assigned_at, other.unassigned_at
                ):
                    truck_obj = truck if hasattr(truck, 'id') else Truck.objects.filter(pk=tid).first()
                    truck_str = str(truck_obj) if truck_obj else f"ID {tid}"
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            f"Truck '{truck_str}' is already assigned to another crew "
                            f"during this period."
                        ]
                    })

        return attrs

    def _sync_readings(self, instance, readings):
        instance.truck_links.all().delete()
        for row in readings:
            truck = row['truck']
            TruckAssignmentTruck.objects.create(
                assignment=instance,
                truck=truck,
                starting_mileage=row['starting_mileage'],
                ending_mileage=row.get('ending_mileage'),
            )

    @transaction.atomic
    def create(self, validated_data):
        readings = validated_data.pop('truck_readings', [])
        instance = TruckAssignment.objects.create(**validated_data)
        self._sync_readings(instance, readings)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        readings = validated_data.pop('truck_readings', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if readings is not None:
            self._sync_readings(instance, readings)
        return instance

    class Meta:
        model = TruckAssignment
        fields = [
            'id',
            'crew',
            'crew_name',
            'trucks',
            'trucks_display',
            'truck_readings',
            'assigned_at',
            'unassigned_at',
        ]
        read_only_fields = ['crew_name', 'trucks_display', 'trucks']
