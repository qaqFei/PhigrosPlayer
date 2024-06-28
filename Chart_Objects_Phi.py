from __future__ import annotations
from dataclasses import dataclass
import typing

import Const
import Tool_Functions

@dataclass
class note:
    type:typing.Literal[1,2,3,4]
    time:typing.Union[int,float]
    positionX:typing.Union[int,float]
    holdTime:typing.Union[int,float]
    speed:typing.Union[int,float]
    floorPosition:typing.Union[int,float]
    effect_random_blocks:typing.Tuple[int]
    id:typing.Union[int,None] = None
    by_judgeLine_id:typing.Union[int,None] = None
    clicked:bool = False
    morebets:bool = False
    master:typing.Union[judgeLine,None] = None
    show_effected:bool = False
    show_effected_hold:bool = False
    effect_times:typing.Union[typing.List[typing.Tuple[int]],typing.Tuple] = ()
    
    def __eq__(self,oth:note):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        note_t = {
            Const.Note.TAP:"t",
            Const.Note.DRAG:"d",
            Const.Note.HOLD:"h",
            Const.Note.FLICK:"f"
        }[self.type]
        return f"{self.master.id}+{self.by_judgeLine_id}{note_t}"
    
    def _cal_holdlength(self,PHIGROS_Y):
        self.hold_length_sec = self.holdTime * self.master.T
        self.hold_length_px = (self.speed * self.hold_length_sec) * PHIGROS_Y
        self.hold_endtime = self.time * self.master.T + self.hold_length_sec
        
        #do other... hehehehe
        self.effect_times = []
        hold_starttime = self.time * self.master.T
        hold_effect_blocktime = (1 / self.master.bpm * 30)
        while True:
            hold_starttime += hold_effect_blocktime
            if hold_starttime >= self.hold_endtime:
                break
            self.effect_times.append((hold_starttime,Tool_Functions.get_effect_random_blocks()))
        
        self.type_string = {
            Const.Note.TAP:"Tap",
            Const.Note.DRAG:"Drag",
            Const.Note.HOLD:"Hold",
            Const.Note.FLICK:"Flick"
        }[self.type]

@dataclass
class speedEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    value:typing.Union[int,float]
    floorPosition:typing.Union[typing.Union[int,float],None] = None

@dataclass
class judgeLineMoveEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]
    start2:typing.Union[int,float]
    end2:typing.Union[int,float]

@dataclass
class judgeLineRotateEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]

@dataclass
class judgeLineDisappearEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]

@dataclass
class judgeLine:
    id:int
    bpm:typing.Union[int,float]
    notesAbove:list[note]
    notesBelow:list[note]
    speedEvents:list[speedEvent]
    judgeLineMoveEvents:list[judgeLineMoveEvent]
    judgeLineRotateEvents:list[judgeLineRotateEvent]
    judgeLineDisappearEvents:list[judgeLineDisappearEvent]

    def __eq__(self,oth):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        return f"JudgeLine-{self.id}"
    
    def _cal_T(self):
        self.T = 1.875 / self.bpm
    
    def set_master_to_notes(self):
        for note in self.notesAbove:
            note.master = self
        for note in self.notesBelow:
            note.master = self
    
    def get_datavar_rotate(self,now_time):
        for rotate_event in self.judgeLineRotateEvents:
            if rotate_event.startTime <= now_time <= rotate_event.endTime:
                return Tool_Functions.interpolation_phi(now_time,rotate_event.startTime,rotate_event.endTime,rotate_event.start,rotate_event.end)
        return 0.0 #never
    
    def get_datavar_disappear(self,now_time):
        for disappear_event in self.judgeLineDisappearEvents:
            if disappear_event.startTime <= now_time <= disappear_event.endTime:
                return Tool_Functions.linear_interpolation(now_time,disappear_event.startTime,disappear_event.endTime,disappear_event.start,disappear_event.end)
        return 0.0 #never
    
    def get_datavar_move(self,now_time,w,h):
        for move_event in self.judgeLineMoveEvents:
            if move_event.startTime <= now_time <= move_event.endTime:
                return (
                    Tool_Functions.interpolation_phi(now_time,move_event.startTime,move_event.endTime,move_event.start,move_event.end) * w,
                    h - Tool_Functions.interpolation_phi(now_time,move_event.startTime,move_event.endTime,move_event.start2,move_event.end2) * h
                )
        return (w * 0.5,h * 0.5) #never

