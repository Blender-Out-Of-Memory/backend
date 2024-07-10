from django.db import models

import os
from typing import Dict

# Same Django app
from .BlendFile import BlendFile
from .Enums import BlenderDataType, RenderOutputType

# Different Django app
# from WorkerManager.models import Worker  # must be path from perspective of folder manage.py lies in
# -> different approach: pass class name to foreign key fields

class RenderTask(models.Model):
    TaskID              = models.CharField(max_length=20, unique=True)
    FileServerAddress   = models.URLField()
    FileServerPort      = models.PositiveIntegerField()# PositiveSmallIntegerField not possible as range is 0-32k
    dataType            = models.CharField(max_length=1)  # choices=[(member.value, member.name) for member in BlenderDataType])
    outputType          = models.CharField(max_length=1)  # , choices=[(member.value, member.name) for member in RenderOutputType])
    StartFrame          = models.PositiveIntegerField()
    EndFrame            = models.PositiveIntegerField()
    FrameStep           = models.PositiveIntegerField()

    @property
    def DataType(self):
        return BlenderDataType(self.dataType)

    @property
    def OutputType(self):
        return RenderOutputType(self.outputType)

    def get_folder(self):
        return os.path.abspath(f"tasks/{self.TaskID}")

    def get_filename(self) -> str:
        if self.DataType == BlenderDataType.SingleFile:
            return "blenderdata.blend"
        else:
            return "blenderdata.zip"

    def to_headers(self) -> Dict:
        return {
            "Task-ID": self.TaskID,
            "File-Server-Address": self.FileServerAddress,
            "File-Server-Port": self.FileServerPort,
            "Blender-Data-Type": self.DataType.value,
            "Output-Type": self.OutputType.value,
            "Start-Frame": self.StartFrame,
            "End-Frame": self.EndFrame,
            "Frame-Step": self.FrameStep,
        }

    @classmethod
    def create(cls, taskID: str, fileServerAddress: str, fileServerPort: int, dataType: BlenderDataType):
        instance = cls(TaskID=taskID, FileServerAddress=fileServerAddress, FileServerPort=fileServerPort, dataType=dataType.value)
        scene = BlendFile.get_current_scene(f"{instance.get_folder()}/{instance.get_filename()}")
        if (scene is None):
            return None

        instance.outputType = RenderOutputType(
            0
        ).value  # blendFile.CurrentScene.outputType
        instance.StartFrame = 0  # blendFile.CurrentScene.StartFrame
        instance.EndFrame   = 0  # blendFile.CurrentScene.EndFrame
        instance.FrameStep  = 0  # blendFile.CurrentScene.FrameStep

        return instance

    # do not define custom constructor, models.Model's constructor must be called to init valid db object
    # might work somehow, but unclean


class Subtask(models.Model):
    Task            = models.ForeignKey(RenderTask, on_delete=models.CASCADE, related_name="Subtasks")  # is CASCADE right ??
    Worker          = models.ForeignKey("WorkerManager.Worker", on_delete=models.CASCADE)           # is CASCADE right ??
    StartFrame      = models.PositiveIntegerField()
    EndFrame        = models.PositiveIntegerField()
    FramesFinished  = models.PositiveIntegerField()
    Portion         = models.FloatField()   # Portion of entire Task, relevant for total progres
                                            # Alternatively recalculate it each time in super task

    # Internal values to avoid unnecessary db requests
    frameStep: int = -1

    def progress(self) -> float:
        if (self.frameStep == -1):
            self.frameStep = self.Task.FrameStep

        frameCount = (self.EndFrame - self.StartFrame) / self.frameStep + 1
        return self.FramesFinished / frameCount

    def progressWeighted(self) -> float:
        return self.progress() * self.Portion

