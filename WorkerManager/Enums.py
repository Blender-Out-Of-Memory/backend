from django.db import models

class WorkerStatus(models.TextChoices):
	Available       = ("AV", "Available")
	Working         = ("WK", "Working")
	Quitting        = ("QT", "Quitting")  # Working but will quit after finishing current task
	Disconnected    = ("DC", "Disconnected")
