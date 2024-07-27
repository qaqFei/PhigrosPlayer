from os import mkdir, chdir, environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = str()
from os.path import exists, isfile, abspath, dirname
from sys import argv
from ctypes import windll
from tempfile import gettempdir
from time import time, sleep
from random import randint, seed
from threading import Thread
import typing
import json

from PIL import Image
from pygame import mixer
import webcvapis

import Chart_Objects_Ppre
import Tool_Functions
import Const

def validFile(fp: str) -> bool:
    return exists(fp) and isfile(fp)

def exitProcess(state: int = 0, text: str = "") -> typing.NoReturn:
    if text: print(text)
    windll.kernel32.ExitProcess(state)

if len(argv) < 3:
    print("Usage: ChartEditer <chart> <audio>")
    print("    if <chart> is __create__, it will create a empty chart.")
    exitProcess()

mixer.init()
sysTempDir = gettempdir()
tempDir = f"{sysTempDir}\\qfppr_editer_{time() * randint(0, 2 << 31)}"
try: mkdir(tempDir)
except FileExistsError: pass
    
ChartFp = argv[1]
AudioFp = argv[2]

if ChartFp == "__create__": # create a empty chart.
    ChartFp = f"{tempDir}\\emptyChart.json"
    with open(ChartFp, "w", encoding="utf-8") as f:
        chartData = {
            "lines": []
        }
        f.write(json.dumps(chartData, ensure_ascii=False))
    del f, chartData

ChartFp = abspath(ChartFp)
AudioFp = abspath(AudioFp)

if not validFile(ChartFp): exitProcess(1, "invaild chart file.")
if not validFile(AudioFp): exitProcess(1, "invaild audio file.")
mixer.music.load(AudioFp)

selfdir = dirname(argv[0])
if selfdir == "": selfdir = abspath(".")
chdir(selfdir)

with open(ChartFp, "r", encoding="utf-8") as f:
    try: ChartJsonData = json.load(f)
    except Exception as e: exitProcess(1, f"load chart as json data error: {repr(e)}")
    if not isinstance(ChartJsonData, dict):
        exitProcess(1, "load chart as json data error: the chart file load as json data type is not a dict.")
    ChartObject = Chart_Objects_Ppre.Chart(
        lines = [
            Chart_Objects_Ppre.judgeLine(
                bpm = lineItem.get("bpm", 140.0), # default bpm is 140; but in fact normal why bpm is not exists in chart file???
                notes = [
                    Chart_Objects_Ppre.note(
                        time = noteItem.get("time", 0.0),
                        type = noteItem.get("type", 1), # default note type is tap.
                        holdtime = noteItem.get("holdtime", 0.0),
                        positionX = noteItem.get("positionX", 0.0),
                        speed = noteItem.get("speed", 1.0),
                        fake = noteItem.get("fake", False),
                        above = noteItem.get("above", True)
                    )
                    for noteItem in lineItem.get("notes", [])
                ],
                speedEvents = [
                    Chart_Objects_Ppre.speedEvent(
                        startTime = speedItem.get("startTime", 0.0),
                        endTime = speedItem.get("endTime", 0.0),
                        value = speedItem.get("value", 0.0)
                    )
                    for speedItem in lineItem.get("speedEvents", [])
                ],
                alphaEvents = [
                    Chart_Objects_Ppre.alphaEvent(
                        startTime = alphaItem.get("startTime", 0.0),
                        endTime = alphaItem.get("endTime", 0.0),
                        start = alphaItem.get("start", 0.0),
                        end = alphaItem.get("end", 0.0),
                        easingType = alphaItem.get("easingType", 1)
                    )
                    for alphaItem in lineItem.get("alphaEvents", [])
                ],
                moveEvents = [
                    Chart_Objects_Ppre.moveEvent(
                        startTime = moveItem.get("startTime", 0.0),
                        endTime = moveItem.get("endTime", 0.0),
                        startX = moveItem.get("startX", 0.0),
                        startY = moveItem.get("startY", 0.0),
                        endX = moveItem.get("endX", 0.0),
                        endY = moveItem.get("endY", 0.0),
                        easingType = moveItem.get("easingType", 1)
                    )
                    for moveItem in lineItem.get("moveEvents", [])
                ],
                rotateEvents = [
                    Chart_Objects_Ppre.alphaEvent(
                        startTime = rotateItem.get("startTime", 0.0),
                        endTime = rotateItem.get("endTime", 0.0),
                        start = rotateItem.get("start", 0.0),
                        end = rotateItem.get("end", 0.0),
                        easingType = rotateItem.get("easingType", 1)
                    )
                    for rotateItem in lineItem.get("rotateEvents", [])
                ]
            )
            for lineItem in ChartJsonData.get("lines", [])
        ]
    )
