#from __future__ import annotations  # to reference SDNA before declaration in circular references

import io
from enum import Enum
from typing import List, Callable, BinaryIO

from RenderTask import RenderOutputType


class Endianness(Enum):
    LittleEndian = "little"
    BigEndian = "big"

class Scene:
    Name: int
    StartFrame: int
    EndFrame: int
    FrameStep: int
    OutputType: RenderOutputType

    def __init__(self, name: int, startFrame: int, endFrame: int, frameStep: int, OutputType: RenderOutputType):
        self.Name = name
        self.StartFrame = startFrame
        self.EndFrame = endFrame
        self.FrameStep = frameStep
        self.OutputType = OutputType

class Header:
    Identifier: str #Int8[7] as string
    PointerSize: int #Int8 as char
    Endianness: Endianness #Int8 as char
    Version: int #Int8[3] as string

    @classmethod
    def read(cls, bytestream: BinaryIO):
        try:
            identifier = bytestream.read(7).decode("ascii")

            pSizeChar = bytestream.read(1).decode("ascii")
            if (pSizeChar == '_'):
                pointerSize = 4
            elif (pSizeChar == '-'):
                pointerSize = 8
            else:
                raise Exception(f"Invalid pointer size char: {pSizeChar}")

            endianChar = bytestream.read(1).decode("ascii")
            if (endianChar == 'v'):
                endianness = Endianness.LittleEndian
            elif (endianChar == 'V'):
                endianness = Endianness.BigEndian
            else:
                raise Exception(f"Invalid endianness char: {endianChar}")

            version = int(bytestream.read(3).decode("ascii")) #Additional error handling ?? / Version checking ??
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
    SDNAnr: int #Int32
    #nr:     int #Int32
    ContentPos: int

    @classmethod
    def read(cls, bytestream: BinaryIO, pointersize: int, endian: Endianness):
        try:
            code = bytestream.read(4).decode("utf-8")

            length = int.from_bytes(bytestream.read(4), endian.value)
            if (length < 0):
                raise Exception(f"Invalid BHead length: {length}")

            bytestream.seek(pointersize, io.SEEK_CUR) # skip oldPtr

            sdnanr = int.from_bytes(bytestream.read(4), endian.value)

            bytestream.seek(pointersize + 4 + 4, io.SEEK_CUR) # skip nr

            pos = bytestream.tell()
            return cls(code, length, sdnanr, pos)

        except Exception as ex:
            print("An error occurred while reading a BHead from file")
            print(ex)
            return None

    def __init__(self, code: str, length: int, sdnanr: int, contentPos: int):
        self.Code = code
        self.Length = length
        self.SDNAnr = sdnanr
        self.ContentPos = contentPos

class REND:
    StartFrame: int
    EndFrame: int
    SceneName: str

    @classmethod
    def read(cls, bytestream: BinaryIO, length: int, endian: Endianness):
        if (length < 4 + 4 + 2): #startFrame + endFrame + 1 char + \0
            print("REND block to small. Length: " + str(length))
            return None

        try:
            startFrame = int.from_bytes(bytestream.read(4), endian.value)
            endFrame = int.from_bytes(bytestream.read(4), endian.value)
            name = bytestream.read(length - 8).decode("utf-8").rstrip('\0')

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
    FieldType: str
    FieldName: str
    FieldSize: int

    def read_instance(self, bytestream: BinaryIO) -> dict:
        return {"FieldType": self.FieldType,
                "FieldSize": self.FieldSize,
                "Value": bytestream.read(self.FieldSize)}

    @classmethod
    def read(cls, bytestream: BinaryIO, endian: Endianness, sdna, pointersize: int):
        try:
            fieldType = int.from_bytes(bytestream.read(2), endian.value)
            if (fieldType <= sdna.Types.Count):
                print(f"Field type index out of bounds: {fieldType}")
                return None

            fieldName = int.from_bytes(bytestream.read(2), endian.value)
            if (fieldType <= sdna.Types.Count):
                print(f"Field name index out of bounds: {fieldName}")
                return None

            fieldNameStr: str = sdna.Types[fieldName]

            if ("*" in fieldNameStr):
                fieldSize = pointersize
            else:
                fieldSize = sdna.TypeSizes.Array[fieldType]
                if ("[" in fieldNameStr):
                    size = int(fieldNameStr[fieldNameStr.index("[") + 1 : fieldNameStr.index("]") - 1])
                    fieldSize *= size

            return cls(sdna.Types.Array[fieldType], fieldNameStr, fieldSize)

        except Exception as ex:
            print("An error occurred while reading field in structure SDNA from file")
            print(ex)
            return None

    def __init__(self, fieldType: str, fieldName: str, fieldSize: int):
        self.FieldType = fieldType
        self.FieldName = fieldName
        self.FieldSize = fieldSize

