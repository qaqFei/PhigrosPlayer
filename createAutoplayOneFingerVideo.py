import json
from os import chdir
from os.path import dirname, abspath
from sys import argv
from ctypes import windll
from random import uniform

import cv2
import numpy
from PIL import Image

import Chart_Functions_Phi
import Chart_Functions_Rpe
import Chart_Objects_Phi
import Chart_Objects_Rpe
import Const
import Tool_Functions
from rpe_easing import ease_funcs

if len(argv) < 4:
    print("Usage: createAutoplayOneFingerVideo <videoFile> <chartFile> <outputVideoFilePath>")
    windll.kernel32.ExitProcess(0)

videoFile = argv[1]
chartFile = argv[2]
outputVideoFilePath = argv[3]

with open(chartFile, "r", encoding="utf-8") as f:
    jsonData = json.load(f)

chartObj = Chart_Functions_Phi.Load_Chart_Object(jsonData) if "formatVersion" in jsonData else Chart_Functions_Rpe.Load_Chart_Object(jsonData)
moveDatas = []

if isinstance(chartObj, Chart_Objects_Phi.Phigros_Chart):
    for line in chartObj.judgeLineList:
        for note in line.notesAbove + line.notesBelow:
            moveDatas.append({
                "time": note.time * (1.875 / line.bpm),
                "pos": note.getNoteClickPos(note.time)
            })
            
            if note.type == Const.Note.HOLD:
                dw = 1 / 12.5 / (1.875 / line.bpm)
                ht = note.time
                while ht < note.time + note.holdTime:
                    ht += dw
                    moveDatas.append({
                        "time": ht * (1.875 / line.bpm),
                        "pos": note.getNoteClickPos(ht)
                    })
            
            if note.type == Const.Note.FLICK:
                e = moveDatas[-1]
                moveDatas.append({
                    "time": e["time"] + 0.05,
                    "pos": (e["pos"][0], e["pos"][1] - 0.1)
                })
elif isinstance(chartObj, Chart_Objects_Rpe.Rpe_Chart): # eq else
    for line in chartObj.JudgeLineList:
        for note in line.notes:
            moveDatas.append({
                "time": chartObj.beat2sec(note.startTime.value, line.bpmfactor),
                "pos": note.getNoteClickPos(note.startTime.value, chartObj, line)
            })
            
            if note.phitype == Const.Note.HOLD:
                dw = chartObj.sec2beat(1 / 12.5, line.bpmfactor)
                ht = note.startTime.value
                while ht < note.endTime.value:
                    ht += dw
                    moveDatas.append({
                        "time": chartObj.beat2sec(ht, line.bpmfactor),
                        "pos": note.getNoteClickPos(ht, chartObj, line)
                    })
            
            if note.phitype == Const.Note.FLICK:
                e = moveDatas[-1]
                moveDatas.append({
                    "time": e["time"] + 0.05,
                    "pos": (e["pos"][0], e["pos"][1] - 0.1)
                })

moveDatas.sort(key = lambda x: x["time"])

moveTimeCount = {}
for e in moveDatas:
    if e["time"] not in moveTimeCount:
        moveTimeCount[e["time"]] = 0
    moveTimeCount[e["time"]] += 1
MorebetsData = [e for e in moveDatas if moveTimeCount[e["time"]] > 1]
for e in MorebetsData:
    e["time"] += uniform(-0.08, 0.08)

moveDatas.append({
    "time": -1.0,
    "pos": (0.5, 0.5)
})
moveDatas.sort(key = lambda x: x["time"])
moveEvents = []
for i, e in enumerate(moveDatas):
    if i != len(moveDatas) - 1:
        ne = moveDatas[i + 1]
        moveEvents.append({
            "st": e["time"],
            "et": ne["time"],
            "sp": e["pos"],
            "ep": ne["pos"]
        })

def gfingerp(sec: float) -> tuple[float, float]:
    for e in moveEvents:
        if e["st"] <= sec < e["et"]:
            return (
                Tool_Functions.easing_interpolation(sec, e["st"], e["et"], e["sp"][0], e["ep"][0], ease_funcs[9]),
                Tool_Functions.easing_interpolation(sec, e["st"], e["et"], e["sp"][1], e["ep"][1], ease_funcs[9])
            )
    return moveEvents[-1]["ep"]

videoCap = cv2.VideoCapture(videoFile)
w, h = int(videoCap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = videoCap.get(cv2.CAP_PROP_FPS)
optWriter = cv2.VideoWriter(outputVideoFilePath, cv2.VideoWriter.fourcc(*'mp4v'), fps, (w, h), True)

selfdir = dirname(argv[0])
if selfdir == "": selfdir = abspath(".")
chdir(selfdir)
finger = Image.open("./Resources/finger.png")
finger = finger.resize((int(w * 0.4), int(w * 0.4 / finger.width * finger.height)))

try:
    sec = 0.0
    while True:
        ret, frame = videoCap.read()
        if not ret or frame is None:
            break
        sec += 1 / fps
        im = Image.fromarray(frame[:, :, ::-1])
        x, y = gfingerp(sec)
        im.paste(finger, tuple(map(int, (
            x * w - finger.width / 2,
            y * h
        ))), finger)
        frame = numpy.array(im)
        optWriter.write(frame[:, :, ::-1])
        print(f"\r{sec:.2f}", end="")
except Exception as e:
    print(repr(e))

videoCap.release()