from typing import Callable
from django.http import HttpResponse, HttpRequest


class WorkerManager:
	freeWorkerCallback: Callable[[], None] = None
	freeWorkerCalled: bool = True  # informed TaskScheduler about available Worker ready

	@staticmethod
	def set_callbacks(freeWorkerCallback: Callable):
		WorkerManager.freeWorkerCallback = freeWorkerCallback
		if (not WorkerManager.freeWorkerCalled):
			WorkerManager.freeWorkerCallback()
			WorkerManager.freeWorkerCalled = True

	@staticmethod
	def register(request) -> HttpResponse:
		pass

	@staticmethod
	def unregister(request) -> HttpResponse:
		pass

