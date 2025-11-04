from django.apps import AppConfig


class AppscheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appschedule'
    verbose_name = 'Schedule Module'

    def ready(self):
        import appschedule.signals
