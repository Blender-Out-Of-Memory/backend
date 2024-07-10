from enum import Enum

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

class TaskStage(Enum):
    Uploading       = 0
    Pending         = 1  # waiting for Worker to be assigned to
    Distributing    = 2
    Rendering       = 3
    Concatenating   = 4
    Finished        = 5
    Expired         = 6  # task result deleted from Server

    def base_progress(self):
        return max(self.value / 5, 1.0)
