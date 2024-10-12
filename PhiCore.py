import time
import typing
import math
import logging
from dataclasses import dataclass
from threading import Thread

from pygame import mixer
from PIL import Image

import webcv
import Const
import PlaySound
import Tool_Functions
import rpe_easing
import Chart_Objects_Phi
import Chart_Objects_Rpe
import Chart_Functions_Phi
import Phigros_Tips

@dataclass
class PhiCoreConfigure:
    SETTER: typing.Callable[[str, typing.Any], typing.Any]
    
    root: webcv.WebCanvas
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
    LoadSuccess: mixer.Sound
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

@dataclass
class PhiCoreConfigureEx:
    infoframe_x: float
    infoframe_y: float
    infoframe_width: float
    infoframe_height: float
    infoframe_ltr: float
    chart_name_text: str
    chart_name_font_text_size: float
    chart_artist_text: str
    chart_artist_text_font_size: float
    chart_level_number: str
    chart_level_number_font_size: float
    chart_level_text: str
    chart_level_text_font_size: float
    tip: str
    tip_font_size: float
    chart_charter_text: str
    chart_charter_text_font_size: float
    chart_illustrator_text: str
    chart_illustrator_text_font_size: float

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
    global Kill_PlayThread_Flag, LoadSuccess
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
    LoadSuccess = config.LoadSuccess
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

def CoreConfigEx(config: PhiCoreConfigureEx):
    global infoframe_x, infoframe_y
    global infoframe_width, infoframe_height, infoframe_ltr
    global chart_name_text, chart_name_font_text_size
    global chart_artist_text, chart_artist_text_font_size
    global chart_level_number, chart_level_number_font_size
    global chart_level_text, chart_level_text_font_size
    global tip, tip_font_size
    global chart_charter_text, chart_charter_text_font_size
    global chart_illustrator_text, chart_illustrator_text_font_size
    
    infoframe_x = config.infoframe_x
    infoframe_y = config.infoframe_y
    infoframe_width = config.infoframe_width
    infoframe_height = config.infoframe_height
    infoframe_ltr = config.infoframe_ltr
    chart_name_text = config.chart_name_text
    chart_name_font_text_size = config.chart_name_font_text_size
    chart_artist_text = config.chart_artist_text
    chart_artist_text_font_size = config.chart_artist_text_font_size
    chart_level_number = config.chart_level_number
    chart_level_number_font_size = config.chart_level_number_font_size
    chart_level_text = config.chart_level_text
    chart_level_text_font_size = config.chart_level_text_font_size
    tip = config.tip
    tip_font_size = config.tip_font_size
    chart_charter_text = config.chart_charter_text
    chart_charter_text_font_size = config.chart_charter_text_font_size
    chart_illustrator_text = config.chart_illustrator_text
    chart_illustrator_text_font_size = config.chart_illustrator_text_font_size

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
                        return
                    
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
                        return
                    
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

