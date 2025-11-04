from django.contrib import admin
from .models import Event, EventDraft, AbsenceReason, EventImage
from django.utils.html import format_html


class BaseCrewTitleAdmin(admin.ModelAdmin):
    def crew_title(self, obj):
        if hasattr(obj, 'crew') and obj.crew:
            crew_name = obj.crew.name
            category = obj.crew.category.name if obj.crew.category else "No category"
            return f"{crew_name} ({category})"
        return "No crew assigned"

    crew_title.short_description = 'Crew'


@admin.register(Event)
class EventAdmin(BaseCrewTitleAdmin):
    list_display = ['title', 'date', 'end_dt', 'crew_title', 'builder', 'job', 'house_model', 'deleted']
    search_fields = ['title']
    list_filter = ['deleted', 'crew__category']

@admin.register(EventDraft)
class EventDraftAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'date', 'end_dt', 'crew', 'job', 'lot', 'house_model',
        'is_absence', 'extended_service', 'created_by', 'created_at'
    )
    list_filter = ('crew', 'job', 'is_absence', 'extended_service', 'created_at')
    search_fields = ('lot', 'address', 'title', 'description', 'notes')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Event Info', {
            'fields': (
                'date', 'end_dt', 'crew', 'job', 'builder', 'house_model',
                'lot', 'address', 'title', 'description', 'notes'
            )
        }),
        ('Status & Details', {
            'fields': (
                'extended_service', 'is_absence', 'absence_reason',
            )
        }),
        ('Audit Info', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(AbsenceReason)
class AbsenceReasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    search_fields = ['name', 'description']
    list_filter = ['is_active']

    
@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('id','event_id', 'event', 'uploaded_by', 'uploaded_at', 'image_preview')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('event__title', 'title', 'lot', 'address')
    readonly_fields = ('image_preview', 'uploaded_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" style="border-radius:4px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);"/>',
                obj.image.url
            )
        return "(No image)"

    image_preview.short_description = 'Preview'
    autocomplete_fields = ['event']
