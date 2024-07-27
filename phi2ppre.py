from sys import argv
from ctypes import windll
import json

import Chart_Functions_Phi

if len(argv) < 2:
    print("Usage: phi2ppre.py <phi_file> <ppre_target_file>")
    windll.kernel32.ExitProcess(0)

with open(argv[1],"r",encoding="utf-8") as f:
    phi_obj = Chart_Functions_Phi.Load_Chart_Object(json.load(f))

ppre_data = {
    "lines": []
}

for line in phi_obj.judgeLineList:
    ppre_line = {
        "bpm": line.bpm,
        "notes": [],
        "speedEvents": [],
        "alphaEvents": [],
        "moveEvents": [],
        "rotateEvents": []
    }
    for note in line.notesAbove:
        ppre_line["notes"].append({
            "time": note.time * 1.875,
            "type": note.type,
            "holdtime": note.holdTime * 1.875,
            "positionX": note.positionX,
            "speed": note.speed,
            "fake": False,
            "above": True
        })
    for note in line.notesBelow:
        ppre_line["notes"].append({
            "time": note.time * 1.875,
            "type": note.type,
            "holdtime": note.holdTime * 1.875,
            "positionX": note.positionX,
            "speed": note.speed,
            "fake": False,
            "above": False
        })
    for e in line.speedEvents:
        ppre_line["speedEvents"].append({
            "startTime": e.startTime * 1.875,
            "endTime": e.endTime * 1.875,
            "value": e.value
        })
    for e in line.judgeLineDisappearEvents:
        ppre_line["alphaEvents"].append({
            "startTime": e.startTime * 1.875,
            "endTime": e.endTime * 1.875,
            "start": e.start,
            "end": e.end,
            "easingType": 1
        })
    for e in line.judgeLineMoveEvents:
        ppre_line["moveEvents"].append({
            "startTime": e.startTime * 1.875,
            "endTime": e.endTime * 1.875,
            "startX": e.start,
            "startY": e.start2,
            "endX": e.end,
            "endY": e.end2,
            "easingType": 1
        })
    for e in line.judgeLineRotateEvents:
        ppre_line["rotateEvents"].append({
            "startTime": e.startTime * 1.875,
            "endTime": e.endTime * 1.875,
            "start": e.start,
            "end": e.end,
            "easingType": 1
        })
    
    ppre_data["lines"].append(ppre_line)

with open(argv[2], "w", encoding="utf-8") as f:
    f.write(json.dumps(ppre_data,ensure_ascii=False))