from __future__ import annotations

import rjsmin
import typing
import json
from dataclasses import dataclass

import const
import tool_funcs

def findevent(
    events: list[
        judgeLineDisappearEvent
        |judgeLineMoveEvent
        |judgeLineRotateEvent
        |speedEvent
    ], t: float
) -> judgeLineDisappearEvent|judgeLineMoveEvent|judgeLineRotateEvent|speedEvent|None:
    l, r = 0, len(events) - 1
    
    while l <= r:
        m = (l + r) // 2
        e = events[m]
        if e.startTime <= t <= e.endTime: return e
        elif e.startTime > t: r = m - 1
        else: l = m + 1
            
    return None

def getFloorPosition(line: judgeLine, t: float) -> float:
    if not line.speedEvents: return 0.0
    
    e: speedEvent = findevent(line.speedEvents, t)
    
    if e is None and t >= line.speedEvents[-1].endTime:
        e = line.speedEvents[-1]
        t = e.endTime
    
    return e.floorPosition + (t - e.startTime) * line.T * e.value

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
    effect_times: const.ClickEffectType | tuple = ()
    state: int = const.NOTE_STATE.MISS
    master_index: int|None = None
    nowpos: tuple[float, float] = (-1.0, -1.0)
    
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
    player_judge_safe_used: bool = False
    player_bad_posandrotate: tuple[tuple[float, float], float]|None = None
    
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
        self.sec = self.time * self.master.T
        self.hold_length_sec = self.holdTime * self.master.T
        self.hold_length_pgry = self.speed * self.hold_length_sec
        self.hold_endtime = self.sec + self.hold_length_sec
        self.player_holdjudge_tomanager_time = max(self.hold_endtime - 0.2, self.sec)
        self.ishold = self.type == const.Note.HOLD
        
        self.type_string = const.TYPE_STRING_MAP[self.type]
        
        self.floorPosition = getFloorPosition(self.master, self.time)
        
        self.effect_times = []
        self.effect_times.append((
            self.sec,
            tool_funcs.get_effect_random_blocks(),
            self.getNoteClickPos(self.time)
        ))
        
        if self.ishold:
            bt = 1 / self.master.bpm * 30
            st = 0.0
            while True:
                st += bt
                if st >= self.hold_length_sec: break
                self.effect_times.append((
                    self.sec + st,
                    tool_funcs.get_effect_random_blocks(),
                    self.getNoteClickPos((self.sec + st) / self.master.T)
                ))
        
        self.player_effect_times = self.effect_times.copy()
    
    def getNoteClickPos(self, time: float) -> typing.Callable[[float|int, float|int], tuple[float, float]]:
        linePos = self.master.get_datavar_move(time, 1.0, 1.0)
        lineRotate = self.master.get_datavar_rotate(time)
        
        cached: bool = False
        cachedata: tuple[float, float]|None = None
        
        def callback(w: int, h: int):
            nonlocal cached, cachedata
            
            if cached: return cachedata
            cached, cachedata = True, tool_funcs.rotate_point(
                linePos[0] * w, linePos[1] * h,
                lineRotate, self.positionX * 0.05625 * w
            )
            
            return cachedata
        
        return callback
    
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
        self.renderNotesAbove = self.notesAbove.copy()
        self.renderNotesBelow = self.notesBelow.copy()
        self.effectNotes = self.notesAbove + self.notesBelow
        self.effectNotes.sort(key = lambda x: x.time)
    
    def _sort_events(self):
        self.speedEvents.sort(key = lambda x: x.startTime)
        self.judgeLineMoveEvents.sort(key = lambda x: x.startTime)
        self.judgeLineRotateEvents.sort(key = lambda x: x.startTime)
        self.judgeLineDisappearEvents.sort(key = lambda x: x.startTime)
    
    def get_datavar_rotate(self, now_time):
        e = findevent(self.judgeLineRotateEvents, now_time)
        return -tool_funcs.linear_interpolation(
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
        
        for line in self.judgeLineList:
            fp = 0.0
            
            for e in line.speedEvents:
                e.floorPosition = fp
                fp += (e.endTime - e.startTime) * e.value * line.T

            for note in line.notesAbove + line.notesBelow:
                self.note_num += 1
                note.master = line
                note.init()
                
        self.combotimes = []
        for line in self.judgeLineList:
            for note in line.notesAbove + line.notesBelow:
                self.combotimes.append(note.sec if not note.ishold else max(note.sec, note.hold_endtime - 0.2))
        self.combotimes.sort()
        
        self.playerNotes = sorted([i for l in self.judgeLineList for i in l.notesAbove + l.notesBelow], key = lambda n: n.sec)
    
    def getCombo(self, t: float):
        l, r = 0, len(self.combotimes)
        while l < r:
            m = (l + r) // 2
            if self.combotimes[m] < t: l = m + 1
            else: r = m
        return l
    
class PPLMPHI_Proxy(tool_funcs.PPLM_ProxyBase):
    def __init__(self, cobj: Phigros_Chart): self.cobj = cobj
    
    def get_lines(self) -> list[judgeLine]: return self.cobj.judgeLineList
    def get_all_pnotes(self) -> list[note]: return self.cobj.playerNotes
    def remove_pnote(self, n: note): self.cobj.playerNotes.remove(n)
    
    def nproxy_stime(self, n: note): return n.sec
    def nproxy_etime(self, n: note): return n.hold_endtime
    def nproxy_hcetime(self, n: note): return n.player_holdjudge_tomanager_time
    
    def nproxy_typein(self, n: note, ts: tuple[int]): return n.type in ts
    def nproxy_typeis(self, n: note, t: int): return n.type == t
    def nproxy_phitype(self, n: note): return n.type
    
    def nproxy_nowpos(self, n: note): return n.nowpos
    def nproxy_effects(self, n: note): return n.player_effect_times
    
    def nproxy_get_pclicked(self, n: note): return n.player_clicked
    def nproxy_set_pclicked(self, n: note, state: bool): n.player_clicked = state
    
    def nproxy_get_wclick(self, n: note): return n.player_will_click
    def nproxy_set_wclick(self, n: note, state: bool): n.player_will_click = state
    
    def nproxy_get_pclick_offset(self, n: note): return n.player_click_offset
    def nproxy_set_pclick_offset(self, n: note, offset: float): n.player_click_offset = offset
    
    def nproxy_get_ckstate(self, n: note): return n.state
    def nproxy_set_ckstate(self, n: note, state: int): n.state = state
    def nproxy_get_ckstate_ishit(self, n: note): return n.state in (const.NOTE_STATE.PERFECT, const.NOTE_STATE.GOOD)
    
    def nproxy_get_cksound_played(self, n: note): return n.player_click_sound_played
    def nproxy_set_cksound_played(self, n: note, state: bool): n.player_click_sound_played = state
    
    def nproxy_get_missed(self, n: note): return n.player_missed
    def nproxy_set_missed(self, n: note, state: bool): n.player_missed = state
    
    def nproxy_get_holdjudged(self, n: note): return n.player_holdjudged
    def nproxy_set_holdjudged(self, n: note, state: bool): n.player_holdjudged = state

    def nproxy_get_holdjudged_tomanager(self, n: note) -> bool: return n.player_holdjudged_tomanager
    def nproxy_set_holdjudged_tomanager(self, n: note, state: bool) -> None: n.player_holdjudged_tomanager = state
    
    def nproxy_get_last_testholdmiss_time(self, n: note): return n.player_last_testholdismiss_time
    def nproxy_set_last_testholdmiss_time(self, n: note, time: float): n.player_last_testholdismiss_time = time
    
    def nproxy_get_safe_used(self, n: note): return n.player_judge_safe_used
    def nproxy_set_safe_used(self, n: note, state: bool): n.player_judge_safe_used = state
    
    def nproxy_get_holdclickstate(self, n: note): return n.player_holdclickstate
    def nproxy_set_holdclickstate(self, n: note, state: int): n.player_holdclickstate = state
    
    def nproxy_get_pbadtime(self, n: note): return n.player_badtime
    def nproxy_set_pbadtime(self, n: note, time: float): n.player_badtime = time

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
