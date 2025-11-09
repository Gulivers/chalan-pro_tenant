from django.apps import AppConfig


class AppcoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appcore'

    def ready(self):
        """// Carga señales de appcore (por ahora, creación automática de tokens)."""
        from . import signals  # noqa: F401