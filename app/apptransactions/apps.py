from django.apps import AppConfig


class ApptransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apptransactions'

    def ready(self):
        import apptransactions.signals 
