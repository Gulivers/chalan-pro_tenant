from django.apps import AppConfig


class AppsearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appsearch'
    verbose_name = 'Semantic Search'

    def ready(self):
        from appsearch import signals  # noqa: F401
