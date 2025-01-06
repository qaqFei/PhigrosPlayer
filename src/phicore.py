from __future__ import annotations

import time
import typing
import math
import logging
import threading
from os import environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
from dataclasses import dataclass
from queue import Queue

from pygame import mixer
from PIL import Image

import webcv
import const
import tool_funcs
import rpe_easing
import chartobj_phi
import chartobj_rpe
import phi_tips
import playsound
import phira_resource_pack

drawUI_Default_Kwargs = {
    f"{k}_{k2}": v
    for k in ("combonumber", "combo", "score", "name", "level", "pause") for k2, v in (("dx", 0.0), ("dy", 0.0), ("scaleX", 1.0), ("scaleY", 1.0), ("color", "rgba(255, 255, 255, 1.0)"))
}
mainFramerateCalculator = tool_funcs.FramerateCalculator()
clickEffectEasingType = 16

@dataclass
class PhiCoreConfig:
    SETTER: typing.Callable[[str, typing.Any], typing.Any]
    
    root: webcv.WebCanvas
    w: int
    h: int
    chart_information: dict
    chart_obj: chartobj_phi.Phigros_Chart | chartobj_rpe.Rpe_Chart
    CHART_TYPE: int
    Resource: dict
    ClickEffectFrameCount: int
    PHIGROS_X: float
    PHIGROS_Y: float
    noteWidth: float
    JUDGELINE_WIDTH: float
    note_max_size_half: float
    audio_length: float
    raw_audio_length: float
    show_start_time: float
    chart_res: dict[str, tuple[Image.Image, tuple[int, int]]]
    clickeffect_randomblock: bool
    clickeffect_randomblock_roundn: int
    LoadSuccess: mixer.Sound
    cksmanager: ClickSoundManager
    enable_clicksound: bool
    rtacc: bool
    noautoplay: bool
    showfps: bool
    lfdaot: bool
    speed: float
    render_range_more: bool
    render_range_more_scale: float
    judgeline_notransparent: bool
    debug: bool
    combotips: bool
    noplaychart: bool
    clicksound_volume: float
    musicsound_volume: float
    enable_controls: bool

@dataclass
class PhiCoreConfigure:
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
    
def CoreConfigure(config: PhiCoreConfig):
    global SETTER
    global root, w, h, chart_information
    global chart_obj, CHART_TYPE
    global Resource
    global ClickEffectFrameCount
    global PHIGROS_X, PHIGROS_Y
    global noteWidth, JUDGELINE_WIDTH
    global note_max_size_half, audio_length
    global raw_audio_length, show_start_time
    global chart_res, clickeffect_randomblock
    global clickeffect_randomblock_roundn, LoadSuccess
    global cksmanager
    global enable_clicksound, rtacc, noautoplay
    global showfps, lfdaot
    global speed, render_range_more
    global render_range_more_scale
    global judgeline_notransparent
    global debug, combotips, noplaychart
    global enable_controls
    
    SETTER = config.SETTER
    root = config.root
    w, h = config.w, config.h
    chart_information = config.chart_information
    chart_obj = config.chart_obj
    CHART_TYPE = config.CHART_TYPE
    Resource = config.Resource
    ClickEffectFrameCount = config.ClickEffectFrameCount
    PHIGROS_X, PHIGROS_Y = config.PHIGROS_X, config.PHIGROS_Y
    noteWidth = config.noteWidth
    JUDGELINE_WIDTH = config.JUDGELINE_WIDTH
    note_max_size_half = config.note_max_size_half
    audio_length = config.audio_length
    raw_audio_length = config.raw_audio_length
    show_start_time = config.show_start_time
    chart_res = config.chart_res
    clickeffect_randomblock = config.clickeffect_randomblock
    clickeffect_randomblock_roundn = config.clickeffect_randomblock_roundn
    LoadSuccess = config.LoadSuccess
    cksmanager = config.cksmanager
    enable_clicksound = config.enable_clicksound
    rtacc = config.rtacc
    noautoplay = config.noautoplay
    showfps = config.showfps
    lfdaot = config.lfdaot
    speed = config.speed
    render_range_more = config.render_range_more
    render_range_more_scale = config.render_range_more_scale
    judgeline_notransparent = config.judgeline_notransparent
    debug = config.debug
    combotips = config.combotips
    noplaychart = config.noplaychart
    enable_controls = config.enable_controls
    
    if Resource["Note_Click_Audio"] is not None: # use in tools
        mixer.music.set_volume(config.musicsound_volume)
        for i in Resource["Note_Click_Audio"].values():
            i.set_volume(config.clicksound_volume)
    
    logging.info("CoreConfigure Done")

def CoreConfigureEx(config: PhiCoreConfigure):
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
    
    logging.info("CoreConfigureEx Done")

class ClickSoundManager:
    def __init__(self, res: dict[int, playsound.directSound]):
        self.res = res
        self.queue: Queue[int|None] = Queue()
        threading.Thread(target=self.runner, daemon=True).start()
    
    def play(self, nt: int):
        self.queue.put(nt)
    
    def stop(self):
        self.queue.put(None)
    
    def runner(self):
        while True:
            nt = self.queue.get()
            if nt is None: break
            self.res[nt].play()

def processClickEffectBase(
    x: float, y: float,
    p: float, rblocks: tuple[tuple[float, float]]|None,
    perfect: bool, noteWidth: float,
    root: webcv.WebCanvas,
    framecount: int,
    enable_rblocks: bool = True,
    rblocks_roundn: float = 0.0,
    caller: typing.Callable[[typing.Callable, typing.Any], typing.Any] = lambda f, *args, **kwargs: f(*args, **kwargs)
):
    if rblocks is None: rblocks = tool_funcs.get_effect_random_blocks()
    
    color = (
        phira_resource_pack.globalPack.perfectRGB
        if perfect else
        phira_resource_pack.globalPack.goodRGB
    )
    
    alpha = (
        phira_resource_pack.globalPack.perfectAlpha
        if perfect else
        phira_resource_pack.globalPack.goodAlpha
    ) / 255
    
    imn = f"Note_Click_Effect_{"Perfect" if perfect else "Good"}"
    effectSize = noteWidth * 1.375
    blockSize = noteWidth / 5.5
    
    if enable_rblocks:
        randomblock_r = effectSize * rpe_easing.ease_funcs[clickEffectEasingType + 1](p) / 1.2
        nowBlockSize = blockSize * (0.4 * math.sin(p * math.pi) + 0.6)
        
        for deg, randdr in rblocks:
            pointr = randomblock_r + randdr * blockSize
            
            if pointr < 0.0: continue
            
            point = tool_funcs.rotate_point(x, y, deg, pointr)
            caller(
                root.run_js_code,
                f"ctx.addRoundRectData(\
                    {point[0] - nowBlockSize / 2},\
                    {point[1] - nowBlockSize / 2},\
                    {nowBlockSize},\
                    {nowBlockSize},\
                    {nowBlockSize * rblocks_roundn}\
                );",
                add_code_array = True
            )
    
        caller(root.run_js_code, f"ctx.drawRoundDatas('rgba{color + ((1.0 - p) * alpha, )}');", add_code_array = True)
    
    caller(
        root.run_js_code,
        f"ctx.drawAlphaImage(\
            {root.get_img_jsvarname(f"{imn}_{int(p * (framecount - 1)) + 1}")},\
            {x - effectSize / 2}, {y - effectSize / 2},\
            {effectSize}, {effectSize}, {alpha}\
        );",
        add_code_array = True
    )

