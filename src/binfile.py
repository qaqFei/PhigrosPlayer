import struct

class ByteReader:
    def __init__(self, data: bytes, intsize: int, magic: bytes):
        self.data = data
        self.intsize = intsize
        self.position = 0
        
        if self.read(len(magic)) != magic:
            raise ValueError("Invalid magic")
    
    def read(self, length: int) -> bytes:
        result = self.data[self.position:self.position + length]
        self.position += length
        return result

    def read_int(self) -> int:
        return int.from_bytes(self.read(self.intsize), byteorder="little")

    def read_float(self) -> float:
        return struct.unpack("f", self.read(4))[0]
    
    def read_string(self) -> str:
        length = self.read_int()
        return self.read(length).decode("utf-8")

class ByteWriter:
    def __init__(self, intsize: int, magic: bytes):
        self.intsize = intsize
        self.data = bytearray()
        self.write(magic)

    def write(self, data: bytes):
        self.data.extend(data)

    def write_int(self, value: int):
        self.write(value.to_bytes(self.intsize, byteorder="little"))

    def write_float(self, value: float):
        self.write(struct.pack("f", value))

    def write_string(self, value: str):
        self.write_int(len(value))
        self.write(value.encode("utf-8"))

class PlayRecorderBase:
    INTSIZE = 16
    MAGIC = b"PPR_PLAYRECORDER"
    PLAY_CLICKSOUND = 0b00000001
    PC_CLICK        = 0b00000010
    PC_RELEASE      = 0b00000100

class PlayRecorderWriter(PlayRecorderBase):
    def __init__(self):
        self.writer = ByteWriter(self.INTSIZE, self.MAGIC)
    
    def clicksound(self, t: float, nt: int):
        self.writer.write_int(self.PLAY_CLICKSOUND)
        self.writer.write_float(t)
        self.writer.write_int(nt)
    
    def pc_click(self, t: float):
        self.writer.write_int(self.PC_CLICK)
        self.writer.write_float(t)
    
    def pc_release(self, t: float):
        self.writer.write_int(self.PC_RELEASE)
        self.writer.write_float(t)

def readPlayRecorder(data: bytes):
    reader = ByteReader(data, PlayRecorderBase.INTSIZE, PlayRecorderBase.MAGIC)
    while reader.position < len(data):
        event = reader.read_int()
        
        match event:
            case PlayRecorderBase.PLAY_CLICKSOUND:
                t = reader.read_float()
                nt = reader.read_int()
                yield event, t, nt
            
            case PlayRecorderBase.PC_CLICK | PlayRecorderBase.PC_RELEASE:
                t = reader.read_float()
                yield event, t
                