import time
import sys
import typing
import math
from dataclasses import dataclass
from threading import Thread

import webcvapis
from pygame import mixer
from PIL import Image

import Const
import PlaySound
import Tool_Functions
import rpe_easing
import Chart_Objects_Phi
import Chart_Objects_Rpe
import Chart_Functions_Phi

@dataclass
class PhiCoreConfigure:
    SETTER: typing.Callable[[str, typing.Any], typing.Any]
    
    root: webcvapis.WebCanvas
    w: int
    h: int
    chart_information: dict
    chart_obj: Chart_Objects_Phi.Phigros_Chart | Chart_Objects_Rpe.Rpe_Chart
    CHART_TYPE: int
    Resource: dict
    ClickEffect_Size: float
    EFFECT_RANDOM_BLOCK_SIZE: float
    ClickEffectFrameCount: int
    PHIGROS_X: float
    PHIGROS_Y: float
    Note_width: float
    JUDGELINE_WIDTH: float
    note_max_size_half: float
    audio_length: float
    raw_audio_length: float
    show_start_time: float
    chart_res: dict[str, tuple[Image.Image,tuple[int, int]]]
    clickeffect_randomblock: bool
    clickeffect_randomblock_roundn: int
    Kill_PlayThread_Flag: bool
    enable_clicksound: bool
    rtacc: bool
    noautoplay: bool
    showfps: bool
    lfdaot: bool
    no_mixer_reset_chart_time: bool
    speed: float
    render_range_more: bool
    render_range_more_scale: float
    judgeline_notransparent: bool
    debug: bool
    combotips: bool
    noplaychart: bool

def CoreConfig(config: PhiCoreConfigure):
    global SETTER
    global root, w, h, chart_information
    global chart_obj, CHART_TYPE
    global Resource, ClickEffect_Size
    global EFFECT_RANDOM_BLOCK_SIZE
    global ClickEffectFrameCount
    global PHIGROS_X, PHIGROS_Y
    global Note_width, JUDGELINE_WIDTH
    global note_max_size_half, audio_length
    global raw_audio_length, show_start_time
    global chart_res, clickeffect_randomblock
    global clickeffect_randomblock_roundn
    global Kill_PlayThread_Flag
    global enable_clicksound, rtacc, noautoplay
    global showfps, lfdaot, no_mixer_reset_chart_time
    global speed, render_range_more
    global render_range_more_scale
    global judgeline_notransparent
    global debug, combotips, noplaychart
    
    SETTER = config.SETTER
    root = config.root
    w, h = config.w, config.h
    chart_information = config.chart_information
    chart_obj = config.chart_obj
    CHART_TYPE = config.CHART_TYPE
    Resource = config.Resource
    ClickEffect_Size = config.ClickEffect_Size
    EFFECT_RANDOM_BLOCK_SIZE = config.EFFECT_RANDOM_BLOCK_SIZE
    ClickEffectFrameCount = config.ClickEffectFrameCount
    PHIGROS_X, PHIGROS_Y = config.PHIGROS_X, config.PHIGROS_Y
    Note_width = config.Note_width
    JUDGELINE_WIDTH = config.JUDGELINE_WIDTH
    note_max_size_half = config.note_max_size_half
    audio_length = config.audio_length
    raw_audio_length = config.raw_audio_length
    show_start_time = config.show_start_time
    chart_res = config.chart_res
    clickeffect_randomblock = config.clickeffect_randomblock
    clickeffect_randomblock_roundn = config.clickeffect_randomblock_roundn
    Kill_PlayThread_Flag = config.Kill_PlayThread_Flag
    enable_clicksound = config.enable_clicksound
    rtacc = config.rtacc
    noautoplay = config.noautoplay
    showfps = config.showfps
    lfdaot = config.lfdaot
    no_mixer_reset_chart_time = config.no_mixer_reset_chart_time
    speed = config.speed
    render_range_more = config.render_range_more
    render_range_more_scale = config.render_range_more_scale
    judgeline_notransparent = config.judgeline_notransparent
    debug = config.debug
    combotips = config.combotips
    noplaychart = config.noplaychart
    
drawUI_Default_Kwargs = {
    f"{k}_{k2}": v
    for k in ("combonumber", "combo", "score", "name", "level", "pause") for k2, v in (("dx", 0.0), ("dy", 0.0), ("scaleX", 1.0), ("scaleY", 1.0), ("color", "rgba(255, 255, 255, 1.0)"))
}
lastCallDrawUI = - float("inf")

class PhigrosPlayManager:
    def __init__(self, noteCount:int):
        self.events: list[typing.Literal["P", "G", "B", "M"]] = []
        self.event_offsets: list[float] = [] # the note click offset (s)
        self.noteCount: int = noteCount
    
    def addEvent(self, event:typing.Literal["P", "G", "B", "M"], offset:float|None = None): # Perfect, Good, Bad, Miss
        self.events.append(event)
        if offset is not None: # offset is only good judge.
            self.event_offsets.append(offset)
    
    def getJudgelineColor(self) -> tuple[int]:
        if "B" in self.events or "M" in self.events:
            return (255, 255, 255) # White
        if "G" in self.events:
            return (162, 238, 255) # FC
        return (254, 255, 169) # AP

    def getCombo(self) -> int:
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                return cut
        return cut
    
    def getAcc(self) -> float: # 实时 Acc
        if not self.events: return 1.0
        acc = 0.0
        allcut = len(self.events)
        for e in self.events:
            if e == "P":
                acc += 1.0 / allcut
            elif e == "G":
                acc += 0.65 / allcut
        return acc
    
    def getAccOfAll(self) -> float:
        acc = 0.0
        for e in self.events:
            if e == "P":
                acc += 1.0 / self.noteCount
            elif e == "G":
                acc += 0.65 / self.noteCount
        return acc
    
    def getMaxCombo(self) -> int:
        r = 0
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                r = max(r, cut)
                cut = 0
        return max(r, cut)
    
    def getScore(self) -> float:
        return self.getAccOfAll() * 900000 + self.getMaxCombo() / self.noteCount * 100000
    
    def getPerfectCount(self) -> int:
        return self.events.count("P")
    
    def getGoodCount(self) -> int:
        return self.events.count("G")
    
    def getBadCount(self) -> int:
        return self.events.count("B")
    
    def getMissCount(self) -> int:
        return self.events.count("M")
    
    def getEarlyCount(self) -> int:
        return len(list(filter(lambda x: x > 0, self.event_offsets)))
    
    def getLateCount(self) -> int:
        return len(list(filter(lambda x: x < 0, self.event_offsets)))
    
    def getLevelString(self) -> typing.Literal["AP", "FC", "V", "S", "A", "B", "C", "F"]:
        score = self.getScore()
        if self.getPerfectCount() == self.noteCount: return "AP"
        elif self.getBadCount() == 0 and self.getMissCount() == 0: return "FC"
        
        if 0 <= score < 700000:
            return "F"
        elif 700000 <= score < 820000:
            return "C"
        elif 820000 <= score < 880000:
            return "B"
        elif 880000 <= score < 920000:
            return "A"
        elif 920000 <= score < 960000:
            return "S"
        elif 960000 <= score < 1000000:
            return "V"
        elif 1000000 <= score:
            return "AP"
    
def process_effect_base(x: float, y: float, p: float, effect_random_blocks, perfect: bool, Task: Chart_Objects_Phi.FrameRenderTask):
    color = (254, 255, 169) if perfect else (162, 238, 255)
    imn = f"Note_Click_Effect_{"Perfect" if perfect else "Good"}"
    if clickeffect_randomblock:
        beforedeg = 0
        block_alpha = (1.0 - p) * 0.85
        randomblock_r = ClickEffect_Size * rpe_easing.ease_funcs[17](p) / 1.35
        block_size = EFFECT_RANDOM_BLOCK_SIZE * (0.4 * math.sin(p * math.pi) + 0.6)
        for deg in effect_random_blocks:
            effect_random_point = Tool_Functions.rotate_point(
                x, y, beforedeg + deg,
                randomblock_r
            )
            Task(
                root.run_js_code,
                f"\
                ctx.roundRectEx(\
                    {effect_random_point[0] - block_size / 2},\
                    {effect_random_point[1] - block_size / 2},\
                    {block_size},\
                    {block_size},\
                    {block_size * clickeffect_randomblock_roundn},\
                    'rgba{color + (block_alpha, )}'\
                );",
                add_code_array = True
            )
            beforedeg += 90
    Task(
        root.run_js_code,
        f"ctx.drawImage(\
            {root.get_img_jsvarname(f"{imn}_{int(p * (ClickEffectFrameCount - 1)) + 1}")},\
            {x - ClickEffect_Size / 2}, {y - ClickEffect_Size / 2},\
            {ClickEffect_Size}, {ClickEffect_Size}\
        );",
        add_code_array = True
    )
        