del f

def Load_Resource():
    global ClickEffect_Size, Note_width
    global note_max_width, note_max_height
    global note_max_width_half, note_max_height_half
    
    print("Loading Resource...")
    Note_width = (0.125 * w + 0.2 * h / 2) / 2
    ClickEffect_Size = Note_width * 1.375
    Resource = {
        "Notes":{
            "Tap": Image.open("./Resources/Notes/Tap.png"),
            "Tap_dub": Image.open("./Resources/Notes/Tap_dub.png"),
            "Drag": Image.open("./Resources/Notes/Drag.png"),
            "Drag_dub": Image.open("./Resources/Notes/Drag_dub.png"),
            "Flick": Image.open("./Resources/Notes/Flick.png"),
            "Flick_dub": Image.open("./Resources/Notes/Flick_dub.png"),
            "Hold_Head": Image.open("./Resources/Notes/Hold_Head.png"),
            "Hold_Head_dub": Image.open("./Resources/Notes/Hold_Head_dub.png"),
            "Hold_End": Image.open("./Resources/Notes/Hold_End.png"),
            "Hold_End_dub": Image.open("./Resources/Notes/Hold_End_dub.png"),
            "Hold_Body": Image.open("./Resources/Notes/Hold_Body.png"),
            "Hold_Body_dub": Image.open("./Resources/Notes/Hold_Body_dub.png"),
            "Tap_Bad": Image.open("./Resources/Notes/Tap_Bad.png")
        },
        "Note_Click_Effect":{
            "Perfect":[
                Image.open(f"./Resources/Note_Click_Effect/Perfect/{i + 1}.png")
                for i in range(30)
            ]
        },
        "Note_Click_Audio":{
            "Tap": open("./Resources/Note_Click_Audio/Tap.wav", "rb").read(),
            "Drag": open("./Resources/Note_Click_Audio/Drag.wav", "rb").read(),
            "Hold": open("./Resources/Note_Click_Audio/Hold.wav", "rb").read(),
            "Flick": open("./Resources/Note_Click_Audio/Flick.wav", "rb").read()
        }
    }
    
    for k,v in Resource["Notes"].items(): # Resize Notes (if Notes is too big) and reg them
        if v.width > Note_width:
            Resource["Notes"][k] = v.resize((int(Note_width),int(Note_width / v.width * v.height)))
        webcv.reg_img(Resource["Notes"][k], f"Note_{k}")
    
    for i in range(30): # reg click effect
        webcv.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
        
    with open("./Resources/font.ttf", "rb") as f:
        webcv.reg_res(f.read(), "PhigrosFont")
    with open(AudioFp, "rb") as f:
        webcv.reg_res(f.read(), "ChartAudio")
    webcv.load_allimg()
    webcv.run_js_code(f"loadFont('PhigrosFont',\"{webcv.get_resource_path("PhigrosFont")}\");")
    while not webcv.run_js_code("font_loaded;"):
        sleep(0.1)
    
    webcv.shutdown_fileserver()
    print("Loading Resource Successfully.")
    note_max_width = max(
        [
            Resource["Notes"]["Tap"].width,
            Resource["Notes"]["Tap_dub"].width,
            Resource["Notes"]["Drag"].width,
            Resource["Notes"]["Drag_dub"].width,
            Resource["Notes"]["Flick"].width,
            Resource["Notes"]["Flick_dub"].width,
            Resource["Notes"]["Hold_Head"].width,
            Resource["Notes"]["Hold_Head_dub"].width,
            Resource["Notes"]["Hold_End"].width
        ]
    )
    note_max_height = max(
        [
            Resource["Notes"]["Tap"].height,
            Resource["Notes"]["Tap_dub"].height,
            Resource["Notes"]["Drag"].height,
            Resource["Notes"]["Drag_dub"].height,
            Resource["Notes"]["Flick"].height,
            Resource["Notes"]["Flick_dub"].height,
            Resource["Notes"]["Hold_Head"].height,
            Resource["Notes"]["Hold_Head_dub"].height,
            Resource["Notes"]["Hold_End"].height
        ]
    )
    note_max_width_half = note_max_width / 2
    note_max_height_half = note_max_height / 2
    return Resource

