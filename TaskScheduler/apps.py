from django.apps import AppConfig


class TaskschedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "TaskScheduler"

    def ready(self):
        from .TaskScheduler import TaskScheduler
        from WorkerManager.WorkerManager import WorkerManager
        WorkerManager.set_callbacks(TaskScheduler.distribute_tasks, TaskScheduler.subtask_finished, TaskScheduler.subtask_failed)