def PlayChart_ThreadFunction():
    global PhigrosPlayManagerObject, Kill_PlayThread_Flag, PlayChart_NowTime
    PlayChart_NowTime = - float("inf")
    PhigrosPlayManagerObject = PhigrosPlayManager(chart_obj.note_num)
    SETTER("PhigrosPlayManagerObject", PhigrosPlayManagerObject)
    KeyDownCount = 0
    keymap = {chr(i): False for i in range(97, 123)}
    
    notes = [i for line in chart_obj.judgeLineList for i in line.notesAbove + line.notesBelow] if CHART_TYPE == Const.CHART_TYPE.PHI else [i for line in chart_obj.JudgeLineList for i in line.notes if not i.isFake]
    
    if CHART_TYPE == Const.CHART_TYPE.PHI:
        def _KeyDown(key: str):
            nonlocal KeyDownCount
            key = key.lower()
            if len(key) != 1: return
            if not (97 <= ord(key) <= 122): return
            if keymap[key]: return
            keymap[key] = True
            KeyDownCount += 1
            
            can_judge_notes = [(i, offset) for i in notes if (
                not i.player_clicked and
                i.type in (Const.Note.TAP, Const.Note.HOLD) and
                abs((offset := (i.time * i.master.T - PlayChart_NowTime))) <= (0.2 if i.type == Const.Note.TAP else 0.16)
            )]
            can_use_safedrag = [(i, offset) for i in notes if (
                i.type == Const.Note.DRAG and
                not i.player_drag_judge_safe_used and
                abs((offset := (i.time * i.master.T - PlayChart_NowTime))) <= 0.16
            )]
            
            can_judge_notes.sort(key = lambda x: x[1])
            can_use_safedrag.sort(key = lambda x: x[1])
            
            if can_judge_notes:
                n, offset = can_judge_notes[0]
                abs_offset = abs(offset)
                if 0.0 <= abs_offset <= 0.08:
                    n.state = Const.NOTE_STATE.PERFECT
                    if n.type == Const.Note.HOLD:
                        n.player_holdjudged = True
                        n.player_holdclickstate = n.state
                    else: # TAP
                        PhigrosPlayManagerObject.addEvent("P")
                elif 0.08 < abs_offset <= 0.16:
                    n.state = Const.NOTE_STATE.GOOD
                    if n.type == Const.Note.HOLD:
                        n.player_holdjudged = True
                        n.player_holdclickstate = n.state
                    else: # TAP
                        PhigrosPlayManagerObject.addEvent("G", offset)
                elif 0.16 < abs_offset <= 0.2: # only tap
                    if can_use_safedrag: # not empty
                        drag, drag_offset = can_use_safedrag[0]
                        if not drag.player_will_click:
                            drag.player_will_click = True
                            drag.player_click_offset = drag_offset
                        drag.player_drag_judge_safe_used = True
                        return None
                    
                    n.player_badtime = PlayChart_NowTime
                    n.state = Const.NOTE_STATE.BAD
                    PhigrosPlayManagerObject.addEvent("B")
                    
                if n.state != Const.NOTE_STATE.MISS:
                    n.player_click_offset = offset
                    n.player_clicked = True
    elif CHART_TYPE == Const.CHART_TYPE.RPE:
        def _KeyDown(key: str):
            nonlocal KeyDownCount
            key = key.lower()
            if len(key) != 1: return
            if not (97 <= ord(key) <= 122): return
            if keymap[key]: return
            keymap[key] = True
            KeyDownCount += 1
            
            can_judge_notes = [(i, offset) for i in notes if (
                not i.player_clicked and
                i.phitype in (Const.Note.TAP, Const.Note.HOLD) and
                abs((offset := (i.secst - PlayChart_NowTime))) <= (0.2 if i.phitype == Const.Note.TAP else 0.16)
            )]
            can_use_safedrag = [(i, offset) for i in notes if (
                i.phitype == Const.Note.DRAG and
                not i.player_drag_judge_safe_used and
                abs((offset := (i.secst - PlayChart_NowTime))) <= 0.16
            )]
            
            can_judge_notes.sort(key = lambda x: x[1])
            can_use_safedrag.sort(key = lambda x: x[1])
            
            if can_judge_notes:
                n, offset = can_judge_notes[0]
                abs_offset = abs(offset)
                if 0.0 <= abs_offset <= 0.08:
                    n.state = Const.NOTE_STATE.PERFECT
                    if n.ishold:
                        n.player_holdjudged = True
                        n.player_holdclickstate = n.state
                    else: # TAP
                        PhigrosPlayManagerObject.addEvent("P")
                elif 0.08 < abs_offset <= 0.16:
                    n.state = Const.NOTE_STATE.GOOD
                    if n.ishold:
                        n.player_holdjudged = True
                        n.player_holdclickstate = n.state
                    else: # TAP
                        PhigrosPlayManagerObject.addEvent("G", offset)
                elif 0.16 < abs_offset <= 0.2: # only tap
                    if can_use_safedrag: # not empty
                        drag, drag_offset = can_use_safedrag[0]
                        if not drag.player_will_click:
                            drag.player_will_click = True
                            drag.player_click_offset = drag_offset
                        drag.player_drag_judge_safe_used = True
                        return None
                    
                    n.player_badtime = PlayChart_NowTime
                    n.player_badtime_beat = chart_obj.sec2beat(n.player_badtime)
                    n.player_badjudge_floorp = n.floorPosition - n.masterLine.playingFloorPosition
                    n.state = Const.NOTE_STATE.BAD
                    PhigrosPlayManagerObject.addEvent("B")
                    
                if n.state != Const.NOTE_STATE.MISS:
                    n.player_click_offset = offset
                    n.player_clicked = True
    
    def _KeyUp(key:str):
        nonlocal KeyDownCount
        key = key.lower()
        if len(key) != 1: return
        if not (97 <= ord(key) <= 122): return
        if KeyDownCount > 0: KeyDownCount -= 1
        keymap[key] = False
    
    root.jsapi.set_attr("PhigrosPlay_KeyDown", _KeyDown)
    root.jsapi.set_attr("PhigrosPlay_KeyUp", _KeyUp)
    root.run_js_code("_PhigrosPlay_KeyDown = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyDown', e.key);});")
    root.run_js_code("_PhigrosPlay_KeyUp = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyUp', e.key);});")
    root.run_js_code("window.addEventListener('keydown', _PhigrosPlay_KeyDown);")
    root.run_js_code("window.addEventListener('keyup', _PhigrosPlay_KeyUp);")
    
    while True:
        keydown = KeyDownCount > 0
        
        for note in notes:
            if CHART_TYPE == Const.CHART_TYPE.PHI:
                note_time_sec = note.time * note.master.T
                
                if ( # (Drag / Flick) judge
                    keydown and
                    not note.player_clicked and
                    note.type in (Const.Note.FLICK, Const.Note.DRAG) and
                    abs((cktime := note_time_sec - PlayChart_NowTime)) <= 0.16 # +- 160ms
                ):
                    note.player_will_click = True
                    
                    if cktime <= 0.0: #late
                        note.player_click_offset = cktime
                
                if ( # if Drag / Flick it`s time to click and judged, click it and update it.
                    note.player_will_click and 
                    not note.player_clicked and 
                    note_time_sec <= PlayChart_NowTime
                ):
                    note.player_clicked = True
                    note.state = Const.NOTE_STATE.PERFECT
                    PhigrosPlayManagerObject.addEvent("P")
                
                if ( # play click sound
                    note.player_clicked and
                    not note.player_click_sound_played and
                    note.state in (Const.NOTE_STATE.PERFECT, Const.NOTE_STATE.GOOD)
                ):
                    if enable_clicksound:
                        Thread(target=PlaySound.Play, args=(Resource["Note_Click_Audio"][note.type_string],)).start()
                    note.player_click_sound_played = True
                
                if ( # miss judge
                    not note.player_clicked and
                    not note.player_missed and
                    note_time_sec - PlayChart_NowTime < - 0.2
                ):
                    note.player_missed = True
                    PhigrosPlayManagerObject.addEvent("M")
                
                if ( # hold judge sustain
                    keydown and
                    note.type == Const.Note.HOLD and 
                    note.player_clicked and
                    note.state != Const.NOTE_STATE.MISS and
                    note.hold_endtime - 0.2 >= PlayChart_NowTime
                ):
                    note.player_last_testholdismiss_time = time.time()
                    
                
                if ( # hold hold sustain miss judge
                    not keydown and
                    note.type == Const.Note.HOLD and
                    note.player_clicked and
                    note.state != Const.NOTE_STATE.MISS and
                    note.hold_endtime - 0.2 >= PlayChart_NowTime and
                    note.player_last_testholdismiss_time + 0.16 <= time.time()
                ):
                    note.player_holdmiss_time = PlayChart_NowTime
                    note.state = Const.NOTE_STATE.MISS
                    note.player_missed = True
                    PhigrosPlayManagerObject.addEvent("M")
                
                if ( # hold end add event to manager judge
                    note.type == Const.Note.HOLD and
                    note.player_holdjudged and # if judged is true, hold state is perfect/good/ miss(miss at clicking)
                    not note.player_holdjudged_tomanager and
                    note.player_holdjudge_tomanager_time <= PlayChart_NowTime
                ):
                    note.player_holdjudged_tomanager = True
                    if note.state == Const.NOTE_STATE.PERFECT: PhigrosPlayManagerObject.addEvent("P")
                    elif note.state == Const.NOTE_STATE.GOOD: PhigrosPlayManagerObject.addEvent("G", note.player_click_offset)
                    else: pass # note state is miss at clicking
            elif CHART_TYPE == Const.CHART_TYPE.RPE:
                if ( # (Drag / Flick) judge
                    keydown and
                    not note.player_clicked and
                    note.phitype in (Const.Note.FLICK, Const.Note.DRAG) and
                    abs((cktime := note.secst - PlayChart_NowTime)) <= 0.16 # +- 160ms
                ):
                    note.player_will_click = True
                    
                    if cktime <= 0.0: #late
                        note.player_click_offset = cktime
                
                if ( # if Drag / Flick it`s time to click and judged, click it and update it.
                    note.player_will_click and 
                    not note.player_clicked and 
                    note.secst <= PlayChart_NowTime
                ):
                    note.player_clicked = True
                    note.state = Const.NOTE_STATE.PERFECT
                    PhigrosPlayManagerObject.addEvent("P")
                
                if ( # play click sound
                    note.player_clicked and
                    not note.player_click_sound_played and
                    note.state in (Const.NOTE_STATE.PERFECT, Const.NOTE_STATE.GOOD)
                ):
                    if enable_clicksound:
                        Thread(target=PlaySound.Play, args=(Resource["Note_Click_Audio"][note.type_string],)).start()
                    note.player_click_sound_played = True
                
                if ( # miss judge
                    not note.player_clicked and
                    not note.player_missed and
                    note.secst - PlayChart_NowTime < - 0.2
                ):
                    note.player_missed = True
                    PhigrosPlayManagerObject.addEvent("M")
                
                
                if ( # hold judge sustain
                    keydown and
                    note.ishold and 
                    note.player_clicked and
                    note.state != Const.NOTE_STATE.MISS and
                    note.secet - 0.2 >= PlayChart_NowTime
                ):
                    note.player_last_testholdismiss_time = time.time()
                
                if ( # hold hold sustain miss judge
                    not keydown and
                    note.ishold and
                    note.player_clicked and
                    note.state != Const.NOTE_STATE.MISS and
                    note.secet - 0.2 >= PlayChart_NowTime and
                    note.player_last_testholdismiss_time + 0.16 <= time.time()
                ):
                    note.player_holdmiss_time = PlayChart_NowTime
                    note.state = Const.NOTE_STATE.MISS
                    note.player_missed = True
                    PhigrosPlayManagerObject.addEvent("M")
                    
                if ( # hold end add event to manager judge
                    note.ishold and
                    note.player_holdjudged and # if judged is true, hold state is perfect/good/ miss(miss at clicking)
                    not note.player_holdjudged_tomanager and
                    note.player_holdjudge_tomanager_time <= PlayChart_NowTime
                ):
                    note.player_holdjudged_tomanager = True
                    if note.state == Const.NOTE_STATE.PERFECT: PhigrosPlayManagerObject.addEvent("P")
                    elif note.state == Const.NOTE_STATE.GOOD: PhigrosPlayManagerObject.addEvent("G", note.player_click_offset)
                    else: pass # note state is miss at clicking
            
        if Kill_PlayThread_Flag:
            root.run_js_code("window.removeEventListener('keydown', _PhigrosPlay_KeyDown);")
            root.run_js_code("window.removeEventListener('keyup', _PhigrosPlay_KeyUp);")
            Kill_PlayThread_Flag = False
            SETTER("Kill_PlayThread_Flag", Kill_PlayThread_Flag)
            return
        time.sleep(1 / 480)
        
