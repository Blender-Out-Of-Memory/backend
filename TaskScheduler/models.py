from django.db import models
import os
from enum import Enum
from .BlendFile import BlendFile


# TODO (maybe): support decrecated output types for older blender versions
# TODO: which of these formats aren't selectable from render settings / aren't valid output format
class RenderOutputType(Enum):
    TARGA = 0
    IRIS = 1
    # R_HAMX = 2, / *DEPRECATED * /%
    # R_FTYPE = 3, / *DEPRECATED * /
    # R_IMF_IMTYPE_JPEG90 = 4,
    # R_MOVIE = 5, / *DEPRECATED * /
    IRIZ = 7  # ??? invalid
    RAWTGA = 14
    AVIRAW = 15
    AVIJPEG = 16
    PNG = 17
    # R_IMF_IMTYPE_AVICODEC = 18, / *DEPRECATED * /
    # R_IMF_IMTYPE_QUICKTIME = 19, / *DEPRECATED * /
    BMP = 20
    RADHDR = 21
    TIFF = 22
    OPENEXR = 23
    FFMPEG = 24
    # R_IMF_IMTYPE_FRAMESERVER = 25, / *DEPRECATED * /
    CINEON = 26
    DPX = 27
    MULTILAYER = 28  # ??? OPENEXR Multilayer or invalid ??
    DDS = 29  # ??? invalid
    JP2 = 30  # JPEG 2000 or JPEG
    # or invalid ??
    H264 = 31  # ??? codec of ffmpeg
    XVID = 32  # ??? invalid
    THEORA = 33  # ??? codec of ffmpeg
    PSD = 34  # ??? invalid
    WEBP = 35
    AV1 = 36  # ??? invalid

    INVALID = 255  # ??? invalid

    def is_video(self):  # and definitely valid format
        return self in {
            RenderOutputType.AVIRAW,
            RenderOutputType.AVIJPEG,
            RenderOutputType.FFMPEG,
        }


class BlenderDataType(Enum):
    SingleFile = 0
    MultiFile = 1


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
            return "blenderdata.blend"
        else:
            return "blenderdata.zip"

    def to_headers(self):
        return {
            "Task-ID": self.TaskID,
            "File-Server-Address": self.FileServerAddress,
            "File-Server-Port": self.FileServerPort,
            "Blender-Data-Type": self.OutputType.value,
            "Output-Type": self.outputType.value,
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
        instance.StartFrame = 0  #  blendFile.CurrentScene.StartFrame
        instance.EndFrame = 0  # blendFile.CurrentScene.EndFrame
        instance.FrameStep = 0  # blendFile.CurrentScene.FrameStep

        return instance

    # do not define custom constructor, models.Model's constructor must be called to init valid db object
    # might work somehow, but unclean


# Create your models here.
