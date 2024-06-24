from django.apps import AppConfig


class TaskschedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TaskScheduler'

    def ready(self):
        # imports for including models in migrations
        # must be set here because apps must be initialized first
        from .TaskScheduler import RenderTask
