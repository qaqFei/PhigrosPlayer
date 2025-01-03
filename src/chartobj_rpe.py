from __future__ import annotations

import math
import typing
import logging
from dataclasses import dataclass, field

import tool_funcs
import rpe_easing
import const

HITSOUND_UNSET = object()

def _init_events(es: list[LineEvent]):
    aes = []
    for i, e in enumerate(es):
        if i != len(es) - 1:
            ne = es[i + 1]
            if e.endTime.value < ne.startTime.value:
                aes.append(LineEvent(e.endTime, ne.startTime, e.end, e.end, 1, isfill=True))
    es.extend(aes)
    es.sort(key = lambda x: x.startTime.value)
    if es: es.append(LineEvent(es[-1].endTime, Beat(31250000, 0, 1), es[-1].end, es[-1].end, 1, isfill=True))

def geteasing_func(t: int):
    try:
        if not isinstance(t, int): t = 1
        t = 1 if t < 1 else (len(rpe_easing.ease_funcs) if t > len(rpe_easing.ease_funcs) else t)
        return rpe_easing.ease_funcs[int(t) - 1]
    except Exception as e:
        logging.warning(f"geteasing_func error: {e}")
        return rpe_easing.ease_funcs[0]

def findevent(events: list[LineEvent|ExtraVar], t: float, timeattr: str = "value") -> LineEvent|ExtraVar|None:
    l, r = 0, len(events) - 1
    
    while l <= r:
        m = (l + r) // 2
        e = events[m]
        st, et = getattr(e.startTime, timeattr), getattr(e.endTime, timeattr)
        if st <= t <= et: return e
        elif st > t: r = m - 1
        else: l = m + 1
            
    return None

def split_different_speednotes(notes: list[Note]) -> list[Note]:
    currs = None
    result, templist = [], []
    
    for n in notes:
        if (h := hash((n.speed, n.yOffset))) != currs:
            if templist: result.append(templist)
            templist = []
            currs = h
        
        templist.append(n)
    
    if templist: result.append(templist)
    return result
        
@dataclass
class Beat:
    var1: int
    var2: int
    var3: int
    
    secvar: float|None = None # only speed events
    
    def __post_init__(self):
        self.value = self.var1 + (self.var2 / self.var3)
        self._hash = hash(self.value)
    
    def __hash__(self) -> int:
        return self._hash
    
    def __repr__(self):
        return f"{self.var1} + {self.var2} / {self.var3} = {self.value}"
    
    def __str__(self): return self.__repr__()
    
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
    hitsound: str|None
    
    clicked: bool = False
    morebets: bool = False
    floorPosition: float = 0.0
    holdLength: float = 0.0
    masterLine: JudgeLine|None = None
    master_index: int|None = None
    nowpos: tuple[float, float] = (-1.0, -1.0)
    
    state: int = const.NOTE_STATE.MISS
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
    player_judge_safe_used: bool = False
    player_bad_posandrotate: tuple[tuple[float, float], float]|None = None
    
    def __post_init__(self):
        self.phitype = {1:1, 2:3, 3:4, 4:2}[self.type]
        self.type_string = const.TYPE_STRING_MAP[self.phitype]
        self.positionX2 = self.positionX / const.RPE_WIDTH
        self.float_alpha = (255 & int(self.alpha)) / 255
        self.ishold = self.type_string == "Hold"
        self.hitsound_reskey = self.phitype if self.hitsound is None else hash(tuple(map(ord, self.hitsound)))
    
    def _init(self, master: Rpe_Chart, avgBpm: float):
        self.secst = master.beat2sec(self.startTime.value, self.masterLine.bpmfactor)
        self.secet = master.beat2sec(self.endTime.value, self.masterLine.bpmfactor)
        self.player_holdjudge_tomanager_time = max(self.secst, self.secet - 0.2)
        
        self.floorPosition = self.masterLine.GetFloorPositionByTime(self.secst)
        if self.ishold: self.holdLength = self.masterLine.GetFloorPositionRange(self.secst, self.secet)

        self.effect_times = []
        self.effect_times.append((
            self.secst,
            tool_funcs.get_effect_random_blocks(),
            self.getNoteClickPos(self.startTime.value, master, self.masterLine)
        ))
        
        if self.ishold:
            bt = 1 / avgBpm * 30
            st = 0.0
            while True:
                st += bt
                if st >= self.secet - self.secst: break
                self.effect_times.append((
                    self.secst + st,
                    tool_funcs.get_effect_random_blocks(),
                    self.getNoteClickPos(master.sec2beat(self.secst + st, self.masterLine.bpmfactor), master, self.masterLine)
                ))
                
        self.player_effect_times = self.effect_times.copy()
        
    def getNoteClickPos(self, time: float, master: Rpe_Chart, line: JudgeLine) -> typing.Callable[[float|int, float|int], tuple[float, float]]:
        linePos = tool_funcs.conrpepos(*line.GetPos(time, master))
        lineRotate = sum([
            line.GetEventValue(time, layer.rotateEvents, 0.0)
            for layer in line.eventLayers
        ])
        
        cached: bool = False
        cachedata: tuple[float, float]|None = None
        
        def callback(w: int, h: int):
            nonlocal cached, cachedata
            
            if cached: return cachedata
            cached, cachedata = True, tool_funcs.rotate_point(
                linePos[0] * w, linePos[1] * h,
                lineRotate, self.positionX2 * w
            )
            
            return cachedata
        
        return callback

    def __eq__(self, value): return self is value

