import os
from queue import Queue
from typing import Callable, Optional, List, Tuple

from .RenderTask import RenderTask, BlenderDataType

def _int_to_task_id(value: int) -> str:
    hex_string = format(value, 'x')
    hex_string = hex_string.zfill(16)
    formatted_hex = '_'.join(hex_string[i:i + 4] for i in range(0, len(hex_string), 4))
    return formatted_hex

class TaskScheduler:
    idCounter: int = 0  # provisional solution
    taskQueue: Queue = Queue()
    highPrioTaskQueue: Queue = Queue()
    uploadingTasks: List[str] = []
    runningTasks: List[RenderTask] = []

    @staticmethod
    def init_new_task() -> Optional[Tuple[str, str]]:  # call before upload to get path to save blend file to
        for i in range(10):
            task_id = _int_to_task_id(TaskScheduler.idCounter)  # provisional solution
            TaskScheduler.idCounter += 1

            try:
                task_folder = f"tasks/{task_id}"
                os.makedirs(task_folder, exist_ok=False)
                TaskScheduler.uploadingTasks.append(task_id)
                return (f"{task_folder}/blendfile.blend", task_id)

            except FileExistsError:
                print("ERROR: Tried to create existing folder for new task. Generating new task id")

        return None

    @staticmethod
    def run_task(task_id: str, progress_callback: Callable, finished_callback: Callable) -> bool:  # call after upload
        if (task_id not in TaskScheduler.uploadingTasks):
            print(f"ERROR: Run task was called on unknown task_id: {task_id}")
            return False

        # take from global configuration ? :
        fileServerAddress = "localhost"
        fileServerPort = 8000

        # currently hard coded, more options (zip file) later:
        blenderDataType = BlenderDataType.SingleFile

        task = RenderTask.create(task_id, fileServerAddress, fileServerPort, blenderDataType)

    # in Frontend: finished_callback(render_result_path: str)