def processClickEffect(
    x: float, y: float,
    p: float, rblocks: tuple[tuple[float, float]],
    perfect: bool,
    caller: typing.Callable[[typing.Callable, typing.Any], typing.Any] = lambda f, *args, **kwargs: f(*args, **kwargs)
):
    return processClickEffectBase(
        x = x, y = y, p = p,
        rblocks = rblocks,
        perfect = perfect,
        noteWidth = noteWidth,
        root = root,
        framecount = ClickEffectFrameCount,
        caller = caller,
        enable_rblocks = clickeffect_randomblock,
        rblocks_roundn = clickeffect_randomblock_roundn
    )

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

# color 一定要传 rgba 的
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
    if clear: root.clear_canvas(wait_execute = True)
    if background: draw_background()
    
    pauseImgWidth, pauseImgHeight = w * (36 / 1920) * pauseUI_scaleX, w * (36 / 1920) / 35 * 41 * pauseUI_scaleY
    pauseImgAlpha = pauseUI_color.split(")")[-2].split(",")[-1].replace(" ", "")
    fps = mainFramerateCalculator.framerate
    reqaf_fps = root.get_framerate()
    
    uidata = [
        {
            "type": "call",
            "name": "translate", "args": [0, - h / 7  + dy]
        } if animationing else None,
        {
            "type": "call",
            "name": "fillRectEx", "args": [
                0, 0, w * process, h / 125,
                "rgba(145, 145, 145, 0.85)"
            ]
        },
        {
            "type": "call",
            "name": "fillRectEx", "args": [
                w * process - w * 0.002, 0,
                w * 0.002, h / 125,
                "rgba(255, 255, 255, 0.9)"
            ]
        },
        {
            "type": "text",
            "text": f"{score}", "fontsize": (w + h) / 75 / 0.75,
            "textBaseline": "middle", "textAlign": "right",
            "x": w * 0.988, "y": h * (58 / 1080),
            "dx": scoreUI_dx, "dy": scoreUI_dy,
            "sx": scoreUI_scaleX, "sy": scoreUI_scaleY,
            "color": scoreUI_color, "rotate": scoreUI_rotate
        },
        {
            "type": "text",
            "text": f"{acc}", "fontsize": (w + h) / 145 / 0.75,
            "textBaseline": "middle", "textAlign": "right",
            "x": w * 0.988, "y": h * (58 / 1080) + (w + h) / 145 / 0.75 * 1.5,
            "dx": scoreUI_dx, "dy": scoreUI_dy,
            "sx": scoreUI_scaleX, "sy": scoreUI_scaleY,
            "color": scoreUI_color, "rotate": scoreUI_rotate
        } if rtacc else None,
        {
            "type": "text",
            "text": f"{combo}", "fontsize": (w + h) / 64.51 / 0.75,
            "textBaseline": "middle", "textAlign": "center",
            "x": w / 2, "y": h * 0.05,
            "dx": combonumberUI_dx, "dy": combonumberUI_dy,
            "sx": combonumberUI_scaleX, "sy": combonumberUI_scaleY,
            "color": combonumberUI_color, "rotate": combonumberUI_rotate
        } if combo_state else None,
        {
            "type": "text",
            "text": f"{combotips}", "fontsize": (w + h) / 142 / 0.75,
            "textBaseline": "middle", "textAlign": "center",
            "x": w / 2, "y": h * 0.095,
            "dx": comboUI_dx, "dy": comboUI_dy,
            "sx": comboUI_scaleX, "sy": comboUI_scaleY,
            "color": comboUI_color, "rotate": comboUI_rotate
        } if combo_state else None,
        {
            "type": "image",
            "image": root.get_img_jsvarname("PauseImg"),
            "x": w * (36 / 1920), "y": h * (41 / 1080),
            "dx": pauseUI_dx, "dy": pauseUI_dy,
            "width": pauseImgWidth, "height": pauseImgHeight,
            "rotate": pauseUI_rotate, "alpha": pauseImgAlpha
        },
        {
            "type": "call",
            "name": "translate", "args": [0, -2 * (- h / 7 + dy)]
        } if animationing else None,
        {
            "type": "text",
            "text": chart_information["Name"], "fontsize": (w + h) / 125 / 0.75,
            "textBaseline": "middle", "textAlign": "left",
            "x": w * 0.0125, "y": h * 0.976 - (w + h) / 125 / 0.75 / 2,
            "dx": nameUI_dx, "dy": nameUI_dy,
            "sx": nameUI_scaleX, "sy": nameUI_scaleY,
            "color": nameUI_color, "rotate": nameUI_rotate
        },
        {
            "type": "text",
            "text": chart_information["Level"], "fontsize": (w + h) / 125 / 0.75,
            "textBaseline": "middle", "textAlign": "right",
            "x": w * 0.9875, "y": h * 0.976 - (w + h) / 125 / 0.75 / 2,
            "dx": levelUI_dx, "dy": levelUI_dy,
            "sx": levelUI_scaleX, "sy": levelUI_scaleY,
            "color": levelUI_color, "rotate": levelUI_rotate
        },
        {
            "type": "text",
            "text": (
                (f"fps {fps:.0f} - " if showfps else "")
                + (f"reqaf fps {reqaf_fps:.0f} - " if showfps else "")
                + "PhigrosPlayer - by qaqFei - github.com/qaqFei/PhigrosPlayer - MIT License"
            ), "fontsize": (w + h) / 275 / 0.75,
            "textBaseline": "bottom", "textAlign": "right",
            "x": w * 0.9875, "y": h * 0.995,
            "dx": 0.0, "dy": 0.0,
            "sx": 1.0, "sy": 1.0,
            "color": "rgba(255, 255, 255, 0.5)", "rotate": 0.0
        },
        {
            "type": "call",
            "name": "translate", "args": [0, - h / 7 + dy]
        } if animationing else None
    ]
    
    root.run_js_code(f"ctx.drawUIItems({uidata});", add_code_array = True)
    mainFramerateCalculator.frame()
             
