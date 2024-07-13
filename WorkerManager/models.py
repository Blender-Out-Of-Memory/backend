from django.db import models

from .Enums import WorkerStatus


class Worker(models.Model):
	WorkerID_INT        = models.PositiveSmallIntegerField(primary_key=True)
	WorkerID            = models.CharField(max_length=21)
	Host                = models.URLField(max_length=255)
	Port                = models.PositiveIntegerField()
	PerformanceScore    = models.PositiveIntegerField()
	Status              = models.CharField(max_length=2, choices=WorkerStatus)
