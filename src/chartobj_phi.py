from __future__ import annotations

import init_logging as _

import typing
import random
import math
from dataclasses import dataclass

import const
import tool_funcs

def findevent(events: list[judgeLineBaseEvent]|list[speedEvent], t: float) -> typing.Optional[judgeLineBaseEvent|speedEvent]:
    l, r = 0, len(events) - 1
    
    while l <= r:
        m = (l + r) // 2
        e = events[m]
        if e.startTime <= t < e.endTime: return e
        elif e.startTime > t: r = m - 1
        else: l = m + 1
            
    return None

def getFloorPosition(line: judgeLine, t: float) -> float:
    if not line.speedEvents: return 0.0
    
    e: speedEvent = findevent(line.speedEvents, t)
    
    if e is None and t >= line.speedEvents[-1].endTime:
        e = line.speedEvents[-1]
        t = e.endTime
    elif e is None:
        return 0.0
    
    return e.floorPosition + (t - e.startTime) * line.T * e.value

def split_different_speednotes(notes: list[Note]) -> list[list[Note]]:
    tempmap: dict[int, list[Note]] = {}
    
    for n in notes:
        h = n.speed
        if h not in tempmap: tempmap[h] = []
        tempmap[h].append(n)
    
    return list(tempmap.values())

def other_fv_initevents(es: list[judgeLineBaseEvent]|list[speedEvent]):
    if not es: return
    
    for i, e in enumerate(es):
        if i != len(es) - 1:
            e.endTime = es[i + 1].startTime
        else:
            e.endTime = const.PGR_INF
            
    if not isinstance(es[0], speedEvent):
        for i, e in enumerate(es):
            if i != len(es) - 1:
                if not e.useEndNode:
                    e.end = es[i + 1].start
                    if isinstance(e, judgeLineMoveEvent):
                        e.end2 = es[i + 1].start2
            else:
                if not e.useEndNode:
                    e.end = e.start
                    if isinstance(e, judgeLineMoveEvent):
                        e.end2 = e.start2

