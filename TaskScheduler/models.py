from django.db import models
import os
from .BlendFile import BlendFile
from .Enums import BlenderDataType, RenderOutputType

class RenderTask(models.Model):
    TaskID = models.CharField(max_length=19, unique=True)
    FileServerAddress = models.URLField()
    FileServerPort = (
        models.PositiveIntegerField()
    )  # PositivePositiveIntegerField not possible as range is 0-32k
    dataType = models.CharField(
        max_length=1
    )  # choices=[(member.value, member.name) for member in BlenderDataType])
    outputType = models.CharField(
        max_length=1
    )  # , choices=[(member.value, member.name) for member in RenderOutputType])
    StartFrame = models.PositiveIntegerField()
    EndFrame = models.PositiveIntegerField()
    FrameStep = models.PositiveIntegerField()

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
            return "example.blend"
        else:
            return "blenderdata.zip"

    def to_headers(self):
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
    def create(
        cls,
        taskID: str,
        fileServerAddress: str,
        fileServerPort: int,
        dataType: BlenderDataType,
    ):
        instance = cls(
            TaskID=taskID,
            FileServerAddress=fileServerAddress,
            FileServerPort=fileServerPort,
            dataType=dataType.value,
        )
        blendFile = BlendFile.read(f"{instance.get_folder()}/{instance.get_filename()}")
        # if (blendFile is None):
        #   return None

        instance.outputType = RenderOutputType(
            0
        ).value  # blendFile.CurrentScene.outputType
        instance.StartFrame = 0  # blendFile.CurrentScene.StartFrame
        instance.EndFrame   = 0  # blendFile.CurrentScene.EndFrame
        instance.FrameStep  = 0  # blendFile.CurrentScene.FrameStep

        return instance

    # do not define custom constructor, models.Model's constructor must be called to init valid db object
    # might work somehow, but unclean


# Create your models here.
