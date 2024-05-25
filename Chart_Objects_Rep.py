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
        self.value = self.var1 + (self.var2 / self.var3)
        return self.value

@dataclass
class Note:
    type:int
    startTime:Beat
    endTime:Beat
    positionX:float
    above:int
    isFake:int
    speed:float
    yOffset:float
    visibleTime:float

@dataclass
class LineEvent:
    startTime:Beat
    endTime:Beat
    start:float
    end:float
    easingType:typing.Union[int,None]

@dataclass
class EventLayer:
    speedEvents:typing.Union[typing.List[LineEvent],None]
    moveXEvents:typing.Union[typing.List[LineEvent],None]
    moveYEvents:typing.Union[typing.List[LineEvent],None]
    rotateEvents:typing.Union[typing.List[LineEvent],None]
    alphaEvents:typing.Union[typing.List[LineEvent],None]

@dataclass
class Extended:
    scaleXEvents:typing.Union[typing.List[LineEvent],None]
    scaleYEvents:typing.Union[typing.List[LineEvent],None]
    colorEvents:typing.Union[typing.List[LineEvent],None]

@dataclass
class MetaData:
    RPEVersion:int
    offset:float
    name:str
    id:str
    song:str
    background:str
    composer:str
    charter:str
    level:str

@dataclass
class BPMEvent:
    startTime:Beat
    bpm:float

@dataclass
class JudgeLine:
    numOfNotes:int
    isCover:int
    Texture:str
    eventLayers:typing.List[EventLayer]
    extended:typing.Union[Extended,None]
    notes:typing.List[Note]

@dataclass
class Rep_Chart:
    META:MetaData
    BPMList:typing.List[BPMEvent]
    JudgeLineList:typing.List[JudgeLine]