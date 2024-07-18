from threading import Thread
import http.client
import queue
from typing import Callable, List, Set, Tuple
import time

from TaskScheduler.models import Subtask


MAX_SENDER_THREADS = 5
MAX_RETRIES = 5
TIMEOUT = 5  # seconds
MANAGER_THREAD_SLEEP_TIME = 0.5 # seconds

class ThreadJob:
	Thread: Thread
	Subtask: Subtask
	Done: bool

	def __init__(self, thread: Thread, subtask: Subtask):
		self.Thread = thread
		self.Subtask = subtask
		self.Done = False


class Sender:
	taskQueue: queue = queue.Queue()
	canceledTasks: Set = set()
	threads: List[ThreadJob] = [ThreadJob(Thread(), None) for i in range(MAX_SENDER_THREADS)]
	sendingFailedCallback: Callable[[Subtask], None] = None

	managerThread = None

	@staticmethod
	def set_callbacks(sendingFailedCb: Callable[[Subtask], None]):
		Sender.sendingFailedCallback = sendingFailedCb

		Sender.managerThread = Thread(target=Sender.assign_tasks, daemon=True)
		Sender.managerThread.start()

	@staticmethod
	def assign_tasks():  # runs on manager thread
		while True:
			time.sleep(0.5)

			for i in range(MAX_SENDER_THREADS):
				if (Sender.threads[i].Thread.is_alive()):
					continue

				if Sender.threads[i].Done is False:  # failed
					Sender.sendingFailedCallback(Sender.threads[i].Subtask)
					Sender.threads[i].Done = True  # so it isn't handled twice if there is no new Subtask that replaces the current one

				# both True and False in Sender.threads[i][2]
				if (Sender.taskQueue.empty()):
					continue

				task = Sender.taskQueue.get()
				if task in Sender.canceledTasks:
					Sender.canceledTasks.remove(task)
					continue

				newThread = Thread(target=Sender.send, args=(task, i))
				newThread.start()
				Sender.threads[i] = ThreadJob(newThread, task)


	@staticmethod
	def add_task(task: Subtask):  # called from "outside" (main thread)
		Sender.taskQueue.put(task)

	@staticmethod
	def cancel_task(task: Subtask):  # called from "outside" (main thread)
		Sender.canceledTasks.add(task)

	@staticmethod
	def send(task: Subtask, threadIndex: int):  # called from manager thread in new thread
		success = False
		tries = 0
		while not success and tries < MAX_RETRIES:
			try:
				tries += 1
				headers = task.to_headers()
				connection = http.client.HTTPConnection(task.Worker.Host, task.Worker.Port, timeout=TIMEOUT)
				connection.request("GET", "STARTTASK", headers=headers)
				response = connection.getresponse()
				connection.close()
				if response.status == 200:
					success = True
				# TODO: handle other statuses

			except Exception as ex:
				print(f"Exception occurred while trying to send Subtask {task.Task.TaskID}:{task.SubtaskIndex} to Worker {task.Worker.WorkerID}")
				print(ex)

		Sender.threads[threadIndex].Done = success