def updateMorebets():
    notes = [i for line in ChartObject.lines for i in line.notes if not i.fake]
    times = {}
    for note in notes:
        if note.time not in times:
            times[note.time] = [note]
        else:
            times[note.time].append(note)
    for v in times.values():
        if len(v) >= 2:
            for i in v:
                i.morebets = True
        else:
            for i in v:
                i.morebets = False

def getEffectRandomBlocksByObject(sed: int):
    seed(sed)
    return tuple((randint(1, 90) for _ in range(4)))

def renderChartView(nt: float): # sec
    webcv.create_rectangle(0, 0, w, h / 2, fillStyle="rgb(0, 120, 215)", wait_execute=True)
        
    for line in ChartObject.lines:
        lineTime = nt / (1 / line.bpm)
        lineAlpha = line.getAlpha(lineTime)
        linePos = line.getMove(lineTime)
        lineRotate = line.getRotate(lineTime)
        
        linePos = (linePos[0] * w, linePos[1] * h / 2)
        lineDrawPos = (
            *Tool_Functions.rotate_point(*linePos, -lineRotate, 5.76 * h / 2),
            *Tool_Functions.rotate_point(*linePos, -lineRotate + 180, 5.76 * h / 2)
        )
        lineColor = (254, 255, 16, lineAlpha)
        lineWebColor = f"rgba{lineColor}"
        if lineColor[-1] > 0.0:
            Tool_Functions.judgeLine_can_render(lineDrawPos, w, h / 2)
            webcv.create_line(
                *lineDrawPos,
                lineWidth = JUDGELINE_WIDTH,
                strokeStyle = lineWebColor,
                wait_execute = True
            )
        
        def process(note: Chart_Objects_Ppre.note):
            if note.type != Const.Note.HOLD and note.time < lineTime:
                return None
            elif note.type == Const.Note.HOLD and note.time + note.holdtime < lineTime:
                return None
            
            holdLength = note.holdtime * (1 / line.bpm) * note.speed * PHIGROS_Y if note.type == Const.Note.HOLD else 0.0
            
            if not (note.type == Const.Note.HOLD and note.time < lineTime):
                noteFloorPosition = line.getNoteFloorPosition(lineTime, note) * PHIGROS_Y
            else:
                noteFloorPosition = - (1.0 - (note.time + note.holdtime - lineTime) / note.holdtime) * holdLength
            
            if noteFloorPosition > (h / 2) * 2:
                return None
            
            rotatenote_at_judgeLine_pos = Tool_Functions.rotate_point(
                *linePos, -lineRotate, note.positionX * PHIGROS_X
            )
            judgeLine_to_note_rotate_deg = (-90 if note.above else 90) - lineRotate
            x, y = Tool_Functions.rotate_point(
                *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, noteFloorPosition
            )
                
            if note.type == Const.Note.HOLD:
                note_hold_draw_length = noteFloorPosition + holdLength
                holdend_x, holdend_y = Tool_Functions.rotate_point(
                    *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_hold_draw_length
                )
                if note.time < lineTime:
                    holdhead_pos = rotatenote_at_judgeLine_pos
                else:
                    holdhead_pos = x, y
                holdbody_range = (
                    Tool_Functions.rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                    Tool_Functions.rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                    Tool_Functions.rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                    Tool_Functions.rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                )
        
            noteCanRender = (
                Tool_Functions.Note_CanRender(w, h / 2, note_max_width_half, note_max_height_half, x, y)
                if note.type != Const.Note.HOLD
                else Tool_Functions.Note_CanRender(w, h / 2, note_max_width_half, note_max_height_half, x, y, holdbody_range)
            )
            
            if noteCanRender:
                lineRotateNote = (judgeLine_to_note_rotate_deg + 90) % 360
                dub_text = "_dub" if note.morebets else ""
                if note.type != Const.Note.HOLD:
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
                
                fix_scale = Const.NOTE_DUB_FIXSCALE if note.morebets else 1.0 # because the note img if has morebets frame, the note will be look small, so we will `*` a fix scale to fix the frame size make the note look is small.
                this_note_width = Note_width * fix_scale
                this_note_height = Note_width / this_note_img.width * this_note_img.height
                
                if note.type == Const.Note.HOLD:
                    this_noteend_height = Note_width / this_note_img_end.width * this_note_img_end.height
                    
                    if note.time < lineTime:
                        holdbody_x, holdbody_y = rotatenote_at_judgeLine_pos
                        holdbody_length = note_hold_draw_length - this_noteend_height / 2
                    else:
                        holdbody_x, holdbody_y = Tool_Functions.rotate_point(
                            *holdhead_pos, judgeLine_to_note_rotate_deg, this_note_height / 2
                        )
                        holdbody_length = holdLength - (this_note_height + this_noteend_height) / 2
                    
                    webcv.run_js_code(
                        f"ctx.drawRotateImage(\
                            {webcv.get_img_jsvarname(this_note_imgname_end)},\
                            {holdend_x},\
                            {holdend_y},\
                            {this_note_width},\
                            {this_noteend_height},\
                            {lineRotateNote},\
                            1.0\
                        );",
                        add_code_array = True
                    )
                    
                    if holdbody_length > 0.0:
                        webcv.run_js_code(
                            f"ctx.drawAnchorESRotateImage(\
                                {webcv.get_img_jsvarname(this_note_imgname_body)},\
                                {holdbody_x},\
                                {holdbody_y},\
                                {this_note_width},\
                                {holdbody_length},\
                                {lineRotateNote},\
                                1.0\
                            );",
                            add_code_array = True
                        )
                
                if not (note.type == Const.Note.HOLD and note.time < lineTime):
                    webcv.run_js_code(
                        f"ctx.drawRotateImage(\
                            {webcv.get_img_jsvarname(this_note_imgname)},\
                            {x},\
                            {y},\
                            {this_note_width},\
                            {this_note_height},\
                            {lineRotateNote},\
                            1.0\
                        );",
                        add_code_array = True
                    )
            
        for i in line.notes:
            process(i)
    
    effect_time = 0.5
    def process_effect(
        note: Chart_Objects_Ppre.note,
        t:float, t_sec:float, line: Chart_Objects_Ppre.judgeLine,
        effect_random_blocks
    ):
        p = (nt - t_sec) / effect_time
        if not (0.0 <= p <= 1.0): return None
        linePos = line.getMove(t)
        linePos = [linePos[0] * w, linePos[1] * h / 2]
        lineRotate = line.getRotate(t)
        x, y = Tool_Functions.rotate_point(
            *linePos,
            -lineRotate,
            note.positionX * PHIGROS_X
        )
        color = (254, 255, 169)
        imn = "Note_Click_Effect_Perfect"
        beforedeg = 0
        for deg in effect_random_blocks:
            block_alpha = (1.0 - p) * 0.85
            effect_random_point = Tool_Functions.rotate_point(
                x, y, beforedeg + deg,
                ClickEffect_Size * Tool_Functions.ease_out(p) / 1.25
            )
            block_size = EFFECT_RANDOM_BLOCK_SIZE
            if p > 0.65: block_size -= (p - 0.65) * EFFECT_RANDOM_BLOCK_SIZE
            webcv.create_rectangle(
                effect_random_point[0] - block_size,
                effect_random_point[1] - block_size,
                effect_random_point[0] + block_size,
                effect_random_point[1] + block_size,
                fillStyle = f"rgba{color + (block_alpha, )}",
                wait_execute = True
            )
            beforedeg += 90
        webcv.create_image(
            f"{imn}_{int(p * (30 - 1)) + 1}",
            x - ClickEffect_Size / 2,
            y - ClickEffect_Size / 2,
            ClickEffect_Size, ClickEffect_Size,
            wait_execute = True
        )
        
    for line in ChartObject.lines:
        beatTime = 1 / line.bpm
        lineTime = nt / beatTime
        for note in line.notes:
            noteTimeSec = note.time * beatTime
            if note.fake:
                continue
            
            if note.time < lineTime:
                if nt - noteTimeSec <= effect_time:
                    process_effect(
                        note,
                        note.time,
                        note.time * beatTime,
                        line,
                        getEffectRandomBlocksByObject(id(note)),
                    )
                
                if note.type == Const.Note.HOLD:
                    hold_t = note.holdtime * beatTime
                    hold_et = noteTimeSec + hold_t
                    efct_et = hold_et + effect_time
                    efct_spt = 1 / line.bpm * 30
                    if efct_et >= nt:
                        temp_time = noteTimeSec + efct_spt
                        while temp_time < nt and temp_time < hold_et:
                            process_effect(
                                note,
                                temp_time / beatTime,
                                temp_time,
                                line,
                                getEffectRandomBlocksByObject(id(note) + temp_time),
                            )
                            temp_time += efct_spt
    
    webcv.clear_rectangle(0, h / 2, w, h, wait_execute=True)

