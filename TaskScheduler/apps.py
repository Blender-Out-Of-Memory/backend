from django.apps import AppConfig

from threading import Thread

class TaskschedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "TaskScheduler"

    def ready(self):
        from .TaskScheduler import TaskScheduler
        from WorkerManager.WorkerManager import WorkerManager
        WorkerManager.set_callbacks(TaskScheduler.distribute_tasks, TaskScheduler.subtask_finished, TaskScheduler.subtask_failed)

        from .ConcatManager import ConcatManager
        Thread(target=ConcatManager.assign_tasks).start()
