from django.contrib import admin
from .models import ManualEntry, ManualCategory

@admin.register(ManualCategory)
class ManualCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(ManualEntry)
class ManualEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'category', 'is_active', 'created_at', 'updated_at')  # Agrega aquí otros campos relevantes
    list_filter = ('category',)
    search_fields = ('id','title', 'summary', 'content',)  # O el campo que uses como identificador
    ordering = ('-created_at',)
    
