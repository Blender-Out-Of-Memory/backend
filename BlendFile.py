import io
from enum import Enum
from typing import List

class Endianness(Enum):
    LittleEndian = "little"
    BigEndian = "big"

class Scene:
    name: int
    start_frame: int
    end_frame: int

class Header:
    identifier: str #Int8[7] as string
    pointerSize: int #Int8 as char
    endianness: Endianness #Int8 as char
    version: int #Int8[3] as string

    @classmethod
    def read(cls, filehandle: io.BufferedIOBase):
        try:
            identifier = filehandle.read(7).decode("ascii")

            pSizeChar = filehandle.read(1).decode("ascii")
            if (pSizeChar == '_'):
                pointerSize = 4
            elif (pSizeChar == '-'):
                pointerSize = 8
            else:
                raise Exception(f"Invalid pointer size char: {pSizeChar}")

            endianChar = filehandle.read(1).decode("ascii")
            if (endianChar == 'v'):
                endianness = Endianness.LittleEndian
            elif (endianChar == 'V'):
                endianness = Endianness.BigEndian
            else:
                raise Exception(f"Invalid endianness char: {endianChar}")

            version = int(filehandle.read(3).decode("ascii")) #Additional error handling ?? / Version checking ??
            return cls(identifier, pointerSize, endianness, version)

        except Exception as ex:
            print("An error occured while reading header from file")
            print(ex)
            return None

    def __init__(self, identifier: str, pointerSize: int, endianness: Endianness, version: int):
        self.identifier = identifier
        self.pointerSize = pointerSize
        self.endianness = endianness
        self.version = version


class BHead:
    code: str
    length: int #Int32
    #oldPtr: int #UInt32 or UInt64
    #SDNAnr: int #Int32
    #nr:     int #Int32

    @classmethod
    def read(cls, filehandle: io.BufferedIOBase, pointersize: int, endian: Endianness):
        try:
            code = filehandle.read(4).decode("utf-8")

            length = int.from_bytes(filehandle.read(4), endian.value)
            if (length < 0):
                raise Exception(f"Invalid BHead length: {length}")

            #oldPtr, SDNAnr, nr
            filehandle.seek(pointersize + 4 + 4, io.SEEK_CUR) # skip [pointersize] bytes

            return cls(code, length)

        except Exception as ex:
            print("An error occured while reading a BHead from file")
            print(ex)
            return None

    def __init__(self, code: str, length: int):
        self.code = code
        self.length = length

class REND:
    startFrame: int
    endFrame: int
    sceneName: str

    @classmethod
    def read(cls, filehandle: io.BufferedIOBase, length: int, endian: Endianness):
        if (length < 4 + 4 + 2): #startFrame + endFrame + 1 char + \0
            print("REND block to small. Length: " + str(length))
            return None

        try:
            startFrame = int.from_bytes(filehandle.read(4), endian.value)
            endFrame = int.from_bytes(filehandle.read(4), endian.value)
            name = filehandle.read(length - 8).decode("utf-8").rstrip('\0')

            return cls(startFrame, endFrame, name)

        except Exception as ex:
            print("An error occured while reading REND block from file")
            print(ex)
            return None

    def __init__(self, startFrame: int, endFrame: int, sceneName: str):
        self.startFrame = startFrame
        self.endFrame = endFrame
        self.sceneName = sceneName

class BlendFile:
    header: Header
    rend: REND #use until scenes are read properly
    bheads: List[BHead]
    scenes: List[Scene]
    current_scene: Scene

    @classmethod
    def read(cls, filepath: str):
        try:
            with open(filepath, "rb") as filehandle:
                header = Header.read(filehandle)
                if (header is None):
                    return None

                bheads = []
                while True:
                    bhead = BHead.read(filehandle, header.pointerSize, header.endianness)
                    if (bhead is None):
                        return None
                    bheads.append(bhead)
                    if (bhead.code == "ENDB"): #substituion for do-while-loop which doesn't exist in python
                        break

                    if (bhead.code == "REND"):
                        rend = REND.read(filehandle, bhead.length, header.endianness)
                        if (rend is None):
                            return None
                    else:
                        filehandle.seek(bhead.length, io.SEEK_CUR)


                scenes = []
                #if (len(scenes) == 0):
                #    return None

                currentScene = None

            return cls(header, rend, scenes, currentScene)

        except Exception as ex:
            print(f"An error occured while reading {filepath}")
            print(ex)
            return None
    def __init__(self, header: Header, rend: REND, scenes: list[Scene], current_scene: Scene):
        self.header = header
        self.rend = rend
        self.scenes = scenes
        self.current_scene = current_scene