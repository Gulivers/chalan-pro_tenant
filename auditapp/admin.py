from django.contrib import admin
from .models import UserActionLog

# admin.site.register(UserActionLog)

class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'action_time', 'full_log')  # Add new column
    search_fields = ('user__username', 'action', 'model_name', 'object_id', 'action_time')  # Enables search
    list_filter = ('action', 'user', 'action_time')  # Filters for easier navigation
    ordering = ('-action_time',)  # Sort by most recent activity first
    date_hierarchy = 'action_time'  # Adds a date-based filter in Django Admin

    # Custom method to display concatenated log
    def full_log(self, obj):
        return f"{obj.user.username} {obj.action} {obj.model_name} {obj.object_id} on {obj.action_time}"

    full_log.short_description = "Full Log"  # Custom column title in the admin

admin.site.register(UserActionLog, UserActionLogAdmin)