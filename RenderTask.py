import os
from enum import Enum

# TODO (maybe): support decrecated output types for older blender versions
# TODO: which of these formats aren't selectable from render settings / aren't valid output format
class RenderOutputType(Enum):
    TARGA       = 0
    IRIS        = 1
    # R_HAMX = 2, / *DEPRECATED * /%
    # R_FTYPE = 3, / *DEPRECATED * /
    # R_IMF_IMTYPE_JPEG90 = 4,
    # R_MOVIE = 5, / *DEPRECATED * /
    IRIZ        = 7         # ??? invalid
    RAWTGA      = 14
    AVIRAW      = 15
    AVIJPEG     = 16
    PNG         = 17
    # R_IMF_IMTYPE_AVICODEC = 18, / *DEPRECATED * /
    # R_IMF_IMTYPE_QUICKTIME = 19, / *DEPRECATED * /
    BMP         = 20
    RADHDR      = 21
    TIFF        = 22
    OPENEXR     = 23
    FFMPEG      = 24
    # R_IMF_IMTYPE_FRAMESERVER = 25, / *DEPRECATED * /
    CINEON      = 26
    DPX         = 27
    MULTILAYER  = 28        # ??? OPENEXR Multilayer or invalid ??
    DDS         = 29        # ??? invalid
    JP2         = 30        # JPEG 2000 or JPEG
    # or invalid ??
    H264        = 31        # ??? codec of ffmpeg
    XVID        = 32        # ??? invalid
    THEORA      = 33        # ??? codec of ffmpeg
    PSD         = 34        # ??? invalid
    WEBP        = 35
    AV1         = 36        # ??? invalid

    INVALID     = 255       # ??? invalid

    def is_video(self): # and definitely valid format
        return self in {RenderOutputType.AVIRAW, RenderOutputType.AVIJPEG, RenderOutputType.FFMPEG}

class BlenderDataType(Enum):
    SingleFile   = 0
    MultiFile    = 1

class RenderTask:
    TaskID: str
    FileServerAddress: str
    FileServerPort: int
    DataType: BlenderDataType
    OutputType: RenderOutputType
    StartFrame: int
    EndFrame: int
    FrameStep: int

    # TODO: Function for WorkerID -> FrameRange

    def get_folder(self):
        return os.path.abspath(f"tasks/{self.TaskID}")

    def get_filename(self) -> str:
        if self.DataType == BlenderDataType.SingleFile:
            return "blenderdata.blend"
        else:
            return "blenderdata.zip"

    def to_headers(self):
        return {"Task-ID": self.TaskID,
                "File-Server-Address": self.FileServerAddress,
                "File-Server-Port": self.FileServerPort,
                "Blender-Data-Type": self.DataType.value,
                "Output-Type": self.OutputType.value,
                "Start-Frame": self.StartFrame,
                "End-Frame": self.EndFrame,
                "Frame-Step": self.FrameStep}
    def __init__(self, taskID: str, fileServerAddress: str, fileServerPort: int, blenderDataType: BlenderDataType, outputType: RenderOutputType, startFrame: int, endFrame: int, frameStep: int):
        self.TaskID = taskID
        self.FileServerAddress = fileServerAddress
        self.FileServerPort = fileServerPort
        self.DataType = blenderDataType
        self.OutputType = outputType
        self.StartFrame = startFrame
        self.EndFrame = endFrame
        self.FrameStep = frameStep