def deleteDrwaUIKwargsDefaultValues(kwargs:dict) -> dict:
    return {k: v for k, v in kwargs.items() if v != drawUI_Default_Kwargs.get(k, None)}   

def drawDebugText(text: str, x: float, y: float, rotate: float, color: str, Task: chartobj_phi.FrameRenderTask):
    Task(
        root.run_js_code,
        f"ctx.drawRotateText(\
            {root.string2sctring_hqm(text)},\
            {",".join(map(str, tool_funcs.rotate_point(x, y, rotate, (w + h) / 75)))},\
            {90 + rotate}, {(w + h) / 85 / 0.75}, '{color}', 1.0, 1.0\
        );",
        add_code_array = True
    )

def rrm_start(Task: chartobj_phi.FrameRenderTask):
    if not render_range_more: return
    lw, lh = w / render_range_more_scale, h / render_range_more_scale
    lr, lt = w / 2 - lw / 2, h / 2 - lh / 2
    rms = 1 / render_range_more_scale
    
    Task(
        root.run_js_code,
        f"ctx.save(); ctx.translate({lr}, {lt}); ctx.scale({rms}, {rms});",
        add_code_array = True
    )

def rrm_end(Task: chartobj_phi.FrameRenderTask):
    if not render_range_more: return
    Task(
        root.run_js_code,
        "ctx.restore();",
        add_code_array = True
    )

def FrameData_ProcessExTask(ExTask: list[tuple[str, typing.Any]]):
    break_flag = False
    
    for ext in ExTask:
        match ext[0]:
            case "break":
                break_flag = True
            case "psound":
                cksmanager.play(ext[1])
        
    return break_flag

