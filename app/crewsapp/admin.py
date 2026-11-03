from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Truck, Crew, TruckAssignment, TruckAssignmentTruck, Category


def _periods_overlap(a1, u1, a2, u2):
    """Check if two time periods overlap. None end means ongoing."""
    from datetime import datetime
    tz = a1.tzinfo if getattr(a1, 'tzinfo', None) else None
    far_future = datetime(9999, 12, 31, 23, 59, 59, tzinfo=tz)
    end1 = u1 if u1 is not None else far_future
    end2 = u2 if u2 is not None else far_future
    return a1 < end2 and end1 > a2


class TruckAssignmentAdminForm(forms.ModelForm):
    class Meta:
        model = TruckAssignment
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        crew = cleaned_data.get('crew')
        assigned_at = cleaned_data.get('assigned_at')
        unassigned_at = cleaned_data.get('unassigned_at')
        instance = self.instance

        if not crew or not assigned_at:
            return cleaned_data

        # No overlapping assignments for the same crew
        qs = TruckAssignment.objects.filter(crew=crew).exclude(
            pk=instance.pk if instance else 0
        )
        for other in qs:
            if _periods_overlap(
                assigned_at, unassigned_at, other.assigned_at, other.unassigned_at
            ):
                raise ValidationError(
                    f"Crew '{crew.name}' already has an overlapping assignment "
                    f"({other.assigned_at} - {other.unassigned_at or 'ongoing'})."
                )

        return cleaned_data


class TruckAssignmentTruckInline(admin.TabularInline):
    model = TruckAssignmentTruck
    extra = 1
    autocomplete_fields = ['truck']
    fields = ['truck', 'starting_mileage', 'ending_mileage']


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = [
        'unit_number',
        'plate_number',
        'make',
        'model',
        'year',
        'fleet_status',
        'status',
        'current_mileage_display',
        'mobile_warehouse_link',
    ]
    list_filter = ('fleet_status', 'make', 'year', 'status')
    search_fields = ['unit_number', 'plate_number', 'vin', 'make', 'model']
    actions = ['create_mobile_warehouse']

    @admin.display(description='Current Mileage')
    def current_mileage_display(self, obj):
        miles = obj.current_mileage()
        return f'{miles} mi' if miles is not None else 'Not recorded'

    @admin.display(description='Mobile Warehouse')
    def mobile_warehouse_link(self, obj):
        try:
            wh = obj.mobile_warehouse
        except Exception:
            return '—'
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:appinventory_warehouse_change', args=[wh.id])
        return format_html('<a href="{}">{}</a>', url, wh.name)

    @admin.action(description='Create mobile warehouse for selected trucks')
    def create_mobile_warehouse(self, request, queryset):
        from appinventory.models import Warehouse
        from django.contrib import messages
        created = 0
        errors = []
        for truck in queryset:
            if not truck.plate_number or not truck.model:
                errors.append(f'Truck {truck}: missing plate_number or model')
                continue
            try:
                if truck.mobile_warehouse:
                    continue
            except Exception:
                pass
            name = f'Truck {truck.plate_number} - {truck.model} Stock'
            location = (
                f'Mobile inventory Truck {truck.plate_number} - {truck.model}'
            )
            existing = Warehouse.objects.filter(name=name).first()
            if existing and existing.truck_id != truck.id:
                errors.append(f"Warehouse '{name}' already exists")
                continue
            Warehouse.objects.create(
                name=name,
                location=location,
                truck=truck,
                is_active=True,
                is_default=False,
            )
            created += 1
        if created:
            messages.success(request, f'{created} mobile warehouse(s) created.')
        if errors:
            messages.warning(request, '; '.join(errors[:5]))


class CrewAdminForm(forms.ModelForm):
    class Meta:
        model = Crew
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        name = (cleaned_data.get('name') or '').strip()
        category = cleaned_data.get('category')
        instance = self.instance

        if name:
            qs = Crew.objects.filter(name__iexact=name, category=category)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                cat_str = category.name if category else 'without category'
                raise ValidationError(
                    f"A crew with name '{name}' already exists in category '{cat_str}'."
                )
        return cleaned_data


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    form = CrewAdminForm
    filter_horizontal = ['members', 'jobs']
    list_display = ['name', 'category', 'status', 'permission_create_event']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(TruckAssignment)
class TruckAssignmentAdmin(admin.ModelAdmin):
    form = TruckAssignmentAdminForm
    list_display = ['id', 'crew', 'trucks_display', 'assigned_at', 'unassigned_at']
    list_filter = ['crew', 'assigned_at']
    search_fields = ['crew__name']
    autocomplete_fields = ['crew']
    inlines = [TruckAssignmentTruckInline]

    @admin.display(description='Trucks')
    def trucks_display(self, obj):
        return ', '.join(str(t) for t in obj.trucks.all()) or '—'
