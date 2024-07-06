from __future__ import annotations
from dataclasses import dataclass, fields
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

@dataclass
class _ExtraVarBase:
    master_start: Beat
    master_end: Beat
    
    def __post_init__(self):
        for field in fields(self):
            if isinstance(getattr(self, field.name), list):
                setattr(self, field.name, [
                    ExtraVarEvent(
                        startTime = Beat(*item["startTime"]),
                        endTime = Beat(*item["endTime"]),
                        easingType = item["easingType"],
                        start = item["start"],
                        end = item["end"]
                    )
                    for item in getattr(self, field.name)
                ])
            elif isinstance(getattr(self, field.name), int|float):
                item = getattr(self, field.name)
                setattr(self, field.name, [ExtraVarEvent(
                    startTime = self.master_start,
                    endTime = self.master_end,
                    easingType = 1,
                    start = item,
                    end = item
                )])
    
@dataclass
class ExtraVar_Chromatic(_ExtraVarBase):
    sampleCount: int|list[ExtraVarEvent] = 3
    power: float|list[ExtraVarEvent] = 0.01

@dataclass
class ExtraVar_CircleBlur(_ExtraVarBase):
    size: float|list[ExtraVarEvent] = 10.0

@dataclass
class ExtraVar_Fisheye(_ExtraVarBase):
    power: float|list[ExtraVarEvent] = -0.1

@dataclass
class ExtraVar_Glitch(_ExtraVarBase):
    power: float|list[ExtraVarEvent] = 0.3
    rate: float|list[ExtraVarEvent] = 0.6
    speed: float|list[ExtraVarEvent] = 5.0
    blockCount: float|list[ExtraVarEvent] = 30.5
    colorRate: float|list[ExtraVarEvent] = 0.01

@dataclass
class ExtraVar_Grayscale(_ExtraVarBase):
    factor: float|list[ExtraVarEvent] = 1.0
    
@dataclass
class ExtraVar_Noise(_ExtraVarBase):
    seed: float|list[ExtraVarEvent] = 81.0
    power: float|list[ExtraVarEvent] = 0.03

@dataclass
class ExtraVar_Pixel(_ExtraVarBase):
    size: float = 10.0

@dataclass
class ExtraVar_RadialBlur(_ExtraVarBase):
    centerX: float|list[ExtraVarEvent] = 0.5
    centerY: float|list[ExtraVarEvent] = 0.5
    power: float|list[ExtraVarEvent] = 0.01
    sampleCount: int|list[ExtraVarEvent] = 3

@dataclass
class ExtraVar_Shockwave(_ExtraVarBase):
    progress: float|list[ExtraVarEvent] = 0.2
    centerX: float|list[ExtraVarEvent] = 0.5
    centerY: float|list[ExtraVarEvent] = 0.5
    width: float|list[ExtraVarEvent] = 0.1
    distortion: float|list[ExtraVarEvent] = 0.8
    expand: float|list[ExtraVarEvent] = 10.0

@dataclass
class ExtraVar_Vignette(_ExtraVarBase):
    color: tuple[int] = (0, 0, 0)
    extend: float|list[ExtraVarEvent] = 0.25
    radius: float|list[ExtraVarEvent] = 15.0
    
    def __post_init__(self):
        _ExtraVarBase.__post_init__(self)
        if isinstance(self.color, list):
            self.color = tuple(self.color)

@dataclass
class ExtraVarEvent:
    startTime: Beat
    endTime: Beat
    easingType: int
    start: float
    end: float

@dataclass
class ExtraEffect:
    start: Beat
    end: Beat
    shader: str
    global_: bool
    vars: (
        ExtraVar_Chromatic|
        ExtraVar_CircleBlur|
        ExtraVar_Fisheye|
        ExtraVar_Glitch|
        ExtraVar_Grayscale|
        ExtraVar_Noise|
        ExtraVar_Pixel|
        ExtraVar_RadialBlur|
        ExtraVar_Shockwave|
        ExtraVar_Vignette|
        None
    )
    
@dataclass
class Extra:
    bpm: list[BPMEvent]
    effects: list[ExtraEffect]
    
    def __post_init__(self):
        for index,bpm in enumerate(self.bpm):
            if index != len(self.bpm) - 1:
                next_bpm = self.bpm[index + 1]
                bpm.dur = next_bpm.startTime.value - bpm.startTime.value
            else:
                bpm.dur = float("inf")
    
    def getReal(self, b:Beat):
        realtime = 0.0
        for bpm in self.bpm:
            if bpm.startTime.value < b.value:
                if bpm.startTime.value + bpm.dur > b.value:
                    realtime += 60 / bpm.bpm * (b.value - bpm.startTime.value)
                else:
                    realtime += 60 / bpm.bpm * bpm.dur
        return realtime
    
del typing,dataclass