def GetFrameRenderTask_Phi(now_t: float, clear: bool = True, rjc: bool = True, pplm: tool_funcs.PhigrosPlayLogicManager|None = None):
    global PlayChart_NowTime
    
    now_t *= speed
    PlayChart_NowTime = now_t
    Task = chartobj_phi.FrameRenderTask([], [])
    if clear: Task(root.clear_canvas, wait_execute = True)
    rrm_start(Task)
    Task(draw_background)
    if noplaychart: Task.ExTask.append(("break", ))
    
    noautoplay = pplm is not None # reset a global variable
    if noautoplay:
        pplm.pc_update(now_t)
    
    for lineIndex, line in enumerate(chart_obj.judgeLineList):
        lineBTime = now_t / line.T
        
        lineFloorPosition = chartobj_phi.getFloorPosition(line, lineBTime) * PHIGROS_Y
        linePos = line.get_datavar_move(lineBTime, w, h)
        lineRotate = line.get_datavar_rotate(lineBTime)
        lineAlpha = line.get_datavar_disappear(lineBTime)
        
        judgeLine_DrawPos = (
            *tool_funcs.rotate_point(*linePos, lineRotate, h * 5.76 / 2),
            *tool_funcs.rotate_point(*linePos, lineRotate + 180, h * 5.76 / 2)
        )
        judgeLine_color = (*((255, 255, 170) if not noautoplay else pplm.ppps.getJudgelineColor()), lineAlpha if not judgeline_notransparent else 1.0)
        judgeLine_webCanvas_color = f"rgba{judgeLine_color}"
        
        if (judgeLine_color[-1] > 0.0 and tool_funcs.lineInScreen(w, h, judgeLine_DrawPos)) or debug:
            Task(
                root.run_js_code,
                f"ctx.drawLineEx(\
                    {",".join(map(str, judgeLine_DrawPos))},\
                    {JUDGELINE_WIDTH},\
                    '{judgeLine_webCanvas_color}'\
                );",
                add_code_array = True,
                order = const.CHART_RENDER_ORDERS.LINE
            )
            
            if debug:
                drawDebugText(f"{lineIndex}", *linePos, lineRotate - 90, "rgba(255, 255, 170, 0.5)", Task)
                
                Task(
                    root.run_js_code,
                    f"ctx.fillRectEx(\
                        {linePos[0] - (w + h) / 250},\
                        {linePos[1] - (w + h) / 250},\
                        {(w + h) / 250 * 2},\
                        {(w + h) / 250 * 2},\
                        'rgb(238, 130, 238)'\
                    );",
                    add_code_array = True
                )
        
        for notesChildren in line.renderNotes.copy():
            for note in notesChildren.copy():
                this_noteitem_clicked = note.sec < now_t
                
                if this_noteitem_clicked and not note.clicked:
                    note.clicked = True
                    if enable_clicksound and not noautoplay:
                        Task.ExTask.append(("psound", note.type))
                
                if not note.ishold and note.clicked:
                    notesChildren.remove(note)
                    continue
                elif note.ishold and now_t > note.hold_endtime:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and note.state == const.NOTE_STATE.BAD:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and not note.ishold and note.player_clicked:
                    notesChildren.remove(note)
                    continue
                elif not note.clicked and (note.floorPosition * PHIGROS_Y - lineFloorPosition) < const.FLOAT_LESSZERO_MAGIC and note.type != const.Note.HOLD:
                    continue
                elif note.ishold and note.speed == 0.0:
                    notesChildren.remove(note)
                    continue
                
                note_now_floorPosition = note.floorPosition * PHIGROS_Y - (
                        lineFloorPosition
                        if not (note.ishold and note.clicked) else (
                        chartobj_phi.getFloorPosition(
                            line, note.time
                        ) * PHIGROS_Y + tool_funcs.linear_interpolation(note.hold_endtime - now_t, 0, note.hold_length_sec, note.hold_length_pgry * PHIGROS_Y, 0)
                    )
                )
                
                if not note.ishold:
                    note_now_floorPosition *= note.speed
                
                if note_now_floorPosition > h * 2:
                    continue
                
                rotatenote_at_judgeLine_pos = tool_funcs.rotate_point(*linePos, lineRotate, note.positionX * PHIGROS_X)
                judgeLine_to_note_rotate_deg = (-90 if note.above else 90) + lineRotate
                x, y = tool_funcs.rotate_point(*rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_now_floorPosition)
                
                note.nowpos = (x / w, y / h)
                
                if note.ishold:
                    note_hold_draw_length = note_now_floorPosition + note.hold_length_pgry * PHIGROS_Y
                    holdend_x, holdend_y = tool_funcs.rotate_point(*rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_hold_draw_length)
                    
                    if note.clicked:
                        holdhead_pos = rotatenote_at_judgeLine_pos
                    else:
                        holdhead_pos = x, y
                        
                    holdbody_range = (
                        tool_funcs.rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg - 90, noteWidth / 2),
                        tool_funcs.rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg - 90, noteWidth / 2),
                        tool_funcs.rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg + 90, noteWidth / 2),
                        tool_funcs.rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg + 90, noteWidth / 2),
                    )
                    
                if note_now_floorPosition > note_max_size_half:
                    plp_lineLength = h * 5.76
                    
                    nlOutOfScreen_nohold = tool_funcs.noteLineOutOfScreen(
                        x, y, rotatenote_at_judgeLine_pos,
                        note_now_floorPosition,
                        lineRotate, plp_lineLength,
                        judgeLine_to_note_rotate_deg,
                        w, h, note_max_size_half
                    )
                    
                    nlOutOfScreen_hold = True if not note.ishold else tool_funcs.noteLineOutOfScreen(
                        holdend_x, holdend_y, rotatenote_at_judgeLine_pos,
                        note_hold_draw_length, lineRotate, plp_lineLength,
                        judgeLine_to_note_rotate_deg, w, h, note_max_size_half
                    )
                    
                    if nlOutOfScreen_nohold and nlOutOfScreen_hold:
                        break
                    
                note_iscan_render = (
                    tool_funcs.noteCanRender(w, h, note_max_size_half, x, y)
                    if not note.ishold
                    else tool_funcs.noteCanRender(w, h, -1, x, y, holdbody_range)
                )
                
                if note_iscan_render:
                    noteRotate = judgeLine_to_note_rotate_deg + 90
                    
                    this_note_img = Resource["Notes"][note.img_keyname]
                    if note.ishold:
                        this_note_img_end = Resource["Notes"][note.img_end_keyname]
                    
                    fix_scale = const.NOTE_DUB_FIXSCALE if note.morebets else 1.0 # because the note img if has morebets frame, the note will be look small, so we will `*` a fix scale to fix the frame size make the note look is small.
                    this_note_width = noteWidth * fix_scale
                    this_note_height = this_note_width / this_note_img.width * this_note_img.height
                        
                    if note.ishold:
                        this_noteend_height = noteWidth / this_note_img_end.width * this_note_img_end.height
                        
                        if note.clicked:
                            holdbody_x,holdbody_y = rotatenote_at_judgeLine_pos
                            holdbody_length = note_hold_draw_length - this_noteend_height / 2
                        else:
                            holdbody_x,holdbody_y = tool_funcs.rotate_point(
                                *holdhead_pos, judgeLine_to_note_rotate_deg, this_note_height / 2
                            )
                            holdbody_length = note.hold_length_pgry * PHIGROS_Y - (this_note_height + this_noteend_height) / 2
                        
                        miss_alpha_change = 0.5 if noautoplay and note.player_missed else 1.0
                        
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(note.imgname_end)},\
                                {holdend_x},\
                                {holdend_y},\
                                {this_note_width},\
                                {this_noteend_height},\
                                {noteRotate},\
                                {miss_alpha_change}\
                            );",
                            add_code_array = True,
                            order = note.draworder
                        )
                        
                        if holdbody_length > 0.0:
                            Task(
                                root.run_js_code,
                                f"ctx.drawAnchorESRotateImage(\
                                    {root.get_img_jsvarname(note.imgname_body)},\
                                    {holdbody_x},\
                                    {holdbody_y},\
                                    {this_note_width},\
                                    {holdbody_length},\
                                    {noteRotate},\
                                    {miss_alpha_change}\
                                );",
                                add_code_array = True,
                                order = note.draworder
                            )
                        
                    if not (note.ishold and note.sec < now_t):
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(note.imgname)},\
                                {x},\
                                {y},\
                                {this_note_width},\
                                {this_note_height},\
                                {noteRotate},\
                                1.0\
                            );",
                            add_code_array = True,
                            order = note.draworder
                        )
                
                    if debug:
                        drawDebugText(f"{lineIndex}+{note.master_index}", x, y, judgeLine_to_note_rotate_deg, "rgba(0, 255, 255, 0.5)", Task)
                        
                        Task(
                            root.run_js_code,
                            f"ctx.fillRectEx(\
                                {x - (w + h) / 250},\
                                {y - (w + h) / 250},\
                                {(w + h) / 250 * 2},\
                                {(w + h) / 250 * 2},\
                                'rgb(0, 255, 0)'\
                            );",
                            add_code_array = True
                        )

            if not notesChildren:
                line.renderNotes.remove(notesChildren)
    Task(root.run_jscode_orders)
    
    effect_time = phira_resource_pack.globalPack.effectDuration
    miss_effect_time = 0.2
    bad_effect_time = 0.5
    
    effect_time *= speed
    miss_effect_time *= speed
    bad_effect_time *= speed
        
    def process_effect(
        sec_t: float,
        rblocks: tuple[tuple[float, float]],
        perfect: bool,
        position: tuple[float, float]
    ):
        p = (now_t - sec_t) / effect_time
        if not (0.0 <= p <= 1.0): return
        processClickEffect(*position, p, rblocks, perfect, Task)
    
    def process_miss(
        note:chartobj_phi.Note
    ):
        t = now_t / note.master.T
        p = (now_t - note.sec) / miss_effect_time
        will_show_effect_pos = line.get_datavar_move(t, w, h)
        will_show_effect_rotate = line.get_datavar_rotate(t)
        pos = tool_funcs.rotate_point(
            *will_show_effect_pos,
            -will_show_effect_rotate,
            note.positionX * PHIGROS_X
        )
        floorp = note.floorPosition - chartobj_phi.getFloorPosition(note.master, t)
        x,y = tool_funcs.rotate_point(
            *pos,
            (-90 if note.above else 90) - will_show_effect_rotate,
            floorp * PHIGROS_Y
        )
        img_keyname = f"{note.type_string}{"_dub" if note.morebets else ""}"
        this_note_img = Resource["Notes"][img_keyname]
        imgname = f"Note_{img_keyname}"
        Task(
            root.run_js_code,
            f"crc2d_enable_rrm = false; ctx.drawRotateImage(\
                {root.get_img_jsvarname(imgname)},\
                {x},\
                {y},\
                {noteWidth},\
                {noteWidth / this_note_img.width * this_note_img.height},\
                {- will_show_effect_rotate},\
                {1 - p ** 0.5}\
            ); crc2d_enable_rrm = true;",
            add_code_array = True
        )
    
    def process_bad(
        note: chartobj_phi.Note
    ):
        p = (now_t - note.player_badtime) / bad_effect_time
            
        if note.player_bad_posandrotate is None:
            t = note.player_badtime / note.master.T
            will_show_effect_pos = line.get_datavar_move(t, w, h)
            will_show_effect_rotate = line.get_datavar_rotate(t)
            
            pos = tool_funcs.rotate_point(
                *will_show_effect_pos,
                -will_show_effect_rotate,
                note.positionX * PHIGROS_X
            )
            floorp = note.floorPosition - chartobj_phi.getFloorPosition(note.master, t)
            x, y = tool_funcs.rotate_point(
                *pos,
                (-90 if note.above else 90) - will_show_effect_rotate,
                floorp * PHIGROS_Y
            )
            
            note.player_bad_posandrotate = ((x, y), -will_show_effect_rotate)
        
        (x, y), nr = note.player_bad_posandrotate
        
        this_note_img = Resource["Notes"]["Bad"]
        Task(
            root.run_js_code,
            f"crc2d_enable_rrm = false; ctx.drawRotateImage(\
                {root.get_img_jsvarname("Note_Bad")},\
                {x},\
                {y},\
                {noteWidth * (const.NOTE_DUB_FIXSCALE if note.morebets else 1.0)},\
                {noteWidth / this_note_img.width * this_note_img.height},\
                {nr},\
                {1 - p ** 3}\
            ); crc2d_enable_rrm = true;",
            add_code_array = True
        )
        
    if noautoplay:
        for pplmckfi in pplm.clickeffects.copy():
            perfect, eft, erbs, position = pplmckfi
            if eft <= now_t <= eft + effect_time:
                process_effect(eft, erbs, perfect, position(w, h))
            
            if eft + effect_time < now_t:
                pplm.clickeffects.remove(pplmckfi)
        
    for line in chart_obj.judgeLineList:
        for note in line.effectNotes.copy():
            if not noautoplay and not note.clicked: break
            
            if not noautoplay:
                for eft, erbs, position in note.effect_times:
                    if eft <= now_t <= eft + effect_time:
                        process_effect(eft, erbs, True, position(w, h))
            else: # noautoplay
                if note.state == const.NOTE_STATE.MISS:
                    if 0.0 <= now_t - note.sec <= miss_effect_time and note.type != const.Note.HOLD:
                        process_miss(note)
                elif note.state == const.NOTE_STATE.BAD:
                    if 0.0 <= now_t - note.player_badtime <= bad_effect_time:
                        process_bad(note)
                    
            if note.effect_times[-1][0] + max(
                effect_time,
                miss_effect_time,
                bad_effect_time
            ) + 0.2 < now_t:
                line.effectNotes.remove(note)
    
    combo = chart_obj.getCombo(now_t) if not noautoplay else pplm.ppps.getCombo()
    now_t /= speed
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = get_stringscore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else get_stringscore(pplm.ppps.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        acc = "100.00%" if not noautoplay else f"{(pplm.ppps.getAcc() * 100):.2f}%",
        clear = False,
        background = False
    )
    
    rrm_end(Task)
    if rjc: Task(root.run_js_wait_code)
    
    if now_t >= raw_audio_length:
        Task.ExTask.append(("break", ))
    
    return Task

