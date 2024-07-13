from __future__ import annotations

from django.db import models

from .BlendFile import ImageType as BlendFileImageType
from .BlendFile import Scene as BlendFileScene

class RenderOutputType(models.TextChoices):
    RGB = (".rgb", "Iris")
    JPG = (".jpg", "JPEG")
    JP2 = (".jp2", "JPEG 200 J2")
    J2C = (".j2c", "JPEG 200 J2K")
    PNG = (".png", "PNG")
    BMP = (".bmp", "BMP")
    TGA = (".tga", "TARGA")
    TGR = (".tga.r", "TARGA Raw")
    CIN = (".cin", "Cineon")
    DPX = (".dpx", "DPX")
    EXR = (".exr", "OpenEXR")
    MXR = (".exr.m", "OpenEXR Multilayer")
    HDR = (".hdr", "Radiance HDR")
    TIF = (".tif", "TIFF")
    WBP = (".webp", "WebP")
    AVJ = (".avi.j", "AVI JPEG")
    AVR = (".avi.r", "AVI RAW")

    # FFmpeg                     # Container (field 'type')
    MPG = (".mpg", "MPEG-1")     # 0
    DVD = (".dvd", "MPEG-2")     # 1
    MP4 = (".mp4", "MPEG-4")     # 2
    AVI = (".avi", "AVI")        # 3
    QKT = (".mov", "QuickTime")  # 4
    DV  = (".dv" , "DV")         # 5
    FLV = (".flv", "Flash")      # 8
    MKV = (".mkv", "Matroska")   # 9
    OGG = (".ogv", "OGG")        # 10
    WBM = (".webm", "WebM")      # 12

    def get_extension(self):
        # get index of second dot if exists
        additionalIndex = self.value[0].find(".", 1)
        end = additionalIndex if (additionalIndex != -1) else len(self.value[0])
        # chars after additionalIndex don't belong to extension
        return self.value[0][0:end]

    @staticmethod
    def from_scene(scene: BlendFileScene) -> RenderOutputType:
        if (scene.OutputType == BlendFileImageType.JP2):
            return RenderOutputType.JP2 if (scene.JP2Codec == 0) else RenderOutputType.J2C

        if (scene.OutputType == BlendFileImageType.FFMPEG):
            return {
                 0: RenderOutputType.MPG,
                 1: RenderOutputType.DVD,
                 2: RenderOutputType.MP4,
                 3: RenderOutputType.AVI,
                 4: RenderOutputType.QKT,
                 5: RenderOutputType.DV,
                 8: RenderOutputType.FLV,
                 9: RenderOutputType.MKV,
                10: RenderOutputType.OGG,
                12: RenderOutputType.WBM
            }[scene.FFmpegContainer]

        return {
            BlendFileImageType.IRIS:                RenderOutputType.RGB,
            BlendFileImageType.R_IMF_IMTYPE_JPEG90: RenderOutputType.JPG,
            BlendFileImageType.PNG:                 RenderOutputType.PNG,
            BlendFileImageType.BMP:                 RenderOutputType.BMP,
            BlendFileImageType.TARGA:               RenderOutputType.TGA,
            BlendFileImageType.RAWTGA:              RenderOutputType.TGR,
            BlendFileImageType.CINEON:              RenderOutputType.CIN,
            BlendFileImageType.DPX:                 RenderOutputType.DPX,
            BlendFileImageType.OPENEXR:             RenderOutputType.EXR,
            BlendFileImageType.MULTILAYER:          RenderOutputType.MXR,
            BlendFileImageType.RADHDR:              RenderOutputType.HDR,
            BlendFileImageType.TIFF:                RenderOutputType.TIF,
            BlendFileImageType.WEBP:                RenderOutputType.WBP,
            BlendFileImageType.AVIJPEG:             RenderOutputType.AVJ,
            BlendFileImageType.AVIRAW:              RenderOutputType.AVR,
        }[scene.OutputType]


class BlenderDataType(models.TextChoices):
    SingleFile = ("SINGL", "SingleFile")
    MultiFile = ("MULTI", "MultiFile")


class TaskStage(models.TextChoices):
    Uploading       = ("1-UPL", "Uploading")
    Pending         = ("2-PEN", "Pending")  # waiting for Worker to be assigned to
    Distributing    = ("3-DIS", "Distributing")
    Rendering       = ("4-REN", "Rendering")
    Concatenating   = ("5-CON", "Concatenating")
    Finished        = ("6-FIN", "Finished")
    Expired         = ("7-EXP", "Expired")  # task result deleted from Server

    def base_progress(self):
        return max(int(self.value[0][0]) / 5, 1.0)