# color一定要传rgba的
def draw_ui(
    process:float = 0.0,
    score:str = "0000000",
    combo_state:bool = False,
    combo:int = 0,
    acc:str = "100.00%",
    clear:bool = True,
    background:bool = True,
    animationing:bool = False,
    dy:float = 0.0,
    
    combonumberUI_dx: float = 0.0,
    combonumberUI_dy: float = 0.0,
    combonumberUI_scaleX: float = 1.0,
    combonumberUI_scaleY: float = 1.0,
    combonumberUI_color: str = "rgba(255, 255, 255, 1.0)",
    combonumberUI_rotate: float = 0.0,
    
    comboUI_dx: float = 0.0,
    comboUI_dy: float = 0.0,
    comboUI_scaleX: float = 1.0,
    comboUI_scaleY: float = 1.0,
    comboUI_color: str = "rgba(255, 255, 255, 1.0)",
    comboUI_rotate: float = 0.0,
    
    scoreUI_dx: float = 0.0,
    scoreUI_dy: float = 0.0,
    scoreUI_scaleX: float = 1.0,
    scoreUI_scaleY: float = 1.0,
    scoreUI_color: str = "rgba(255, 255, 255, 1.0)",
    scoreUI_rotate: float = 0.0,
    
    nameUI_dx: float = 0.0,
    nameUI_dy: float = 0.0,
    nameUI_scaleX: float = 1.0,
    nameUI_scaleY: float = 1.0,
    nameUI_color: str = "rgba(255, 255, 255, 1.0)",
    nameUI_rotate: float = 0.0,
    
    levelUI_dx: float = 0.0,
    levelUI_dy: float = 0.0,
    levelUI_scaleX: float = 1.0,
    levelUI_scaleY: float = 1.0,
    levelUI_color: str = "rgba(255, 255, 255, 1.0)",
    levelUI_rotate: float = 0.0,
    
    pauseUI_dx: float = 0.0, # in fact, timeUI...
    pauseUI_dy: float = 0.0,
    pauseUI_scaleX: float = 1.0,
    pauseUI_scaleY: float = 1.0,
    pauseUI_color: str = "rgba(255, 255, 255, 1.0)",
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
            {h * (58 / 1080) + scoreUI_dy},\
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
                {h * (58 / 1080) + (w + h) / 145 / 0.75 * 1.5 + scoreUI_dy},\
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
    
    pauseImgWidth, pauseImgHeight = w * (36 / 1920) * pauseUI_scaleX, h * (41 / 1080) * pauseUI_scaleY
    pauseImgAlpha = pauseUI_color.split(")")[-2].split(",")[-1].replace(" ", "")
    root.run_js_code(
        f"ctx.drawRotateImage(\
            {root.get_img_jsvarname("PauseImg")},\
            {w * (36 / 1920) + pauseImgWidth / 2 + pauseUI_dx}, {h * (41 / 1080) + pauseImgHeight / 2 + pauseUI_dy},\
            {pauseImgWidth}, {pauseImgHeight},\
            {pauseUI_rotate}, {pauseImgAlpha}\
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
        root.run_js_code(f"ctx.translate(0, {- h / 7 + dy});", add_code_array = True)
    
    lastCallDrawUI = time.time()

def CheckMusicOffsetAndEnd(now_t: float, Task: Chart_Objects_Phi.FrameRenderTask):
    global show_start_time
    
    if now_t >= raw_audio_length:
        Task.ExTask.append(("break", ))
    
    if not lfdaot and not no_mixer_reset_chart_time and mixer.music.get_busy():
        this_music_pos = mixer.music.get_pos() % (raw_audio_length * 1000)
        offset_judge_range = (1000 / 60) * 4
        if abs(music_offset := this_music_pos - (time.time() - show_start_time) * 1000) >= offset_judge_range:
            if abs(music_offset) < raw_audio_length * 1000 * 0.75:
                show_start_time -= music_offset / 1000
                SETTER("show_start_time", show_start_time)
                logging.warning(f"mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset)}ms)")
             
def deleteDrwaUIKwargsDefaultValues(kwargs:dict) -> dict:
    return {k: v for k, v in kwargs.items() if v != drawUI_Default_Kwargs.get(k, None)}   

def GetFrameRenderTask_Phi(
    now_t:float,
    judgeLine_Configs:Chart_Objects_Phi.judgeLine_Configs,
    clear: bool = True,
    rjc: bool = True
):
    
    # Important!!! note 和 note_item 不是同一个东西!!!!!
    
    global PlayChart_NowTime
    
    now_t *= speed
    PlayChart_NowTime = now_t
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    Chart_Functions_Phi.Update_JudgeLine_Configs(judgeLine_Configs, now_t, w, h)
    if clear: Task(root.clear_canvas, wait_execute = True)
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
        if not (0.0 <= p <= 1.0): return
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
                        if note.hold_endtime + effect_time >= now_t:
                            for temp_time, hold_effect_random_blocks in note.effect_times:
                                if temp_time < now_t and now_t - temp_time <= effect_time:
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
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = get_stringscore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else get_stringscore(PhigrosPlayManagerObject.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        acc = "100.00%" if not noautoplay else f"{(PhigrosPlayManagerObject.getAcc() * 100):.2f}%",
        clear = False,
        background = False
    )
    
    CheckMusicOffsetAndEnd(now_t, Task)
    if rjc: Task(root.run_js_wait_code)
    return Task

def GetFrameRenderTask_Rpe(
    now_t:float,
    clear: bool = True,
    rjc: bool = True
):
    global PlayChart_NowTime
    
    now_t *= speed
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    if clear: Task(root.clear_canvas, wait_execute = True)
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
            ) and not negative_alpha and now_t >= 0.0
            
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
        if not (0.0 <= p <= 1.0): return
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
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = get_stringscore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else get_stringscore(PhigrosPlayManagerObject.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        acc = "100.00%" if not noautoplay else f"{(PhigrosPlayManagerObject.getAcc() * 100):.2f}%",
        clear = False,
        background = False,
        **deleteDrwaUIKwargsDefaultValues(attachUIData)
    )
    now_t += chart_obj.META.offset / 1000
    CheckMusicOffsetAndEnd(now_t, Task)
    if rjc: Task(root.run_js_wait_code)
    return Task

def Get_LevelNumber() -> str:
    lv = chart_information["Level"].lower()
    if "lv." in lv:
        return lv.split("lv.")[1]
    elif "lv" in lv:
        return lv.split("lv")[1]
    elif "level" in lv:
        return lv.split("level")[1]
    else:
        return "?"
    
def Get_LevelText() -> str:
    return chart_information["Level"].split(" ")[0]

def BeginLoadingAnimation(p: float, clear: bool = True, fcb: typing.Callable[[], typing.Any] = lambda: None) -> Chart_Objects_Phi.FrameRenderTask:
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    
    if clear: Task(root.clear_canvas, wait_execute = True)
    all_ease_value = Tool_Functions.begin_animation_eases.im_ease(p)
    background_ease_value = Tool_Functions.begin_animation_eases.background_ease(p) * 1.25
    info_data_ease_value = Tool_Functions.begin_animation_eases.info_data_ease((p - 0.2) * 3.25)
    info_data_ease_value_2 = Tool_Functions.begin_animation_eases.info_data_ease((p - 0.275) * 3.25)
    im_size = 1 / 2.5
    
    Task(draw_background)
    
    fcb()
    Task(
        root.create_polygon,
        [
            (-w * 0.1,0),
            (-w * 0.1,h),
            (background_ease_value * w - w * 0.1,h),
            (background_ease_value * w,0),
            (-w * 0.1,0)
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = f"rgba(0, 0, 0, {0.75 * (1 - p)})",
        wait_execute = True
    )
    
    Task(
        root.run_js_code,
        f"ctx.translate({all_ease_value * w},0.0);",
        add_code_array = True
    )
    
    Task(
        root.create_polygon,
        [
            (infoframe_x + infoframe_ltr,infoframe_y - infoframe_height),
            (infoframe_x + infoframe_ltr + infoframe_width,infoframe_y - infoframe_height),
            (infoframe_x + infoframe_width,infoframe_y),
            (infoframe_x,infoframe_y),
            (infoframe_x + infoframe_ltr,infoframe_y - infoframe_height)
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = "rgba(0, 0, 0, 0.75)",
        wait_execute = True
    )
    
    Task(
        root.create_polygon,
        [
            (infoframe_x + w * 0.225 + infoframe_ltr,infoframe_y - infoframe_height * 1.03),
            (infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215,infoframe_y - infoframe_height * 1.03),
            (infoframe_x + w * 0.225 + infoframe_width * 0.215,infoframe_y + infoframe_height * 0.03),
            (infoframe_x + w * 0.225,infoframe_y + infoframe_height * 0.03),
            (infoframe_x + w * 0.225 + infoframe_ltr,infoframe_y - infoframe_height * 1.03)
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = "#FFFFFF",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + infoframe_ltr * 2,
        infoframe_y - infoframe_height * 0.65,
        text = chart_name_text,
        font = f"{(chart_name_font_text_size)}px PhigrosFont",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + infoframe_ltr * 2,
        infoframe_y - infoframe_height * 0.31,
        text = chart_artist_text,
        font = f"{(chart_artist_text_font_size)}px PhigrosFont",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
        infoframe_y - infoframe_height * 1.03 * 0.58,
        text = chart_level_number,
        font = f"{(chart_level_number_font_size)}px PhigrosFont",
        textAlign = "center",
        textBaseline = "middle",
        fillStyle = "#2F2F2F",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
        infoframe_y - infoframe_height * 1.03 * 0.31,
        text = chart_level_text,
        font = f"{(chart_level_text_font_size)}px PhigrosFont",
        textAlign = "center",
        textBaseline = "middle",
        fillStyle = "#2F2F2F",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.065,
        h * 0.95,
        text = f"Tip: {tip}",
        font = f"{tip_font_size}px PhigrosFont",
        textBaseline = "bottom",
        fillStyle = f"rgba(255, 255, 255, {Tool_Functions.begin_animation_eases.tip_alpha_ease(p)})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1375 + (1 - info_data_ease_value) * -1 * w * 0.075,
        h * 0.5225,
        text = "Chart",
        font = f"{w / 98}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1375 + (1 - info_data_ease_value) * -1 * w * 0.075,
        h * 0.5225 + w / 98 * 1.25,
        text = chart_charter_text,
        font = f"{chart_charter_text_font_size}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1235 + (1 - info_data_ease_value_2) * -1 * w * 0.075,
        h * 0.565 + w / 98 * 1.25,
        text = "Illustration",
        font = f"{w / 98}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1235 + (1 - info_data_ease_value_2) * -1 * w * 0.075,
        h * 0.565 + w / 98 * 1.25 + w / 98 * 1.25,
        text = chart_illustrator_text,
        font = f"{chart_illustrator_text_font_size}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
        wait_execute = True
    )
    
    Task(
        root.create_image,
        "begin_animation_image",
        w * 0.65 - w * im_size * 0.5, h * 0.5 - h * im_size * 0.5,
        width = w * im_size,
        height = h * im_size,
        wait_execute = True
    )
    
    Task(
        root.run_js_code,
        f"ctx.translate(-{all_ease_value * w},0.0);",
        add_code_array = True
    )
    
    Task(root.run_js_wait_code)
    return Task

def BeginJudgeLineAnimation(p: float) -> Chart_Objects_Phi.FrameRenderTask:
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    val = rpe_easing.ease_funcs[12](p)
    Task(
        draw_ui,
        animationing = True,
        dy = h / 7 * val
    )
    Task(
        root.create_line,
        w / 2 - (val * w / 2), h / 2,
        w / 2 + (val * w / 2), h / 2,
        strokeStyle = Const.JUDGELINE_PERFECT_COLOR,
        lineWidth = JUDGELINE_WIDTH / render_range_more_scale if render_range_more else JUDGELINE_WIDTH,
        wait_execute = True
    )
    Task(root.run_js_wait_code)
    return Task

def Begin_Animation(clear: bool = True, fcb: typing.Callable[[], typing.Any] = lambda: None):
    animation_time = 4.5
    
    chart_name_text = chart_information["Name"]
    chart_name_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_name_text)}).width;") / 50
    chart_level_number = Get_LevelNumber()
    chart_level_number_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_level_number) if len(chart_level_number) >= 2 else "'00'"}).width;") / 50
    if len(chart_level_number) == 1:
        chart_level_number_width_1px /= 1.35
    chart_level_text = Get_LevelText()
    chart_level_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_level_text) if len(chart_level_text) >= 2 else "'00'"}).width;") / 50
    chart_artist_text = chart_information["Artist"]
    chart_artist_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_artist_text)}).width;") / 50
    chart_charter_text = chart_information["Charter"]
    chart_charter_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_charter_text)}).width;") / 50
    chart_illustrator_text = chart_information["Illustrator"]
    chart_illustrator_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_illustrator_text)}).width;") / 50
    tip = Phigros_Tips.get_tip()
    tip_font_size = w * 0.020833 / 1.25
    infoframe_x = w * 0.095
    infoframe_y = h * 0.47
    infoframe_width = 0.3 * w
    infoframe_height = 0.118 * h
    infoframe_ltr = w * 0.01
    infoframe_text_place_width = w * 0.23
    chart_name_font_text_size = infoframe_text_place_width * 0.75 / chart_name_text_width_1px
    chart_level_number_font_size = infoframe_width * 0.215 * 0.45 / chart_level_number_width_1px
    chart_level_text_font_size = infoframe_width * 0.215 * 0.175 / chart_level_text_width_1px
    chart_artist_text_font_size = infoframe_text_place_width * 0.65 / chart_artist_text_width_1px
    chart_charter_text_font_size = infoframe_text_place_width * 0.65 / chart_charter_text_width_1px
    chart_illustrator_text_font_size = infoframe_text_place_width * 0.65 / chart_illustrator_text_width_1px
    if chart_name_font_text_size > w * 0.020833 * 0.75:
        chart_name_font_text_size = w * 0.020833 * 0.75
    if chart_artist_text_font_size > w * 0.020833 * 0.65:
        chart_artist_text_font_size = w * 0.020833 * 0.65
    if chart_charter_text_font_size > w * 0.020833 * 0.65:
        chart_charter_text_font_size = w * 0.020833 * 0.65
    if chart_illustrator_text_font_size > w * 0.020833 * 0.65:
        chart_illustrator_text_font_size = w * 0.020833 * 0.65
    
    CoreConfigEx(PhiCoreConfigureEx(
        infoframe_x = infoframe_x,
        infoframe_y = infoframe_y,
        infoframe_width = infoframe_width,
        infoframe_height = infoframe_height,
        infoframe_ltr = infoframe_ltr,
        chart_name_text = chart_name_text,
        chart_name_font_text_size = chart_name_font_text_size,
        chart_artist_text = chart_artist_text,
        chart_artist_text_font_size = chart_artist_text_font_size,
        chart_level_number = chart_level_number,
        chart_level_number_font_size = chart_level_number_font_size,
        chart_level_text = chart_level_text,
        chart_level_text_font_size = chart_level_text_font_size,
        tip = tip,
        tip_font_size = tip_font_size,
        chart_charter_text = chart_charter_text,
        chart_charter_text_font_size = chart_charter_text_font_size,
        chart_illustrator_text = chart_illustrator_text,
        chart_illustrator_text_font_size = chart_illustrator_text_font_size
    ))
    
    LoadSuccess.play()
    
    animation_st = time.time()
    while True:
        p = (time.time() - animation_st) / animation_time
        if p > 1.0:
            break
        
        Task = BeginLoadingAnimation(p, clear, fcb)
        Task.ExecTask()
        
