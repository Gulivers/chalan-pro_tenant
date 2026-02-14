from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Truck, Crew, TruckAssignment, Category


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

    def clean_trucks(self):
        trucks = self.cleaned_data.get('trucks')
        if not trucks:
            return trucks
        ids = [t.id for t in trucks]
        if len(ids) != len(set(ids)):
            raise ValidationError("Duplicate trucks are not allowed.")
        return trucks

    def clean(self):
        cleaned_data = super().clean()
        crew = cleaned_data.get('crew')
        trucks = cleaned_data.get('trucks')
        assigned_at = cleaned_data.get('assigned_at')
        unassigned_at = cleaned_data.get('unassigned_at')
        instance = self.instance

        if not crew or not assigned_at:
            return cleaned_data

        truck_ids = list(trucks.values_list('id', flat=True)) if trucks else []

        # No overlapping assignments for the same crew
        qs = TruckAssignment.objects.filter(crew=crew).exclude(pk=instance.pk if instance else 0)
        for other in qs:
            if _periods_overlap(assigned_at, unassigned_at, other.assigned_at, other.unassigned_at):
                raise ValidationError(
                    f"Crew '{crew.name}' already has an overlapping assignment "
                    f"({other.assigned_at} - {other.unassigned_at or 'ongoing'})."
                )

        # No overlapping assignments for the same truck
        for truck in trucks or []:
            others = TruckAssignment.objects.filter(trucks=truck).exclude(pk=instance.pk if instance else 0)
            for other in others:
                if _periods_overlap(assigned_at, unassigned_at, other.assigned_at, other.unassigned_at):
                    raise ValidationError(
                        f"Truck '{truck}' is already assigned to another crew during this period."
                    )

        return cleaned_data


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'model', 'year', 'status']
    list_filter = ('model', 'year', 'status')
    search_fields = ['plate_number', 'model', 'year', 'status']


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

admin.site.register(Category)


@admin.register(TruckAssignment)
class TruckAssignmentAdmin(admin.ModelAdmin):
    form = TruckAssignmentAdminForm
    list_display = ['id', 'crew', 'trucks_display', 'assigned_at', 'unassigned_at']
    list_filter = ['crew', 'assigned_at']
    search_fields = ['crew__name']
    filter_horizontal = ['trucks']
    autocomplete_fields = ['crew']

    @admin.display(description='Trucks')
    def trucks_display(self, obj):
        return ', '.join(str(t) for t in obj.trucks.all()) or '—'