def GetFrameRenderTask_Rpe(now_t: float, clear: bool = True, rjc: bool = True, pplm: tool_funcs.PhigrosPlayLogicManager|None = None):
    global PlayChart_NowTime
    
    now_t *= speed
    Task = chartobj_phi.FrameRenderTask([], [])
    if clear: Task(root.clear_canvas, wait_execute = True)
    rrm_start(Task)
    Task(draw_background)
    PlayChart_NowTime = now_t
    if noplaychart: Task.ExTask.append(("break", ))
    
    now_t -= chart_obj.META.offset / 1000
    attachUIData = {}
    
    noautoplay = pplm is not None # reset a global variable
    if noautoplay:
        pplm.pc_update(now_t)
    
    for line_index, line in enumerate(chart_obj.judgeLineList):
        linePos, lineAlpha, lineRotate, lineColor, lineScaleX, lineScaleY, lineText = line.GetState(chart_obj.sec2beat(now_t, line.bpmfactor), (255, 255, 170) if not noautoplay else pplm.ppps.getJudgelineColor(), chart_obj)
        beatTime = chart_obj.sec2beat(now_t, line.bpmfactor)
        if judgeline_notransparent: lineAlpha = 1.0
        linePos = (linePos[0] * w, linePos[1] * h)
        judgeLine_DrawPos = (
            *tool_funcs.rotate_point(*linePos, lineRotate, w * 4000 / const.RPE_WIDTH * lineScaleX / 2),
            *tool_funcs.rotate_point(*linePos, lineRotate + 180, w * 4000 / const.RPE_WIDTH * lineScaleX / 2)
        )
        negative_alpha = lineAlpha < 0.0
        judgeLine_webCanvas_color = f"rgba{lineColor + (lineAlpha, )}"
        
        if line.Texture != "line.png" and lineAlpha > 0.0:
            _, texture_size = chart_res[line.Texture]
            texture_width, texture_height = tool_funcs.conimgsize(*texture_size, w, h)
            texture_width *= lineScaleX; texture_height *= lineScaleY
            if tool_funcs.TextureLine_CanRender(w, h, (texture_width ** 2 + texture_height ** 2) ** 0.5 / 2, *linePos):
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
                    add_code_array = True,
                    order = const.CHART_RENDER_ORDERS.LINE
                )
        elif lineText is not None and lineAlpha > 0.0:
            Task(
                root.run_js_code,
                f"ctx.drawRPEMultipleRotateText(\
                    '{root.string2cstring(lineText)}',\
                    {linePos[0]},\
                    {linePos[1]},\
                    {lineRotate},\
                    {(w + h) / 75 * 1.35},\
                    '{judgeLine_webCanvas_color}',\
                    {lineScaleX},\
                    {lineScaleY}\
                );",
                add_code_array = True,
                order = const.CHART_RENDER_ORDERS.LINE
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
        elif lineAlpha > 0.0 and tool_funcs.lineInScreen(w, h, judgeLine_DrawPos):
            Task(
                root.run_js_code,
                f"ctx.drawLineEx(\
                    {",".join(map(str, judgeLine_DrawPos))},\
                    {JUDGELINE_WIDTH * lineScaleY},\
                    '{judgeLine_webCanvas_color}'\
                );",
                add_code_array = True,
                order = const.CHART_RENDER_ORDERS.LINE
            )
            
        if debug and line.attachUI is None and tool_funcs.pointInScreen(linePos, w, h):
            drawDebugText(f"{line_index}", *linePos, lineRotate - 90, "rgba(255, 255, 170, 0.5)", Task)
            
            Task(
                root.run_js_code,
                f"ctx.fillRectEx(\
                    {linePos[0] - (w + h) / 250},\
                    {linePos[1] - (w + h) / 250},\
                    {(w + h) / 250 * 2},\
                    {(w + h) / 250 * 2},\
                    'rgb(238, 130, 238)'\
                );",
                add_code_array = True
            )
        
        line.playingFloorPosition = line.GetFloorPositionByTime(now_t)
        
        for notesChildren in line.renderNotes.copy():
            for note in notesChildren.copy():
                note_clicked = note.startTime.value < beatTime
                
                if note_clicked and not note.clicked:
                    note.clicked = True
                    if enable_clicksound and not note.isFake and not noautoplay:
                        Task.ExTask.append(("psound", note.hitsound_reskey))
                
                if not note.ishold and note.clicked:
                    notesChildren.remove(note)
                    continue
                elif note.ishold and beatTime > note.endTime.value:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and note.state == const.NOTE_STATE.BAD:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and not note.ishold and note.player_clicked:
                    notesChildren.remove(note)
                    continue
                
                noteFloorPosition = (note.floorPosition - line.playingFloorPosition) * h * note.speed + note.yOffset / const.RPE_HEIGHT * h
                if line.isCover and noteFloorPosition < const.FLOAT_LESSZERO_MAGIC and not note.clicked and not note.ishold:
                    continue
                
                noteAtJudgeLinePos = tool_funcs.rotate_point(
                    *linePos, lineRotate, note.positionX2 * w
                )
                lineToNoteRotate = (-90 if note.above == 1 else 90) + lineRotate
                x, y = tool_funcs.rotate_point(
                    *noteAtJudgeLinePos, lineToNoteRotate, noteFloorPosition
                )
                
                if enable_controls:
                    rpex = tool_funcs.aconrpepos(x, y)[0]
                    ax, px, sx, yx = line.controlEvents.gtvalue(rpex)
                    noteFloorPosition *= yx
                    x, y = tool_funcs.rotate_point(
                        *noteAtJudgeLinePos, lineToNoteRotate, noteFloorPosition
                    )
                    rpex, rpey = tool_funcs.aconrpepos(x, y)
                    noteAlpha = note.float_alpha * ax
                    rpex *= px
                    noteWidthX = note.width * sx
                    x, y = tool_funcs.conrpepos(rpex, rpey)
                else:
                    noteAlpha = note.float_alpha
                    noteWidthX = note.width
                
                note.nowpos = (x / w, y / h)
                    
                if note.ishold:
                    holdLength = note.holdLength * h * note.speed
                    noteHoldDrawLength = noteFloorPosition + holdLength
                    
                    if line.isCover and noteHoldDrawLength < 0 and not note.clicked:
                        continue
                    
                    holdend_x, holdend_y = tool_funcs.rotate_point(
                        *noteAtJudgeLinePos, lineToNoteRotate, noteHoldDrawLength
                    )
                    
                    if note.clicked:
                        holdhead_pos = noteAtJudgeLinePos
                    else:
                        holdhead_pos = x, y
                        
                    holdbody_range = (
                        tool_funcs.rotate_point(*holdhead_pos, lineToNoteRotate - 90, noteWidth / 2),
                        tool_funcs.rotate_point(holdend_x, holdend_y, lineToNoteRotate - 90, noteWidth / 2),
                        tool_funcs.rotate_point(holdend_x, holdend_y, lineToNoteRotate + 90, noteWidth / 2),
                        tool_funcs.rotate_point(*holdhead_pos, lineToNoteRotate + 90, noteWidth / 2),
                    )
                    
                if noteFloorPosition > note_max_size_half:
                    plp_lineLength = w * 4000 / const.RPE_WIDTH
                    
                    nlOutOfScreen_nohold = tool_funcs.noteLineOutOfScreen(
                        x, y, noteAtJudgeLinePos,
                        noteFloorPosition,
                        lineRotate, plp_lineLength,
                        lineToNoteRotate,
                        w, h, note_max_size_half
                    )
                    
                    nlOutOfScreen_hold = True if not note.ishold else tool_funcs.noteLineOutOfScreen(
                        holdend_x, holdend_y, noteAtJudgeLinePos,
                        noteHoldDrawLength, lineRotate, plp_lineLength,
                        lineToNoteRotate, w, h, note_max_size_half
                    )
                    
                    if nlOutOfScreen_nohold and nlOutOfScreen_hold:
                        break # it is safe to break, because speed and yOffset value is same in a notesChildren.
                
                canRender = (
                    tool_funcs.noteCanRender(w, h, note_max_size_half, x, y)
                    if not note.ishold
                    else tool_funcs.noteCanRender(w, h, -1, x, y, holdbody_range)
                ) and not negative_alpha and now_t >= 0.0
                
                if canRender and abs(now_t - note.secst) <= note.visibleTime:
                    noteRotate = lineRotate + (0 if note.above == 1 else 180)
                    
                    this_note_img = Resource["Notes"][note.img_keyname]
                    if note.ishold:
                        this_note_img_end = Resource["Notes"][note.img_end_keyname]
                        
                    fix_scale = const.NOTE_DUB_FIXSCALE if note.morebets else 1.0
                    this_note_width = noteWidth * fix_scale
                    this_note_height = noteWidth / this_note_img.width * this_note_img.height
                    
                    if note.ishold:
                        this_noteend_height = noteWidth / this_note_img_end.width * this_note_img_end.height
                        
                        if note.clicked:
                            holdbody_x, holdbody_y = noteAtJudgeLinePos
                            holdbody_length = noteHoldDrawLength - this_noteend_height / 2
                        else:
                            holdbody_x, holdbody_y = tool_funcs.rotate_point(
                                *holdhead_pos, lineToNoteRotate, this_note_height / 2
                            )
                            holdbody_length = holdLength - (this_note_height + this_noteend_height) / 2
                        
                        if holdbody_length < 0.0:
                            holdbody_length = 0.0
                            
                        miss_alpha_change = 0.5 if noautoplay and note.player_missed else 1.0
                        
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(note.imgname_end)},\
                                {holdend_x},\
                                {holdend_y},\
                                {this_note_width * noteWidthX},\
                                {this_noteend_height},\
                                {noteRotate},\
                                {noteAlpha * miss_alpha_change}\
                            );",
                            add_code_array = True,
                            order = note.draworder
                        )
                        
                        if holdbody_length > 0.0:
                            Task(
                                root.run_js_code,
                                f"ctx.drawAnchorESRotateImage(\
                                    {root.get_img_jsvarname(note.imgname_body)},\
                                    {holdbody_x},\
                                    {holdbody_y},\
                                    {this_note_width * noteWidthX},\
                                    {holdbody_length},\
                                    {noteRotate},\
                                    {noteAlpha * miss_alpha_change}\
                                );",
                                add_code_array = True,
                                order = note.draworder
                            )
                    
                    if not (note.ishold and note.startTime.value < beatTime):
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(note.imgname)},\
                                {x},\
                                {y},\
                                {this_note_width * noteWidthX},\
                                {this_note_height},\
                                {noteRotate},\
                                {noteAlpha}\
                            );",
                            add_code_array = True,
                            order = note.draworder
                        )
                        
                    if debug:
                        drawDebugText(f"{line_index}+{note.master_index}", x, y, lineToNoteRotate, "rgba(0, 255, 255, 0.5)", Task)
                        
                        Task(
                            root.run_js_code,
                            f"ctx.fillRectEx(\
                                {x - (w + h) / 250},\
                                {y - (w + h) / 250},\
                                {(w + h) / 250 * 2},\
                                {(w + h) / 250 * 2},\
                                'rgb(0, 255, 0)'\
                            );",
                            add_code_array = True
                        )
        
            
            if not notesChildren:
                line.renderNotes.remove(notesChildren)
    
    Task(root.run_jscode_orders)
    
    effect_time = phira_resource_pack.globalPack.effectDuration
    miss_effect_time = 0.2
    bad_effect_time = 0.5
    
    effect_time *= speed
    miss_effect_time *= speed
    bad_effect_time *= speed
        
    def process_effect(
        sec_t: float,
        rblocks: tuple[tuple[float, float]],
        perfect: bool,
        position: tuple[float, float]
    ):
        p = (now_t - sec_t) / effect_time
        if not (0.0 <= p <= 1.0): return
        processClickEffect(*position, p, rblocks, perfect, Task)
    
    def process_miss(
        note: chartobj_rpe.Note
    ):
        t = chart_obj.sec2beat(now_t, note.masterLine.bpmfactor)
        p = (now_t - note.secst) / miss_effect_time
        linePos = tool_funcs.conrpepos(*line.GetPos(t, chart_obj)); linePos = (linePos[0] * w, linePos[1] * h)
        lineRotate = sum([line.GetEventValue(t, layer.rotateEvents, 0.0) for layer in line.eventLayers])
        pos = tool_funcs.rotate_point(
            *linePos,
            lineRotate,
            note.positionX2 * w
        )
        floorp = note.floorPosition - line.playingFloorPosition
        x, y = tool_funcs.rotate_point(
            *pos,
            (-90 if note.above == 1 else 90) + lineRotate,
            floorp * h
        )
        img_keyname = f"{note.type_string}{"_dub" if note.morebets else ""}"
        this_note_img = Resource["Notes"][img_keyname]
        imgname = f"Note_{img_keyname}"
        Task(
            root.run_js_code,
            f"ctx.drawRotateImage(\
                {root.get_img_jsvarname(imgname)},\
                {x},\
                {y},\
                {noteWidth * note.width},\
                {noteWidth / this_note_img.width * this_note_img.height},\
                {lineRotate},\
                {note.float_alpha * (1 - p ** 0.5)}\
            );",
            add_code_array = True
        )
    
    def process_bad(
        note: chartobj_rpe.Note
    ):
        p = (now_t - note.player_badtime) / bad_effect_time
            
        if note.player_bad_posandrotate is None:
            t = chart_obj.sec2beat(note.player_badtime, note.masterLine.bpmfactor)
            linePos = tool_funcs.conrpepos(*line.GetPos(t, chart_obj)); linePos = (linePos[0] * w, linePos[1] * h)
            lineRotate = sum([line.GetEventValue(t, layer.rotateEvents, 0.0) for layer in line.eventLayers])
            pos = tool_funcs.rotate_point(
                *linePos,
                lineRotate,
                note.positionX2 * w
            )
            x, y = tool_funcs.rotate_point(
                *pos,
                (-90 if note.above == 1 else 90) + lineRotate,
                note.masterLine.GetFloorPositionRange(t, note.startTime.value) * h
            )
            note.player_bad_posandrotate = ((x, y), lineRotate)
        
        (x, y), nr = note.player_bad_posandrotate
            
        this_note_img = Resource["Notes"]["Bad"]
        Task(
            root.run_js_code,
            f"ctx.drawRotateImage(\
                {root.get_img_jsvarname("Note_Bad")},\
                {x},\
                {y},\
                {noteWidth * note.width * (const.NOTE_DUB_FIXSCALE if note.morebets else 1.0)},\
                {noteWidth / this_note_img.width * this_note_img.height},\
                {nr},\
                {note.float_alpha * (1 - p ** 3)}\
            );",
            add_code_array = True
        )
    
    if noautoplay:
        for pplmckfi in pplm.clickeffects.copy():
            perfect, eft, erbs, position = pplmckfi
            if eft <= now_t <= eft + effect_time:
                process_effect(eft, erbs, perfect, position(w, h))
            
            if eft + effect_time < now_t:
                pplm.clickeffects.remove(pplmckfi)
                
    for line in chart_obj.judgeLineList:
        for note in line.effectNotes.copy():
            if not noautoplay and not note.clicked: break
            
            if not noautoplay:
                for eft, erbs, position in note.effect_times:
                    if eft <= now_t <= eft + effect_time:
                        process_effect(eft, erbs, True, position(w, h))
            else: # noautoplay
                if note.state == const.NOTE_STATE.MISS:
                    if 0.0 <= now_t - note.secst <= miss_effect_time and not note.ishold:
                        process_miss(note)
                elif note.state == const.NOTE_STATE.BAD:
                    if 0.0 <= now_t - note.player_badtime <= bad_effect_time:
                        process_bad(note)
                
            if note.effect_times[-1][0] + max(
                effect_time,
                miss_effect_time,
                bad_effect_time
            ) + 0.2 < now_t:
                line.effectNotes.remove(note)
    
    combo = chart_obj.getCombo(now_t) if not noautoplay else pplm.ppps.getCombo()
    now_t /= speed
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = get_stringscore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else get_stringscore(pplm.ppps.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        acc = "100.00%" if not noautoplay else f"{(pplm.ppps.getAcc() * 100):.2f}%",
        clear = False,
        background = False,
        **deleteDrwaUIKwargsDefaultValues(attachUIData)
    )
    now_t += chart_obj.META.offset / 1000
    
    rrm_end(Task)
    if rjc: Task(root.run_js_wait_code)
    
    if now_t >= raw_audio_length:
        Task.ExTask.append(("break", ))
    
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

