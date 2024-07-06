from __future__ import annotations
from dataclasses import dataclass
import typing

import Const
import Tool_Functions
import rpe_easing

@dataclass
class note:
    type: typing.Literal[1,2,3,4]
    time: int|float
    positionX: int|float
    holdTime: int|float
    speed: int|float
    floorPosition: int|float
    width: int|float
    alpha: int|float
    fake: bool
    VisibleTime: int|float
    effect_random_blocks: tuple[int]
    id: int|None = None
    by_judgeLine_id: int|None = None
    clicked: bool = False
    morebets: bool = False
    master: judgeLine|None = None
    show_effected: bool = False
    show_effected_hold: bool = False
    effect_times: list[tuple[int]] | tuple = ()
    
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
    
    def _init(self,PHIGROS_Y):
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
    startTime: int|float
    endTime: int|float
    value: int|float
    floorPosition: int|float|None = None

@dataclass
class judgeLineMoveEvent:
    startTime: int|float
    endTime: int|float
    start: int|float
    end: int|float
    start2: int|float
    end2: int|float

@dataclass
class judgeLineRotateEvent:
    startTime: int|float
    endTime: int|float
    start: int|float
    end: int|float

@dataclass
class judgeLineDisappearEvent:
    startTime: int|float
    endTime: int|float
    start: int|float
    end: int|float

@dataclass
class TextEvent:
    startTime: int|float
    value: str

@dataclass
class judgeLine:
    id: int
    bpm: int|float
    notesAbove: list[note]
    notesBelow: list[note]
    speedEvents: list[speedEvent]
    judgeLineMoveEvents: list[judgeLineMoveEvent]
    judgeLineRotateEvents: list[judgeLineRotateEvent]
    judgeLineDisappearEvents: list[judgeLineDisappearEvent]
    TextJudgeLine: bool
    TextEvents: list[TextEvent]

    def __post_init__(self):
        self.T = 1.875 / self.bpm
        self.TextEvents.sort(key = lambda x: x.startTime, reverse = True)

    def __eq__(self,oth):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        return f"JudgeLine-{self.id}"
    
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

    def get_datavar_text(self,now_time):
        for e in self.TextEvents: # sort by startTime and reverse
            if e.startTime <= now_time:
                return e.value
        return ""

@dataclass
class Phigros_Chart:
    formatVersion: int
    offset: int|float
    judgeLineList: list[judgeLine]
    Extra_Enable: bool
    Extra: dict
    
    def __post_init__(self):
        self.note_num = 0
        for judgeLine in self.judgeLineList:
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

            #count
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                if not note.fake:
                    self.note_num += 1
    
    def init_holdlength(self,PHIGROS_Y):
        for judgeLine in self.judgeLineList:
            for note in judgeLine.notesAbove:
                note._init(PHIGROS_Y)
            for note in judgeLine.notesBelow:
                note._init(PHIGROS_Y)
    
    def _specification_events(self,event: typing.Union[
        list[judgeLineMoveEvent],
        list[judgeLineDisappearEvent],
        list[judgeLineRotateEvent]
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
        list[judgeLineMoveEvent],
        list[judgeLineDisappearEvent],
        list[judgeLineRotateEvent]
    ]) -> bool:
        for index,e in enumerate(event):
            if index != len(event) - 1:
                if e.endTime != event[index + 1].startTime:
                    return False
        return True
    
    def get_all_note(self) -> list[note]:
       return [j for i in self.judgeLineList for j in i.notesAbove + i.notesBelow]
    
    def get_datavar_extra(self,now_time): # now_time: sec
        target_item = []
        for extra_efct_item in self.Extra["effects"]:
            if extra_efct_item["startTime"] <= now_time <= extra_efct_item["endTime"]:
                values = {k: 0.0 for k in extra_efct_item["vars"].keys()}
                for k, v in extra_efct_item["vars"].items():
                    for e in v:
                        if e["startTime"] <= now_time <= e["endTime"]:
                            values[k] = Tool_Functions.easing_interpolation(now_time, e["startTime"], e["endTime"], e["start"], e["end"], rpe_easing.ease_funcs[e["easingType"]])
                            break
                target_item.append({
                    "shader": extra_efct_item["shader"],
                    "vars": values
                })
        
        # print(target_item)
        
        return target_item

@dataclass
class RenderTask:
    func: typing.Callable
    args: typing.Iterable
    kwargs: typing.Mapping

@dataclass
class FrameRenderTask:
    RenderTasks: list[RenderTask]
    ExTask: list[tuple]
    
    def __call__(
        self,
        func: typing.Callable,
        *args: typing.Iterable,
        **kwargs: typing.Mapping
    ):
        self.RenderTasks.append(RenderTask(func, args, kwargs))
    
    def ExecTask(
        self
    ):
        for t in self.RenderTasks:
            t.func(*t.args, **t.kwargs)
        self.RenderTasks.clear()

@dataclass
class judgeLine_Config_Item:
    line: judgeLine
    rotate: float = 0.0
    disappear: float = 0.0
    pos: tuple[float,float] = (0.0, 0.0)
    time: float = 0.0

@dataclass
class judgeLine_Configs:
    Configs: list[judgeLine_Config_Item]

del typing,dataclass