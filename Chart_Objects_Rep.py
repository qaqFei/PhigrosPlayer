from __future__ import annotations
from dataclasses import dataclass
import typing

from PIL import Image

import Const

@dataclass
class Beat:
    var1:int
    var2:int
    var3:int
    
    @property
    def value(self) -> float:
        return self.var1 + (self.var2 / self.var3)
    
    def __hash__(self) -> int:
        return hash((self.var1,self.var2,self.var3))

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
    floorPosition:float = 0.0
    morebets:bool = False
    clicked:bool = False
    
    def Init(self,bpm:float,events:typing.List[LineEvent]):
        beat_time = 60 / bpm
        for e in events:
            if e.endTime.value < self.startTime.value:
                self.floorPosition += (e.endTime.value - e.startTime.value) * beat_time * e.start
            elif e.startTime.value < self.startTime.value < e.endTime.value:
                self.floorPosition += (self.startTime.value - e.startTime.value) * beat_time * e.start
                break
        self.floorPosition *= Const.REP_CONST.SPEED_UNIT / (675 * 2)

@dataclass
class LineEvent:
    startTime:Beat
    endTime:Beat
    start:float
    end:float
    easingType:typing.Union[int,None]
    
    def Get_Value(self,process:float) -> float:
        return self.start + (self.end - self.start) * process

    def Get_EventProcess(self,beat_time:float) -> float:
        return (beat_time - self.startTime.value) / (self.endTime.value - self.startTime.value)

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
    
    def Get_Notedy(self,bpm:float,now_t:float) -> float:
        dy = 0.0
        beat_time = 60 / bpm
        JudgeLine_SpeedEvents = [e for item in self.eventLayers if item.speedEvents is not None for e in item.speedEvents]
        for SpeedEvent in JudgeLine_SpeedEvents:
            if SpeedEvent.startTime.value < now_t < SpeedEvent.endTime.value:
                dy += (now_t - SpeedEvent.startTime.value) * beat_time * SpeedEvent.start
            elif SpeedEvent.endTime.value <= now_t:
                dy += (SpeedEvent.endTime.value - SpeedEvent.startTime.value) * beat_time * SpeedEvent.start
        return dy * Const.REP_CONST.SPEED_UNIT / (675 * 2)

@dataclass
class Rep_Chart:
    META:MetaData
    BPMList:typing.List[BPMEvent]
    JudgeLineList:typing.List[JudgeLine]
    numOfNotes:int = 0
    
    def Init(self):
        self.numOfNotes = sum([item.numOfNotes for item in self.JudgeLineList])
        
        for JudgeLine in self.JudgeLineList:
            JudgeLine_SpeedEvents = [e for item in JudgeLine.eventLayers if item.speedEvents is not None for e in item.speedEvents]
            for item in JudgeLine.notes:
                item.Init(self.BPMList[0].bpm,JudgeLine_SpeedEvents)
        
        every_note_times = {}
        notes = [item for JudgeLine in self.JudgeLineList for item in JudgeLine.notes]
        for item in notes:
            if item.startTime not in every_note_times:
                every_note_times[item.startTime] = 1
            else:
                every_note_times[item.startTime] += 1
        morebets_beat = [beat for beat in every_note_times.keys() if every_note_times[beat] > 1]
        for item in notes:
            if item.startTime in morebets_beat:
                item.morebets = True

@dataclass
class EventLayer_FrameData:
    speedValue:typing.Union[float,None]
    moveXValue:float
    moveYValue:float
    rotateValue:float
    alphaValue:float

@dataclass
class JudgeLine_FrameData:
    speed:float
    x:float
    y:float
    dy:float
    EventLayer_Data:typing.Union[EventLayer_FrameData,None]
    draw_pos:typing.Union[typing.Tuple[float,float,float,float],None]

@dataclass
class Note_FrameData:
    x:float
    y:float
    rotate:float
    type:int
    positionX:float
    imname:str
    im:typing.Union[Image.Image,None]

@dataclass
class FrameData:
    bpm:float
    beat_time:float
    JudgeLine_Data:typing.List[JudgeLine_FrameData]
    now_t_beat:float
    Note_Data:typing.List[Note_FrameData]
    
del typing,dataclass