@dataclass
class Note:
    type: typing.Literal[1,2,3,4]
    time: float
    positionX: float
    holdTime: float
    speed: float
    floorPosition: float
    above: bool
    
    effect_random_blocks: typing.Optional[tuple[int]] = None
    id: typing.Optional[int] = None
    clicked: bool = False # this attr mean is "this note click time is <= now time", so if disable autoplay and click time <= now time but user is not click this attr still is true.
    morebets: bool = False
    master: typing.Optional[judgeLine] = None
    effect_times: const.ClickEffectType | tuple = ()
    state: int = const.NOTE_STATE.MISS
    master_index: typing.Optional[int] = None
    sec: typing.Optional[float] = None
    nowpos: tuple[float, float] = (-1.0, -1.0)
    nowrotate: float = 0.0
    
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
    player_bad_posandrotate: typing.Optional[tuple[tuple[float, float], float]] = None
    
    presentation_mode_click_time: float = float("nan")
    presentation_mode_clicked: bool = False
    
    def __post_init__(self):
        self.id = tool_funcs.Get_A_New_NoteId()
        self.effect_random_blocks = tool_funcs.newRandomBlocks()
    
    def __eq__(self, oth: typing.Any):
        if not isinstance(oth, Note):
            return NotImplemented
        return self.id == oth.id

    def __hash__(self) -> int:
        return self.id
    
    def init(self) -> None:
        self.hold_length_sec = self.holdTime * self.master.T
        self.hold_length_pgry = self.speed * self.hold_length_sec
        self.hold_endtime = self.sec + self.hold_length_sec
        self.player_holdjudge_tomanager_time = max(self.hold_endtime - 0.2, self.sec)
        self.ishold = self.type == const.NOTE_TYPE.HOLD
        self.draworder = const.NOTE_RORDER_MAP[self.type]
        
        self.type_string = const.TYPE_STRING_MAP[self.type]
        
        self.floorPosition = getFloorPosition(self.master, self.time)
        
        self.effect_times = []
        self.effect_times.append((
            self.sec,
            tool_funcs.newRandomBlocks(),
            self.getNoteClickPos(self.time)
        ))
        
        if self.ishold:
            bt = 30 / self.master.bpm
            st = 0.0
            while True:
                st += bt
                if st >= self.hold_length_sec: break
                self.effect_times.append((
                    self.sec + st,
                    tool_funcs.newRandomBlocks(),
                    self.getNoteClickPos((self.sec + st) / self.master.T)
                ))
        
        self.player_effect_times = self.effect_times.copy()
        
        dub_text = "_dub" if self.morebets else ""
        if not self.ishold:
            self.img_keyname = f"{self.type_string}{dub_text}"
            self.imgname = f"Note_{self.img_keyname}"
        else:
            self.img_keyname = f"{self.type_string}_Head{dub_text}"
            self.imgname = f"Note_{self.img_keyname}"
            
            self.img_body_keyname = f"{self.type_string}_Body{dub_text}"
            self.imgname_body = f"Note_{self.img_body_keyname}"
            
            self.img_end_keyname = f"{self.type_string}_End{dub_text}"
            self.imgname_end = f"Note_{self.img_end_keyname}"
    
    def getNoteClickPos(self, time: float) -> tuple[typing.Callable[[int, int], tuple[float, float]], float]:
        lineRotate = self.master.getRotate(time)
        
        cached: bool = False
        cachedata: typing.Optional[tuple[float, float]] = None
        
        def callback(w: int, h: int):
            nonlocal cached, cachedata
            
            if cached: return cachedata
            cached, cachedata = True, tool_funcs.rotate_point(
                *self.master.getMove(time, w, h),
                lineRotate, self.positionX * w * const.PGR_UW
            )
            
            return cachedata
        
        return callback, lineRotate

    def dump(self):
        return {
            "type": self.type,
            "time": self.time,
            "holdTime": self.holdTime,
            "positionX": self.positionX,
            "speed": self.speed,
            "floorPosition": self.floorPosition
        }
    
@dataclass
class speedEvent:
    startTime: float
    endTime: float
    value: float
    floorPosition: typing.Optional[float] = None
    
    def dump(self):
        return {
            "startTime": self.startTime,
            "endTime": self.endTime,
            "value": self.value,
            "floorPosition": self.floorPosition
        }

@dataclass
class judgeLineBaseEvent:
    startTime: float
    endTime: float
    start: float
    end: float

@dataclass
class judgeLineMoveEvent(judgeLineBaseEvent):
    start2: float
    end2: float
    
    def dump(self):
        return {
            "startTime": self.startTime,
            "endTime": self.endTime,
            "start": self.start,
            "end": self.end,
            "start2": self.start2,
            "end2": self.end2
        }

@dataclass
class judgeLineRotateEvent(judgeLineBaseEvent):
    def dump(self):
        return {
            "startTime": self.startTime,
            "endTime": self.endTime,
            "start": self.start,
            "end": self.end
        }

@dataclass
class judgeLineDisappearEvent(judgeLineBaseEvent):
    def dump(self):
        return {
            "startTime": self.startTime,
            "endTime": self.endTime,
            "start": self.start,
            "end": self.end
        }