@dataclass
class LineEvent:
    startTime: Beat
    endTime: Beat
    start: float|str|list[int]
    end: float|str|list[int]
    easingType: int = 1
    easingLeft: float = 0.0
    easingRight: float = 1.0
    
    bezier: int = 0
    bezierPoints: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    
    easingFunc: typing.Callable[[float], float] = rpe_easing.ease_funcs[0]
    
    floorPosition: float|None = None # only speed events have this
    isfill: bool = False
    
    def __post_init__(self):
        self.easingFunc = geteasing_func(self.easingType) if not self.bezier else tool_funcs.createBezierFunction(self.bezierPoints)
        self.easingLeft = max(0.0, min(1.0, self.easingLeft))
        self.easingRight = max(0.0, min(1.0, self.easingRight))
        
        if self.easingLeft != 0.0 or self.easingRight != 1.0:
            self.easingFunc = tool_funcs.createCuttingEasingFunction(self.easingFunc, self.easingLeft, self.easingRight)
    
@dataclass
class EventLayer:
    speedEvents: list[LineEvent]
    moveXEvents: list[LineEvent]
    moveYEvents: list[LineEvent]
    rotateEvents: list[LineEvent]
    alphaEvents: list[LineEvent]
    
    def __post_init__(self):
        self.speedEvents.sort(key = lambda x: x.startTime.value)
        self.moveXEvents.sort(key = lambda x: x.startTime.value)
        self.moveYEvents.sort(key = lambda x: x.startTime.value)
        self.rotateEvents.sort(key = lambda x: x.startTime.value)
        self.alphaEvents.sort(key = lambda x: x.startTime.value)
        
        _init_events(self.speedEvents)
        _init_events(self.moveXEvents)
        _init_events(self.moveYEvents)
        _init_events(self.rotateEvents)
        _init_events(self.alphaEvents)
        
@dataclass
class Extended:
    scaleXEvents: list[LineEvent]
    scaleYEvents: list[LineEvent]
    colorEvents: list[LineEvent]
    textEvents: list[LineEvent]
    
    def __post_init__(self):
        self.scaleXEvents.sort(key = lambda x: x.startTime.value)
        self.scaleYEvents.sort(key = lambda x: x.startTime.value)
        self.colorEvents.sort(key = lambda x: x.startTime.value)
        self.textEvents.sort(key = lambda x: x.startTime.value)

        _init_events(self.scaleXEvents)
        _init_events(self.scaleYEvents)
        _init_events(self.colorEvents)
        _init_events(self.textEvents)

@dataclass
class ControlItem:
    sval: float
    tval: float
    easing: int
    easingFunc: typing.Callable[[float], float] = rpe_easing.ease_funcs[0]
    next: ControlItem|None = None
    
    def __post_init__(self):
        self.easingFunc = geteasing_func(self.easing)

