from django.db import models
from django.contrib.auth.models import User

class UserActionLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    # action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Action Type")
    action = models.CharField(max_length=10, verbose_name="Action Type")
    model_name = models.CharField(max_length=255, verbose_name="Model Affected")
    object_id = models.CharField(null=True, max_length=255, verbose_name="Object ID")
    action_time = models.DateTimeField(auto_now_add=True, verbose_name="Action Time")
    details = models.TextField(null=True, blank=True, verbose_name="Details")

    def __str__(self):
        return f"{self.user.username} {self.action} {self.model_name} {self.object_id} on {self.action_time}"