@dataclass
class judgeLine:
    bpm: float
    notesAbove: list[Note]
    notesBelow: list[Note]
    speedEvents: list[speedEvent]
    judgeLineMoveEvents: list[judgeLineMoveEvent]
    judgeLineRotateEvents: list[judgeLineRotateEvent]
    judgeLineDisappearEvents: list[judgeLineDisappearEvent]
    
    master: typing.Optional[Chart] = None
    
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
        
        self._sortEvents()
        for i, n in enumerate(self.notesAbove): n.master_index = i
        for i, n in enumerate(self.notesBelow): n.master_index = i
        
        self.notesAbove.sort(key = lambda x: x.time)
        self.notesBelow.sort(key = lambda x: x.time)
        
        self.effectNotes = self.notesAbove + self.notesBelow
        self.effectNotes.sort(key = lambda x: x.time)
        
        self.renderNotes = split_different_speednotes(self.notesAbove) + split_different_speednotes(self.notesBelow)
        for rnc in self.renderNotes:
            rnc.sort(key = lambda x: x.time)
    
    def _sortEvents(self):
        self.speedEvents.sort(key = lambda x: x.startTime)
        self.judgeLineMoveEvents.sort(key = lambda x: x.startTime)
        self.judgeLineRotateEvents.sort(key = lambda x: x.startTime)
        self.judgeLineDisappearEvents.sort(key = lambda x: x.startTime)
    
    def getRotate(self, now_time: float):
        e = findevent(self.judgeLineRotateEvents, now_time)
        return -tool_funcs.linear_interpolation(
            now_time,
            e.startTime, e.endTime,
            e.start, e.end
        ) if e is not None else 0.0
    
    def getAlpha(self, now_time: float):
        e = findevent(self.judgeLineDisappearEvents, now_time)
        return tool_funcs.linear_interpolation(
            now_time,
            e.startTime, e.endTime,
            e.start, e.end
        ) if e is not None else 0.0
    
    def _getMoveRaw(self, now_time: float):
        e: judgeLineMoveEvent = findevent(self.judgeLineMoveEvents, now_time)
        return (
            tool_funcs.linear_interpolation(now_time, e.startTime, e.endTime, e.start, e.end),
            tool_funcs.linear_interpolation(now_time, e.startTime, e.endTime, e.start2, e.end2)
        ) if e is not None else (0.0, 0.0)
    
    def getMove(self, now_time: float, w: int, h: int):
        raw = self._getMoveRaw(now_time)
        
        # if self.master.formatVersion not in (1, 3):
        #     return (
        #         w / 2 + raw[0] * h * 0.1,
        #         h / 2 - raw[1] * h * 0.1
        #     )
        
        return (raw[0] * w, (1.0 - raw[1]) * h)

    def initPresentationMode(self):
        perfect = const.NOTE_JUDGE_RANGE.PERFECT
        for n in self.notesAbove + self.notesBelow:
            if n.type in (const.NOTE_TYPE.DRAG, const.NOTE_TYPE.FLICK):
                n.presentation_mode_clicked = True
                continue
            
            n.presentation_mode_click_time = n.time * self.T + tool_funcs.linear_interpolation(
                (math.sin(n.time * self.T) + math.cos(n.time * self.T)) / 1.6, 0.0, 1.0,
                -perfect / 3.2, perfect / 3
            ) + random.uniform(-perfect, perfect) / 7
    
    def dump(self):
        return {
            "bpm": self.bpm,
            "notesAbove": [n.dump() for n in self.notesAbove],
            "notesBelow": [n.dump() for n in self.notesBelow],
            "speedEvents": [e.dump() for e in self.speedEvents],
            "judgeLineMoveEvents": [e.dump() for e in self.judgeLineMoveEvents],
            "judgeLineRotateEvents": [e.dump() for e in self.judgeLineRotateEvents],
            "judgeLineDisappearEvents": [e.dump() for e in self.judgeLineDisappearEvents]
        }

@dataclass
class Chart:
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
                
                line._sortEvents()
                    
            self.offset = 0.0
        
        self.note_num = 0
        
        for line in self.judgeLineList:
            line.master = self
            for note in line.notesAbove + line.notesBelow:
                note.sec = note.time * line.T
        
        notes = [i for l in self.judgeLineList for i in l.notesAbove + l.notesBelow]
        notes.sort(key = lambda n: n.sec)
        last_time = float("nan")
        last_note: typing.Optional[Note] = None
        for n in notes:
            if last_time == n.sec:
                last_note.morebets = True
                n.morebets = True
                
            last_time = n.sec
            last_note = n
            
        for line in self.judgeLineList:
            fp = 0.0
            
            if self.formatVersion not in (1, 3):
                other_fv_initevents(line.speedEvents)
                other_fv_initevents(line.judgeLineMoveEvents)
                other_fv_initevents(line.judgeLineDisappearEvents)
                other_fv_initevents(line.judgeLineRotateEvents)
            
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

    def dump(self):
        return {
            "formatVersion": 3,
            "offset": 0.0,
            "judgeLineList": [line.dump() for line in self.judgeLineList]
        }
    
