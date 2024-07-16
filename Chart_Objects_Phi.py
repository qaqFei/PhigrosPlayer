from __future__ import annotations
from base64 import b64decode
from dataclasses import dataclass
import io
import typing

from PIL import Image

import Const
import Tool_Functions
import rpe_easing

def getFloorPosition(line:judgeLine, t:float) -> float:
    if not line.speedEvents: return 0.0
    for speed_event in line.speedEvents:
        if speed_event.startTime <= t <= speed_event.endTime:
            return speed_event.floorPosition + (
                t - speed_event.startTime
            ) * line.T * speed_event.value
    last_speed_event = line.speedEvents[-1]
    return last_speed_event.floorPosition + (t - last_speed_event.endTime) * line.T * last_speed_event.value

@dataclass
class note:
    type: typing.Literal[1,2,3,4]
    time: float
    positionX: float
    holdTime: float
    speed: float
    floorPosition: float
    width: float
    alpha: float
    fake: bool
    VisibleTime: float
    effect_random_blocks: tuple[int]
    above: bool
    id: int|None = None
    by_judgeLine_id: int|None = None
    clicked: bool = False
    morebets: bool = False
    master: judgeLine|None = None
    show_effected: bool = False
    show_effected_hold: bool = False
    effect_times: list[tuple[int]] | tuple = ()
    state: int = Const.NOTE_STATE.MISS
    player_clicked: bool = False
    player_click_offset: float = 0.0
    player_click_sound_played: bool = False
    player_will_click: bool = False
    player_missed: bool = False
    
    def __eq__(self, oth:object):
        if not isinstance(oth, note):
            return NotImplemented
        return self.id == oth.id

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
    
    def _init(self, PHIGROS_Y):
        self.hold_length_sec = self.holdTime * self.master.T
        self.hold_length_px = (self.speed * self.hold_length_sec) * PHIGROS_Y
        self.hold_endtime = self.time * self.master.T + self.hold_length_sec
        
        self.effect_times = []
        hold_starttime = self.time * self.master.T
        hold_effect_blocktime = (1 / self.master.bpm * 30)
        while True:
            hold_starttime += hold_effect_blocktime
            if hold_starttime >= self.hold_endtime:
                break
            self.effect_times.append((hold_starttime, Tool_Functions.get_effect_random_blocks()))
        
        self.type_string = {
            Const.Note.TAP:"Tap",
            Const.Note.DRAG:"Drag",
            Const.Note.HOLD:"Hold",
            Const.Note.FLICK:"Flick"
        }[self.type]
        
        self.floorPosition = getFloorPosition(self.master, self.time)

@dataclass
class speedEvent:
    startTime: float
    endTime: float
    value: float
    floorPosition: float|None = None

@dataclass
class judgeLineMoveEvent:
    startTime: float
    endTime: float
    start: float
    end: float
    start2: float
    end2: float

@dataclass
class judgeLineRotateEvent:
    startTime: float
    endTime: float
    start: float
    end: float

@dataclass
class judgeLineDisappearEvent:
    startTime: float
    endTime: float
    start: float
    end: float

@dataclass
class TextEvent:
    startTime: float
    value: str

@dataclass
class ScaleEvent:
    startTime: float
    endTime: float
    start: float
    end: float
    easingType: int
    easingFunc: typing.Callable|None = None
    
    def __post_init__(self):
        self.easingFunc = rpe_easing.ease_funcs[self.easingType - 1]

@dataclass
class ColorEvent:
    startTime: float
    value: list[int]

