from django.apps import AppConfig


class WorkermanagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'WorkerManager'

    def ready(self):
        from .WorkerManager import WorkerManager
        from .Sender import Sender
        from .models import Worker
        from .Enums import WorkerStatus
        Sender.set_callbacks(WorkerManager.sending_failed)

        for worker in Worker.objects.all():
            worker.Status = WorkerStatus.Disconnected
            worker.save()