def renderEventView():
    pass

def __():
    updateMorebets()
    
    st = time()
    mixer.music.play()
    while True:
        webcv.clear_canvas(wait_execute=True)
        renderChartView(time() - st)
        renderEventView()
        webcv.run_js_wait_code()

webcv = webcvapis.WebCanvas(
    width = 0, height = 0,
    x = 0, y = 0,
    debug = "--debug" in argv,
    title = "PhigrosPlayer - ChartEditer",
    resizable = False,
    html_path = ".\\web_canvas_editer.html"
)
webdpr = webcv.run_js_code("window.devicePixelRatio;")
w, h = int(webcv.winfo_screenwidth() * 0.61803398874989484820458683436564 * 0.7), int(webcv.winfo_screenheight() * 0.61803398874989484820458683436564 * 0.7 * 2)
webcv.resize(w, h)
w_legacy, h_legacy = webcv.winfo_legacywindowwidth(), webcv.winfo_legacywindowheight()
dw_legacy, dh_legacy = w - w_legacy, h - h_legacy
dw_legacy *= webdpr; dh_legacy *= webdpr
dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
del w_legacy, h_legacy
webcv.resize(w + dw_legacy, h + dh_legacy)
webcv.move(int(webcv.winfo_screenwidth() / 2 - (w + dw_legacy) / webdpr / 2), int(webcv.winfo_screenheight() / 2 - (h + dh_legacy) / webdpr / 2))
PHIGROS_X, PHIGROS_Y = 0.05625 * w, 0.6 * h / 2
JUDGELINE_WIDTH = h * 0.0075 / 2
EventEdit_uiDy = 0.0
Resource = Load_Resource()
EFFECT_RANDOM_BLOCK_SIZE = Note_width / 12.5
Thread(target=__, daemon=True).start()
webcv.loop_to_close()
exitProcess(0)