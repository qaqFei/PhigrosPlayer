from __future__ import annotations

import rjsmin
import typing
import json
from dataclasses import dataclass

import const
import tool_funcs

def getFloorPosition(line: judgeLine, t: float) -> float:
    if not line.speedEvents: return 0.0
    for speed_event in line.speedEvents:
        if speed_event.startTime <= t <= speed_event.endTime:
            return speed_event.floorPosition + (t - speed_event.startTime) * line.T * speed_event.value
    last_speed_event = line.speedEvents[-1]
    return last_speed_event.floorPosition + (t - last_speed_event.endTime) * line.T * last_speed_event.value

def findevent(
    events: list[
        judgeLineDisappearEvent
        |judgeLineMoveEvent
        |judgeLineRotateEvent
    ], t: float
) -> judgeLineDisappearEvent|judgeLineMoveEvent|judgeLineRotateEvent|None:
    l, r = 0, len(events) - 1
    
    while l <= r:
        m = (l + r) // 2
        e = events[m]
        if e.startTime <= t <= e.endTime: return e
        elif e.startTime > t: r = m - 1
        else: l = m + 1
            
    return None

@dataclass
class note:
    type: typing.Literal[1,2,3,4]
    time: float
    positionX: float
    holdTime: float
    speed: float
    floorPosition: float
    above: bool
    effect_random_blocks: tuple[int]|None = None
    id: int|None = None
    clicked: bool = False # this attr mean is "this note click time is <= now time", so if disable autoplay and click time <= now time but user is not click this attr still is true.
    morebets: bool = False
    master: judgeLine|None = None
    show_effected: bool = False
    effect_times: list[tuple[int]] | tuple = ()
    state: int = const.NOTE_STATE.MISS
    master_index: int|None = None
    player_clicked: bool = False
    player_click_offset: float = 0.0
    player_click_sound_played: bool = False
    player_will_click: bool = False
    player_missed: bool = False
    player_badtime: float = float("nan")
    player_holdmiss_time: float = float("inf")
    player_last_testholdismiss_time: float = -float("inf")
    player_holdjudged: bool = False
    player_holdclickstate: int = const.NOTE_STATE.MISS
    player_holdjudged_tomanager: bool = False
    player_holdjudge_tomanager_time: float = float("nan") # init at note._init function
    player_drag_judge_safe_used: bool = False
    
    render_skiped: bool = False
    
    def __post_init__(self):
        self.id = tool_funcs.Get_A_New_NoteId()
        self.effect_random_blocks = tool_funcs.get_effect_random_blocks()
    
    def __eq__(self, oth:object):
        if not isinstance(oth, note):
            return NotImplemented
        return self.id == oth.id

    def __hash__(self) -> int:
        return self.id
    
    def init(self) -> None:
        self.hold_length_sec = self.holdTime * self.master.T
        self.hold_length_pgry = self.speed * self.hold_length_sec
        self.hold_endtime = self.time * self.master.T + self.hold_length_sec
        self.player_holdjudge_tomanager_time = self.hold_endtime - 0.2 if self.hold_length_sec >= 0.2 else self.time * self.master.T
        
        self.effect_times = []
        hold_starttime = self.time * self.master.T
        hold_effect_blocktime = (1 / self.master.bpm * 30)
        while True:
            hold_starttime += hold_effect_blocktime
            if hold_starttime >= self.hold_endtime:
                break
            self.effect_times.append((hold_starttime, tool_funcs.get_effect_random_blocks()))
        
        self.type_string = {
            const.Note.TAP:"Tap",
            const.Note.DRAG:"Drag",
            const.Note.HOLD:"Hold",
            const.Note.FLICK:"Flick"
        }[self.type]
        
        self.floorPosition = getFloorPosition(self.master, self.time)
    
    def getNoteClickPos(self, time: float) -> tuple[float, float]:
        linePos = self.master.get_datavar_move(time, 1.0, 1.0)
        lineRotate = self.master.get_datavar_rotate(time)
        return tool_funcs.rotate_point(*linePos, - lineRotate, self.positionX * 0.05625)
    
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
class judgeLine:
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
        for i, n in enumerate(self.notesAbove): n.master_index = i
        for i, n in enumerate(self.notesBelow): n.master_index = i
        self.notesAbove.sort(key = lambda x: x.time)
        self.notesBelow.sort(key = lambda x: x.time)
    
    def _sort_events(self):
        self.speedEvents.sort(key = lambda x: x.startTime)
        self.judgeLineMoveEvents.sort(key = lambda x: x.startTime)
        self.judgeLineRotateEvents.sort(key = lambda x: x.startTime)
        self.judgeLineDisappearEvents.sort(key = lambda x: x.startTime)

    def set_master_to_notes(self):
        for note in self.notesAbove:
            note.master = self
        for note in self.notesBelow:
            note.master = self
    
    def get_datavar_rotate(self, now_time):
        e = findevent(self.judgeLineRotateEvents, now_time)
        return tool_funcs.linear_interpolation(
            now_time,
            e.startTime,
            e.endTime,
            e.start,
            e.end
        ) if e is not None else 0.0
    
    def get_datavar_disappear(self, now_time):
        e = findevent(self.judgeLineDisappearEvents, now_time)
        return tool_funcs.linear_interpolation(
            now_time,
            e.startTime,
            e.endTime,
            e.start,
            e.end
        ) if e is not None else 0.0
    
    def _get_datavar_move_rawphi(self, now_time):
        e = findevent(self.judgeLineMoveEvents, now_time)
        return (
            tool_funcs.linear_interpolation(now_time, e.startTime, e.endTime, e.start, e.end),
            tool_funcs.linear_interpolation(now_time, e.startTime, e.endTime, e.start2, e.end2)
        ) if e is not None else (0.0, 0.0)
    
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
            judgeLine.set_master_to_notes()
            
            last_speedEvent_floorPosition = 0.0
            for speedEvent in judgeLine.speedEvents:
                speedEvent.floorPosition = last_speedEvent_floorPosition
                last_speedEvent_floorPosition += (speedEvent.endTime - speedEvent.startTime) * speedEvent.value * judgeLine.T

            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                self.note_num += 1
                note.init()
    
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
    
    def __call__(self, func: typing.Callable, *args: typing.Iterable, **kwargs: typing.Mapping[str, typing.Any]):
        self.RenderTasks.append(RenderTask(func, args, kwargs))
    
    def ExecTask(self):
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
                args = list(rendertask.args)
                if rendertask.func.__code__.co_name == "run_js_code":
                    args[0] = rjsmin.jsmin(args[0])
                    
                task_data["render"].append({
                    "func_name": rendertask.func.__code__.co_name,
                    "args": args,
                    "kwargs": rendertask.kwargs
                })
            
            data["data"].append(task_data)
        
        return json.dumps(data)

del typing, dataclass