def BeginLoadingAnimation(p: float, clear: bool = True, fcb: typing.Callable[[], typing.Any] = lambda: None) -> chartobj_phi.FrameRenderTask:
    Task = chartobj_phi.FrameRenderTask([], [])
    
    if clear: Task(root.clear_canvas, wait_execute = True)
    all_ease_value = tool_funcs.begin_animation_eases.im_ease(p)
    background_ease_value = tool_funcs.begin_animation_eases.background_ease(p) * 1.25
    info_data_ease_value = tool_funcs.begin_animation_eases.info_data_ease((p - 0.2) * 3.25)
    info_data_ease_value_2 = tool_funcs.begin_animation_eases.info_data_ease((p - 0.275) * 3.25)
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
        fillStyle = f"rgba(255, 255, 255, {tool_funcs.begin_animation_eases.tip_alpha_ease(p)})",
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
    
    baimg_w = w * im_size
    baimg_h = h * im_size
    dpower = tool_funcs.getDPower(baimg_w, baimg_h, 75)
    Task(
        root.run_js_code,
        f"ctx.drawDiagonalRectangleClipImage(\
            {w * 0.65 - baimg_w / 2}, {h * 0.5 - baimg_h / 2},\
            {w * 0.65 + baimg_w / 2}, {h * 0.5 + baimg_h / 2},\
            {root.get_img_jsvarname("begin_animation_image")},\
            0, 0, {baimg_w}, {baimg_h}, {dpower}, 1.0\
        );",
        add_code_array = True
    )
    
    Task(
        root.run_js_code,
        f"ctx.translate(-{all_ease_value * w},0.0);",
        add_code_array = True
    )
    
    Task(root.run_js_wait_code)
    return Task

