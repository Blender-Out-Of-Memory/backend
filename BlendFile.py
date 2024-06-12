import io
from enum import Enum
from typing import List, Callable

class Endianness(Enum):
    LittleEndian = "little"
    BigEndian = "big"

class Scene:
    Name: int
    StartFrame: int
    EndFrame: int

class Header:
    Identifier: str #Int8[7] as string
    PointerSize: int #Int8 as char
    Endianness: Endianness #Int8 as char
    Version: int #Int8[3] as string

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
            print("An error occurred while reading header from file")
            print(ex)
            return None

    def __init__(self, identifier: str, pointerSize: int, endianness: Endianness, version: int):
        self.Identifier = identifier
        self.PointerSize = pointerSize
        self.Endianness = endianness
        self.Version = version


class BHead:
    Code: str
    Length: int #Int32
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
            print("An error occurred while reading a BHead from file")
            print(ex)
            return None

    def __init__(self, code: str, length: int):
        self.Code = code
        self.Length = length

class REND:
    StartFrame: int
    EndFrame: int
    SceneName: str

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
            print("An error occurred while reading REND block from file")
            print(ex)
            return None

    def __init__(self, startFrame: int, endFrame: int, sceneName: str):
        self.StartFrame = startFrame
        self.EndFrame = endFrame
        self.SceneName = sceneName

class Field:
    FieldType: int
    FieldName: str

    @classmethod
    def read(cls, filehandle: io.BufferedIOBase, endian: Endianness):
        try:
            fieldType = int.from_bytes(filehandle.read(2), endian.value)
            fieldName = int.from_bytes(filehandle.read(2), endian.value)
            return cls(fieldType, fieldName)

        except Exception as ex:
            print("An error occurred while reading field in structure SDNA from file")
            print(ex)
            return None

    def __init__(self, fieldType: int, fieldName: str):
        self.FieldType = fieldType
        self.FieldName = fieldName
class Structure:
    Type: int
    FieldCount: int
    Fields: list[Field]

    @classmethod
    def read(cls, filehandle: io.BufferedIOBase, endian: Endianness):
        try:
            type = int.from_bytes(filehandle.read(2), endian.value)
            fieldCount = int.from_bytes(filehandle.read(2), endian.value)
            fields = []
            for i in range(fieldCount):
                fields.append(Field.read(filehandle, endian))

            return cls(type, fieldCount, fields)

        except Exception as ex:
            print("An error occurred while reading structure SDNA from file")
            return None

    def __init__(self, type: int, fieldCount: int, fields: list[Field]):
        self.Type = type
        self.FieldCount = fieldCount
        self.Fields = fields

class SDNAList:
    Identifier: str
    Count: int
    Array: list

    @classmethod
    def read(cls, filehandle: io.BufferedIOBase, endian: Endianness, arrayReadFunc: Callable, count: int = -1):
        try:
            identifier = filehandle.read(4).decode("utf-8")
            count = count if count != -1 else int.from_bytes(filehandle.read(4), endian.value)

            array = []
            for i in range(count):
                try:
                    array.append(arrayReadFunc(filehandle, endian))
                except Exception as ex:
                    pass

            return cls(identifier, count, array)

        except Exception as ex:
            print("An error occurred while reading a SDNAList from file")
            print(ex)

    def __init__(self, identifier: str, count: int, array: list):
        self.Identifier = identifier
        self.Count = count
        self.Array = array


def read_null_terminated_str(filehandle: io.BufferedIOBase, *args) -> str:
    bts: bytes = bytes()
    char = filehandle.read(1)
    while char != b'\x00':
        bts += char
        char = filehandle.read(1)

    return bts.decode('utf-8')

def read_ushort(filehandle: io.BufferedIOBase, endian: Endianness) -> int:
    return int.from_bytes(filehandle.read(2), endian.value)

class SDNA:
    Identifier: str
    Names: SDNAList
    Types: SDNAList
    TypeSizes: SDNAList
    Structures: SDNAList

    def __align_to_4__(filehandle: io.BufferedIOBase):
        offset = filehandle.tell() % 4
        if offset != 0:
            filehandle.seek(4 - offset, io.SEEK_CUR)

    @classmethod
    def read(cls, filehandle: io.BufferedIOBase, endian: Endianness):
        try:
            identifier = filehandle.read(4).decode("utf-8")
            if (identifier != "SDNA"):
                print(f"Invalid SDNA identifier: {identifier}")
                return None

            # Read null terminated string

            names = SDNAList.read(filehandle, endian, read_null_terminated_str)
            if (names is None):
                return None

            SDNA.__align_to_4__(filehandle)
            types = SDNAList.read(filehandle, endian, read_null_terminated_str)
            if (types is None):
                print(f"Can't proceed to SDNAList TypeSizes as SDNAList Types is None")
                return None

            SDNA.__align_to_4__(filehandle)
            typeSizes = SDNAList.read(filehandle, endian, read_ushort, types.Count)
            if (typeSizes is None):
                return None

            SDNA.__align_to_4__(filehandle)
            structures = SDNAList.read(filehandle, endian, Structure.read)
            if (structures is None):
                return None

            return cls(identifier, names, types, typeSizes, structures)

        except Exception as ex:
            print("Error while reading a SDNA from file")
            print(ex)
            return None

    def __init__(self, identifier: str, names: list, types: list, typeSizes: list, structures: list):
        self.Identifier = identifier
        self.Names = names
        self.Types = types
        self.TypeSizes = typeSizes
        self.Structures = structures



class BlendFile:
    Header: Header
    REND: REND #use until scenes are read properly
    BHeads: List[BHead]
    Scenes: List[Scene]
    CurrentScene: Scene
    SDNA: SDNA

    @classmethod
    def read(cls, filepath: str):
        try:
            with open(filepath, "rb") as filehandle:
                header = Header.read(filehandle)
                if (header is None):
                    return None

                bheads = []
                scenePositions = []
                while True:
                    bhead = BHead.read(filehandle, header.PointerSize, header.Endianness)
                    if (bhead is None):
                        return None

                    bheads.append(bhead)
                    if (bhead.Code == "ENDB"):  # substitution for do-while-loop which doesn't exist in python
                        break

                    if (bhead.Code == "REND"):
                        rend = REND.read(filehandle, bhead.Length, header.Endianness)
                        if (rend is None):
                            return None

                    elif (bhead.Code == "DNA1"):
                        sdna = SDNA.read(filehandle, header.Endianness)
                        if (sdna is None):
                            return None

                    else:
                        if (bhead.Code.startswith("SC")):
                            scenePositions.append(filehandle.tell())

                        filehandle.seek(bhead.Length, io.SEEK_CUR)


                scenes = []

                #if (len(scenes) == 0):
                #    return None

                currentScene = None

            return cls(header, rend, scenes, currentScene, sdna)

        except Exception as ex:
            print(f"An error occured while reading {filepath}")
            print(ex)
            return None
    def __init__(self, header: Header, rend: REND, scenes: list[Scene], current_scene: Scene, sdna: SDNA):
        self.Header = header
        self.REND = rend
        self.Scenes = scenes
        self.CurrentScene = current_scene
        self.SDNA = sdna


a = BlendFile.read("C:\\Users\\Tobi\\Documents\\1Studium\\VS\\Backend\\Server\\tasks\\0000_0000_0000_0000\\blenderfiles\\blenderdata.blend")