def get_stringscore(score:float) -> str:
    score_integer = int(score + 0.5)
    return f"{score_integer:>7}".replace(" ","0")

def draw_background():
    root.run_js_code(
        f"ctx.drawImage(\
           {root.get_img_jsvarname("background")},\
            0, 0, {w}, {h},\
        );",
        add_code_array = True
    )
    
def draw_ui(
    process:float = 0.0,
    score:str = "0000000",
    combo_state:bool = False,
    combo:int = 0,
    now_time:str = "0:00/0:00",
    acc:str = "100.00%",
    clear:bool = True,
    background:bool = True,
    animationing:bool = False,
    dy:float = 0.0,
    
    combonumberUI_dx: float = 0.0,
    combonumberUI_dy: float = 0.0,
    combonumberUI_scaleX: float = 1.0,
    combonumberUI_scaleY: float = 1.0,
    combonumberUI_color: str = "rgb(255, 255, 255)",
    combonumberUI_rotate: float = 0.0,
    
    comboUI_dx: float = 0.0,
    comboUI_dy: float = 0.0,
    comboUI_scaleX: float = 1.0,
    comboUI_scaleY: float = 1.0,
    comboUI_color: str = "rgb(255, 255, 255)",
    comboUI_rotate: float = 0.0,
    
    scoreUI_dx: float = 0.0,
    scoreUI_dy: float = 0.0,
    scoreUI_scaleX: float = 1.0,
    scoreUI_scaleY: float = 1.0,
    scoreUI_color: str = "rgb(255, 255, 255)",
    scoreUI_rotate: float = 0.0,
    
    nameUI_dx: float = 0.0,
    nameUI_dy: float = 0.0,
    nameUI_scaleX: float = 1.0,
    nameUI_scaleY: float = 1.0,
    nameUI_color: str = "rgb(255, 255, 255)",
    nameUI_rotate: float = 0.0,
    
    levelUI_dx: float = 0.0,
    levelUI_dy: float = 0.0,
    levelUI_scaleX: float = 1.0,
    levelUI_scaleY: float = 1.0,
    levelUI_color: str = "rgb(255, 255, 255)",
    levelUI_rotate: float = 0.0,
    
    pauseUI_dx: float = 0.0, # in fact, timeUI...
    pauseUI_dy: float = 0.0,
    pauseUI_scaleX: float = 1.0,
    pauseUI_scaleY: float = 1.0,
    pauseUI_color: str = "rgb(255, 255, 255)",
    pauseUI_rotate: float = 0.0
):
    global lastCallDrawUI
    
    if clear:
        root.clear_canvas(wait_execute = True)
    if background:
        draw_background()
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,{- h / 7 + dy});",add_code_array=True)
    
    root.create_rectangle(
        0, 0,
        w * process, h / 125,
        fillStyle = "rgba(145, 145, 145, 0.85)",
        wait_execute = True
    )
    
    root.create_rectangle(
        w * process - w * 0.002, 0,
        w * process, h / 125,
        fillStyle = "rgba(255, 255, 255, 0.9)",
        wait_execute = True
    )
    
    root.run_js_code(
        f"ctx.drawUIText(\
            '{root.process_code_string_syntax_tostring(score)}',\
            {w * 0.988 + scoreUI_dx},\
            {h * 0.045 + scoreUI_dy},\
            {scoreUI_rotate},\
            {scoreUI_scaleX},\
            {scoreUI_scaleY},\
            '{scoreUI_color}',\
            {(w + h) / 75 / 0.75},\
            'right',\
        );",
        add_code_array = True
    )
    
    if rtacc:
        root.run_js_code(
            f"ctx.drawUIText(\
                '{root.process_code_string_syntax_tostring(acc)}',\
                {w * 0.988 + scoreUI_dx},\
                {h * 0.0875 + scoreUI_dy},\
                {scoreUI_rotate},\
                {scoreUI_scaleX},\
                {scoreUI_scaleY},\
                '{scoreUI_color}',\
                {(w + h) / 145 / 0.75},\
                'right',\
            );",
            add_code_array = True
        )
    
    if combo_state:
        root.run_js_code(
            f"ctx.drawUIText(\
                '{root.process_code_string_syntax_tostring(f"{combo}")}',\
                {w / 2 + combonumberUI_dx},\
                {h * 0.05 + combonumberUI_dy},\
                {combonumberUI_rotate},\
                {combonumberUI_scaleX},\
                {combonumberUI_scaleY},\
                '{combonumberUI_color}',\
                {(w + h) / 75 / 0.75},\
                'center',\
            );",
            add_code_array = True
        )
        
        root.run_js_code(
            f"ctx.drawUIText(\
                '{root.process_code_string_syntax_tostring(combotips)}',\
                {w / 2 + comboUI_dx},\
                {h * 0.095 + comboUI_dy},\
                {comboUI_rotate},\
                {comboUI_scaleX},\
                {comboUI_scaleY},\
                '{comboUI_color}',\
                {(w + h) / 100 / 0.75},\
                'center',\
            );",
            add_code_array = True
        )
        
    root.run_js_code(
        f"ctx.drawUIText(\
            '{root.process_code_string_syntax_tostring(now_time)}',\
            {pauseUI_dx},\
            {h * 0.01 + (w + h) / 175 / 0.75 / 2 + pauseUI_dy},\
            {pauseUI_rotate},\
            {pauseUI_scaleX},\
            {pauseUI_scaleY},\
            '{pauseUI_color}',\
            {(w + h) / 175 / 0.75},\
            'left',\
        );",
        add_code_array = True
    )
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,-2 * {- h / 7 + dy});",add_code_array=True)
        
    root.run_js_code(
        f"ctx.drawUIText(\
            '{root.process_code_string_syntax_tostring(chart_information["Name"])}',\
            {w * 0.0125 + nameUI_dx},\
            {h * 0.976 - (w + h) / 125 / 0.75 / 2 + nameUI_dy},\
            {nameUI_rotate},\
            {nameUI_scaleX},\
            {nameUI_scaleY},\
            '{nameUI_color}',\
            {(w + h) / 125 / 0.75},\
            'left',\
        );",
        add_code_array = True
    )
        
    root.run_js_code(
        f"ctx.drawUIText(\
            '{root.process_code_string_syntax_tostring(chart_information["Level"])}',\
            {w * 0.9875 + levelUI_dx},\
            {h * 0.976 - (w + h) / 125 / 0.75 / 2 + levelUI_dy},\
            {levelUI_rotate},\
            {levelUI_scaleX},\
            {levelUI_scaleY},\
            '{levelUI_color}',\
            {(w + h) / 125 / 0.75},\
            'right',\
        );",
        add_code_array = True
    )
    
    try: fps = (1.0 / (time.time() - lastCallDrawUI))
    except ZeroDivisionError: fps = float("inf")
    
    root.create_text(
        text = (f"fps {fps:.0f} - " if showfps else "") + "PhigrosPlayer - by qaqFei - github.com/qaqFei/PhigrosPlayer - MIT License",
        x = w * 0.9875,
        y = h * 0.995,
        textAlign = "right",
        textBaseline = "bottom",
        strokeStyle = "rgba(255, 255, 255, 0.5)",
        fillStyle = "rgba(255, 255, 255, 0.5)",
        font = f"{((w + h) / 275 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,{- h / 7 + dy});",add_code_array=True)
    
    lastCallDrawUI = time.time()