@dataclass
class ControlEvents:
    alphaControls: list[ControlItem]
    posControls: list[ControlItem]
    sizeControls: list[ControlItem]
    yControls: list[ControlItem]
    
    def __post_init__(self):
        self.alphaControls.sort(key = lambda x: x.sval)
        self.posControls.sort(key = lambda x: x.sval)
        self.sizeControls.sort(key = lambda x: x.sval)
        self.yControls.sort(key = lambda x: x.sval)
        self._inite(self.alphaControls)
        self._inite(self.posControls)
        self._inite(self.sizeControls)
        self._inite(self.yControls)
    
    def _inite(self, es: list[ControlItem]):
        for i, e in enumerate(es):
            if i != len(es) - 1:
                e.next = es[i + 1]
    
    def _gtvalue(self, s: float, es: list[ControlItem], default: float = 1.0):
        for e in es:
            if e.next is None:
                return e.sval
            if e.sval <= s <= e.next.sval:
                return e.easingFunc((s - e.sval) / (e.next.sval - e.sval)) * (e.next.tval - e.tval) + e.tval
        return default
    
    def gtvalue(self, x: float):
        return (
            self._gtvalue(x, self.alphaControls, 1.0),
            self._gtvalue(x, self.posControls, 0.0),
            self._gtvalue(x, self.sizeControls, 1.0),
            self._gtvalue(x, self.yControls, 0.0)
        )

@dataclass
class MetaData:
    RPEVersion: int
    offset: int
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
    isCover: int
    Texture: str
    attachUI: str|None
    eventLayers: list[EventLayer]
    extended: Extended|None
    notes: list[Note]
    bpmfactor: float
    father: int|JudgeLine # in other object, __post_init__ change this value to a line
    zOrder: int
    isGif: bool
    
    controlEvents: ControlEvents
    
    playingFloorPosition: float = 0.0
    effectNotes: list[Note]|None = None
    renderNotes: list[list[Note]]|None = None
    
    def GetEventValue(self, t: float, es: list[LineEvent], default):
        if not es: return default
        
        e = findevent(es, t)
        
        if e is None:
            if t >= es[-1].endTime.value:
                return es[-1].end
            return default
        
        if isinstance(e.start, float|int):
            return tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start, e.end, e.easingFunc)
        elif isinstance(e.start, str):
            return tool_funcs.rpe_text_tween(e.start, e.end, tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, 0.0, 1.0, e.easingFunc), e.isfill)
        elif isinstance(e.start, list):
            r = tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[0], e.end[0], e.easingFunc)
            g = tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[1], e.end[1], e.easingFunc)
            b = tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[2], e.end[2], e.easingFunc)
            return (r, g, b)
    
    def GetPos(self, t: float, master: Rpe_Chart) -> list[float, float]:
        linePos = [
            sum(self.GetEventValue(t, layer.moveXEvents, 0.0) for layer in self.eventLayers),
            sum(self.GetEventValue(t, layer.moveYEvents, 0.0) for layer in self.eventLayers)
        ]
            
        if self.father != -1:
            try:
                sec = master.beat2sec(t, self.bpmfactor)
                
                fatherBeat = master.sec2beat(sec, self.father.bpmfactor)
                fatherPos = self.father.GetPos(fatherBeat, master)
                fatherRotate = sum(self.father.GetEventValue(fatherBeat, layer.rotateEvents, 0.0) for layer in self.father.eventLayers)
                
                if fatherRotate == 0.0:
                    return list(map(lambda v1, v2: v1 + v2, fatherPos, linePos))
                
                return list(map(lambda v1, v2: v1 + v2, fatherPos, 
                    tool_funcs.rotate_point(
                        0.0, 0.0,
                        90 - (math.degrees(math.atan2(*linePos)) + fatherRotate),
                        tool_funcs.getLineLength(*linePos, 0.0, 0.0)
                    )
                ))
            except IndexError:
                pass
            
        return linePos
    
    def GetState(self, t: float, defaultColor: tuple[int, int, int], master: Rpe_Chart) -> tuple[tuple[float, float], float, float, tuple[int, int, int], float, float, str|None]:
        "linePos, lineAlpha, lineRotate, lineColor, lineScaleX, lineScaleY, lineText"
        linePos = self.GetPos(t, master)
        lineAlpha = 0.0
        lineRotate = 0.0
        lineColor = defaultColor
        if (self.extended and self.extended.textEvents) or self.attachUI:
            lineColor = (255, 255, 255)
        lineScaleX = 1.0
        lineScaleY = 1.0
        lineText = None
        
        for layer in self.eventLayers:
            lineAlpha += self.GetEventValue(t, layer.alphaEvents, 0.0)
            lineRotate += self.GetEventValue(t, layer.rotateEvents, 0.0)
        
        if self.extended:
            lineScaleX = self.GetEventValue(t, self.extended.scaleXEvents, lineScaleX)
            lineScaleY = self.GetEventValue(t, self.extended.scaleYEvents, lineScaleY)
            lineColor = self.GetEventValue(t, self.extended.colorEvents, lineColor)
            lineText = self.GetEventValue(t, self.extended.textEvents, lineText)
        
        if t < 0.0 and self.attachUI is None:
            lineAlpha = -255
        
        return tool_funcs.conrpepos(*linePos), lineAlpha / 255, lineRotate, lineColor, lineScaleX, lineScaleY, lineText
    
    def GetEventRawFloorPosition(self, e: LineEvent, l: float, r: float) -> float:
        st, et = e.startTime.secvar, e.endTime.secvar
        
        if l <= st <= r <= et:
            v1, v2 = st, r
        elif st <= l <= et <= r:
            v1, v2 = l, et
        elif l <= st <= et <= r:
            v1, v2 = st, et
        elif st <= l <= r <= et:
            v1, v2 = l, r
        else:
            return 0.0
        
        if e.start == e.end:
            return (v2 - v1) * e.start
        else:
            s1 = tool_funcs.linear_interpolation(v1, st, et, e.start, e.end)
            s2 = tool_funcs.linear_interpolation(v2, st, et, e.start, e.end)
            return (v2 - v1) * (s1 + s2) / 2
    
    def GetFloorPositionRange(self, l: float, r: float):
        yl, yr = l, r
        l, r = sorted((l, r))
                    
        return (self.GetFloorPositionByTime(r) - self.GetFloorPositionByTime(l)) * (-1.0 if yl > yr else 1.0)
    
    def GetFloorPositionByTime(self, t: float):
        fp = 0.0
        
        for layer in self.eventLayers:
            if not layer.speedEvents: continue
            e = findevent(layer.speedEvents, t, "secvar")
            
            if e is None:
                if t >= layer.speedEvents[-1].endTime.secvar:
                    e = layer.speedEvents[-1]
                    t = e.endTime.secvar
                else:
                    continue
                
            fp += e.floorPosition + self.GetEventRawFloorPosition(e, e.startTime.secvar, t)
        
        return fp * 120 / const.RPE_HEIGHT

    def __hash__(self) -> int:
        return id(self)
    
    def __eq__(self, oth) -> bool:
        return self is oth

