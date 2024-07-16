import re
from typing import Callable, List
from http import HTTPStatus

from django.db.models import Max, QuerySet
from django.http import HttpResponse, HttpRequest, FileResponse

from .models import Worker
from .Enums import WorkerStatus
from .Sender import Sender

# Different Django app
from TaskScheduler.models import RenderTask, Subtask
from TaskScheduler.Enums import SubtaskStage, TaskStage


def _int_to_id(value: int, prefix: str) -> str:
	hex_string = format(value, 'x')
	hex_string = hex_string.zfill(16)
	formatted_hex = '_'.join(hex_string[i:i + 4] for i in range(0, len(hex_string), 4))
	return f"{prefix}{formatted_hex}"

def _id_to_int(value: str, prefix: str) -> int:
	hex_string = value[len(prefix):]
	hex_string.replace("_", "")
	return int(hex_string, 16)

def _is_valid_id(id: str, prefix: str) -> bool:
	pattern = prefix + r"{prefix}[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}"
	return re.fullmatch(pattern, id) is not None


class WorkerManager:
	idCounter: int = 0

	freeWorkerCallback: Callable[[], None] = None
	freeWorkerCalled: bool = True  # TaskScheduler knows about available Worker

	subtaskFinishedCallback: Callable[[RenderTask], None] = None

	subtaskFailedCallback: Callable[[Subtask], None] = None


	### Called via URL
	@staticmethod
	def set_callbacks(freeWorkerCb: Callable[[], None],
					  subtaskFinishedCb: Callable[[RenderTask], None],
					  subtaskFailedCb: Callable[[Subtask], None]):

		WorkerManager.freeWorkerCallback = freeWorkerCb
		if (not WorkerManager.freeWorkerCalled):
			WorkerManager.freeWorkerCallback()
			WorkerManager.freeWorkerCalled = True

		WorkerManager.subtaskFinishedCallback = subtaskFinishedCb
		WorkerManager.subtaskFailedCallback = subtaskFailedCb

	@staticmethod
	def register(request: HttpRequest) -> HttpResponse:
		difference = {"Worker-Id", "Host", "Port", "Performance-Score"}.difference(request.headers)
		print(difference)
		if difference:  # difference is not empty -> header fields missing
			print("Difference not empty, sending response")
			return HttpResponse(f"Missing header fields for registration: {", ".join(difference)}".encode("utf-8"), content_type="text/plain", status=HTTPStatus.BAD_REQUEST)

		workerID = request.headers["Worker-Id"]

		if not _is_valid_id(workerID, "W-"):
			print(f"Invalid Worker ID: {workerID}")
			max = Worker.objects.aggregate(Max("WorkerID_Int"))["WorkerID_Int__max"]
			WorkerManager.idCounter = 0 if (max is None) else max + 1
			workerID = _int_to_id(WorkerManager.idCounter, "W-")
			workerID_int = WorkerManager.idCounter

		else:
			workerID_int = _id_to_int(workerID, "W-")
			if (WorkerManager.idCounter <= workerID_int):
				WorkerManager.idCounter = workerID_int

		host = request.headers["Host"]
		# TODO: check request.headers["Host"] is valid

		try:
			port = int(request.headers["Port"])
			if (port <= 0 or port > 65535):
				raise ValueError(f"Invalid port {port}")
		except:
			return HttpResponse(f"Invalid port header field: {request.headers["Port"]}", status=HTTPStatus.BAD_REQUEST)

		try:
			score = int(request.headers["Performance-Score"])
			if (score <= 0):
				raise ValueError(f"Invalid performance score {score}")
		except:
			return HttpResponse(f"Invalid performance score header field: {request.headers["Performance-Score"]}", status=HTTPStatus.BAD_REQUEST)

		Worker(WorkerID_Int=workerID_int, WorkerID=workerID, Host=host, Port=port, PerformanceScore=score, Status=WorkerStatus.Available).save()
		WorkerManager.freeWorkerCallback()

		return HttpResponse("Registered worker successfully", status=HTTPStatus.OK, headers={"Worker-Id": workerID})

	@staticmethod
	def unregister(request: HttpRequest) -> HttpResponse:
		difference = {"Worker-Id"}.difference(request.headers)  # TODO (later): add some kind of authentication key
		if difference:  # difference is not empty -> header fields missing
			return HttpResponse(f"Missing header fields for unregistration: {", ".join(difference)}", status=HTTPStatus.BAD_REQUEST)

		workerID = request.headers["Worker-Id"]
		if not _is_valid_id(workerID, "W-"):
			return HttpResponse("Invalid WorkerID", status=HTTPStatus.BAD_REQUEST)

		workerID_int = _id_to_int(workerID, "W-")
		filtered: QuerySet = Worker.objects.filter(WorkerID_Int=workerID_int)
		if not filtered.exists():
			return HttpResponse("Unknown WorkerID", Status=HTTPStatus.BAD_REQUEST)

		newStatus = WorkerStatus.Quitting  # provisional, optimistic assertion
		if ("Unregistration-Type" in request.headers):
			if (request.headers["Unregistration-Type"] == "Quitting"):
				newStatus = WorkerStatus.Quitting
			elif (request.headers["Unregistration-Type"] == "Force-Quitting"):
				newStatus = WorkerStatus.Disconnected
				# TODO: call TaskScheduler to redistribute subtask

		filtered.first().Status = newStatus

	@staticmethod
	def receive_result(request: HttpRequest):
		difference = {"Worker-Id", "Task-Id", "Subtask-Index", "Frame"}.difference(set(request.headers))
		if difference:  # difference is not empty -> header fields missing
			return HttpResponse(f"Missing header fields: {", ".join(difference)}", status=HTTPStatus.BAD_REQUEST)

		# Check WorkerID
		workerID = request.headers["Worker-Id"]
		if not _is_valid_id(workerID, "W-"):
			return HttpResponse("Invalid WorkerID", status=HTTPStatus.BAD_REQUEST)

		workerID_int = _id_to_int(workerID, "W-")
		filtered: QuerySet = Worker.objects.filter(WorkerID_Int=workerID_int)
		if not filtered.exists():
			return HttpResponse("Unknown WorkerID", Status=HTTPStatus.BAD_REQUEST)

		# Check TaskID
		taskID = request.headers["Task-Id"]
		if not _is_valid_id(taskID, "T-"):
			return HttpResponse("Invalid TaskID", status=HTTPStatus.BAD_REQUEST)

		taskID_int = _id_to_int(taskID, "T-")
		filtered: QuerySet = RenderTask.objects.filter(TaskID_Int=taskID_int)
		if not filtered.exists():
			return HttpResponse("Unknown TaskID", Status=HTTPStatus.BAD_REQUEST)

		task = filtered[0]

		# Check Subtask
		try:
			subtaskIndex = request.headers["Subtask-Index"]
		except:
			return HttpResponse("Invalid value in header field 'Subtask-Index'", status=HTTPStatus.BAD_REQUEST)

		filtered = Subtask.objects.filter(Task=taskID_int, Worker=workerID_int, SubtaskIndex=subtaskIndex)
		if not filtered.exists():
			return HttpResponse("Worker not responsible for this task", status=HTTPStatus.BAD_REQUEST)

		subtask = filtered[0]

		# Check Frame
		try:
			frame = int(request.headers["Frame"])
		except:
			return HttpResponse("Invalid value in header field 'Frame'", status=HTTPStatus.BAD_REQUEST)

		if (frame < subtask.StartFrame or frame > subtask.EndFrame):
			return HttpResponse(f"Got unexpected frame {frame}", status=HTTPStatus.BAD_REQUEST)  # other HTTPStatus: not responsible
			# TODO: Check if Worker runs with wrong task


		filepath = f"{task.get_folder()}{str(frame)}{task.OutputType.get_extension()}"
		with open(filepath, 'wb') as file:
			file.write(request.body)

		subtask.LastestFrame = frame

		if (frame == subtask.EndFrame):
			subtask.Stage = SubtaskStage.Finished
			WorkerManager.subtaskFinishedCallback(task)

		subtask.save()

	@staticmethod
	def download_blender_data(request: HttpRequest):
		# TODO: check if Worker is responsible for task
		difference = {"Task-Id"}.difference(set(request.headers))
		if difference:  # difference is not empty -> header fields missing
			return HttpResponse(f"Missing header fields: {", ".join(difference)}", status=HTTPStatus.BAD_REQUEST)

		# Check TaskID
		taskID = request.headers["Task-Id"]
		if not _is_valid_id(taskID, "T-"):
			return HttpResponse("Invalid TaskID", status=HTTPStatus.BAD_REQUEST)

		taskID_int = _id_to_int(taskID, "T-")
		filtered: QuerySet = RenderTask.objects.filter(TaskID_Int=taskID_int)
		if not filtered.exists():
			return HttpResponse("Unknown TaskID", Status=HTTPStatus.BAD_REQUEST)

		task = filtered[0]
		if (TaskStage(task.Stage) == TaskStage.Expired):
			return HttpResponse("Stage of Task is 'Expired'. Blender data doesn't exist anymore", Status=HTTPStatus.BAD_REQUEST)

		path = task.get_blender_data_path()
		with open(path, "rb") as file:
			response = FileResponse(file)

		return response

	### Called from TaskScheduler
	@staticmethod
	def distribute_subtasks(subtasks: List[Subtask]):
		for subtask in subtasks:
			Sender.add_task(subtask)


	### Callback for Sender
	@staticmethod
	def sending_failed(subtask: Subtask):
		WorkerManager.subtaskFailedCallback(subtask)