@dataclass
class Phigros_Chart:
    formatVersion:int
    offset:typing.Union[int,float]
    judgeLineList:list[judgeLine]
    
    def init(self):
        for judgeLine in self.judgeLineList:
            #cal T
            judgeLine._cal_T()
            
            #set_master_to_notes
            judgeLine.set_master_to_notes()
            
            #specification_events
            self._specification_events(judgeLine.judgeLineMoveEvents)
            self._specification_events(judgeLine.judgeLineDisappearEvents)
            self._specification_events(judgeLine.judgeLineRotateEvents)
            
            #init_speed_floorposition
            last_speedEvent_floorPosition = 0.0
            for speedEvent in judgeLine.speedEvents:
                speedEvent.floorPosition = last_speedEvent_floorPosition
                last_speedEvent_floorPosition += (speedEvent.endTime - speedEvent.startTime) * speedEvent.value * judgeLine.T
        
        #cal_note_num
        self.note_num = sum([len(judgeLine.notesAbove) + len(judgeLine.notesBelow) for judgeLine in self.judgeLineList])
    
    def init_holdlength(self,PHIGROS_Y):
        for judgeLine in self.judgeLineList:
            for note in judgeLine.notesAbove:
                note._cal_holdlength(PHIGROS_Y)
            for note in judgeLine.notesBelow:
                note._cal_holdlength(PHIGROS_Y)
    
    def _specification_events(self,event:typing.Union[
        typing.List[judgeLineMoveEvent],
        typing.List[judgeLineDisappearEvent],
        typing.List[judgeLineRotateEvent]
    ]):
        if not event: #empty
            return
        
        event.sort(key=lambda x:x.startTime)
        
        for e in event:
            if e.startTime > e.endTime:
                e.endTime = e.startTime
                e.start = e.end
                if hasattr(e,"start2"):
                    e.start2 = e.end2

        while True:
            for index,e in enumerate(event):
                start = e.startTime
                if index != len(event) - 1:
                    end = event[index + 1].startTime
                else:
                    end = 9999999.0
                e.startTime,e.endTime = start,end
            if self._is_specification_events(event):
                break
        
        event[0].startTime = -9999999.0
        event[-1].endTime = 9999999.0
    
    def _is_specification_events(self,event:typing.Union[
        typing.List[judgeLineMoveEvent],
        typing.List[judgeLineDisappearEvent],
        typing.List[judgeLineRotateEvent]
    ]) -> bool:
        for index,e in enumerate(event):
            if index != len(event) - 1:
                if e.endTime != event[index + 1].startTime:
                    return False
        return True
    
    def get_all_note(self) -> list[note]:
       return [j for i in self.judgeLineList for j in i.notesAbove + i.notesBelow]

@dataclass
class RenderTask:
    func:typing.Callable
    args:typing.Iterable
    kwargs:typing.Mapping

@dataclass
class FrameRenderTask:
    RenderTasks:list[RenderTask]
    ExTask:typing.List[tuple]
    
    def __call__(
        self,
        func:typing.Callable,
        *args:typing.Iterable,
        **kwargs:typing.Mapping
    ):
        self.RenderTasks.append(RenderTask(func,args,kwargs))
    
    def ExecTask(
        self
    ):
        for t in self.RenderTasks:
            t.func(*t.args,**t.kwargs)
        self.RenderTasks.clear()

@dataclass
class judgeLine_Config_Item:
    line:judgeLine
    rotate:float
    disappear:float
    pos:typing.Tuple[float,float]
    time:float

@dataclass
class judgeLine_Configs:
    Configs:typing.List[judgeLine_Config_Item]

del typing,dataclass