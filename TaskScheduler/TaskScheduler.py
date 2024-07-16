from typing import Optional, Tuple
from django.db.models import Max

from .models import RenderTask, Subtask, BlenderDataType, SubtaskStage
from .Enums import TaskStage
from WorkerManager.WorkerManager import WorkerManager
from WorkerManager.models import Worker
from WorkerManager.Enums import WorkerStatus


# Duplicate in WorkerManager/WorkerManager.py
def _int_to_id(value: int, prefix: str) -> str:
    hex_string = format(value, 'x')
    hex_string = hex_string.zfill(16)
    formatted_hex = '_'.join(hex_string[i:i + 4] for i in range(0, len(hex_string), 4))
    return f"{prefix}{formatted_hex}"


class TaskScheduler:
    idCounter: int = 0  # provisional solution


    ### Methods for API
    @staticmethod
    def init_new_task(user) -> Optional[Tuple[str, str]]:  # call before upload to get path to save blend file to
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
            task = RenderTask.create(TaskScheduler.idCounter, taskID, fileServerAddress, fileServerPort, blenderDataType, user)
            TaskScheduler.idCounter += 1

        return None if (task is None) else (task.TaskID, task.get_blender_data_path())

    @staticmethod
    def run_task(task_id: str) -> bool:  # call after upload
        try:
            task = RenderTask.objects.get(TaskID=task_id)
        except:
            print(f"ERROR: Run task was called on unknown task_id: {task_id}")
            return False

        created = task.complete()
        TaskScheduler.distribute_tasks()
        return created

    @staticmethod
    def distribute_tasks():
        print("Called distribute")
        workers = Worker.objects.filter(Status=WorkerStatus.Available)
        if not workers.exists():
            print("No workers available")
            return

        subtasks = []
        resourcesLeft = True
        # First check if there are Subtasks that failed and must be reassigned
        pendingSubtasks = Subtask.objects.filter(Stage=SubtaskStage.Pending)
        if (pendingSubtasks.exists()):
            # TODO: better distribution
            subtasksList = list(pendingSubtasks)
            subtask = Subtask(SubtaskIndex=0, Task=subtasksList[0].Task, Worker=workers[0],
                              StartFrame=subtasksList[0].StartFrame, EndFrame=subtasksList[0].EndFrame,
                              Portion=1)
            subtask.save()
            subtasks.append(subtask)

            resourcesLeft = False

        if (resourcesLeft):
            tasks = RenderTask.objects.filter(Stage=TaskStage.Pending)
            if (tasks.exists()):
                subtask = Subtask(SubtaskIndex=0, Task=tasks[0], Worker=workers[0],
                                  StartFrame=tasks[0].StartFrame, EndFrame=tasks[0].EndFrame,
                                  Portion=1)
                subtask.save()
                subtasks.append(subtask)
                tasks[0].Stage = TaskStage.Distributing
                # task[0].save()

        WorkerManager.distribute_subtasks(subtasks)


    ### Methods for WorkerManager (Callbacks)
    @staticmethod
    def subtask_finished(task: RenderTask):
        if (task.is_finished()):
            task.Stage = TaskStage.Finished
            task.save()
            # TODO: set metadata: e.g. time finished

    @staticmethod
    def subtask_failed(subtask: Subtask):
        pass

