from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache, cache
import typing

import Tool_Functions
import rpe_easing
import Const
        
def _init_events(es: list[LineEvent]):
    aes = []
    for i, e in enumerate(es):
        if i != len(es) - 1:
            ne = es[i + 1]
            if e.endTime.value < ne.startTime.value:
                aes.append(LineEvent(
                    e.endTime, ne.startTime, e.end, e.end, 1
                ))
    es.extend(aes)
    es.sort(key = lambda x: x.startTime.value)
    if es: es.append(LineEvent(
        es[-1].endTime, Beat(31250000, 0, 1), es[-1].end, es[-1].end, 1
    ))
        
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
    
    clicked: bool = False
    morebets: bool = False
    floorPosition: float = 0.0
    holdLength: float = 0.0
    show_effected: bool = False
    masterLine: JudgeLine|None = None
    
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
    
    player_badtime_beat: float = float("nan")
    player_badjudge_floorp: float = float("nan")
    
    def __post_init__(self):
        self.phitype = {1:1, 2:3, 3:4, 4:2}[self.type]
        self.type_string = {
            Const.Note.TAP: "Tap",
            Const.Note.DRAG: "Drag",
            Const.Note.HOLD: "Hold",
            Const.Note.FLICK: "Flick"
        }[self.phitype]
        self.positionX2 = self.positionX / 1350
        self.float_alpha = (255 & int(self.alpha)) / 255
        self.ishold = self.type_string == "Hold"
        self.effect_random_blocks = Tool_Functions.get_effect_random_blocks()
    
    def _init(self, master: Rpe_Chart, avgBpm: float):
        self.effect_times = []
        hold_starttime = master.beat2sec(self.startTime.value)
        hold_effect_blocktime = 1 / avgBpm * 30
        hold_endtime = master.beat2sec(self.endTime.value)
        self.player_holdjudge_tomanager_time = max(0, master.beat2sec(self.endTime.value) - 0.2)
        while True:
            hold_starttime += hold_effect_blocktime
            if hold_starttime >= hold_endtime:
                break
            self.effect_times.append((hold_starttime, Tool_Functions.get_effect_random_blocks()))
        
        self.secst = master.beat2sec(self.startTime.value)
        self.secet = master.beat2sec(self.endTime.value)

