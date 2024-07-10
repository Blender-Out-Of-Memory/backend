from django.db import models

from .Enums import WorkerStatus


class Worker(models.Model):
    WorkerID:           models.CharField(max_length=21)
    Host:               models.URLField(max_length=255)
    Port:               models.PositiveIntegerField()
    PerformanceScore:   models.PositiveIntegerField()
    status:             models.CharField(max_length=1)

    @property
    def Status(self):
        return WorkerStatus(self.Status)
