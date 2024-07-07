from django.apps import AppConfig


class TaskschedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "TaskScheduler"

    def ready(self):
        import TaskScheduler.models  # This ensures models are loaded