@dataclass
class judgeLine:
    id: int
    bpm: float
    notesAbove: list[note]
    notesBelow: list[note]
    speedEvents: list[speedEvent]
    judgeLineMoveEvents: list[judgeLineMoveEvent]
    judgeLineRotateEvents: list[judgeLineRotateEvent]
    judgeLineDisappearEvents: list[judgeLineDisappearEvent]
    TextJudgeLine: bool
    TextEvents: list[TextEvent]
    EnableTexture: bool
    Texture: str|None
    ScaleXEvents: list[ScaleEvent]
    ScaleYEvents: list[ScaleEvent]
    ColorEvents: list[ColorEvent]

    def __post_init__(self):
        self.T = 1.875 / self.bpm
        if self.EnableTexture:
            try:
                self.TexturePillowObject = Image.open(io.BytesIO(bytes(b64decode(self.Texture))))
            except Exception:
                self.EnableTexture = False
        
        spes = []
        self.speedEvents.sort(key = lambda x: x.startTime)
        for i, e in enumerate(self.speedEvents):
            if i != len(self.speedEvents) - 1:
                ne = self.speedEvents[i + 1]
                if ne.startTime != e.endTime:
                    if ne.startTime < e.endTime:
                        ne.startTime = e.endTime
                        ne.floorPosition = None
                    elif ne.startTime > e.endTime:
                        spes.append(speedEvent(e.endTime, ne.startTime, e.value, None))
        self.speedEvents += spes
        
        self.speedEvents.sort(key = lambda x: x.startTime) # it cannot sort, if sort it -> cal floorPosition will be error. (i donot know why...)
        self.judgeLineMoveEvents.sort(key = lambda x: x.startTime)
        self.judgeLineRotateEvents.sort(key = lambda x: x.startTime)
        self.judgeLineDisappearEvents.sort(key = lambda x: x.startTime)
        self.TextEvents.sort(key = lambda x: x.startTime, reverse = True)
        self.ScaleXEvents.sort(key = lambda x: x.startTime)
        self.ScaleYEvents.sort(key = lambda x: x.startTime)
        self.ColorEvents.sort(key = lambda x: x.startTime, reverse = True)

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
        for e in self.judgeLineRotateEvents:
            if e.startTime <= now_time <= e.endTime:
                return Tool_Functions.interpolation_phi(
                    now_time,
                    e.startTime,
                    e.endTime,
                    e.start,
                    e.end
                )
        return 0.0 #never
    
    def get_datavar_disappear(self,now_time):
        for e in self.judgeLineDisappearEvents:
            if e.startTime <= now_time <= e.endTime:
                return Tool_Functions.linear_interpolation(
                    now_time,
                    e.startTime,
                    e.endTime,
                    e.start,
                    e.end
                )
        return 0.0 #never
    
    def get_datavar_move(self,now_time,w,h):
        for e in self.judgeLineMoveEvents:
            if e.startTime <= now_time <= e.endTime:
                return (
                    Tool_Functions.interpolation_phi(now_time, e.startTime, e.endTime, e.start, e.end) * w,
                    h - Tool_Functions.interpolation_phi(now_time, e.startTime, e.endTime, e.start2, e.end2) * h
                )
        return (0.0, 0.0) #never

    def get_datavar_text(self,now_time):
        for e in self.TextEvents: # sort by startTime and reverse
            if e.startTime <= now_time:
                return e.value
        return ""

    def get_datavar_scale(self,now_time):
        xs, ys = 1.0, 1.0
        
        for ce_x in self.ScaleXEvents:
            if ce_x.startTime <= now_time <= ce_x.endTime:
                xs = Tool_Functions.easing_interpolation(now_time, ce_x.startTime, ce_x.endTime, ce_x.start, ce_x.end, ce_x.easingFunc)
                break
        
        for ce_y in self.ScaleYEvents:
            if ce_y.startTime <= now_time <= ce_y.endTime:
                ys = Tool_Functions.easing_interpolation(now_time, ce_y.startTime, ce_y.endTime, ce_y.start, ce_y.end, ce_x.easingFunc)
                break
        
        return xs, ys
    
    def get_datavar_color(self, now_time):
        if not self.ColorEvents:
            return [254, 255, 169]
        
        for e in self.ColorEvents: # sort by startTime and reverse
            if e.startTime <= now_time:
                return e.value
        
        return [254, 255, 169]

@dataclass
class Phigros_Chart:
    formatVersion: int
    offset: float
    judgeLineList: list[judgeLine]
    Extra_Enable: bool
    Extra: dict
    
    def __post_init__(self):
        self.note_num = 0
        for judgeLine in self.judgeLineList:
            #set_master_to_notes
            judgeLine.set_master_to_notes()
            
            #init_speed_floorposition
            last_speedEvent_floorPosition = 0.0
            for speedEvent in judgeLine.speedEvents:
                speedEvent.floorPosition = last_speedEvent_floorPosition
                last_speedEvent_floorPosition += (speedEvent.endTime - speedEvent.startTime) * speedEvent.value * judgeLine.T

            #count
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                if not note.fake:
                    self.note_num += 1
    
    def init_notes(self, PHIGROS_Y:float):
        for judgeLine in self.judgeLineList:
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                note._init(PHIGROS_Y)
    
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
                    "global": extra_efct_item["global"],
                    "vars": values
                })
        
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
        **kwargs: typing.Mapping[str, typing.Any]
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