class PPLMRPE_Proxy(tool_funcs.PPLM_ProxyBase):
    def __init__(self, cobj: Rpe_Chart): self.cobj = cobj
    
    def get_lines(self): return self.cobj.judgeLineList
    def get_all_pnotes(self): return self.cobj.playerNotes
    def remove_pnote(self, n: Note): self.cobj.playerNotes.remove(n)
    
    def nproxy_stime(self, n: Note): return n.secst
    def nproxy_etime(self, n: Note): return n.secet
    def nproxy_hcetime(self, n: Note): return n.player_holdjudge_tomanager_time
    
    def nproxy_typein(self, n: Note, ts: tuple[int]): return n.phitype in ts
    def nproxy_typeis(self, n: Note, t: int): return n.phitype == t
    def nproxy_phitype(self, n: Note): return n.phitype
    
    def nproxy_nowpos(self, n: Note): return n.nowpos
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
    
    def nproxy_get_holdjudged_tomanager(self, n: Note): return n.player_holdjudged_tomanager
    def nproxy_set_holdjudged_tomanager(self, n: Note, state: bool): n.player_holdjudged_tomanager = state
    
    def nproxy_get_last_testholdmiss_time(self, n: Note): return n.player_last_testholdismiss_time
    def nproxy_set_last_testholdmiss_time(self, n: Note, time: float): n.player_last_testholdismiss_time = time
    
    def nproxy_get_safe_used(self, n: Note): return n.player_judge_safe_used
    def nproxy_set_safe_used(self, n: Note, state: bool): n.player_judge_safe_used = state
    
    def nproxy_get_holdclickstate(self, n: Note): return n.player_holdclickstate
    def nproxy_set_holdclickstate(self, n: Note, state: int): n.player_holdclickstate = state
    
    def nproxy_get_pbadtime(self, n: Note): return n.player_badtime
    def nproxy_set_pbadtime(self, n: Note, time: float): n.player_badtime = time
    
