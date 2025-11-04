from django.contrib import admin
from .models import Truck, Crew, TruckAssignment, Category

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'model', 'year', 'status']
    list_filter = ('model', 'year', 'status')
    search_fields = ['plate_number', 'model', 'year', 'status']


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    filter_horizontal = ['members', 'jobs']
    list_display = ['name', 'category', 'status', 'permission_create_event']
    list_filter = ['category']
    search_fields = ['name']

admin.site.register(Category)
# admin.site.register(Crew)
admin.site.register(TruckAssignment)
