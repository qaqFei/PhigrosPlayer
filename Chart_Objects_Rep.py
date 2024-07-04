from __future__ import annotations
from dataclasses import dataclass
import typing

@dataclass
class Beat:
    var1:int
    var2:int
    var3:int
    
    @property
    def value(self) -> float:
        return self.var1 + (self.var2 / self.var3)
    
    def __hash__(self) -> int:
        return hash((self.var1, self.var2, self.var3))
    
@dataclass
class Note:
    type: int
    startTime: Beat
    endTime: Beat
    positionX: float
    above: int
    isFake: int
    speed: float
    yOffset: float
    visibleTime: float
    width: float
    alpha: int

@dataclass
class LineEvent:
    startTime: Beat
    endTime: Beat
    start: float|str
    end: float|str
    easingType: typing.Union[int,None]

@dataclass
class EventLayer:
    speedEvents: list[LineEvent]|None
    moveXEvents: list[LineEvent]|None
    moveYEvents: list[LineEvent]|None
    rotateEvents: list[LineEvent]|None
    alphaEvents: list[LineEvent]|None

@dataclass
class Extended:
    scaleXEvents: list[LineEvent]|None
    scaleYEvents: list[LineEvent]|None
    colorEvents: list[LineEvent]|None
    textEvents: list[LineEvent]|None

@dataclass
class MetaData:
    RPEVersion: int
    offset: float
    name: str
    id: str
    song: str
    background: str
    composer: str
    charter: str
    level: str

@dataclass
class BPMEvent:
    startTime: Beat
    bpm: float

@dataclass
class JudgeLine:
    numOfNotes: int
    isCover: int
    Texture: str
    eventLayers: list[EventLayer]
    extended: Extended|None
    notes: list[Note]

@dataclass
class Rep_Chart:
    META: MetaData
    BPMList: list[BPMEvent]
    JudgeLineList: list[JudgeLine]
    
del typing,dataclass