def BeginJudgeLineAnimation(p: float) -> chartobj_phi.FrameRenderTask:
    Task = chartobj_phi.FrameRenderTask([], [])
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
        strokeStyle = const.JUDGELINE_PERFECT_COLOR,
        lineWidth = JUDGELINE_WIDTH / render_range_more_scale if render_range_more else JUDGELINE_WIDTH,
        wait_execute = True
    )
    Task(root.run_js_wait_code)
    return Task

def Begin_Animation(clear: bool = True, fcb: typing.Callable[[], typing.Any] = lambda: None):
    animation_time = 4.5
    
    chart_name_text = chart_information["Name"]
    chart_name_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(chart_name_text)}).width;") / 50
    chart_level_number = Get_LevelNumber()
    chart_level_number_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(chart_level_number) if len(chart_level_number) >= 2 else "'00'"}).width;") / 50
    if len(chart_level_number) == 1:
        chart_level_number_width_1px /= 1.35
    chart_level_text = Get_LevelText()
    chart_level_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(chart_level_text) if len(chart_level_text) >= 2 else "'00'"}).width;") / 50
    chart_artist_text = chart_information["Artist"]
    chart_artist_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(chart_artist_text)}).width;") / 50
    chart_charter_text = chart_information["Charter"]
    chart_charter_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(chart_charter_text)}).width;") / 50
    chart_illustrator_text = chart_information["Illustrator"]
    chart_illustrator_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(chart_illustrator_text)}).width;") / 50
    tip = phi_tips.get_tip()
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
    
    CoreConfigureEx(PhiCoreConfigure(
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

def initFinishAnimation(pplm: tool_funcs.PhigrosPlayLogicManager|None = None):
    global im_size
    global ChartNameString, ChartNameStringFontSize
    global ChartLevelString, ChartLevelStringFontSize
    global ScoreString, LevelName, MaxCombo, AccString
    global PerfectCount, GoodCount, BadCount, MissCount
    global EarlyCount, LateCount
    
    im_size = 0.475
    LevelName = "AP" if not noautoplay else pplm.ppps.getLevelString()
    EarlyCount = 0 if not noautoplay else pplm.ppps.getEarlyCount()
    LateCount = 0 if not noautoplay else pplm.ppps.getLateCount()
    PerfectCount = chart_obj.note_num if not noautoplay else pplm.ppps.getPerfectCount()
    GoodCount = 0 if not noautoplay else pplm.ppps.getGoodCount()
    BadCount = 0 if not noautoplay else pplm.ppps.getBadCount()
    MissCount = 0 if not noautoplay else pplm.ppps.getMissCount()
    Acc = 1.0 if not noautoplay else pplm.ppps.getAcc()
    ScoreString = "1000000" if not noautoplay else get_stringscore(pplm.ppps.getScore())
    MaxCombo = chart_obj.note_num if not noautoplay else pplm.ppps.getMaxCombo()
    AccString = f"{(Acc * 100):.2f}%"
    ChartNameString = chart_information["Name"]
    ChartNameStringFontSize = w * im_size * 0.65 / (root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(ChartNameString)}).width;") / 50)
    ChartLevelString = chart_information["Level"]
    ChartLevelStringFontSize = w * im_size * 0.25 / (root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(ChartLevelString)}).width;") / 50)
    if ChartNameStringFontSize > w * 0.0275:
        ChartNameStringFontSize = w * 0.0275
    if ChartLevelStringFontSize > w * 0.0275 * 0.5:
        ChartLevelStringFontSize = w * 0.0275 * 0.5