def ChartStart_Animation(fcb: typing.Callable[[], typing.Any] = lambda: None):
    csat = 1.25
    st = time.time()
    while True:
        p = (time.time() - st) / csat
        if p > 1.0:
            break
        
        fcb()
        Task = BeginJudgeLineAnimation(p)
        Task.ExecTask()
    
    time.sleep(0.35)

def initFinishAnimation():
    global im_size
    global ChartNameString, ChartNameStringFontSize
    global ChartLevelString, ChartLevelStringFontSize
    global ScoreString, LevelName, MaxCombo, AccString
    global PerfectCount, GoodCount, BadCount, MissCount
    global EarlyCount, LateCount
    
    im_size = 0.475
    LevelName = "AP" if not noautoplay else PhigrosPlayManagerObject.getLevelString()
    EarlyCount = 0 if not noautoplay else PhigrosPlayManagerObject.getEarlyCount()
    LateCount = 0 if not noautoplay else PhigrosPlayManagerObject.getLateCount()
    PerfectCount = chart_obj.note_num if not noautoplay else PhigrosPlayManagerObject.getPerfectCount()
    GoodCount = 0 if not noautoplay else PhigrosPlayManagerObject.getGoodCount()
    BadCount = 0 if not noautoplay else PhigrosPlayManagerObject.getBadCount()
    MissCount = 0 if not noautoplay else PhigrosPlayManagerObject.getMissCount()
    Acc = 1.0 if not noautoplay else PhigrosPlayManagerObject.getAcc()
    ScoreString = "1000000" if not noautoplay else get_stringscore(PhigrosPlayManagerObject.getScore())
    MaxCombo = chart_obj.note_num if not noautoplay else PhigrosPlayManagerObject.getMaxCombo()
    AccString = f"{(Acc * 100):.2f}%"
    ChartNameString = chart_information["Name"]
    ChartNameStringFontSize = w * im_size * 0.65 / (root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(ChartNameString)}).width;") / 50)
    ChartLevelString = chart_information["Level"]
    ChartLevelStringFontSize = w * im_size * 0.25 / (root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(ChartLevelString)}).width;") / 50)
    if ChartNameStringFontSize > w * 0.0275:
        ChartNameStringFontSize = w * 0.0275
    if ChartLevelStringFontSize > w * 0.0275 * 0.5:
        ChartLevelStringFontSize = w * 0.0275 * 0.5

