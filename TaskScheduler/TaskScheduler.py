from typing import Optional, Tuple
from django.db.models import Max

from .models import RenderTask, BlenderDataType
# from WorkerManager.WorkerManager import WorkerManager


def _int_to_id(value: int, prefix: str) -> str:
    hex_string = format(value, 'x')
    hex_string = hex_string.zfill(16)
    formatted_hex = '_'.join(hex_string[i:i + 4] for i in range(0, len(hex_string), 4))
    return f"{prefix}{formatted_hex}"


class TaskScheduler:
    idCounter: int = 0  # provisional solution

    @staticmethod
    def init_new_task() -> Optional[Tuple[str, str]]:  # call before upload to get path to save blend file to
        if (RenderTask.objects.filter(TaskID_Int=TaskScheduler.idCounter).exists()):
            TaskScheduler.idCounter = RenderTask.objects.aggregate(Max('TaskID_Int'))['TaskID_Int__max'] + 1

        # take from global configuration ? :
        fileServerAddress = "localhost"
        fileServerPort = 8000

        # currently hard coded, more options (zip file) later:
        blenderDataType = BlenderDataType.SingleFile

        MAX_TRIES = 10
        tries = 0
        task = None
        while (tries < MAX_TRIES and task is None):
            taskID = _int_to_id(TaskScheduler.idCounter, "T-")  # provisional solution
            task = RenderTask.create(TaskScheduler.idCounter, taskID, fileServerAddress, fileServerPort, blenderDataType)
            TaskScheduler.idCounter += 1

        return None if (task is None) else (task.TaskID, task.get_blender_data_path())

    @staticmethod
    def run_task(task_id: str) -> bool:  # call after upload
        try:
            task = RenderTask.objects.get(TaskID=task_id)
        except:
            print(f"ERROR: Run task was called on unknown task_id: {task_id}")
            return False

        return task.complete()