@dataclass
class LineEvent:
    startTime: Beat
    endTime: Beat
    start: float|str|list[int]
    end: float|str|list[int]
    easingType: int
    easingFunc: typing.Callable[[float], float] = rpe_easing.ease_funcs[0]
    
    def __post_init__(self):
        if not isinstance(self.easingType, int): self.easingType = 1
        self.easingType = 1 if self.easingType < 1 else (len(rpe_easing.ease_funcs) if self.easingType > len(rpe_easing.ease_funcs) else self.easingType)
        self.easingFunc = rpe_easing.ease_funcs[self.easingType - 1]
    
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
    father: int
    zOrder: int
    
    playingFloorPosition: float = 0.0
    textureLineRawTextureSize: tuple[int, int]|None = None # when has value at loaded res.
    
    def GetEventValue(self, t:float, es: list[LineEvent], default):
        for e in es:
            if e.startTime.value <= t <= e.endTime.value:
                if isinstance(e.start, float|int):
                    return Tool_Functions.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start, e.end, e.easingFunc)
                elif isinstance(e.start, str):
                    return e.start
                elif isinstance(e.start, list):
                    r = Tool_Functions.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[0], e.end[0], e.easingFunc)
                    g = Tool_Functions.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[1], e.end[1], e.easingFunc)
                    b = Tool_Functions.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[2], e.end[2], e.easingFunc)
                    return (r, g, b)
        return default
    
    @lru_cache
    def GetPos(self, t: float, master: Rpe_Chart):
        linePos = [0.0, 0.0]
        for layer in self.eventLayers:
            linePos[0] += self.GetEventValue(t, layer.moveXEvents, 0.0)
            linePos[1] += self.GetEventValue(t, layer.moveYEvents, 0.0)
        if self.father != -1:
            try:
                father = master.JudgeLineList[self.father]
                fatherPos = father.GetPos(t, master)
                linePos = [linePos[0] + fatherPos[0], linePos[1] + fatherPos[1]]
            except IndexError:
                pass
        return linePos
    
    def GetSpeed(self, t: float):
        v = 0.0
        for layer in self.eventLayers:
            for e in layer.speedEvents:
                if e.startTime.value <= t <= e.endTime.value:
                    v += Tool_Functions.linear_interpolation(t, e.startTime.value, e.endTime.value, e.start, e.end)
                    break # loop for other layers
        return v
    
    def GetState(self, t: float, defaultColor: list[int, int, int], master: Rpe_Chart) -> dict:
        "linePos, lineAlpha, lineRotate, lineColor, lineScaleX, lineScaleY, lineText"
        linePos, lineAlpha, lineRotate, lineColor, lineScaleX, lineScaleY, lineText = self.GetPos(t, master), 0.0, 0.0, defaultColor, 1.0, 1.0, None
        
        for layer in self.eventLayers:
            lineAlpha += self.GetEventValue(t, layer.alphaEvents, 0.0)
            lineRotate += self.GetEventValue(t, layer.rotateEvents, 0.0)
        
        if self.extended:
            lineScaleX = self.GetEventValue(t, self.extended.scaleXEvents, lineScaleX)
            lineScaleY = self.GetEventValue(t, self.extended.scaleYEvents, lineScaleY)
            lineColor = self.GetEventValue(t, self.extended.colorEvents, lineColor)
            lineText = self.GetEventValue(t, self.extended.textEvents, lineText)
            
        return Tool_Functions.conrpepos(*linePos), lineAlpha / 255, lineRotate, lineColor, lineScaleX, lineScaleY, lineText
    
    def GetNoteFloorPosition(self, t: float, n: Note, master: Rpe_Chart):
        l, r = master.beat2sec(t), master.beat2sec(n.startTime.value)
        return self.GetFloorPosition(*sorted((l, r)), master) * (-1.0 if l > r else 1.0)
    
    def GetFloorPosition(self, l: float, r: float, master: Rpe_Chart):
        fp = 0.0
        for layer in self.eventLayers:
            for e in layer.speedEvents:
                st, et = master.beat2sec(e.startTime.value), master.beat2sec(e.endTime.value)
                if l <= st <= r <= et:
                    v1, v2 = st, r
                elif st <= l <= et <= r:
                    v1, v2 = st, l
                elif l <= st <= et <= r:
                    v1, v2 = st, et
                elif st <= l <= r <= et:
                    v1, v2 = l, r
                else:
                    continue
                if e.start == e.end:
                    fp += (v2 - v1) * e.start
                else:
                    s1 = Tool_Functions.linear_interpolation(v1, st, et, e.start, e.end)
                    s2 = Tool_Functions.linear_interpolation(v2, st, et, e.start, e.end)
                    fp += (v2 - v1) * (s1 + s2) / 2
        return fp * 120 / 900

    def GetHoldLength(self, t: float, n: Note, master: Rpe_Chart):
        sect = master.beat2sec(n.endTime.value) - master.beat2sec(n.startTime.value)
        speed = self.GetSpeed(t)
        return sect * speed * 120 / 900

    def __hash__(self) -> int:
        return id(self)
    
    def __eq__(self, oth) -> bool:
        if isinstance(oth, JudgeLine):
            return self is oth
        return False

@dataclass
class Rpe_Chart:
    META: MetaData
    BPMList: list[BPMEvent]
    JudgeLineList: list[JudgeLine]
    
    def __post_init__(self):
        self.BPMList.sort(key=lambda x: x.startTime.value)
        
        try: avgBpm = sum([e.bpm for e in self.BPMList]) / len(self.BPMList)
        except ZeroDivisionError: avgBpm = 140.0
        for line in self.JudgeLineList:
            for note in line.notes:
                note._init(self, avgBpm)
                note.masterLine = line
        
        self.note_num = len([i for line in self.JudgeLineList for i in line.notes if not i.isFake])
    
    @cache
    def sec2beat(self, t: float):
        beat = 0.0
        for i, e in enumerate(self.BPMList):
            if i != len(self.BPMList) - 1:
                et_beat = self.BPMList[i + 1].startTime.value - e.startTime.value
                et_sec = et_beat * (60 / e.bpm)
                
                if t >= et_sec:
                    beat += et_beat
                    t -= et_sec
                else:
                    beat += t / (60 / e.bpm)
                    break
            else:
                beat += t / (60 / e.bpm)
        return beat
    
    @cache
    def beat2sec(self, t: float):
        sec = 0.0
        for i, e in enumerate(self.BPMList):
            if i != len(self.BPMList) - 1:
                et_beat = self.BPMList[i + 1].startTime.value - e.startTime.value
                
                if t >= et_beat:
                    sec += et_beat * (60 / e.bpm)
                    t -= et_beat
                else:
                    sec += t * (60 / e.bpm)
                    break
            else:
                sec += t * (60 / e.bpm)
        return sec

    def __hash__(self) -> int:
        return id(self)
    
    def __eq__(self, oth) -> bool:
        if isinstance(oth, JudgeLine):
            return self is oth
        return False
    
del typing,dataclass