def Chart_Finish_Animation_Frame(p: float, rjc: bool = True):
    root.clear_canvas(wait_execute = True)
    im_ease_value = Tool_Functions.finish_animation_eases.all_ease(p)
    im_ease_pos = w * 1.25 * (1 - im_ease_value)
    data_block_1_ease_value = Tool_Functions.finish_animation_eases.all_ease(p - 0.015)
    data_block_1_ease_pos = w * 1.25 * (1 - data_block_1_ease_value)
    data_block_2_ease_value = Tool_Functions.finish_animation_eases.all_ease(p - 0.035)
    data_block_2_ease_pos = w * 1.25 * (1 - data_block_2_ease_value)
    data_block_3_ease_value = Tool_Functions.finish_animation_eases.all_ease(p - 0.055)
    data_block_3_ease_pos = w * 1.25 * (1 - data_block_3_ease_value)
    button_ease_value = Tool_Functions.finish_animation_eases.button_ease(p * 4.5 - 0.95)
    level_size = 0.125
    level_size *= Tool_Functions.finish_animation_eases.level_size_ease(p)
    button_ease_pos = - w * Const.FINISH_UI_BUTTON_SIZE * (1 - button_ease_value)
    
    draw_background()
    
    root.create_image(
        "finish_animation_image",
        w * 0.3 - w * im_size * 0.5 + im_ease_pos,
        h * 0.5 - h * im_size * 0.5,
        width = w * im_size,
        height = h * im_size,
        wait_execute = True
    )
    
    root.create_text(
        w * 0.3 - w * im_size * 0.5 + w * im_size * 0.05 + im_ease_pos,
        h * 0.5 + h * im_size * 0.5 - h * im_size * 0.04,
        text = ChartNameString,
        font = f"{ChartNameStringFontSize}px PhigrosFont",
        textAlign = "left",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF", 
        wait_execute = True
    )
    
    root.create_text(
        w * 0.3 + w * im_size * 0.5 - w * im_size * 0.125 + im_ease_pos,
        h * 0.5 + h * im_size * 0.5 - h * im_size * 0.04,
        text = ChartLevelString,
        font = f"{ChartLevelStringFontSize}px PhigrosFont",
        textAlign = "right",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF", 
        wait_execute = True
    )
        
    
    root.create_polygon(
        [
            (w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05, h * 0.5 - h * im_size * 0.5),
            (w * 0.25 + w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05, h * 0.5 - h * im_size * 0.5),
            (w * 0.25 + w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.5),
            (w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.5),
            (w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05, h * 0.5 - h * im_size * 0.5),
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = "#00000066",
        wait_execute = True
    )
    
    root.create_polygon(
        [
            (w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545),
            (w * 0.25 + w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545),
            (w * 0.25 + w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545 + h * im_size * 0.205),
            (w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545 + h * im_size * 0.205),
            (w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545),
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = "#00000066",
        wait_execute = True
    )
    
    root.create_polygon(
        [
            (w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205),
            (w * 0.25 + w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205),
            (w * 0.25 + w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205),
            (w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205),
            (w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205),
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = "#00000066",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.06,
        h * 0.433,
        text = ScoreString,
        font = f"{(w + h) / 42}px PhigrosFont",
        fillStyle = f"rgba(255, 255, 255, {Tool_Functions.finish_animation_eases.score_alpha_ease(p)})",
        wait_execute = True
    )
    
    root.run_js_code(
        f"ctx.globalAlpha = {Tool_Functions.finish_animation_eases.level_alpha_ease(p)};",
        add_code_array = True
    )
    
    root.create_image(
        f"Level_{LevelName}",
        w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.6 - level_size * w / 2,
        h * 0.375 - level_size * w / 2,
        width = w * level_size,
        height = w * level_size,
        wait_execute = True
    )
    
    root.run_js_code(
        "ctx.globalAlpha = 1.0;",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.globalAlpha = {Tool_Functions.finish_animation_eases.playdata_alpha_ease(p - 0.02)}",
        add_code_array = True
    )
    
    root.create_text( # Max Combo
        w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 + w * im_size / 45,
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625,
        text = f"{MaxCombo}",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 70}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 + w * im_size / 45,
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625 + (w + h) / 70 / 2 * 1.25,
        text = "Max Combo",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 150}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text( # Accuracy
        w * 0.25 + w * im_size * 0.38 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 45,
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625,
        text = AccString,
        textAlign = "end",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 70}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 + w * im_size * 0.38 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 45,
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625 + (w + h) / 70 / 2 * 1.25,
        text = "Accuracy",
        textAlign = "end",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 150}px PhigrosFont",
        wait_execute = True
    )
    
    root.run_js_code(
        f"ctx.globalAlpha = {Tool_Functions.finish_animation_eases.playdata_alpha_ease(p - 0.04)}",
        add_code_array = True
    )
    
    root.create_text( # Perfect Count
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.125),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
        text = f"{PerfectCount}",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 75}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.125),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
        text = "Perfect",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 185}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text( # Good Count
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.315),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
        text = f"{GoodCount}",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 75}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.315),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
        text = "Good",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 185}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text( # Bad Conut
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.505),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
        text = f"{BadCount}",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 75}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.505),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
        text = "Bad",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 185}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text( # Miss Count
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.695),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
        text = f"{MissCount}",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 75}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.695),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
        text = "Miss",
        textAlign = "center",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 185}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text( # Early Count
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.875),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.375,
        text = "Early",
        textAlign = "start",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 150}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.925),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.375,
        text = f"{EarlyCount}",
        textAlign = "end",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 150}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text( # Late Count
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.875),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.625,
        text = "Late",
        textAlign = "start",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 150}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.925),
        h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.625,
        text = f"{LateCount}",
        textAlign = "end",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 150}px PhigrosFont",
        wait_execute = True
    )
    
    root.run_js_code(
        "ctx.globalAlpha = 1.0;",
        add_code_array = True
    )
    
    Retry_Button_Width = w * Const.FINISH_UI_BUTTON_SIZE
    Retry_Button_Height = w * Const.FINISH_UI_BUTTON_SIZE / 190 * 145
    Retry_imsize = Retry_Button_Height * 0.3
    
    Continue_Button_Width, Continue_Button_Height = Retry_Button_Width, Retry_Button_Height
    Continue_imsize = Retry_imsize
    
    root.create_image( # Retry Button
        "Button_Left",
        button_ease_pos, 0,
        width = Retry_Button_Width,
        height = Retry_Button_Height,
        wait_execute = True
    )
    
    root.create_image(
        "Retry",
        button_ease_pos + w * Const.FINISH_UI_BUTTON_SIZE * 0.3 - Retry_imsize / 2,
        Retry_Button_Height / 2 - (Retry_Button_Height * (8 / 145)) - Retry_imsize / 2,
        width = Retry_imsize,
        height = Retry_imsize,
        wait_execute = True
    )
    
    root.create_image( # Continue Button
        "Button_Right",
        w - button_ease_pos - Continue_Button_Width, h - Continue_Button_Height,
        width = Continue_Button_Width,
        height = Continue_Button_Height,
        wait_execute = True
    )
    
    root.create_image(
        "Arrow_Right",
        w - (button_ease_pos + w * Const.FINISH_UI_BUTTON_SIZE * 0.35 + Continue_imsize / 2),
        h - (Continue_Button_Height / 2 - (Continue_Button_Height * (8 / 145)) * 1.15 + Continue_imsize / 2),
        width = Continue_imsize,
        height = Continue_imsize,
        wait_execute = True
    )
    if rjc: root.run_js_wait_code()

def Chart_BeforeFinish_Animation_Frame(p: float, a1_combo: int|None, rjc: bool = True):
    v = p ** 2
    if not noautoplay:
        draw_ui(
            process = 1.0,
            score = ScoreString,
            combo_state = chart_obj.note_num >= 3,
            combo = chart_obj.note_num,
            acc = AccString,
            animationing = True,
            dy = h / 7 * (1 - v)
        )
    else:
        draw_ui(
            process = 1.0,
            score = ScoreString,
            combo_state = a1_combo >= 3,
            combo = a1_combo,
            acc = AccString,
            animationing = True,
            dy = h / 7 * (1 - v)
        )
        
    if rjc: root.run_js_wait_code()