class PPLMPHI_Proxy(tool_funcs.PPLM_ProxyBase):
    def __init__(self, cobj: Chart): self.cobj = cobj
    
    def get_lines(self) -> list[judgeLine]: return self.cobj.judgeLineList
    def get_all_pnotes(self) -> list[Note]: return self.cobj.playerNotes
    def remove_pnote(self, n: Note): self.cobj.playerNotes.remove(n)
    
    def nproxy_stime(self, n: Note): return n.sec
    def nproxy_etime(self, n: Note): return n.hold_endtime
    def nproxy_hcetime(self, n: Note): return n.player_holdjudge_tomanager_time
    
    def nproxy_typein(self, n: Note, ts: tuple[int]): return n.type in ts
    def nproxy_typeis(self, n: Note, t: int): return n.type == t
    def nproxy_phitype(self, n: Note): return n.type
    
    def nproxy_nowpos(self, n: Note): return n.nowpos
    def nproxy_nowrotate(self, n: Note) -> float: return n.nowrotate
    def nproxy_effects(self, n: Note): return n.player_effect_times
    
    def nproxy_get_pclicked(self, n: Note): return n.player_clicked
    def nproxy_set_pclicked(self, n: Note, state: bool): n.player_clicked = state
    
    def nproxy_get_wclick(self, n: Note): return n.player_will_click
    def nproxy_set_wclick(self, n: Note, state: bool): n.player_will_click = state
    
    def nproxy_get_pclick_offset(self, n: Note): return n.player_click_offset
    def nproxy_set_pclick_offset(self, n: Note, offset: float): n.player_click_offset = offset
    
    def nproxy_get_ckstate(self, n: Note): return n.state
    def nproxy_set_ckstate(self, n: Note, state: int): n.state = state
    def nproxy_get_ckstate_ishit(self, n: Note): return n.state in (const.NOTE_STATE.PERFECT, const.NOTE_STATE.GOOD)
    
    def nproxy_get_cksound_played(self, n: Note): return n.player_click_sound_played
    def nproxy_set_cksound_played(self, n: Note, state: bool): n.player_click_sound_played = state
    
    def nproxy_get_missed(self, n: Note): return n.player_missed
    def nproxy_set_missed(self, n: Note, state: bool): n.player_missed = state
    
    def nproxy_get_holdjudged(self, n: Note): return n.player_holdjudged
    def nproxy_set_holdjudged(self, n: Note, state: bool): n.player_holdjudged = state

    def nproxy_get_holdjudged_tomanager(self, n: Note) -> bool: return n.player_holdjudged_tomanager
    def nproxy_set_holdjudged_tomanager(self, n: Note, state: bool) -> None: n.player_holdjudged_tomanager = state
    
    def nproxy_get_last_testholdmiss_time(self, n: Note): return n.player_last_testholdismiss_time
    def nproxy_set_last_testholdmiss_time(self, n: Note, time: float): n.player_last_testholdismiss_time = time
    
    def nproxy_get_safe_used(self, n: Note): return n.player_judge_safe_used
    def nproxy_set_safe_used(self, n: Note, state: bool): n.player_judge_safe_used = state
    
    def nproxy_get_holdclickstate(self, n: Note): return n.player_holdclickstate
    def nproxy_set_holdclickstate(self, n: Note, state: int): n.player_holdclickstate = state
    
    def nproxy_get_pbadtime(self, n: Note): return n.player_badtime
    def nproxy_set_pbadtime(self, n: Note, time: float): n.player_badtime = time
