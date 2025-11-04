# admin.py

from django.contrib import admin
from .models import WorkPrice, Builder, Job, HouseModel, Contract, ContractDetails

admin.site.site_header = "Chalan-Pro Administration"
admin.site.site_title = "Chalan-Pro Admin"
admin.site.index_title = "Welcome to the Chalan-Pro Admin Panel"

@admin.register(WorkPrice)
class WorkPriceAdmin(admin.ModelAdmin):
    list_display = ['name', 'trim', 'rough', 'unit_price']
    list_filter = ('builders',)
    search_fields = ['name', 'trim', 'rough']

@admin.register(Builder)
class BuilderAdmin(admin.ModelAdmin):
    list_display = ['name', 'party', 'trim_amount', 'rough_amount', 'travel_price_amount']
    list_filter = ('jobs',)
    search_fields = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['name', 'builder']
    list_filter = ('builder',)
    search_fields = ['name', 'id']

@admin.register(HouseModel)
class HouseModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ('jobs',)
    search_fields = ['name']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'builder', 'job', 'house_model', 'lot', 'sqft', 'address', 'total', 'date_created']
    list_filter = ['type', 'builder', 'job', 'date_created']
    search_fields = ['house_model__name', 'builder__name', 'job__name', 'address', 'type']

@admin.register(ContractDetails)
class ContractDetailsAdmin(admin.ModelAdmin):
    list_display = ['cdname', 'cdtrim', 'cdtrim_qty', 'cdrough', 'cdrough_qty', 'cdunit_price', 'cdwork_price']
    list_filter = ['cdwork_price']
    search_fields = ['cdname', 'cdwork_price__name']