@dataclass
class Rpe_Chart:
    META: MetaData
    BPMList: list[BPMEvent]
    judgeLineList: list[JudgeLine]
    
    combotimes: list[float]|None = None
    
    def __post_init__(self):
        self.BPMList = list(filter(lambda x: x.bpm != 0.0, self.BPMList))
        self.BPMList.sort(key=lambda x: x.startTime.value)
        self.judgeLineList = list(filter(lambda x: x.bpmfactor != 0.0, self.judgeLineList))
        self.combotimes = []
        
        try: avgBpm = sum([e.bpm for e in self.BPMList]) / len(self.BPMList)
        except ZeroDivisionError: avgBpm = 140.0
        
        for line in self.judgeLineList:
            if line.father != -1:
                line.father = self.judgeLineList[line.father]
                
            for layer in line.eventLayers:
                fp = 0.0
                for e in layer.speedEvents:
                    e.startTime.secvar = self.beat2sec(e.startTime.value, line.bpmfactor)
                    e.endTime.secvar = self.beat2sec(e.endTime.value, line.bpmfactor)
                    e.floorPosition = fp
                    fp += line.GetEventRawFloorPosition(e, e.startTime.secvar, e.endTime.secvar)
            
            for i, note in enumerate(line.notes):
                note.master_index = i
                note.masterLine = line
                note._init(self, avgBpm)
                if not note.isFake:
                    self.combotimes.append(note.secst if not note.ishold else max(note.secst, note.secet - 0.2))
            
            line.notes.sort(key=lambda x: x.startTime.value)
            line.effectNotes = [i for i in line.notes if not i.isFake]
            line.renderNotes = (
                split_different_speednotes([i for i in line.notes if i.above == 1])
                + split_different_speednotes([i for i in line.notes if i.above != 1])
            )
        
        self.note_num = len([i for line in self.judgeLineList for i in line.notes if not i.isFake])
        self.judgeLineList.sort(key = lambda x: x.zOrder)
        self.combotimes.sort()
        self.playerNotes = sorted([i for line in self.judgeLineList for i in line.notes if not i.isFake], key = lambda x: x.secst)
    
    def getCombo(self, t: float):
        l, r = 0, len(self.combotimes)
        while l < r:
            m = (l + r) // 2
            if self.combotimes[m] < t: l = m + 1
            else: r = m
        return l
    
    def sec2beat(self, t: float, bpmfactor: float):
        beat = 0.0
        for i, e in enumerate(self.BPMList):
            bpmv = e.bpm * bpmfactor
            if i != len(self.BPMList) - 1:
                et_beat = self.BPMList[i + 1].startTime.value - e.startTime.value
                et_sec = et_beat * (60 / bpmv)
                
                if t >= et_sec:
                    beat += et_beat
                    t -= et_sec
                else:
                    beat += t / (60 / bpmv)
                    break
            else:
                beat += t / (60 / bpmv)
        return beat
    
    def beat2sec(self, t: float, bpmfactor: float):
        sec = 0.0
        for i, e in enumerate(self.BPMList):
            bpmv = e.bpm * bpmfactor
            if i != len(self.BPMList) - 1:
                et_beat = self.BPMList[i + 1].startTime.value - e.startTime.value
                
                if t >= et_beat:
                    sec += et_beat * (60 / bpmv)
                    t -= et_beat
                else:
                    sec += t * (60 / bpmv)
                    break
            else:
                sec += t * (60 / bpmv)
        return sec

    def __hash__(self) -> int:
        return id(self)
    
    def __eq__(self, oth) -> bool:
        if isinstance(oth, JudgeLine):
            return self is oth
        return False

@dataclass
class ExtraVar:
    startTime: Beat
    endTime: Beat
    easingType: int
    start: float|list[float]
    end: float|list[float]
    
    def __post_init__(self):
        self.easingFunc = geteasing_func(self.easingType)
    
@dataclass
class ExtraEffect:
    start: Beat
    end: Beat
    shader: str
    vars: dict[str, list[ExtraVar]]
    
@dataclass
class Extra:
    enable: bool
    bpm: list[BPMEvent]
    effects: list[ExtraEffect]
    
    def getValues(self, t: float):
        beat = 0.0
        for i, e in enumerate(self.bpm):
            if i != len(self.bpm) - 1:
                et_beat = self.bpm[i + 1].startTime.value - e.startTime.value
                et_sec = et_beat * (60 / e.bpm)
                
                if t >= et_sec:
                    beat += et_beat
                    t -= et_sec
                else:
                    beat += t / (60 / e.bpm)
                    break
            else:
                beat += t / (60 / e.bpm)
        
        result = []
        
        for e in self.effects:
            if e.start.value <= beat <= e.end.value:
                values = {}
                for k, v in e.vars.items():
                    ev = JudgeLine.GetEventValue(None, beat, v, v[0].start if v else None)
                    if ev is not None: values.update({k: ev})
                result.append((e.shader, values))
                
        return result
    