def Chart_Finish_Animation_Frame(p: float, rjc: bool = True):
    root.clear_canvas(wait_execute = True)
    im_ease_value = tool_funcs.finish_animation_eases.all_ease(p)
    im_ease_pos = w * 1.25 * (1 - im_ease_value)
    data_block_1_ease_value = tool_funcs.finish_animation_eases.all_ease(p - 0.015)
    data_block_1_ease_pos = w * 1.25 * (1 - data_block_1_ease_value)
    data_block_2_ease_value = tool_funcs.finish_animation_eases.all_ease(p - 0.035)
    data_block_2_ease_pos = w * 1.25 * (1 - data_block_2_ease_value)
    data_block_3_ease_value = tool_funcs.finish_animation_eases.all_ease(p - 0.055)
    data_block_3_ease_pos = w * 1.25 * (1 - data_block_3_ease_value)
    button_ease_value = tool_funcs.finish_animation_eases.button_ease(p * 4.5 - 0.95)
    level_size = 0.125
    level_size *= tool_funcs.finish_animation_eases.level_size_ease(p)
    button_ease_pos = - w * const.FINISH_UI_BUTTON_SIZE * (1 - button_ease_value)
    
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
        fillStyle = f"rgba(255, 255, 255, {tool_funcs.finish_animation_eases.score_alpha_ease(p)})",
        wait_execute = True
    )
    
    root.run_js_code(
        f"ctx.globalAlpha = {tool_funcs.finish_animation_eases.level_alpha_ease(p)};",
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
        f"ctx.globalAlpha = {tool_funcs.finish_animation_eases.playdata_alpha_ease(p - 0.02)}",
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
        f"ctx.globalAlpha = {tool_funcs.finish_animation_eases.playdata_alpha_ease(p - 0.04)}",
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
    
    Retry_Button_Width = w * const.FINISH_UI_BUTTON_SIZE
    Retry_Button_Height = w * const.FINISH_UI_BUTTON_SIZE / 190 * 145
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
        button_ease_pos + w * const.FINISH_UI_BUTTON_SIZE * 0.3 - Retry_imsize / 2,
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
        w - (button_ease_pos + w * const.FINISH_UI_BUTTON_SIZE * 0.35 + Continue_imsize / 2),
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