def CheckMusicOffsetAndEnd(now_t: float, Task: Chart_Objects_Phi.FrameRenderTask):
    if now_t >= raw_audio_length:
        Task.ExTask.append(("break",))
    
    if not lfdaot and not no_mixer_reset_chart_time and mixer.music.get_busy():
        this_music_pos = mixer.music.get_pos() % (raw_audio_length * 1000)
        offset_judge_range = (1000 / 60) * 4
        if abs(music_offset := this_music_pos - (time.time() - show_start_time) * 1000) >= offset_judge_range:
            if abs(music_offset) < raw_audio_length * 1000 * 0.75:
                Task.ExTask.append(("set", "show_start_time", show_start_time - music_offset / 1000))
                print(f"Warning: mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset)}ms)")
             
def deleteDrwaUIKwargsDefaultValues(kwargs:dict) -> dict:
    return {k: v for k, v in kwargs.items() if v != drawUI_Default_Kwargs.get(k, None)}   

def GetFrameRenderTask_Phi(
    now_t:float,
    judgeLine_Configs:Chart_Objects_Phi.judgeLine_Configs
):
    
    # Important!!! note 和 note_item 不是同一个东西!!!!!
    
    global PlayChart_NowTime
    
    now_t *= speed
    PlayChart_NowTime = now_t
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    Chart_Functions_Phi.Update_JudgeLine_Configs(judgeLine_Configs, now_t, w, h)
    Task(root.clear_canvas, wait_execute = True)
    Task(draw_background)
    if noplaychart: Task.ExTask.append(("break", ))
    
    if render_range_more:
        fr_x = w / 2 - w / render_range_more_scale / 2
        fr_y = h / 2 - h / render_range_more_scale / 2
    
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.translate({fr_x},{fr_y});",
            add_code_array = True
        )
    
    for judgeLine_cfg in judgeLine_Configs.Configs:
        judgeLine:Chart_Objects_Phi.judgeLine = judgeLine_cfg.line
        this_judgeLine_T = judgeLine.T
        judgeLine_note_dy = Chart_Objects_Phi.getFloorPosition(judgeLine, judgeLine_cfg.time) * PHIGROS_Y
        judgeLine_DrawPos = (
            *Tool_Functions.rotate_point(*judgeLine_cfg.pos, -judgeLine_cfg.rotate, 5.76 * h / 2),
            *Tool_Functions.rotate_point(*judgeLine_cfg.pos, -judgeLine_cfg.rotate + 180, 5.76 * h / 2)
        )
        judgeLine_color = (*((254, 255, 169) if not noautoplay else PhigrosPlayManagerObject.getJudgelineColor()), judgeLine_cfg.disappear if not judgeline_notransparent else 1.0)
        judgeLine_webCanvas_color = f"rgba{judgeLine_color}"
        if judgeLine_color[-1] > 0.0:
            if render_range_more:
                Task(
                    root.run_js_code,
                    f"ctx.scale({1.0 / render_range_more_scale},{1.0 / render_range_more_scale});",
                    add_code_array = True
                )
            
            Task(
                root.run_js_code,
                f"ctx.drawLineEx(\
                    {", ".join(map(str, judgeLine_DrawPos))},\
                    {JUDGELINE_WIDTH},\
                    '{judgeLine_webCanvas_color}'\
                );",
                add_code_array = True
            )
            
            if debug:
                Task(
                    root.create_text,
                    *Tool_Functions.rotate_point(*judgeLine_cfg.pos, 90 - judgeLine_cfg.rotate - 180, (w + h) / 75),
                    text = f"{judgeLine.id}",
                    font = f"{(w + h) / 85 / 0.75}px PhigrosFont",
                    textAlign = "center",
                    textBaseline = "middle",
                    strokeStyle = "rgba(254, 255, 169, 0.5)",
                    fillStyle = "rgba(254, 255, 169, 0.5)",
                    wait_execute = True
                )
                
                Task(
                    root.create_rectangle,
                    judgeLine_cfg.pos[0] - (w + h) / 250,
                    judgeLine_cfg.pos[1] - (w + h) / 250,
                    judgeLine_cfg.pos[0] + (w + h) / 250,
                    judgeLine_cfg.pos[1] + (w + h) / 250,
                    fillStyle = "rgb(238, 130, 238)",
                    wait_execute = True
                )
                    
            if render_range_more:
                Task(
                    root.run_js_code,
                    f"ctx.scale({render_range_more_scale},{render_range_more_scale});",
                    add_code_array = True
                )
        
        def process(notes_list:typing.List[Chart_Objects_Phi.note], t:typing.Literal[1, -1]): # above => t = 1, below => t = -1
            for note_item in notes_list:
                this_note_sectime = note_item.time * this_judgeLine_T
                this_noteitem_clicked = this_note_sectime < now_t
                this_note_ishold = note_item.type == Const.Note.HOLD
                
                if this_noteitem_clicked and not note_item.clicked:
                    note_item.clicked = True
                    if enable_clicksound and not noautoplay:
                        Task.ExTask.append((
                            "thread-call",
                            "PlaySound.Play",
                            f'(Resource["Note_Click_Audio"]["{note_item.type_string}"],)' #use eval to get data tip:this string -> eval(string):tpule (arg to run thread-call)
                        ))
                    
                if not this_note_ishold and note_item.clicked:
                    continue
                elif this_note_ishold and now_t > note_item.hold_endtime:
                    continue
                elif noautoplay and note_item.state == Const.NOTE_STATE.BAD:
                    continue
                elif noautoplay and not this_note_ishold and note_item.player_clicked:
                    continue
                elif not note_item.clicked and (note_item.floorPosition - judgeLine_note_dy / PHIGROS_Y) < -0.001 and note_item.type != Const.Note.HOLD:
                    continue
                
                note_now_floorPosition = note_item.floorPosition * PHIGROS_Y - (
                        judgeLine_note_dy
                        if not (this_note_ishold and note_item.clicked) else (
                        Chart_Objects_Phi.getFloorPosition(
                            judgeLine,note_item.time
                        ) * PHIGROS_Y + Tool_Functions.linear_interpolation(note_item.hold_endtime - now_t, 0, note_item.hold_length_sec, note_item.hold_length_px, 0)
                    )
                )
                
                if note_now_floorPosition > h * 2 and not render_range_more:
                    continue
                
                rotatenote_at_judgeLine_pos = Tool_Functions.rotate_point(
                    *judgeLine_cfg.pos,-judgeLine_cfg.rotate,note_item.positionX * PHIGROS_X
                )
                judgeLine_to_note_rotate_deg = (-90 if t == 1 else 90) - judgeLine_cfg.rotate
                x, y = Tool_Functions.rotate_point(
                    *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_now_floorPosition
                )
                
                if this_note_ishold:
                    note_hold_draw_length = note_now_floorPosition + note_item.hold_length_px
                    holdend_x, holdend_y = Tool_Functions.rotate_point(
                        *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_hold_draw_length
                    )
                    if note_item.clicked:
                        holdhead_pos = rotatenote_at_judgeLine_pos
                    else:
                        holdhead_pos = x, y
                    holdbody_range = (
                        Tool_Functions.rotate_point(*holdhead_pos,judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        Tool_Functions.rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        Tool_Functions.rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                        Tool_Functions.rotate_point(*holdhead_pos,judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                    )
                    
                if not render_range_more:
                    note_iscan_render = (
                        Tool_Functions.Note_CanRender(w, h, note_max_size_half, x, y)
                        if not this_note_ishold
                        else Tool_Functions.Note_CanRender(w, h, note_max_size_half, x, y, holdbody_range)
                    )
                else:
                    note_iscan_render = (
                        Tool_Functions.Note_CanRender(
                            w, h, note_max_size_half,
                            x / render_range_more_scale + fr_x,
                            y / render_range_more_scale + fr_y
                        )
                        if not this_note_ishold
                        else Tool_Functions.Note_CanRender(
                            w, h, note_max_size_half,
                            x / render_range_more_scale + fr_x,
                            y / render_range_more_scale + fr_y,[
                            (holdbody_range[0][0] / render_range_more_scale + fr_x,holdbody_range[0][1] / render_range_more_scale + fr_y),
                            (holdbody_range[1][0] / render_range_more_scale + fr_x,holdbody_range[1][1] / render_range_more_scale + fr_y),
                            (holdbody_range[2][0] / render_range_more_scale + fr_x,holdbody_range[2][1] / render_range_more_scale + fr_y),
                            (holdbody_range[3][0] / render_range_more_scale + fr_x,holdbody_range[3][1] / render_range_more_scale + fr_y)
                        ])
                    )
                
                if note_iscan_render:
                    noteRotate = judgeLine_to_note_rotate_deg + 90
                    dub_text = "_dub" if note_item.morebets else ""
                    if not this_note_ishold:
                        this_note_img_keyname = f"{note_item.type_string}{dub_text}"
                        this_note_img = Resource["Notes"][this_note_img_keyname]
                        this_note_imgname = f"Note_{this_note_img_keyname}"
                    else:
                        this_note_img_keyname = f"{note_item.type_string}_Head{dub_text}"
                        this_note_img = Resource["Notes"][this_note_img_keyname]
                        this_note_imgname = f"Note_{this_note_img_keyname}"
                        
                        this_note_img_body_keyname = f"{note_item.type_string}_Body{dub_text}"
                        this_note_imgname_body = f"Note_{this_note_img_body_keyname}"
                        
                        this_note_img_end_keyname = f"{note_item.type_string}_End{dub_text}"
                        this_note_img_end = Resource["Notes"][this_note_img_end_keyname]
                        this_note_imgname_end = f"Note_{this_note_img_end_keyname}"
                    
                    fix_scale = Const.NOTE_DUB_FIXSCALE if note_item.morebets else 1.0 # because the note img if has morebets frame, the note will be look small, so we will `*` a fix scale to fix the frame size make the note look is small.
                    this_note_width = Note_width * fix_scale
                    this_note_height = Note_width / this_note_img.width * this_note_img.height
                        
                    if this_note_ishold:
                        this_noteend_height = Note_width / this_note_img_end.width * this_note_img_end.height
                        
                        if note_item.clicked:
                            holdbody_x,holdbody_y = rotatenote_at_judgeLine_pos
                            holdbody_length = note_hold_draw_length - this_noteend_height / 2
                        else:
                            holdbody_x,holdbody_y = Tool_Functions.rotate_point(
                                *holdhead_pos, judgeLine_to_note_rotate_deg, this_note_height / 2
                            )
                            holdbody_length = note_item.hold_length_px - (this_note_height + this_noteend_height) / 2
                        
                        miss_alpha_change = 0.5 if noautoplay and note_item.player_missed else 1.0
                        
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(this_note_imgname_end)},\
                                {holdend_x},\
                                {holdend_y},\
                                {this_note_width},\
                                {this_noteend_height},\
                                {noteRotate},\
                                {miss_alpha_change}\
                            );",
                            add_code_array = True
                        )
                        
                        if holdbody_length > 0.0:
                            Task(
                                root.run_js_code,
                                f"ctx.drawAnchorESRotateImage(\
                                    {root.get_img_jsvarname(this_note_imgname_body)},\
                                    {holdbody_x},\
                                    {holdbody_y},\
                                    {this_note_width},\
                                    {holdbody_length},\
                                    {noteRotate},\
                                    {miss_alpha_change}\
                                );",
                                add_code_array = True
                            )
                        
                    if not (this_note_ishold and this_note_sectime < now_t):
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(this_note_imgname)},\
                                {x},\
                                {y},\
                                {this_note_width},\
                                {this_note_height},\
                                {noteRotate},\
                                1.0\
                            );",
                            add_code_array = True
                        )
        process(judgeLine.notesAbove,1)
        process(judgeLine.notesBelow,-1)

    
    effect_time = 0.5
    miss_effect_time = 0.2
    bad_effect_time = 0.5
        
    def process_effect(
        note:Chart_Objects_Phi.note,
        t:float,
        effect_random_blocks,
        perfect:bool
    ):
        p = (now_t - t * note.master.T) / effect_time
        if not (0.0 <= p <= 1.0): return None
        will_show_effect_pos = judgeLine.get_datavar_move(t, w, h)
        will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
        pos = Tool_Functions.rotate_point(
            *will_show_effect_pos,
            -will_show_effect_rotate,
            note.positionX * PHIGROS_X
        )
        process_effect_base(*pos, p, effect_random_blocks, perfect, Task)
    
    def process_miss(
        note:Chart_Objects_Phi.note
    ):
        t = now_t / note.master.T
        p = (now_t - note.time * note.master.T) / miss_effect_time
        will_show_effect_pos = judgeLine.get_datavar_move(t, w, h)
        will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
        pos = Tool_Functions.rotate_point(
            *will_show_effect_pos,
            -will_show_effect_rotate,
            note.positionX * PHIGROS_X
        )
        floorp = note.floorPosition - Chart_Objects_Phi.getFloorPosition(note.master, t)
        x,y = Tool_Functions.rotate_point(
            *pos,
            (-90 if note.above else 90) - will_show_effect_rotate,
            floorp * PHIGROS_Y
        )
        img_keyname = f"{note.type_string}{"_dub" if note.morebets else ""}"
        this_note_img = Resource["Notes"][img_keyname]
        this_note_imgname = f"Note_{img_keyname}"
        Task(
            root.run_js_code,
            f"crc2d_enable_rrm = false; ctx.drawRotateImage(\
                {root.get_img_jsvarname(this_note_imgname)},\
                {x},\
                {y},\
                {Note_width},\
                {Note_width / this_note_img.width * this_note_img.height},\
                {- will_show_effect_rotate},\
                {1 - p ** 0.5}\
            ); crc2d_enable_rrm = true;",
            add_code_array = True
        )
    
    def process_bad(
        note:Chart_Objects_Phi.note
    ):
        t = note.player_badtime / note.master.T
        p = (now_t - note.player_badtime) / bad_effect_time
        will_show_effect_pos = judgeLine.get_datavar_move(t, w, h)
        will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
        pos = Tool_Functions.rotate_point(
            *will_show_effect_pos,
            -will_show_effect_rotate,
            note.positionX * PHIGROS_X
        )
        floorp = note.floorPosition - Chart_Objects_Phi.getFloorPosition(note.master, t)
        x,y = Tool_Functions.rotate_point(
            *pos,
            (-90 if note.above else 90) - will_show_effect_rotate,
            floorp * PHIGROS_Y
        )
        this_note_img = Resource["Notes"]["Bad"]
        Task(
            root.run_js_code,
            f"crc2d_enable_rrm = false; ctx.drawRotateImage(\
                {root.get_img_jsvarname("Note_Bad")},\
                {x},\
                {y},\
                {Note_width * (Const.NOTE_DUB_FIXSCALE if note.morebets else 1.0)},\
                {Note_width / this_note_img.width * this_note_img.height},\
                {- will_show_effect_rotate},\
                {1 - p ** 3}\
            ); crc2d_enable_rrm = true;",
            add_code_array = True
        )
        
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.scale({1.0 / render_range_more_scale},{1.0 / render_range_more_scale});",
            add_code_array = True
        )
        
    for judgeLine in chart_obj.judgeLineList:
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            note_time = note.time * judgeLine.T
            note_ishold = note.type == Const.Note.HOLD
            if not note_ishold and note.show_effected:
                continue
            
            if not noautoplay:
                if note.clicked:
                    if now_t - note_time <= effect_time:
                        process_effect(
                            note,
                            note.time,
                            note.effect_random_blocks,
                            True
                        )
                    else:
                        note.show_effected = True
                    
                    if note_ishold:
                        efct_et = note.hold_endtime + effect_time
                        if efct_et >= now_t:
                            for temp_time, hold_effect_random_blocks in note.effect_times:
                                if temp_time < now_t:
                                    if now_t - temp_time <= effect_time:
                                        process_effect(
                                            note,
                                            temp_time / judgeLine.T,
                                            hold_effect_random_blocks,
                                            True
                                        )
            else: # noautoplay
                if note.player_holdjudged or (note.state == Const.NOTE_STATE.PERFECT or note.state == Const.NOTE_STATE.GOOD and note.player_clicked):
                    if note_time - note.player_click_offset <= now_t:
                        if now_t - (note_time - note.player_click_offset) <= effect_time:
                            process_effect(
                                note,
                                note.time - note.player_click_offset / note.master.T,
                                note.effect_random_blocks,
                                note.state == Const.NOTE_STATE.PERFECT if note.type != Const.Note.HOLD else note.player_holdclickstate == Const.NOTE_STATE.PERFECT
                            )
                        else:
                            note.show_effected = True
                elif note.state == Const.NOTE_STATE.MISS:
                    if 0.0 <= now_t - note_time <= miss_effect_time and note.type != Const.Note.HOLD:
                        process_miss(note)
                elif note.state == Const.NOTE_STATE.BAD:
                    if 0.0 <= now_t - note.player_badtime <= bad_effect_time:
                        process_bad(note)
                        
                if note_ishold and note.player_holdjudged and note.player_holdclickstate != Const.NOTE_STATE.MISS:
                    efct_et = note.player_holdmiss_time + effect_time
                    if efct_et >= now_t:
                        for temp_time, hold_effect_random_blocks in note.effect_times:
                            if temp_time < now_t:
                                if now_t - temp_time <= effect_time:
                                    if temp_time + effect_time <= efct_et:
                                        process_effect(
                                            note,
                                            temp_time / judgeLine.T,
                                            hold_effect_random_blocks,
                                            note.player_holdclickstate == Const.NOTE_STATE.PERFECT
                                        )
                    
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.scale({render_range_more_scale},{render_range_more_scale});",
            add_code_array = True
        )
    
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.translate(-{fr_x},-{fr_y});",
            add_code_array = True
        )
    
    if render_range_more:
        line_poses = [
            # (fr_x,fr_y),
            (fr_x + w / render_range_more_scale,fr_y),
            (fr_x + w / render_range_more_scale,fr_y + h / render_range_more_scale),
            (fr_x,fr_y + h / render_range_more_scale),
            (fr_x,fr_y)
        ]
        Task(
            root.run_js_code,
            f"ctx.lineWidth = {JUDGELINE_WIDTH / render_range_more_scale}; ctx.strokeStyle = \"{Const.RENDER_RANGE_MORE_FRAME_LINE_COLOR}\"; ctx.beginPath(); ctx.moveTo({fr_x},{fr_y});",
            add_code_array = True
        )
        for line_pos in line_poses:
            Task(
                root.run_js_code,
                f"ctx.lineTo({line_pos[0]},{line_pos[1]});",
                add_code_array = True
            )
        Task(
            root.run_js_code,
            "ctx.closePath(); ctx.stroke();",
            add_code_array = True
        )
    
    combo = Chart_Functions_Phi.Cal_Combo(now_t, chart_obj) if not noautoplay else PhigrosPlayManagerObject.getCombo()
    now_t /= speed
    time_text = f"{Tool_Functions.Format_Time(now_t)}/{Tool_Functions.Format_Time(audio_length)}"
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = get_stringscore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else get_stringscore(PhigrosPlayManagerObject.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        now_time = time_text,
        acc = "100.00%" if not noautoplay else f"{(PhigrosPlayManagerObject.getAcc() * 100):.2f}%",
        clear = False,
        background = False
    )
    
    CheckMusicOffsetAndEnd(now_t, Task)
    Task(root.run_js_wait_code)
    return Task

