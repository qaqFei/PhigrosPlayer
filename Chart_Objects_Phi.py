from __future__ import annotations
from dataclasses import dataclass
import typing
import json

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
    effect_random_blocks: tuple[int]
    above: bool
    id: int|None = None
    by_judgeLine_id: int|None = None
    clicked: bool = False # this attr mean is "this note click time is <= now time", so if disable autoplay and click time <= now time but user is not click this attr still is true.
    morebets: bool = False
    master: judgeLine|None = None
    show_effected: bool = False
    effect_times: list[tuple[int]] | tuple = ()
    state: int = Const.NOTE_STATE.MISS
    player_clicked: bool = False
    player_click_offset: float = 0.0
    player_click_sound_played: bool = False
    player_will_click: bool = False
    player_missed: bool = False
    player_badtime: float = float("nan")
    player_holdmiss_time: float = float("inf")
    player_last_testholdismiss_time: float = -float("inf")
    player_holdjudged: bool = False
    player_holdclickstate: int = Const.NOTE_STATE.MISS
    player_holdjudged_tomanager: bool = False
    player_holdjudge_tomanager_time: float = float("nan") # init at note._init function
    player_drag_judge_safe_used: bool = False
    
    def __eq__(self, oth:object):
        if not isinstance(oth, note):
            return NotImplemented
        return self.id == oth.id

    def __hash__(self) -> int:
        return self.id
    
    def __repr__(self) -> str:
        note_t = {
            Const.Note.TAP:"t",
            Const.Note.DRAG:"d",
            Const.Note.HOLD:"h",
            Const.Note.FLICK:"f"
        }[self.type]
        return f"{self.master.id}+{self.by_judgeLine_id}{note_t}"
    
    def _init(self, PHIGROS_Y) -> None:
        self.hold_length_sec = self.holdTime * self.master.T
        self.hold_length_px = (self.speed * self.hold_length_sec) * PHIGROS_Y
        self.hold_endtime = self.time * self.master.T + self.hold_length_sec
        self.player_holdjudge_tomanager_time = self.hold_endtime - 0.2 if self.hold_length_sec >= 0.2 else self.time * self.master.T
        
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
    
    def getNoteClickPos(self, time: float) -> tuple[float, float]:
        linePos = self.master.get_datavar_move(time, 1.0, 1.0)
        lineRotate = self.master.get_datavar_rotate(time)
        return Tool_Functions.rotate_point(
            *linePos, - lineRotate, self.positionX * 0.05625
        )
    
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
    
    def __post_init__(self):
        self.T = 1.875 / self.bpm
        
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
        
        self._sort_events()
    
    def _sort_events(self):
        self.speedEvents.sort(key = lambda x: x.startTime) # it cannot sort, if sort it -> cal floorPosition will be error. (i donot know why...)
        self.judgeLineMoveEvents.sort(key = lambda x: x.startTime)
        self.judgeLineRotateEvents.sort(key = lambda x: x.startTime)
        self.judgeLineDisappearEvents.sort(key = lambda x: x.startTime)

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        return f"JudgeLine-{self.id}"
    
    def set_master_to_notes(self):
        for note in self.notesAbove:
            note.master = self
        for note in self.notesBelow:
            note.master = self
    
    def get_datavar_rotate(self, now_time):
        for e in self.judgeLineRotateEvents:
            if e.startTime <= now_time <= e.endTime:
                return Tool_Functions.linear_interpolation(
                    now_time,
                    e.startTime,
                    e.endTime,
                    e.start,
                    e.end
                )
        return 0.0
    
    def get_datavar_disappear(self, now_time):
        for e in self.judgeLineDisappearEvents:
            if e.startTime <= now_time <= e.endTime:
                return Tool_Functions.linear_interpolation(
                    now_time,
                    e.startTime,
                    e.endTime,
                    e.start,
                    e.end
                )
        return 0.0
    
    def _get_datavar_move_rawphi(self, now_time):
        v = (0.0, 0.0)
        for e in self.judgeLineMoveEvents:
            if e.startTime <= now_time <= e.endTime:
                v = (
                    Tool_Functions.linear_interpolation(now_time, e.startTime, e.endTime, e.start, e.end),
                    Tool_Functions.linear_interpolation(now_time, e.startTime, e.endTime, e.start2, e.end2)
                )
                break
        return v
    
    def get_datavar_move(self, now_time, w, h):
        raw = self._get_datavar_move_rawphi(now_time)
        return (raw[0] * w, (1.0 - raw[1]) * h)

@dataclass
class Phigros_Chart:
    formatVersion: int
    offset: float
    judgeLineList: list[judgeLine]
    
    def __post_init__(self):
        if self.offset != 0.0:
            for line in self.judgeLineList:
                offset_time = self.offset / line.T
                for note in line.notesAbove + line.notesBelow:
                    note.time += offset_time
                
                if line.speedEvents:
                    for e in line.speedEvents:
                        e.startTime += offset_time
                        e.endTime += offset_time
                        e.floorPosition = None
                    line.speedEvents[0].startTime = 0.0
                
                if line.judgeLineMoveEvents:
                    for e in line.judgeLineMoveEvents:
                        e.startTime += offset_time
                        e.endTime += offset_time
                
                if line.judgeLineDisappearEvents:
                    for e in line.judgeLineDisappearEvents:
                        e.startTime += offset_time
                        e.endTime += offset_time
                
                if line.judgeLineRotateEvents:
                    for e in line.judgeLineRotateEvents:
                        e.startTime += offset_time
                        e.endTime += offset_time
                
                line._sort_events()
                    
            self.offset = 0.0
            
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
                self.note_num += 1
    
    def init_notes(self, PHIGROS_Y:float):
        for judgeLine in self.judgeLineList:
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                note._init(PHIGROS_Y)
    
    def get_all_note(self) -> list[note]:
       return [j for i in self.judgeLineList for j in i.notesAbove + i.notesBelow]
    
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

@dataclass
class FrameTaskRecorder_Meta:
    frame_speed: int
    frame_num: int
    render_range_more: bool
    render_range_more_scale: float
    size: tuple[float, float]

@dataclass
class FrameTaskRecorder:
    meta: FrameTaskRecorder_Meta
    data: typing.Iterable[FrameRenderTask]
    
    def jsonify(self):
        data = {
            "meta": {
                "frame_speed": self.meta.frame_speed,
                "frame_num": self.meta.frame_num,
                "render_range_more": self.meta.render_range_more,
                "render_range_more_scale": self.meta.render_range_more_scale,
                "size": self.meta.size
            },
            "data": []
        }
        
        for task in self.data:
            task_data = {
                "render": [],
                "ex": list(map(list, task.ExTask))
            }
            
            for rendertask in task.RenderTasks:
                task_data["render"].append({
                    "func_name":rendertask.func.__code__.co_name,
                    "args":list(rendertask.args),
                    "kwargs":rendertask.kwargs
                })
            
            data["data"].append(task_data)
        
        return json.dumps(data)

del typing, dataclass