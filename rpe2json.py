#i can't write this file, because i don't know rpe format... how can tell me?????????  welcome to my github to create a issue. thank you very much!!!
from sys import argv
import json
import math

import Chart_Functions_Rep

with open(argv[1],"r",encoding="utf-8") as f:
    rpe_obj = Chart_Functions_Rep.Load_Chart_Object(json.loads(f.read()))

tween = [
  lambda t: t, # 0 - Linear
  lambda t: 1 - math.cos(t * math.pi / 2), # 1 - EaseInSine
  lambda t: math.sin(t * math.pi / 2), # 2 - EaseOutSine
  lambda t: (1 - math.cos(t * math.pi)) / 2, # 3 - EaseInOutSine
  lambda t: t ** 2, # 4 - EaseInQuad
  lambda t: 1 - (t - 1) ** 2, # 5 - EaseOutQuad
  lambda t: (t ** 2 if (t := t * 2) < 1 else -((t - 2) ** 2 - 2)) / 2, # 6 - EaseInOutQuad
  lambda t: t ** 3, # 7 - EaseInCubic
  lambda t: 1 + (t - 1) ** 3, # 8 - EaseOutCubic
  lambda t: (t ** 3 if (t := t * 3) < 1 else -((t - 2) ** 3 + 2)) / 2, # 9 - EaseInOutCubic
  lambda t: t ** 4, # 10 - EaseInQuart
  lambda t: 1 - (t - 1) ** 4, # 11 - EaseOutQuart
  lambda t: (t ** 4 if (t := t * 2) < 1 else -((t - 2) ** 4 - 2)) / 2, # 12 - EaseInOutQuart
  lambda t: 0, # 13 - Zero
  lambda t: 1 # 14 - One
]

phi_data = {
    "formatVersion": 3,
    "offset": 0,
    "judgeLineList" :[]
}

split_event_length = 20

bpm = rpe_obj.BPMList[0].bpm
T = 1.875 / 120

for rpe_judgeLine in rpe_obj.JudgeLineList:
    phi_judgeLine = {
        "bpm": 120,
        "notesAbove": [],
        "notesBelow": [],
        "speedEvents": [],
        "judgeLineMoveEvents": [],
        "judgeLineRotateEvents": [],
        "judgeLineDisappearEvents": []
    }
    
    for EventLayer in rpe_judgeLine.eventLayers:
        if EventLayer.alphaEvents is not None:
            for Event in EventLayer.alphaEvents:
                st = Event.startTime.value
                et = Event.endTime.value
                sv = Event.start / 255.0
                ev = Event.end / 255.0
                ease_func = tween[Event.easingType] if Event.easingType <= len(tween) - 1 else tween[0]
                events = []
                for i in range(split_event_length):
                    est = (et - st) / split_event_length * i + st
                    eet = est + (et - st) / split_event_length
                    esv = ease_func(i / split_event_length) * (ev - sv) + sv
                    eev = ease_func((i + 1) / split_event_length) * (ev - sv) + sv
                    events.append({
                        "startTime": est * (60 / bpm) / T,
                        "endTime": eet * (60 / bpm) / T,
                        "start": esv,
                        "end": eev
                    })
                phi_judgeLine["judgeLineDisappearEvents"] += events
        
        if EventLayer.rotateEvents is not None:
            for Event in EventLayer.rotateEvents:
                st = Event.startTime.value
                et = Event.endTime.value
                sv = - Event.start
                ev = - Event.end
                ease_func = tween[Event.easingType] if Event.easingType <= len(tween) - 1 else tween[0]
                events = []
                for i in range(split_event_length):
                    est = (et - st) / split_event_length * i + st
                    eet = est + (et - st) / split_event_length
                    esv = ease_func(i / split_event_length) * (ev - sv) + sv
                    eev = ease_func((i + 1) / split_event_length) * (ev - sv) + sv
                    events.append({
                        "startTime": est * (60 / bpm) / T,
                        "endTime": eet * (60 / bpm) / T,
                        "start": esv,
                        "end": eev
                    })
                phi_judgeLine["judgeLineRotateEvents"] += events
        
        if EventLayer.speedEvents is not None:
            for Event in EventLayer.speedEvents:
                st = Event.startTime.value
                et = Event.endTime.value
                sv = - Event.start
                phi_judgeLine["speedEvents"].append({
                    "startTime": st * (60 / bpm) / T,
                    "endTime": et * (60 / bpm) / T,
                    "value": sv * (120 / 450 / 2) / T / 0.6
                })
    
    for Note in rpe_judgeLine.notes:
        phi_note = {
            "type": Note.type if Note.type == 1 or Note.type == 2 else {3:4,4:3}[Note.type],
            "time": Note.startTime.value * (60 / bpm) / T,
            "holdTime": Note.endTime.value * (60 / bpm) / T - Note.startTime.value * (60 / bpm) / T,
            "speed": Note.speed * (120 / 450 / 2) / T / 0.6,
            "positionX": Note.positionX / 450 / 2 / 0.05625,
            "floorPosition": None
        }
        
        floorPosition = 0.0
        for e in phi_judgeLine["speedEvents"]:
            if e["startTime"] <= phi_note["time"] <= e["endTime"]:
                floorPosition += (phi_note["time"] - e["startTime"]) * T * e["value"]
            elif e["endTime"] < phi_note["time"]:
                floorPosition += (e["endTime"] - e["startTime"]) * T * e["value"]
        phi_note["floorPosition"] = floorPosition
        
        if Note.above:
            phi_judgeLine["notesAbove"].append(phi_note)
        else:
            phi_judgeLine["notesBelow"].append(phi_note)
    
    phi_data["judgeLineList"].append(phi_judgeLine)

with open(argv[2],"w",encoding="utf-8") as f:
    f.write(json.dumps(phi_data,ensure_ascii=False))