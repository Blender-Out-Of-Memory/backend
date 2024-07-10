from enum import Enum


class WorkerStatus(Enum):
	Available = 1
	Working = 2
	Quitting = 3  # will quit after finishing current task
	Disconnected = 4
