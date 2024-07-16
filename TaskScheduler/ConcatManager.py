import os
import subprocess
from threading import Thread
from queue import Queue
from typing import List, Tuple
import zipfile

from .models import RenderTask
from .Enums import RenderOutputType, BlenderDataType, TaskStage


MAX_CONCAT_THREADS = 2


class ThreadJob:
	Thread: Thread
	RenderTask: RenderTask
	Done: bool

	def __init__(self, thread: Thread, renderTask: RenderTask):
		self.Thread = thread
		self.RenderTask = renderTask
		self.Done = False


class ConcatManager:
	queue: Queue = Queue()
	threads: List[ThreadJob] = [ThreadJob(Thread(), None) for i in range(MAX_CONCAT_THREADS)]

	@staticmethod
	def add_task(task: RenderTask):
		ConcatManager.queue.put(task)

	@staticmethod
	def assign_tasks():
		while True:
			for i in range(MAX_CONCAT_THREADS):
				if (ConcatManager.threads[i].Thread.is_alive()):
					continue

				if ConcatManager.threads[i].Done is False:  # failed
					# TODO: callback if failed
					ConcatManager.threads[i].Done = True  # so it isn't handled twice if there is no new Subtask that replaces the current one

				task = ConcatManager.queue.get()

				newThread = Thread(target=ConcatManager.concatenate, args=(task, i))
				newThread.start()
				ConcatManager.threads[i] = ThreadJob(newThread, task)

	@staticmethod
	def concatenate(task: RenderTask, threadIndex: int):
		print(f"Starting concatenating for task {task.TaskID}")
		directory = task.get_folder()
		inputFormat = RenderOutputType(task.OutputType).get_extension()
		inputFormats = [inputFormat]
		outputFormat = "zip" if (BlenderDataType(task.DataType) == BlenderDataType.SingleFile) else inputFormat.lstrip(".")
		fps = 30  # TODO: add option for user to concatenate images to video and ask for frame rate

		result = ConcatManager.process_media(directory, inputFormats, outputFormat, fps)
		success = result[1]
		if success:
			task.Stage = TaskStage.Finished
		else:
			print(result[0])

		ConcatManager.threads[threadIndex].Done = success


	@staticmethod
	def process_media(directory: str, input_formats: List[str], output_format: str, fps=30) -> Tuple[str, bool]:
		# alle zusammenzufügende/ zu zippende files nach Name geordnet rein ins array
		files = [f for f in os.listdir(directory) if any(f.endswith(ext) for ext in input_formats)]
		if not files:
			return (f"Didn't find any files with the specified input formats: {", ".join(input_formats)}", False)

		output_file = os.path.join(directory, "output." + output_format)

		# Liste der gängigen/ zulässigen Output-Videoformate (alles ergänzbar, solange ffmpeg das jeweilige Format processed bekommt)
		video_formats = ["mp4", "mkv", "mov", "avi", "flv"]

		if output_format in video_formats:
			# temporäre Textdatei mit den Dateinamen für ffmpeg
			with open(os.path.join(directory, "filelist.txt"), 'w') as f:
				for file in files:
					f.write(f"file '{os.path.abspath(os.path.join(directory, file))}'\n")

			# ffmpeg Befehl, da das über os tatsächlich besser geht, als über das ffmpeg py module (kann ich aber auch nochmal mit rumspielen)
			ffmpeg_command = [
				"ffmpeg", "-f", "concat", "-safe", "0", "-i",
				os.path.join(directory, "filelist.txt"), "-r", str(fps), "-c:v", "libx264", output_file
			]
			subprocess.run(ffmpeg_command, check=True)
			os.remove(os.path.join(directory, "filelist.txt"))

		elif output_format == "zip":
			with zipfile.ZipFile(output_file, 'w') as zipf:
				for file in files:
					zipf.write(os.path.join(directory, file), arcname=file)

		else:
			return ("Invalid output format", False)

		# noch schnell die bearbeiteten Dateien löschen (gegebenenfalls erst später außerhalb der Funktion gewollt/ anzustoßen)
		for file in files:
			os.remove(os.path.join(directory, file))

		return (output_file, True)