class Structure:
    Type: str
    FieldCount: int
    Fields: list[Field]

    def read_instance(self, bytestream: BinaryIO) -> dict:
        struct = {}
        for field in self.Fields:
            struct[field.FieldName] = field.read_instance(bytestream)

        return struct

    @classmethod
    def read(cls, bytestream: BinaryIO, endian: Endianness, sdna, pointersize: int):
        try:
            type = int.from_bytes(bytestream.read(2), endian.value)
            if (type <= sdna.Types.Count):
                print(f"Structure type index out of bounds: {type}")
                return None

            fieldCount = int.from_bytes(bytestream.read(2), endian.value)
            fields = []
            for i in range(fieldCount):
                fields.append(Field.read(bytestream, endian, sdna, pointersize))

            return cls(sdna.Types.Array[type], fieldCount, fields)

        except Exception as ex:
            print("An error occurred while reading structure SDNA from file")
            return None

    def __init__(self, type: str, fieldCount: int, fields: list[Field]):
        self.Type = type
        self.FieldCount = fieldCount
        self.Fields = fields

class SDNAList:
    Identifier: str
    Count: int
    Array: list

    @classmethod
    def read(cls, bytestream: BinaryIO, endian: Endianness, arrayReadFunc: Callable, count: int = -1):
        try:
            identifier = bytestream.read(4).decode("utf-8")
            count = count if count != -1 else int.from_bytes(bytestream.read(4), endian.value)

            array = []
            for i in range(count):
                try:
                    array.append(arrayReadFunc(bytestream, endian))
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


def read_null_terminated_str(bytestream: BinaryIO, *args) -> str:
    bts: bytes = bytes()
    char = bytestream.read(1)
    while char != b'\x00':
        bts += char
        char = bytestream.read(1)

    return bts.decode('utf-8')

def read_ushort(bytestream: BinaryIO, endian: Endianness) -> int:
    return int.from_bytes(bytestream.read(2), endian.value)

class SDNA:
    Identifier: str
    Names: SDNAList
    Types: SDNAList
    TypeSizes: SDNAList
    Structures: SDNAList

    def read_struct(self, bytestream: BinaryIO, sdnaNr: int, endian: Endianness) -> dict:
        return self.Structures.Array[sdnaNr].read_instance(bytestream, endian)

    def read_struct_from_name(self, bytestream: BinaryIO, structName: str, endian: Endianness) -> dict:
        struct = next(filter(lambda x: x.Type == structName, self.Structures.Array), None)
        if struct is None:
            print(f"Failed to find struct {structName}")
            return None

        return struct.read_instance(bytestream, endian)

    def read_struct_from_bhead(self, bytestream: BinaryIO, bhead: BHead, endian: Endianness) -> dict:
        bytestream.seek(bhead.ContentPos)
        return self.read_struct(bytestream, bhead.SDNAnr, endian)
    def __align_to_4__(bytestream: BinaryIO):
        offset = bytestream.tell() % 4
        if offset != 0:
            bytestream.seek(4 - offset, io.SEEK_CUR)

    @classmethod
    def read(cls, bytestream: BinaryIO, endian: Endianness):
        try:
            identifier = bytestream.read(4).decode("utf-8")
            if (identifier != "SDNA"):
                print(f"Invalid SDNA identifier: {identifier}")
                return None

            # Read null terminated string

            names = SDNAList.read(bytestream, endian, read_null_terminated_str)
            if (names is None):
                return None

            SDNA.__align_to_4__(bytestream)
            types = SDNAList.read(bytestream, endian, read_null_terminated_str)
            if (types is None):
                print(f"Can't proceed to SDNAList TypeSizes as SDNAList Types is None")
                return None

            SDNA.__align_to_4__(bytestream)
            typeSizes = SDNAList.read(bytestream, endian, read_ushort, types.Count)
            if (typeSizes is None):
                return None

            SDNA.__align_to_4__(bytestream)
            structures = SDNAList.read(bytestream, endian, Structure.read)
            if (structures is None):
                return None

            return cls(identifier, names, types, typeSizes, structures)

        except Exception as ex:
            print("Error while reading a SDNA from file")
            print(ex)
            return None

    def __init__(self, identifier: str, names: SDNAList, types: SDNAList, typeSizes: SDNAList, structures: SDNAList):
        self.Identifier = identifier
        self.Names = names
        self.Types = types
        self.TypeSizes = typeSizes
        self.Structures = structures


