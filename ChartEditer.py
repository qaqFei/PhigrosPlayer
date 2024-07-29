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
import dataclasses

from PIL import Image
from pygame import mixer
import webcvapis

import Chart_Objects_Ppre
import Tool_Functions
import Const
import rpe_easing

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

MousePos = (0, 0)

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
                    Chart_Objects_Ppre.rotateEvent(
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
    global IconSize
    
    print("Loading Resource...")
    Note_width = (0.125 * w + 0.2 * h) / 2 / 2
    ClickEffect_Size = Note_width * 1.375
    IconSize = (w / 2 + h) / 100
    Resource = {
        "Notes": {
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
        "Note_Click_Effect": {
            "Perfect":[
                Image.open(f"./Resources/Note_Click_Effect/Perfect/{i + 1}.png")
                for i in range(30)
            ]
        },
        "Note_Click_Audio": {
            "Tap": open("./Resources/Note_Click_Audio/Tap.wav", "rb").read(),
            "Drag": open("./Resources/Note_Click_Audio/Drag.wav", "rb").read(),
            "Hold": open("./Resources/Note_Click_Audio/Hold.wav", "rb").read(),
            "Flick": open("./Resources/Note_Click_Audio/Flick.wav", "rb").read()
        },
        "Icons": {
            "Play": Image.open("./Resources/Edit_Play.png"),
            "Pause": Image.open("./Resources/Edit_Pause.png"),
            "ChangeValue": Image.open("./Resources/Edit_ChangeValue.png"),
            "Back": Image.open("./Resources/Edit_Back.png"),
            "Save": Image.open("./Resources/Edit_Save.png"),
            "Replay": Image.open("./Resources/Edit_Replay.png"),
            "Add": Image.open("./Resources/Edit_Add.png"),
            "Delete": Image.open("./Resources/Edit_Delete.png")
        }
    }
    
    for k,v in Resource["Notes"].items(): # Resize Notes (if Notes is too big) and reg them
        if v.width > Note_width:
            Resource["Notes"][k] = v.resize((int(Note_width),int(Note_width / v.width * v.height)))
        webcv.reg_img(Resource["Notes"][k], f"Note_{k}")
    
    for i in range(30): # reg click effect
        webcv.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
    
    for k, v in Resource["Icons"].items():
        webcv.reg_img(v, f"Icon_{k}")
        
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
    webcv.create_rectangle(0, 0, w / 2, h / 2, fillStyle="rgb(0, 120, 215)", wait_execute=True)
        
    for line in ChartObject.lines:
        lineTime = nt / (60 / line.bpm)
        lineAlpha = line.getAlpha(lineTime)
        linePos = line.getMove(lineTime)
        lineRotate = line.getRotate(lineTime)
        
        linePos = (linePos[0] * w / 2, linePos[1] * h / 2)
        lineDrawPos = (
            *Tool_Functions.rotate_point(*linePos, -lineRotate, 5.76 * h / 2),
            *Tool_Functions.rotate_point(*linePos, -lineRotate + 180, 5.76 * h / 2)
        )
        lineColor = (254, 255, 16, lineAlpha)
        lineWebColor = f"rgba{lineColor}"
        if lineColor[-1] > 0.0:
            Tool_Functions.judgeLine_can_render(lineDrawPos, w / 2, h / 2)
            webcv.create_line(
                *lineDrawPos,
                lineWidth = JUDGELINE_WIDTH,
                strokeStyle = lineWebColor,
                wait_execute = True
            )
            
        webcv.create_text(
            *Tool_Functions.rotate_point(*linePos, 90 - lineRotate - 180, (w + h) / 75 / 2),
            text = f"{ChartObject.lines.index(line)}",
            font = f"{(w + h) / 85 / 0.75 / 2}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            strokeStyle = "rgba(254, 255, 169, 0.5)",
            fillStyle = "rgba(254, 255, 169, 0.5)",
            wait_execute = True
        )
        
        webcv.create_rectangle(
            linePos[0] - (w + h) / 250 / 2,
            linePos[1] - (w + h) / 250 / 2,
            linePos[0] + (w + h) / 250 / 2,
            linePos[1] + (w + h) / 250 / 2,
            fillStyle = "rgb(238, 130, 238)",
            wait_execute = True
        )
        
        def process(note: Chart_Objects_Ppre.note):
            if note.type != Const.Note.HOLD and note.time < lineTime:
                return None
            elif note.type == Const.Note.HOLD and note.time + note.holdtime < lineTime:
                return None
            
            holdLength = note.holdtime * (60 / line.bpm) * note.speed * PHIGROS_Y if note.type == Const.Note.HOLD else 0.0
            
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
                Tool_Functions.Note_CanRender(w / 2, h / 2, note_max_width_half, note_max_height_half, x, y)
                if note.type != Const.Note.HOLD
                else Tool_Functions.Note_CanRender(w / 2, h / 2, note_max_width_half, note_max_height_half, x, y, holdbody_range)
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
        if note.fake: return None
        p = (nt - t_sec) / effect_time
        if not (0.0 <= p <= 1.0): return None
        linePos = line.getMove(t)
        linePos = [linePos[0] * w / 2, linePos[1] * h / 2]
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
        beatTime = 60 / line.bpm
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
    
    webcv.clear_rectangle(0, h / 2, w / 2, h, wait_execute=True)
    webcv.clear_rectangle(w / 2, 0, w, h, wait_execute=True)

def getEventViewTimeLengthPx(t: float):
    return h / 2 * (t / EventEdit_viewRange)

def inRect(rect, x, y):
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]

def MouseDown(x, y, button):
    global EventEdit_lineIndex
    global isPlaying
    global EventEdit_uiDy, PlayTime
    global eventEditing, editingEvent
    global eventAdding, addingEvent
    global noteEditing, editingNote
    
    if inRect(JudgeLineIndexChangeValueRect, x, y) and button == 0:
        result = webcv.run_js_code(f"prompt('Please input judgeLine index(0 ~ {len(ChartObject.lines) - 1}): ');")
        if result in list(map(str, range(0, len(ChartObject.lines)))):
            EventEdit_lineIndex = int(result)
        elif result is not None:
            webcv.run_js_code("alert('Invalid index.');")
    elif inRect(PlayButtonRect, x, y) and button == 0:
        isPlaying = not isPlaying
    elif inRect(ReplayButtonRect, x, y) and button == 0:
        isPlaying, EventEdit_uiDy, PlayTime = False, 0.0, 0.0
    elif inRect(AddJudgeLineRect, x, y) and button == 0:
        bpm = parseFloat(webcv.run_js_code("prompt('Please input bpm: ');"), -float("inf"))
        if bpm != -float("inf") and bpm > 0.0:
            ChartObject.lines.append(Chart_Objects_Ppre.judgeLine(
                bpm = bpm, notes = [], speedEvents = [], alphaEvents = [], moveEvents = [], rotateEvents = []
            ))
            webcv.run_js_code(f"alert('JudgeLine added. index: {len(ChartObject.lines) - 1}');")
        else:
            webcv.run_js_code("alert('Invalid bpm.');")
    elif inRect(DeleteJudgeLineRect, x, y) and button == 0:
        if webcv.run_js_code("prompt('delete this judge line(input \\'true\\' or \\'false\\')?');") == "true":
            line = ChartObject.lines[EventEdit_lineIndex]
            EventEdit_lineIndex = max(0, EventEdit_lineIndex - 1)
            fixOutRangeViewIndex()
            ChartObject.lines.remove(line)
            webcv.run_js_code("alert('JudgeLine deleted.');")
    elif inRect(getEventViewRect(1), x, y) and button == 0 and not eventEditing:
        e = getEventByyPos(y, ChartObject.lines[EventEdit_lineIndex].speedEvents)
        if e is None: return
        eventEditing, editingEvent = True, e
        webcv.run_js_code(f'''
            eventDataInput({"{"}
                startTime: {e.startTime},
                endTime: {e.endTime},
                startValue: {e.value},
                endValue: {e.value},
                easingType: -1,
                disableEasing: true
            {"}"}, _editEvent);
        ''')
    elif inRect(getEventViewRect(2), x, y) and button == 0 and not eventEditing:
        e = getEventByyPos(y, ChartObject.lines[EventEdit_lineIndex].alphaEvents)
        if e is None: return
        eventEditing, editingEvent = True, e
        webcv.run_js_code(f'''
            eventDataInput({"{"}
                startTime: {e.startTime},
                endTime: {e.endTime},
                startValue: {e.start},
                endValue: {e.end},
                easingType: {e.easingType}
            {"}"}, _editEvent);
        ''')
    elif inRect(getEventViewRect(3), x, y) and button == 0 and not eventEditing:
        e = getEventByyPos(y, ChartObject.lines[EventEdit_lineIndex].moveEvents)
        if e is None: return
        eventEditing, editingEvent = True, e
        webcv.run_js_code(f'''
            eventDataInput({"{"}
                startTime: {e.startTime},
                endTime: {e.endTime},
                startValue: '{e.startX}, {e.startY}',
                endValue: '{e.endX}, {e.endY}',
                easingType: {e.easingType}
            {"}"}, _editEvent);
        ''')
    elif inRect(getEventViewRect(4), x, y) and button == 0 and not eventEditing:
        e = getEventByyPos(y, ChartObject.lines[EventEdit_lineIndex].rotateEvents)
        if e is None: return
        eventEditing, editingEvent = True, e
        webcv.run_js_code(f'''
            eventDataInput({"{"}
                startTime: {e.startTime},
                endTime: {e.endTime},
                startValue: {e.start},
                endValue: {e.end},
                easingType: {e.easingType}
            {"}"}, _editEvent);
        ''')
    elif inRect(getEventViewRect(1), x, y) and button == 2 and not eventAdding:
        lineTime = getEventTimeByyPos(y)
        eventAdding, addingEvent = True, Chart_Objects_Ppre.speedEvent(lineTime, lineTime, 1.0)
    elif inRect(getEventViewRect(2), x, y) and button == 2 and not eventAdding:
        lineTime = getEventTimeByyPos(y)
        eventAdding, addingEvent = True, Chart_Objects_Ppre.alphaEvent(lineTime, lineTime, 1.0, 1.0, 1)
    elif inRect(getEventViewRect(3), x, y) and button == 2 and not eventAdding:
        lineTime = getEventTimeByyPos(y)
        eventAdding, addingEvent = True, Chart_Objects_Ppre.moveEvent(lineTime, lineTime, 0.5, 0.5, 0.5, 0.5, 1)
    elif inRect(getEventViewRect(4), x, y) and button == 2 and not eventAdding:
        lineTime = getEventTimeByyPos(y)
        eventAdding, addingEvent = True, Chart_Objects_Ppre.rotateEvent(lineTime, lineTime, 0, 0, 1)
    elif inRect(NoteViewRect, x, y) and button == 0 and not noteEditing:
        line = ChartObject.lines[EventEdit_lineIndex]
        for note in line.notes:
            if inRect(getNoteRect(note), x, y):
                noteEditing, editingNote = True, note
                webcv.run_js_code(f'''
                    noteDataInput({"{"}
                        time: {note.time},
                        type: {note.type},
                        holdtime: {note.holdtime},
                        positionX: {note.positionX},
                        speed: {note.speed},
                        fake: {note.fake},
                        above: {note.above}
                    {"}"}, _editNote)
                ''')
                break

def getNoteRect(note: Chart_Objects_Ppre.note):
    noteX = w / 2 + (note.positionX * PHIGROS_X + w / 4) * (5 / 8)
    noteY = (1.0 - (note.time - EventEdit_uiDy) / EventEdit_viewRange) * h / 2
    holdLength = getEventViewTimeLengthPx(note.holdtime)
    return (
        noteX - note_max_width_half * 1.25, noteY - note_max_height_half * 1.25 - holdLength,
        noteX + note_max_width_half * 1.25, noteY + note_max_height_half * 1.25
    )

def MouseUp(x: int, y: int, button: int):
    global eventAdding, addingEvent
    
    if eventAdding and addingEvent is not None and button == 2:
        addingEvent.endTime = getEventTimeByyPos(y)
        if isinstance(addingEvent, Chart_Objects_Ppre.speedEvent):
            ChartObject.lines[EventEdit_lineIndex].speedEvents.append(addingEvent)
        elif isinstance(addingEvent, Chart_Objects_Ppre.alphaEvent):
            ChartObject.lines[EventEdit_lineIndex].alphaEvents.append(addingEvent)
        elif isinstance(addingEvent, Chart_Objects_Ppre.moveEvent):
            ChartObject.lines[EventEdit_lineIndex].moveEvents.append(addingEvent)
        elif isinstance(addingEvent, Chart_Objects_Ppre.rotateEvent):
            ChartObject.lines[EventEdit_lineIndex].rotateEvents.append(addingEvent)
        addingEvent.startTime, addingEvent.endTime = sorted((addingEvent.startTime, addingEvent.endTime))
        eventAdding, addingEvent = False, None

def MouseMoving(x: int, y: int):
    global MousePos
    MousePos = (x, y)
    if eventAdding and addingEvent is not None:
        addingEvent.endTime = getEventTimeByyPos(y)

def getEventViewRect(n: int):
    return (
        w / 2 * (1.2 / 8 * (n - 1)), h / 2,
        w / 2 * (1.2 / 8 * (n - 1) + 1 / 8), h
    )

def getEventByyPos(y: int, es: list[Chart_Objects_Ppre.speedEvent | Chart_Objects_Ppre.alphaEvent | Chart_Objects_Ppre.moveEvent | Chart_Objects_Ppre.rotateEvent]):
    lineTime = getEventTimeByyPos(y)
    for e in es:
        if e.startTime <= lineTime <= e.endTime:
            return e
    return None

def getEventTimeByyPos(y: int):
    return EventEdit_uiDy + (h / 2 - (y - h / 2)) / (h / 2) * EventEdit_viewRange

def renderAEvent(e: Chart_Objects_Ppre.speedEvent | Chart_Objects_Ppre.alphaEvent | Chart_Objects_Ppre.moveEvent | Chart_Objects_Ppre.rotateEvent, color: str):
    est = e.startTime
    eet = e.endTime
    est_y = h - getEventViewTimeLengthPx(est) + EventEdit_uiDy / EventEdit_viewRange * h / 2
    eet_y = h - getEventViewTimeLengthPx(eet) + EventEdit_uiDy / EventEdit_viewRange * h / 2
    if est_y < h / 2 or eet_y > h:
        return None
    if isinstance(e, Chart_Objects_Ppre.speedEvent):
        left_x = 0
    elif isinstance(e, Chart_Objects_Ppre.alphaEvent):
        left_x = w * (1.2 / 8)
    elif isinstance(e, Chart_Objects_Ppre.moveEvent):
        left_x = w * (2.4 / 8)
    elif isinstance(e, Chart_Objects_Ppre.rotateEvent):
        left_x = w * (3.6 / 8)
    left_x /= 2
    webcv.create_rectangle(left_x, est_y, left_x + w / 2 * (1 / 8), eet_y, fillStyle=color, wait_execute=True)
    webcv.create_line(left_x, est_y, left_x + w / 2 * (1 / 8), est_y, lineWidth = JUDGELINE_WIDTH / 2, strokeStyle = "#F308", wait_execute=True)
    webcv.create_line(left_x, eet_y, left_x + w / 2 * (1 / 8), eet_y, lineWidth = JUDGELINE_WIDTH / 2, strokeStyle = "#F308", wait_execute=True)
    
def renderEditView():
    global EventEdit_lineIndex
    global JudgeLineIndexChangeValueRect
    global PlayButtonRect
    global ReplayButtonRect
    global AddJudgeLineRect
    global DeleteJudgeLineRect
    global NoteViewRect
    
    webcv.run_js_code(f"chartViewImdata = ctx.getImageData(0, 0, {w / 2}, {h / 2});", add_code_array=True)
    
    webcv.create_rectangle(0, h / 2, w / 2, h, fillStyle="#888", wait_execute=True)
    timeLinetime = int(EventEdit_uiDy) - 1
    while True:
        timeLiney = h - (h / 2) * (timeLinetime - EventEdit_uiDy) / EventEdit_viewRange
        webcv.create_line(
            0, timeLiney, w / 2 * (4.6 / 8), timeLiney,
            lineWidth = JUDGELINE_WIDTH / 4 * (3.0 if timeLinetime % 1.0 == 0.0 else 1.0),
            strokeStyle = "#EEE",
            wait_execute = True
        )
        webcv.create_text(
            w / 2 * (4.6 / 8) + 1.5, timeLiney,
            text = f"{timeLinetime:.2f}",
            font = f"{(w / 2 + h) / 175 * 1.25}px PhigrosFont",
            textAlign = "start",
            textBaseline = "middle",
            fillStyle = "#000",
            wait_execute = True
        )
        timeLinetime += EventEdit_timeLineLength
        if timeLinetime > EventEdit_uiDy + EventEdit_viewRange:
            break
    
    line = ChartObject.lines[EventEdit_lineIndex]
    
    for e in line.speedEvents:
        renderAEvent(e, "#00F8")
    
    for e in line.alphaEvents:
        renderAEvent(e, "#00F8")

    for e in line.moveEvents:
        renderAEvent(e, "#00F8")
    
    for e in line.rotateEvents:
        renderAEvent(e, "#00F8")
    
    if eventAdding and addingEvent is not None:
        renderAEvent(addingEvent, "#F0F8")
    
    webcv.run_js_code("ctx.putImageData(chartViewImdata, 0, 0);", add_code_array=True)
    
    webcv.create_text(
        w / 2 * (0.5 / 8), h / 2,
        text = "speedEvents",
        font = f"{(w / 2 + h) / 150 * 1.25}px PhigrosFont",
        textAlign = "center",
        textBaseline = "bottom",
        fillStyle = "#000",
        wait_execute = True
    )
    
    webcv.create_text(
        w / 2 * (1.7 / 8), h / 2,
        text = "alphaEvents",
        font = f"{(w / 2 + h) / 150 * 1.25}px PhigrosFont",
        textAlign = "center",
        textBaseline = "bottom",
        fillStyle = "#000",
        wait_execute = True
    )
    
    webcv.create_text(
        w / 2 * (2.9 / 8), h / 2,
        text = "moveEvents",
        font = f"{(w / 2 + h) / 150 * 1.25}px PhigrosFont",
        textAlign = "center",
        textBaseline = "bottom",
        fillStyle = "#000",
        wait_execute = True
    )
    
    webcv.create_text(
        w / 2 * (4.1 / 8), h / 2,
        text = "rotateEvents",
        font = f"{(w / 2 + h) / 150 * 1.25}px PhigrosFont",
        textAlign = "center",
        textBaseline = "bottom",
        fillStyle = "#000",
        wait_execute = True
    )
    
    webcv.create_text(
        w / 2 * (5.15 / 8), h / 2 + h / 2 * 0.03,
        text = f"judgeLine: {EventEdit_lineIndex}",
        font = f"{(w / 2 + h) / 125 * 1.25}px PhigrosFont",
        textAlign = "start",
        textBaseline = "middle",
        fillStyle = "#000",
        wait_execute = True
    )
    
    webcv.create_text(
        w / 2 * (5.15 / 8), h / 2 + h / 2 * 0.075,
        text = f"bpm: {line.bpm}",
        font = f"{(w / 2 + h) / 125 * 1.25}px PhigrosFont",
        textAlign = "start",
        textBaseline = "middle",
        fillStyle = "#000",
        wait_execute = True
    )
    
    JudgeLineIndexChangeValueRect = (
        w / 2 * (6.33 / 8) - IconSize / 2,
        h / 2 + h / 2 * 0.03 - IconSize / 2,
        w / 2 * (6.33 / 8) + IconSize / 2,
        h / 2 + h / 2 * 0.03 + IconSize / 2,
    )
    
    webcv.create_image(
        "Icon_ChangeValue",
        *JudgeLineIndexChangeValueRect[:2],
        width = IconSize, height = IconSize,
        wait_execute = True
    )
    
    PlayButtonRect = (
        w / 2 * (6.65 / 8) - IconSize / 2,
        h / 2 + h / 2 * 0.03 - IconSize / 2,
        w / 2 * (6.65 / 8) + IconSize / 2,
        h / 2 + h / 2 * 0.03 + IconSize / 2,
    )
    
    webcv.create_image(
        f"Icon_{"Pause" if isPlaying else "Play"}",
        *PlayButtonRect[:2],
        width = IconSize, height = IconSize,
        wait_execute = True
    )
    
    ReplayButtonRect = (
        w / 2 * (6.85 / 8) - IconSize / 2,
        h / 2 + h / 2 * 0.03 - IconSize / 2,
        w / 2 * (6.85 / 8) + IconSize / 2,
        h / 2 + h / 2 * 0.03 + IconSize / 2,
    )
    
    webcv.create_image(
        "Icon_Replay",
        *ReplayButtonRect[:2],
        width = IconSize, height = IconSize,
        wait_execute = True
    )
    
    AddJudgeLineRect = (
        w / 2 * (5.2 / 8) - IconSize / 2,
        h / 2 + h / 2 * 0.125 - IconSize / 2,
        w / 2 * (5.2 / 8) + IconSize / 2,
        h / 2 + h / 2 * 0.125 + IconSize / 2,
    )
    
    webcv.create_image(
        "Icon_Add",
        *AddJudgeLineRect[:2],
        width = IconSize, height = IconSize,
        wait_execute = True
    )
    
    DeleteJudgeLineRect = (
        w / 2 * (5.45 / 8) - IconSize / 2,
        h / 2 + h / 2 * 0.125 - IconSize / 2,
        w / 2 * (5.45 / 8) + IconSize / 2,
        h / 2 + h / 2 * 0.125 + IconSize / 2,
    )
    
    webcv.create_image(
        "Icon_Delete",
        *DeleteJudgeLineRect[:2],
        width = IconSize, height = IconSize,
        wait_execute = True
    )
    
    # noteView, tip: noteView共享eventView的数据
    webcv.run_js_code(f"leftImdata = ctx.getImageData(0, 0, {w / 2}, {h});", add_code_array=True)
    
    NoteViewRect = (
        w / 2, 0,
        w / 2 + w / 2 * (5 / 8), h / 2
    )
    
    webcv.create_rectangle(w / 2, 0, w, h / 2, fillStyle="#AAA", wait_execute=True)
    timeLinetime = int(EventEdit_uiDy) - 1
    while True:
        timeLiney = h / 2 - (h / 2) * (timeLinetime - EventEdit_uiDy) / EventEdit_viewRange
        webcv.create_line(
            w / 2, timeLiney, w / 2 + w / 2 * (5 / 8), timeLiney,
            lineWidth = JUDGELINE_WIDTH / 4 * (3.0 if timeLinetime % 1.0 == 0.0 else 1.0),
            strokeStyle = "#EEE",
            wait_execute = True
        )
        webcv.create_text(
            w / 2 + w / 2 * (5 / 8) + 1.5, timeLiney,
            text = f"{timeLinetime:.2f}",
            font = f"{(w / 2 + h) / 175 * 1.25}px PhigrosFont",
            textAlign = "start",
            textBaseline = "middle",
            fillStyle = "#000",
            wait_execute = True
        )
        timeLinetime += EventEdit_timeLineLength
        if timeLinetime > EventEdit_uiDy + EventEdit_viewRange:
            break

    for note in line.notes:
        noteY = h / 2 - getEventViewTimeLengthPx(note.time) + EventEdit_uiDy / EventEdit_viewRange * h / 2
        holdLength = getEventViewTimeLengthPx(note.holdtime)
        
        if note.type != Const.Note.HOLD and not (0 <= noteY <= h / 2):
            continue
        elif note.type == Const.Note.HOLD and (noteY < 0.0 or noteY - holdLength > h / 2):
            continue
        
        if note.type != Const.Note.HOLD:
            this_note_img_keyname = f"{note.type_string}"
            this_note_img = Resource["Notes"][this_note_img_keyname]
            this_note_imgname = f"Note_{this_note_img_keyname}"
        else:
            this_note_img_keyname = f"{note.type_string}_Head"
            this_note_img = Resource["Notes"][this_note_img_keyname]
            this_note_imgname = f"Note_{this_note_img_keyname}"
            
            this_note_img_body_keyname = f"{note.type_string}_Body"
            this_note_imgname_body = f"Note_{this_note_img_body_keyname}"
            
            this_note_img_end_keyname = f"{note.type_string}_End"
            this_note_img_end = Resource["Notes"][this_note_img_end_keyname]
            this_note_imgname_end = f"Note_{this_note_img_end_keyname}"
        
        noteX = w / 2 + w / 4 * (5 / 8) + note.positionX * PHIGROS_X * (5 / 8)
        
        webcv.run_js_code(
            f"ctx.drawRotateImage(\
                {webcv.get_img_jsvarname(this_note_imgname)},\
                {noteX},\
                {noteY},\
                {Note_width},\
                {Note_width / this_note_img.width * this_note_img.height},\
                0.0,\
                1.0\
            );",
            add_code_array = True
        )
        
        if note.type == Const.Note.HOLD:
            webcv.run_js_code(
                f"ctx.drawRotateImage(\
                    {webcv.get_img_jsvarname(this_note_imgname_end)},\
                    {noteX},\
                    {noteY - this_note_img.height / 2 - holdLength - this_note_img_end.height / 2},\
                    {this_note_img.width},\
                    {Note_width / this_note_img_end.width * this_note_img_end.height},\
                    0.0,\
                    1.0\
                );",
                add_code_array = True
            )
            
            if holdLength > 0.0:
                webcv.run_js_code(
                    f"ctx.drawAnchorESRotateImage(\
                        {webcv.get_img_jsvarname(this_note_imgname_body)},\
                        {noteX},\
                        {noteY - this_note_img.height / 2},\
                        {Note_width},\
                        {holdLength},\
                        0.0,\
                        1.0\
                    );",
                    add_code_array = True
                )
    
    webcv.clear_rectangle(w / 2, h / 2, w, h, wait_execute=True)
    
    webcv.run_js_code("ctx.putImageData(leftImdata, 0, 0);", add_code_array=True)
    
@Tool_Functions.NoJoinThreadFunc
def MouseWheel(face: int): # -1 / 1
    global EventEdit_uiDy
    face = face / abs(face)
    d = EventEdit_viewRange * 0.15 * face
    
    lastv = 0.0
    fcut = 80
    added = 0.0
    st = time()
    while True:
        p = (time() - st) / 0.5
        if p > 1.0: break
        v = 1.0 - (1.0 - p) ** 3
        dv = v - lastv
        lastv = v
        EventEdit_uiDy += dv * d
        added +=  dv * d
        sleep(1 / fcut)
    EventEdit_uiDy += d - added

def KeyDown(
    key: str,
    ctrl: bool,
    shift: bool,
    alt: bool,
    repeat: bool
):
    global noteEditing, editingNote
    key = key.lower()
    
    if not repeat and inRect((w / 2, 0, w / 2 + w / 2 * (5 / 8), h / 2), *MousePos):
        if key in ("t", "d", "h", "f"):
            notePositionX = ((MousePos[0] - w / 2) / (w / 2 * (5 / 8)) - 0.5) * (1 / 0.05625)
            noteTime = (h / 2 - MousePos[1]) / (h / 2) * EventEdit_viewRange + EventEdit_uiDy
            noteTime = int(noteTime / EventEdit_timeLineLength) * EventEdit_timeLineLength
            noteType = {
                "t": Const.Note.TAP,
                "d": Const.Note.DRAG,
                "h": Const.Note.HOLD,
                "f": Const.Note.FLICK
            }[key]
            note = Chart_Objects_Ppre.note(
                time = noteTime,
                type = noteType,
                holdtime = 0.0,
                positionX = notePositionX,
                speed = 1.0,
                fake = False,
                above = True
            )
            line = ChartObject.lines[EventEdit_lineIndex]
            line.notes.append(note)
            if key == "h":
                pass

def parseFloat(s: str, default: float):
    try:
        return float(s)
    except Exception:
        return default

def parseRangeInt(s: str, default: int, r: range):
    try:
        v = int(float(s))
        if v in r:
            return v
        raise Exception
    except Exception:
        return default

def parseTwoFloats(s: str, default: tuple[int, int]):
    s = s.replace("，", ",")
    slist = list(map(lambda x: x.replace(" ", ""), s.split(",")))
    if len(slist) < 2: return default
    s1 = slist[0]
    s2 = slist[1]
    return (parseFloat(s1, default[0]), parseFloat(s2, default[1]))

def fixOutRangeViewIndex():
    global EventEdit_lineIndex
    try:
        ChartObject.lines[EventEdit_lineIndex]
    except IndexError:
        ChartObject.lines.append(Chart_Objects_Ppre.judgeLine(
            bpm = 140,
            notes = [],
            speedEvents = [],
            alphaEvents = [],
            moveEvents = [],
            rotateEvents = []
        ))
        EventEdit_lineIndex = 0

def editEvent(data: dict):
    global editingEvent, eventEditing
    
    if isinstance(editingEvent, Chart_Objects_Ppre.speedEvent):
        if not data:
            if webcv.run_js_code("prompt('delete this event(input \\'true\\' or \\'false\\')?');") == "true":
                try: ChartObject.lines[EventEdit_lineIndex].speedEvents.remove(editingEvent)
                except ValueError: webcv.run_js_code("alert('event not found in line.')")
            eventEditing, editingEvent = False, None
            return None
        startTime = parseFloat(data["startTime"], editingEvent.startTime)
        endTime = parseFloat(data["endTime"], editingEvent.endTime)
        value = (parseFloat(data["startValue"], editingEvent.value) + parseFloat(data["endValue"], editingEvent.value)) / 2.0
        editingEvent.startTime, editingEvent.endTime, editingEvent.value = startTime, endTime, value
        webcv.run_js_code(f'''
            alert("changed speedEvent: {webcv.process_code_string_syntax_tostring(json.dumps(dataclasses.asdict(editingEvent), indent=4))}");
        ''')
    elif isinstance(editingEvent, Chart_Objects_Ppre.alphaEvent):
        if not data:
            if webcv.run_js_code("prompt('delete this event(input \\'true\\' or \\'false\\')?');") == "true":
                try: ChartObject.lines[EventEdit_lineIndex].alphaEvents.remove(editingEvent)
                except ValueError: webcv.run_js_code("alert('event not found in line.')")
            eventEditing, editingEvent = False, None
            return None
        startTime = parseFloat(data["startTime"], editingEvent.startTime)
        endTime = parseFloat(data["endTime"], editingEvent.endTime)
        start = parseFloat(data["startValue"], editingEvent.start)
        end = parseFloat(data["endValue"], editingEvent.end)
        easingType = parseRangeInt(data["easingType"], editingEvent.easingType, range(1, len(rpe_easing.ease_funcs) + 1))
        editingEvent.startTime, editingEvent.endTime, editingEvent.start, editingEvent.end, editingEvent.easingType = startTime, endTime, start, end, easingType
        webcv.run_js_code(f'''
            alert("changed alphaEvent: {webcv.process_code_string_syntax_tostring(json.dumps(dataclasses.asdict(editingEvent), indent=4))}");
        ''')
    elif isinstance(editingEvent, Chart_Objects_Ppre.moveEvent):
        if not data:
            if webcv.run_js_code("prompt('delete this event(input \\'true\\' or \\'false\\')?');") == "true":
                try: ChartObject.lines[EventEdit_lineIndex].moveEvents.remove(editingEvent)
                except ValueError: webcv.run_js_code("alert('event not found in line.')")
            eventEditing, editingEvent = False, None
            return None
        startTime = parseFloat(data["startTime"], editingEvent.startTime)
        endTime = parseFloat(data["endTime"], editingEvent.endTime)
        startX, startY = parseTwoFloats(data["startValue"], (editingEvent.startX, editingEvent.startY))
        endX, endY = parseTwoFloats(data["endValue"], (editingEvent.endX, editingEvent.endY))
        easingType = parseRangeInt(data["easingType"], editingEvent.easingType, range(1, len(rpe_easing.ease_funcs) + 1))
        editingEvent.startTime, editingEvent.endTime, editingEvent.startX, editingEvent.startY, editingEvent.endX, editingEvent.endY, editingEvent.easingType = startTime, endTime, startX, startY, endX, endY, easingType
        webcv.run_js_code(f'''
            alert("changed moveEvent: {webcv.process_code_string_syntax_tostring(json.dumps(dataclasses.asdict(editingEvent), indent=4))}");
        ''')
    elif isinstance(editingEvent, Chart_Objects_Ppre.rotateEvent):
        if not data:
            if webcv.run_js_code("prompt('delete this event(input \\'true\\' or \\'false\\')?');") == "true":
                try: ChartObject.lines[EventEdit_lineIndex].rotateEvents.remove(editingEvent)
                except ValueError: webcv.run_js_code("alert('event not found in line.')")
            eventEditing, editingEvent = False, None
            return None
        startTime = parseFloat(data["startTime"], editingEvent.startTime)
        endTime = parseFloat(data["endTime"], editingEvent.endTime)
        start = parseFloat(data["startValue"], editingEvent.start)
        end = parseFloat(data["endValue"], editingEvent.end)
        easingType = parseRangeInt(data["easingType"], editingEvent.easingType, range(1, len(rpe_easing.ease_funcs) + 1))
        editingEvent.startTime, editingEvent.endTime, editingEvent.start, editingEvent.end, editingEvent.easingType = startTime, endTime, start, end, easingType
        webcv.run_js_code(f'''
            alert("changed rotateEvent: {webcv.process_code_string_syntax_tostring(json.dumps(dataclasses.asdict(editingEvent), indent=4))}");
        ''')
    
    eventEditing, editingEvent = False, None

def editNote(data: dict):
    global noteEditing, editingNote
    
    if not data:
        if webcv.run_js_code("prompt('delete this note(input \\'true\\' or \\'false\\')?');") == "true":
            try: ChartObject.lines[EventEdit_lineIndex].notes.remove(editingNote)
            except ValueError: webcv.run_js_code("alert('note not found in line.')")
        noteEditing, editingNote = False, None
        return None
    
    time = parseFloat(data["time"], editingNote.time)
    type = parseRangeInt(data["type"], editingNote.type, range(1, 4 + 1))
    holdtime = parseFloat(data["holdtime"], editingNote.holdtime)
    positionX = parseFloat(data["positionX"], editingNote.positionX)
    speed = parseFloat(data["speed"], editingNote.speed)
    fake = data["fake"]
    above = data["above"]
    
    editingNote.time, editingNote.type, editingNote.holdtime, editingNote.positionX, editingNote.speed, editingNote.fake, editingNote.above = time, type, holdtime, positionX, speed, fake, above
    editingNote.__post_init__()
    webcv.run_js_code(f'''
        alert("changed note: {webcv.process_code_string_syntax_tostring(json.dumps(dataclasses.asdict(editingNote), indent=4))}");
    ''')
    
    noteEditing, editingNote = False, None

def main():
    global EventEdit_uiDy
    global isPlaying, PlayTime
    global eventEditing, editingEvent
    global eventAdding, addingEvent
    global noteEditing, editingNote
    
    fixOutRangeViewIndex()
    updateMorebets()
    webcv.jsapi.set_attr("MouseWheel", MouseWheel)
    webcv.jsapi.set_attr("MouseDown", MouseDown)
    webcv.jsapi.set_attr("MouseUp", MouseUp)
    webcv.jsapi.set_attr("MouseMoving", MouseMoving)
    webcv.jsapi.set_attr("KeyDown", KeyDown)
    webcv.jsapi.set_attr("editEvent", editEvent)
    webcv.jsapi.set_attr("editNote", editNote)
    webcv.run_js_code("_MouseWheel = (e) => {pywebview.api.call_attr('MouseWheel', e.delta || e.wheelDelta);};")
    webcv.run_js_code("_MouseDown = (e) => {pywebview.api.call_attr('MouseDown', e.clientX, e.clientY, e.button);};")
    webcv.run_js_code("_MouseUp = (e) => {pywebview.api.call_attr('MouseUp', e.clientX, e.clientY, e.button);};")
    webcv.run_js_code("_MouseMoving = (e) => {pywebview.api.call_attr('MouseMoving', e.clientX, e.clientY);};")
    webcv.run_js_code("_KeyDown = (e) => {pywebview.api.call_attr('KeyDown', e.key, e.ctrlKey, e.shiftKey, e.altKey, e.repeat);};")
    webcv.run_js_code("_editEvent = (data) => pywebview.api.call_attr('editEvent', data);")
    webcv.run_js_code("_editNote = (data) => pywebview.api.call_attr('editNote', data);")
    webcv.run_js_code("window.addEventListener('wheel', _MouseWheel);")
    webcv.run_js_code("window.addEventListener('mousedown', _MouseDown);")
    webcv.run_js_code("window.addEventListener('mouseup', _MouseUp);")
    webcv.run_js_code("window.addEventListener('mousemove', _MouseMoving);")
    webcv.run_js_code("window.addEventListener('keydown', _KeyDown);")
    
    isPlaying = False
    lastisPlaying = False
    PlayingTimeStartTime = None
    PlayTime = 0.0
    eventEditing, editingEvent = False, None
    eventAdding, addingEvent = False, None
    noteEditing, editingNote = False, None
    
    while True:
        webcv.clear_canvas(wait_execute=True)
        updateMorebets()
        renderChartView(PlayTime)
        fixOutRangeViewIndex()
        renderEditView()
        webcv.run_js_wait_code()
        
        if lastisPlaying is not isPlaying:
            if isPlaying:
                PlayTime = int(PlayTime)
                PlayingTimeStartTime = time()
                mixer.music.play()
                mixer.music.set_pos(0)
                try:
                    mixer.music.set_pos(PlayTime)
                except Exception:
                    PlayTime = 0.0
            else:
                PlayTime = EventEdit_uiDy * (60 / ChartObject.lines[EventEdit_lineIndex].bpm)
                mixer.music.fadeout(250)
            lastisPlaying = isPlaying
        
        if isPlaying:
            PlayTime += time() - PlayingTimeStartTime
            PlayingTimeStartTime = time()
            EventEdit_uiDy = PlayTime / (60 / ChartObject.lines[EventEdit_lineIndex].bpm)
        else:
            PlayTime = EventEdit_uiDy * (60 / ChartObject.lines[EventEdit_lineIndex].bpm)

webcv = webcvapis.WebCanvas(
    width = 0, height = 0,
    x = 0, y = 0,
    debug = "--debug" in argv,
    title = "PhigrosPlayer - ChartEditer",
    resizable = False,
    html_path = ".\\web_canvas_editer.html"
)
webdpr = webcv.run_js_code("window.devicePixelRatio;")
w, h = int(webcv.winfo_screenwidth() * 0.75), int(webcv.winfo_screenheight() * 0.75)
webcv.resize(w, h)
w_legacy, h_legacy = webcv.winfo_legacywindowwidth(), webcv.winfo_legacywindowheight()
dw_legacy, dh_legacy = w - w_legacy, h - h_legacy
dw_legacy *= webdpr; dh_legacy *= webdpr
dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
del w_legacy, h_legacy
webcv.resize(w + dw_legacy, h + dh_legacy)
webcv.move(int(webcv.winfo_screenwidth() / 2 - (w + dw_legacy) / webdpr / 2), int(webcv.winfo_screenheight() / 2 - (h + dh_legacy) / webdpr / 2))
PHIGROS_X, PHIGROS_Y = 0.05625 * w / 2, 0.6 * h / 2
JUDGELINE_WIDTH = h * 0.0075 / 2
EventEdit_uiDy = 0.0
EventEdit_viewRange = 3.5
EventEdit_timeLineLength = 1 / 4
EventEdit_lineIndex = 0
Resource = Load_Resource()
EFFECT_RANDOM_BLOCK_SIZE = Note_width / 12.5
Thread(target=main, daemon=True).start()
webcv.loop_to_close()
exitProcess(0)