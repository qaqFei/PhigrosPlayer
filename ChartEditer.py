from os import mkdir, chdir
from os.path import exists, isfile, abspath, dirname
from sys import argv
from ctypes import windll
from tempfile import gettempdir
from time import time, sleep
from random import randint
import typing
import json

from PIL import Image
import webcvapis

import Chart_Objects_Ppre

def validFile(fp: str) -> bool:
    return exists(fp) and isfile(fp)

def exitProcess(state: int = 0, text: str = "") -> typing.NoReturn:
    if text: print(text)
    windll.kernel32.ExitProcess(state)

if len(argv) < 3:
    print("Usage: ChartEditer <chart> <audio>")
    print("    if <chart> is __create__, it will create a empty chart.")
    exitProcess()

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
AudioFp = abspath(ChartFp)

if not validFile(ChartFp): exitProcess(1, "invaild chart file.")
if not validFile(AudioFp): exitProcess(1, "invaild audio file.")

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
                        time = tuple(noteItem.get("time", [0, 0, 1])),
                        type = noteItem.get("type", 1), # default note type is tap.
                        holdtime = tuple(noteItem.get("holdtime", [0, 0, 1])),
                        positionX = noteItem.get("positionX", 0.0),
                        fake = noteItem.get("fake", False)
                    )
                    for noteItem in lineItem.get("notes", [])
                ],
                speedEvents = [
                    Chart_Objects_Ppre.speedEvent(
                        startTime = tuple(speedItem.get("startTime", [0, 0, 1])),
                        endTime = tuple(speedItem.get("endTime", [0, 0, 1])),
                        start = speedItem.get("start", 0.0),
                        end = speedItem.get("end", 0.0)
                    )
                    for speedItem in lineItem.get("speedEvents", [])
                ],
                alphaEvents = [
                    Chart_Objects_Ppre.alphaEvent(
                        startTime = tuple(alphaItem.get("startTime", [0, 0, 1])),
                        endTime = tuple(alphaItem.get("endTime", [0, 0, 1])),
                        start = alphaItem.get("start", 0.0),
                        end = alphaItem.get("end", 0.0),
                        easingType = alphaItem.get("easingType", 1)
                    )
                    for alphaItem in lineItem.get("alphaEvents", [])
                ],
                moveEvents = [
                    Chart_Objects_Ppre.moveEvent(
                        startTime = tuple(moveItem.get("startTime", [0, 0, 1])),
                        endTime = tuple(moveItem.get("endTime", [0, 0, 1])),
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
                        startTime = tuple(rotateItem.get("startTime", [0, 0, 1])),
                        endTime = tuple(rotateItem.get("endTime", [0, 0, 1])),
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
    Note_width = (0.125 * w + 0.2 * h) / 2
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
        
    with open("./Resources/font.ttf","rb") as f:
        webcv.reg_res(f.read(),"PhigrosFont")
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

webcv = webcvapis.WebCanvas(
    width = 0, height = 0,
    x = 0, y = 0,
    title = "PhigrosPlayer - ChartEditer - By qaqFei - MIT License",
    resizable = False,
    html_path = ".\\web_canvas_editer.html"
)
webdpr = webcv.run_js_code("window.devicePixelRatio;")
w, h = int(webcv.winfo_screenwidth() * 0.61803398874989484820458683436564), int(webcv.winfo_screenheight() * 0.61803398874989484820458683436564)
webcv.resize(w, h)
w_legacy, h_legacy = webcv.winfo_legacywindowwidth(), webcv.winfo_legacywindowheight()
dw_legacy, dh_legacy = w - w_legacy, h - h_legacy
dw_legacy *= webdpr; dh_legacy *= webdpr
dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
del w_legacy, h_legacy
webcv.resize(w + dw_legacy, h + dh_legacy)
webcv.move(int(webcv.winfo_screenwidth() / 2 - (w + dw_legacy) / webdpr / 2), int(webcv.winfo_screenheight() / 2 - (h + dh_legacy) / webdpr / 2))
Resource = Load_Resource()
webcv.loop_to_close()
exitProcess(0)