class BlendFile:
    Header: Header
    REND: REND #use until scenes are read properly
    BHeads: List[BHead]
    #Scenes: List[Scene]
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
                        filehandle.seek(bhead.Length, io.SEEK_CUR)

                sceneBHeads = list(filter(lambda bhead: bhead.Code.startswith("SC"), bheads))
                #scenes: list[Scene] = []
                currentScene = None
                for bhead in sceneBHeads:
                    scene = sdna.read_struct_from_bhead(filehandle, bhead, header.Endianness)
                    if (scene is None):
                        print("Failed to read Scene")
                        continue
                    if not ("id" in scene):
                        print("ID attribute missing in Scene")
                        continue

                    id = sdna.read_struct_from_name(io.BytesIO(scene["id"]["Value"]), scene["id"]["FieldType"], header.Endianness)
                    if (id is None):
                        print("Failed to read ID")
                        continue
                    if ("name" not in scene):
                        print("Name attribute missing in ID")
                        continue

                    name = id["name"]["Value"].decode("utf-8").rstrip("\x00")
                    if (name != REND.SceneName):
                        continue

                    if not ("r" in scene):
                        print("RenderData attribute \"r\" missing in Scene")
                        continue

                    renderData = sdna.read_struct_from_name(io.BytesIO(scene["r"]["Value"]), scene["r"]["FieldType"], header.Endianness)
                    # FieldType should be "RenderData"
                    if (renderData is None):
                        print("Failed to read RenderData")
                    if not {"sfra", "efra", "frame_step"}.issubset(renderData.keys()):
                        print("Required frame information in RenderData is missing")
                        continue
                    if ("im_format" not in renderData):
                        print("ImageFormatData attribute \"im_fomrat\" missing in RenderData")
                        continue

                    sfra = int.from_bytes(renderData["sfra"]["Value"], header.Endianness)
                    efra = int.from_bytes(renderData["efra"]["Value"], header.Endianness)
                    frame_step = int.from_bytes(renderData["frame_step"]["Value"], header.Endianness)

                    im_format = sdna.read_struct_from_name(io.BytesIO(renderData["im_format"]["Value"]), renderData["im_format"]["FieldType"], header.Endianness)
                    if (im_format is None):
                        print("Failed to read ImageFormat")
                        continue
                    if ("imtype" not in im_format):
                        print("Required information missing in ImageFormat")
                        continue

                    imtype = int.from_bytes(im_format["imtype"]["Value"], header.Endianness)
                    if not any(element.value == imtype for element in RenderOutputType):
                        print("Unknown output type")
                        continue

                    currentScene = Scene(name, sfra, efra, frame_step, RenderOutputType(im_format))
                    #scenes.append(currentScene)
                if (currentScene is None):
                    print("No scene with the name specified in REND was found")
                    return None

            return cls(header, rend, currentScene, sdna)

        except Exception as ex:
            print(f"An error occured while reading {filepath}")
            print(ex)
            return None
    def __init__(self, header: Header, rend: REND, current_scene: Scene, sdna: SDNA):
        self.Header = header
        self.REND = rend
        #self.Scenes = scenes
        self.CurrentScene = current_scene
        self.SDNA = sdna


a = BlendFile.read("/Users/tobiaskuffert/Projects/1HPI/VS/Backend/Server/tasks/0000_0000_0000_0000/blenderfiles/blenderdata.blend")
#a = BlendFile.read("C:\\Users\\Tobi\\Documents\\1Studium\\VS\\Backend\\Server\\tasks\\0000_0000_0000_0000\\blenderfiles\\blenderdata.blend")