def GetFrameRenderTask_Rpe(
    now_t:float
):
    global PlayChart_NowTime
    
    now_t *= speed
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    Task(root.clear_canvas, wait_execute = True)
    Task(draw_background)
    PlayChart_NowTime = now_t
    if noplaychart: Task.ExTask.append(("break", ))
    
    now_t -= chart_obj.META.offset / 1000
    beatTime = chart_obj.sec2beat(now_t)
    attachUIData = {}
    
    for line_index, line in sorted(enumerate(chart_obj.JudgeLineList), key = lambda x: x[1].zOrder):
        linePos, lineAlpha, lineRotate, lineColor, lineScaleX, lineScaleY, lineText = line.GetState(chart_obj.sec2beat(now_t), (254, 255, 169) if not noautoplay else PhigrosPlayManagerObject.getJudgelineColor(), chart_obj)
        if judgeline_notransparent: lineAlpha = 1.0
        linePos = (linePos[0] * w, linePos[1] * h)
        judgeLine_DrawPos = (
            *Tool_Functions.rotate_point(*linePos, lineRotate, w * 4000 / 1350 * lineScaleX / 2),
            *Tool_Functions.rotate_point(*linePos, lineRotate + 180, w * 4000 / 1350 * lineScaleX / 2)
        )
        negative_alpha = lineAlpha < 0.0
        judgeLine_webCanvas_color = f"rgba{lineColor + (lineAlpha, )}"
        if line.Texture != "line.png" and lineAlpha > 0.0:
            _, texture_size = chart_res[line.Texture]
            texture_width = texture_size[0] / 1104 * w * 0.75 * lineScaleX
            texture_height = texture_size[1] / 621 * h * 0.75 * lineScaleY
            if Tool_Functions.TextureLine_CanRender(w, h, (texture_width ** 2 + texture_height ** 2) ** 0.5 / 2, *linePos):
                Task(
                    root.run_js_code,
                    f"{f"setTextureLineColorFilterColorMatrixValueByRgbValue{tuple(map(lambda x: x / 255, lineColor))}; ctx.filter = 'url(#textureLineColorFilter)'; " if lineColor != (255, 255, 255) else ""}ctx.drawRotateImage(\
                        {root.get_img_jsvarname(f"lineTexture_{line_index}")},\
                        {linePos[0]},\
                        {linePos[1]},\
                        {texture_width},\
                        {texture_height},\
                        {lineRotate},\
                        {lineAlpha}\
                    ); {"ctx.filter = 'none';" if lineColor != (255, 255, 255) else ""}",
                    add_code_array = True
                )
        elif lineText is not None and lineAlpha > 0.0:
            Task(
                root.run_js_code,
                f"ctx.drawRotateText(\
                    '{root.process_code_string_syntax_tostring(lineText)}',\
                    {linePos[0]},\
                    {linePos[1]},\
                    {lineRotate},\
                    {(w + h) / 75 * 1.35},\
                    '{judgeLine_webCanvas_color}',\
                    {lineScaleX},\
                    {lineScaleY}\
                );",
                add_code_array = True
            )
        elif line.attachUI is not None:
            if line.attachUI in ("combonumber", "combo", "score", "name", "level", "pause"):
                attachUIData.update({
                    f"{line.attachUI}UI_dx": linePos[0] - w / 2,
                    f"{line.attachUI}UI_dy": linePos[1] - h / 2,
                    f"{line.attachUI}UI_scaleX": lineScaleX,
                    f"{line.attachUI}UI_scaleY": lineScaleY,
                    f"{line.attachUI}UI_color": judgeLine_webCanvas_color,
                    f"{line.attachUI}UI_rotate": lineRotate
                })
        elif lineAlpha > 0.0:
            Task(
                root.run_js_code,
                f"ctx.drawLineEx(\
                    {", ".join(map(str, judgeLine_DrawPos))},\
                    {JUDGELINE_WIDTH * lineScaleY},\
                    '{judgeLine_webCanvas_color}'\
                );",
                add_code_array = True
            )
            
        if debug and line.attachUI is None and Tool_Functions.point_in_screen(linePos, w, h) and lineAlpha > 0.0:
            Task(
                root.create_text,
                *Tool_Functions.rotate_point(*linePos, 90 + lineRotate - 180, (w + h) / 75),
                text = f"{line_index}",
                font = f"{(w + h) / 85 / 0.75}px PhigrosFont",
                textAlign = "center",
                textBaseline = "middle",
                strokeStyle = "rgba(254, 255, 169, 0.5)",
                fillStyle = "rgba(254, 255, 169, 0.5)",
                wait_execute = True
            )
            
            Task(
                root.create_rectangle,
                linePos[0] - (w + h) / 250,
                linePos[1] - (w + h) / 250,
                linePos[0] + (w + h) / 250,
                linePos[1] + (w + h) / 250,
                fillStyle = "rgb(238, 130, 238)",
                wait_execute = True
            )
        
        line.playingFloorPosition = line.GetFloorPosition(0.0, now_t, chart_obj)
        for note in line.notes:
            note_clicked = note.startTime.value < beatTime
            
            if note_clicked and not note.clicked:
                note.clicked = True
                if enable_clicksound and not note.isFake and not noautoplay:
                    Task.ExTask.append((
                        "thread-call",
                        "PlaySound.Play",
                        f'(Resource["Note_Click_Audio"]["{note.type_string}"],)' #use eval to get data tip:this string -> eval(string):tpule (arg to run thread-call)
                    ))
            
            if not note.ishold and note.clicked:
                continue
            elif note.ishold and beatTime > note.endTime.value:
                continue
            elif noautoplay and note.state == Const.NOTE_STATE.BAD:
                continue
            elif noautoplay and not note.ishold and note.player_clicked:
                continue
            
            noteFloorPosition = (note.floorPosition - line.playingFloorPosition) * h
            if noteFloorPosition < 0 and not note.clicked:
                continue
            
            noteAtJudgeLinePos = Tool_Functions.rotate_point(
                *linePos, lineRotate, note.positionX2 * w
            )
            lineToNoteRotate = (-90 if note.above == 1 else 90) + lineRotate
            x, y = Tool_Functions.rotate_point(
                *noteAtJudgeLinePos, lineToNoteRotate, noteFloorPosition
            )
            
            if note.ishold:
                holdLength = note.holdLength * h
                noteHoldDrawLength = noteFloorPosition + holdLength
                holdend_x, holdend_y = Tool_Functions.rotate_point(
                    *noteAtJudgeLinePos, lineToNoteRotate, noteHoldDrawLength
                )
                if note.clicked:
                    holdhead_pos = noteAtJudgeLinePos
                else:
                    holdhead_pos = x, y
                holdbody_range = (
                    Tool_Functions.rotate_point(*holdhead_pos, lineToNoteRotate - 90, Note_width / 2),
                    Tool_Functions.rotate_point(holdend_x, holdend_y, lineToNoteRotate - 90, Note_width / 2),
                    Tool_Functions.rotate_point(holdend_x, holdend_y, lineToNoteRotate + 90, Note_width / 2),
                    Tool_Functions.rotate_point(*holdhead_pos, lineToNoteRotate + 90, Note_width / 2),
                )
            
            canRender = (
                Tool_Functions.Note_CanRender(w, h, note_max_size_half, x, y)
                if not note.ishold
                else Tool_Functions.Note_CanRender(w, h, note_max_size_half, x, y, holdbody_range)
            ) and not negative_alpha
            
            if canRender and abs(now_t - note.secst) <= note.visibleTime:
                noteRotate = lineRotate + (0 if note.above == 1 else 180)
                dub_text = "_dub" if note.morebets else ""
                if not note.ishold:
                    this_note_img_keyname = f"{note.type_string}{dub_text}"
                    this_note_img = Resource["Notes"][this_note_img_keyname]
                    this_note_imgname = f"Note_{this_note_img_keyname}"
                else:
                    this_note_img_keyname = f"{note.type_string}_Head{dub_text}"
                    this_note_img = Resource["Notes"][this_note_img_keyname]
                    this_note_imgname = f"Note_{this_note_img_keyname}"
                    
                    this_note_img_body_keyname = f"{note.type_string}_Body{dub_text}"
                    this_note_imgname_body = f"Note_{this_note_img_body_keyname}"
                    
                    this_note_img_end_keyname = f"{note.type_string}_End{dub_text}"
                    this_note_img_end = Resource["Notes"][this_note_img_end_keyname]
                    this_note_imgname_end = f"Note_{this_note_img_end_keyname}"
                    
                fix_scale = Const.NOTE_DUB_FIXSCALE if note.morebets else 1.0
                this_note_width = Note_width * fix_scale
                this_note_height = Note_width / this_note_img.width * this_note_img.height
                
                if note.ishold:
                    this_noteend_height = Note_width / this_note_img_end.width * this_note_img_end.height
                    
                    if note.clicked:
                        holdbody_x, holdbody_y = noteAtJudgeLinePos
                        holdbody_length = noteHoldDrawLength - this_noteend_height / 2
                    else:
                        holdbody_x, holdbody_y = Tool_Functions.rotate_point(
                            *holdhead_pos, lineToNoteRotate, this_note_height / 2
                        )
                        holdbody_length = holdLength - (this_note_height + this_noteend_height) / 2
                    
                    if holdbody_length < 0.0:
                        holdbody_length = 0.0
                        
                    miss_alpha_change = 0.5 if noautoplay and note.player_missed else 1.0
                    
                    Task(
                        root.run_js_code,
                        f"ctx.drawRotateImage(\
                            {root.get_img_jsvarname(this_note_imgname_end)},\
                            {holdend_x},\
                            {holdend_y},\
                            {this_note_width * note.width},\
                            {this_noteend_height},\
                            {noteRotate},\
                            {note.float_alpha * miss_alpha_change}\
                        );",
                        add_code_array = True
                    )
                    
                    if holdbody_length > 0.0:
                        Task(
                            root.run_js_code,
                            f"ctx.drawAnchorESRotateImage(\
                                {root.get_img_jsvarname(this_note_imgname_body)},\
                                {holdbody_x},\
                                {holdbody_y},\
                                {this_note_width * note.width},\
                                {holdbody_length},\
                                {noteRotate},\
                                {note.float_alpha * miss_alpha_change}\
                            );",
                            add_code_array = True
                        )
                
                if not (note.ishold and note.startTime.value < beatTime):
                    Task(
                        root.run_js_code,
                        f"ctx.drawRotateImage(\
                            {root.get_img_jsvarname(this_note_imgname)},\
                            {x},\
                            {y},\
                            {this_note_width * note.width},\
                            {this_note_height},\
                            {noteRotate},\
                            {note.float_alpha}\
                        );",
                        add_code_array = True
                    )
                    
    effect_time = 0.5
    miss_effect_time = 0.2
    bad_effect_time = 0.5
        
    def process_effect(
        note: Chart_Objects_Rpe.Note,
        t: float,
        effect_random_blocks,
        perfect: bool
    ):
        p = (now_t - chart_obj.beat2sec(t)) / effect_time
        if not (0.0 <= p <= 1.0): return None
        linePos = Tool_Functions.conrpepos(*line.GetPos(t, chart_obj)); linePos = (linePos[0] * w, linePos[1] * h)
        lineRotate = sum([line.GetEventValue(t, layer.rotateEvents, 0.0) for layer in line.eventLayers])
        pos = Tool_Functions.rotate_point(
            *linePos,
            lineRotate,
            note.positionX2 * w
        )
        process_effect_base(*pos, p, effect_random_blocks, perfect, Task)
    
    def process_miss(
        note:Chart_Objects_Rpe.Note
    ):
        t = chart_obj.sec2beat(now_t)
        p = (now_t - note.secst) / miss_effect_time
        linePos = Tool_Functions.conrpepos(*line.GetPos(t, chart_obj)); linePos = (linePos[0] * w, linePos[1] * h)
        lineRotate = sum([line.GetEventValue(t, layer.rotateEvents, 0.0) for layer in line.eventLayers])
        pos = Tool_Functions.rotate_point(
            *linePos,
            lineRotate,
            note.positionX2 * w
        )
        floorp = note.floorPosition - line.playingFloorPosition
        x, y = Tool_Functions.rotate_point(
            *pos,
            (-90 if note.above == 1 else 90) + lineRotate,
            floorp * h
        )
        img_keyname = f"{note.type_string}{"_dub" if note.morebets else ""}"
        this_note_img = Resource["Notes"][img_keyname]
        this_note_imgname = f"Note_{img_keyname}"
        Task(
            root.run_js_code,
            f"ctx.drawRotateImage(\
                {root.get_img_jsvarname(this_note_imgname)},\
                {x},\
                {y},\
                {Note_width * note.width},\
                {Note_width / this_note_img.width * this_note_img.height},\
                {lineRotate},\
                {note.float_alpha * (1 - p ** 0.5)}\
            );",
            add_code_array = True
        )
    
    def process_bad(
        note:Chart_Objects_Rpe.Note
    ):
        t = note.player_badtime_beat
        p = (now_t - note.player_badtime) / bad_effect_time
        linePos = Tool_Functions.conrpepos(*line.GetPos(t, chart_obj)); linePos = (linePos[0] * w, linePos[1] * h)
        lineRotate = sum([line.GetEventValue(t, layer.rotateEvents, 0.0) for layer in line.eventLayers])
        pos = Tool_Functions.rotate_point(
            *linePos,
            lineRotate,
            note.positionX2 * w
        )
        x, y = Tool_Functions.rotate_point(
            *pos,
            (-90 if note.above == 1 else 90) + lineRotate,
            note.player_badjudge_floorp * h
        )
        this_note_img = Resource["Notes"]["Bad"]
        Task(
            root.run_js_code,
            f"ctx.drawRotateImage(\
                {root.get_img_jsvarname("Note_Bad")},\
                {x},\
                {y},\
                {Note_width * note.width * (Const.NOTE_DUB_FIXSCALE if note.morebets else 1.0)},\
                {Note_width / this_note_img.width * this_note_img.height},\
                {lineRotate},\
                {note.float_alpha * (1 - p ** 3)}\
            );",
            add_code_array = True
        )
    
    for line in chart_obj.JudgeLineList:
        for note in line.notes:
            if not note.ishold and note.show_effected:
                continue
            elif note.isFake:
                continue
            
            if not noautoplay:
                if note.clicked:
                    if now_t - note.secst <= effect_time:
                        process_effect(
                            note,
                            note.startTime.value,
                            note.effect_random_blocks,
                            True
                        )
                    else:
                        note.show_effected = True
                    
                    if note.ishold:
                        efct_et = chart_obj.beat2sec(note.endTime.value) + effect_time
                        if efct_et >= now_t:
                            for temp_time, hold_effect_random_blocks in note.effect_times:
                                if temp_time < now_t:
                                    if now_t - temp_time <= effect_time:
                                        process_effect(
                                            note,
                                            chart_obj.sec2beat(temp_time),
                                            hold_effect_random_blocks,
                                            True
                                        )
            else: # noautoplay
                if note.player_holdjudged or (note.state == Const.NOTE_STATE.PERFECT or note.state == Const.NOTE_STATE.GOOD and note.player_clicked):
                    if note.secst - note.player_click_offset <= now_t:
                        if now_t - (note.secst - note.player_click_offset) <= effect_time:
                            process_effect(
                                note,
                                chart_obj.sec2beat(note.secst - note.player_click_offset),
                                note.effect_random_blocks,
                                note.state == Const.NOTE_STATE.PERFECT if not note.ishold else note.player_holdclickstate == Const.NOTE_STATE.PERFECT
                            )
                        else:
                            note.show_effected = True
                elif note.state == Const.NOTE_STATE.MISS:
                    if 0.0 <= now_t - note.secst <= miss_effect_time and not note.ishold:
                        process_miss(note)
                elif note.state == Const.NOTE_STATE.BAD:
                    if 0.0 <= now_t - note.player_badtime <= bad_effect_time:
                        process_bad(note)
                        
                if note.ishold and note.player_holdjudged and note.player_holdclickstate != Const.NOTE_STATE.MISS:
                    efct_et = note.player_holdmiss_time + effect_time
                    if efct_et >= now_t:
                        for temp_time, hold_effect_random_blocks in note.effect_times:
                            if temp_time < now_t:
                                if now_t - temp_time <= effect_time:
                                    if temp_time + effect_time <= efct_et:
                                        process_effect(
                                            note,
                                            chart_obj.sec2beat(temp_time),
                                            hold_effect_random_blocks,
                                            note.player_holdclickstate == Const.NOTE_STATE.PERFECT
                                        )
    
    combo = len([i for line in chart_obj.JudgeLineList for i in line.notes if not i.isFake and ((not i.ishold and i.clicked) or (i.ishold and i.secet - 0.2 < now_t))]) if not noautoplay else PhigrosPlayManagerObject.getCombo()
    now_t /= speed
    time_text = f"{Tool_Functions.Format_Time(now_t)}/{Tool_Functions.Format_Time(audio_length)}"
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = get_stringscore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else get_stringscore(PhigrosPlayManagerObject.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        now_time = time_text,
        acc = "100.00%" if not noautoplay else f"{(PhigrosPlayManagerObject.getAcc() * 100):.2f}%",
        clear = False,
        background = False,
        **deleteDrwaUIKwargsDefaultValues(attachUIData)
    )
    now_t += chart_obj.META.offset / 1000
    CheckMusicOffsetAndEnd(now_t, Task)
    Task(root.run_js_wait_code)
    return Task