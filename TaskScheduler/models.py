from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import os
import shutil
from typing import Dict, Tuple, List

# Same Django app
from .BlendFile import BlendFile
from .Enums import BlenderDataType, RenderOutputType, TaskStage

# Different Django app
# from WorkerManager.models import Worker  # must be path from perspective of folder manage.py lies in
# -> different approach: pass class name to foreign key fields

class RenderTask(models.Model):
    TaskID_Int          = models.PositiveSmallIntegerField(primary_key=True)
    TaskID              = models.CharField(max_length=21, unique=True)  # for developement
    FileServerAddress   = models.URLField()
    FileServerPort      = models.PositiveIntegerField()  # PositiveSmallIntegerField not possible as range is 0-32k
    DataType            = models.CharField(max_length=5, choices=BlenderDataType)
    OutputType          = models.CharField(max_length=6, null=True, choices=RenderOutputType)
    StartFrame          = models.PositiveIntegerField(null=True)
    EndFrame            = models.PositiveIntegerField(null=True)
    FrameStep           = models.PositiveIntegerField(null=True)
    Stage               = models.CharField(max_length=5, choices=TaskStage)
    created_by          = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.CASCADE)
    StartedAt           = models.DateTimeField(default=timezone.now)
    FinishedAt          = models.DateTimeField(null=True)

    def get_folder(self) -> str:
        return os.path.abspath(f"tasks/{self.TaskID}/")

    def get_blender_data_path(self) -> str:
        filename = "blenderdata." + ("blend" if (self.DataType == BlenderDataType.SingleFile) else "zip")
        return f"{self.get_folder()}/{filename}"

    def get_result_path(self) -> str:
        return f"{self.get_folder()}/result{self.OutputType.get_extension()}"

    def to_headers(self) -> Dict:
        return {
            "Task-ID": self.TaskID,
            "File-Server-Address": self.FileServerAddress,
            "File-Server-Port": self.FileServerPort,
            "Blender-Data-Type": self.DataType,
            "Output-Type": self.OutputType,
            "Start-Frame": self.StartFrame,
            "End-Frame": self.EndFrame,
            "Frame-Step": self.FrameStep,
        }

    def update_finish(self):
        self.FinishedAt = timezone.now()
        self.save()

    def progres_simple(self) -> Tuple[TaskStage, float, float]:  # (TaskStage, current stage progress, total progress)
        totalProgress = self.Stage.base_progress()

        if (self.Stage.value >= TaskStage.Finished.value):
            currentStageProgress = 1.0
            self.update_finish()

        if (self.Stage == TaskStage.Concatenating):
            currentStageProgress = 0.0  # to be done

        if (self.Stage == TaskStage.Rendering):
            subtasks = self.Subtask_set.all()
            currentStageProgress = 0.0
            for subtask in subtasks:
                currentStageProgress += subtask.progress_weighted()

        if (self.Stage == TaskStage.Distributing):
            currentStageProgress = 0.0  # to be done

        if (self.Stage == TaskStage.Pending):
            currentStageProgress = float("-inf")  # alternatively show progress in pending tasks queue

        if (self.Stage == TaskStage.Uploading):
            currentStageProgress = 0.0  # to be done

        currentStageProgress = max(1.0, currentStageProgress)
        totalProgress += currentStageProgress / 3

        return (self.Stage, currentStageProgress, totalProgress)

    def progress_detailed(self) -> List[Tuple[float, float]]:  # array of (portion, progress)
        report = []
        if (self.Stage == TaskStage.Rendering):
            subtasks = self.Subtask_set.all()
            for subtask in subtasks:
                report.append((subtask.Portion, subtask.progress()))

        return report


    @classmethod
    def create(cls, taskID_int: int, taskID: str, fileServerAddress: str, fileServerPort: int, dataType: BlenderDataType):
        task_folder = f"tasks/{taskID}"

        try:
            if os.path.exists(task_folder):
                shutil.rmtree(task_folder)
        except Exception as ex:
            print("ERROR: Failed to remove task folder (that shouldn't exist btw)")
            print(ex)
            return None

        try:
            os.makedirs(task_folder, exist_ok=False)
        except:
            print("ERROR: Failed to create new folder for new task")
            return None

        instance = cls(TaskID_Int=taskID_int, TaskID=taskID, FileServerAddress=fileServerAddress, FileServerPort=fileServerPort, DataType=dataType, Stage=TaskStage.Uploading)
        instance.save()
        return instance

    def complete(self) -> bool:
        scene = BlendFile.get_current_scene(self.get_blender_data_path())
        if (scene is None):
            return False

        self.StartFrame = scene.StartFrame
        self.EndFrame   = scene.EndFrame
        self.FrameStep  = scene.FrameStep
        self.Stage      = TaskStage.Pending

        self.OutputType = RenderOutputType.from_scene(scene)

        return True

    # do not define custom constructor, models.Model's constructor must be called to init valid db object
    # might work somehow, but unclean


class Subtask(models.Model):
    Task            = models.ForeignKey(RenderTask, on_delete=models.CASCADE, related_name="Subtasks")  # is CASCADE right ??
    Worker          = models.ForeignKey("WorkerManager.Worker", on_delete=models.CASCADE)           # is CASCADE right ??
    StartFrame      = models.PositiveIntegerField()
    EndFrame        = models.PositiveIntegerField()
    LastestFrame    = models.PositiveIntegerField()
    Portion         = models.FloatField()   # Portion of entire Task, relevant for total progres
                                            # Alternatively recalculate it each time in super task

    # Internal values to avoid unnecessary db requests
    frameStep: int = -1

    def progress(self) -> float:
        if (self.frameStep == -1):
            self.frameStep = self.Task.FrameStep

        totalFrames = (self.EndFrame - self.StartFrame) / self.frameStep + 1
        framesDone = (self.LastestFrame - self.StartFrame) / self.frameStep + 1
        return framesDone / totalFrames

    def progress_weighted(self) -> float:
        return self.progress() * self.Portion

