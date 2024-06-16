#i can't write this file, because i don't know rpe format... how can tell me?????????  welcome to my github to create a issue. thank you very much!!!
from sys import argv
import json
import math

from tqdm import trange

import Chart_Functions_Rep
import Chart_Objects_Rep

with open(argv[1],"r",encoding="utf-8") as f:
    rpe_obj = Chart_Functions_Rep.Load_Chart_Object(json.load(f))

ease_funcs = [
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
T = 1.875 / 120

for index,bpm in enumerate(rpe_obj.BPMList):
    if index != len(rpe_obj.BPMList) - 1:
        next_bpm = rpe_obj.BPMList[index + 1]
        bpm.dur = next_bpm.startTime.value - bpm.startTime.value
    else:
        bpm.dur = float("inf")

def getReal(b:Chart_Objects_Rep.Beat):
    realtime = 0.0
    for bpm in rpe_obj.BPMList:
        if bpm.startTime.value < b.value:
            if bpm.startTime.value + bpm.dur > b.value:
                realtime += 60 / bpm.bpm * (b.value - bpm.startTime.value)
            else:
                realtime += 60 / bpm.bpm * bpm.dur
    return realtime

def get_moves_state(moves,t):
    x,y = 0,0
    for e in moves:
        if e["st"] <= t <= e["et"]:
            if e["type"] == "x":
                x = (t - e["st"]) / (e["et"] - e["st"]) * (e["ev"] - e["sv"]) + e["sv"]
            elif e["type"] == "y":
                y = (t - e["st"]) / (e["et"] - e["st"]) * (e["ev"] - e["sv"]) + e["sv"]
    return x,y

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
    
    moves = []
    
    for eventLayer in rpe_judgeLine.eventLayers:
        if eventLayer.alphaEvents is not None:
            for e in eventLayer.alphaEvents:
                st = getReal(e.startTime) / T
                et = getReal(e.endTime) / T
                sv,ev = 255 & e.start,255 & e.end
                sv /= 255; ev /= 255
                ease = ease_funcs[e.easingType] if e.easingType < len(ease_funcs) else ease_funcs[0]
                for i in range(split_event_length):
                    se_st = st + i * (et - st) / split_event_length
                    se_et = st + (i + 1) * (et - st) / split_event_length
                    se_sv = ease(i / split_event_length) * (ev - sv) + sv
                    se_ev = ease((i + 1) / split_event_length) * (ev - sv) + sv
                    phi_judgeLine["judgeLineDisappearEvents"].append({
                        "startTime": se_st,
                        "endTime": se_et,
                        "start": se_sv,
                        "end": se_ev
                    })
        
        if eventLayer.rotateEvents is not None:
            for e in eventLayer.rotateEvents:
                st = getReal(e.startTime) / T
                et = getReal(e.endTime) / T
                sv,ev = e.start,e.end
                sv *= -1; ev *= -1
                ease = ease_funcs[e.easingType] if e.easingType < len(ease_funcs) else ease_funcs[0]
                for i in range(split_event_length):
                    se_st = st + i * (et - st) / split_event_length
                    se_et = st + (i + 1) * (et - st) / split_event_length
                    se_sv = ease(i / split_event_length) * (ev - sv) + sv
                    se_ev = ease((i + 1) / split_event_length) * (ev - sv) + sv
                    phi_judgeLine["judgeLineRotateEvents"].append({
                        "startTime": se_st,
                        "endTime": se_et,
                        "start": se_sv,
                        "end": se_ev
                    })
        
        if eventLayer.moveXEvents is not None:
            for e in eventLayer.moveXEvents:
                st = getReal(e.startTime) / T
                et = getReal(e.endTime) / T
                sv,ev = e.start,e.end
                ease = ease_funcs[e.easingType] if e.easingType < len(ease_funcs) else ease_funcs[0]
                for i in range(split_event_length):
                    se_st = st + i * (et - st) / split_event_length
                    se_et = st + (i + 1) * (et - st) / split_event_length
                    se_sv = ease(i / split_event_length) * (ev - sv) + sv
                    se_ev = ease((i + 1) / split_event_length) * (ev - sv) + sv
                    moves.append({
                        "type":"x",
                        "st":se_st,
                        "et":se_et,
                        "sv":se_sv,
                        "ev":se_ev
                    })
        
        if eventLayer.moveYEvents is not None:
            for e in eventLayer.moveYEvents:
                st = getReal(e.startTime) / T
                et = getReal(e.endTime) / T
                sv,ev = e.start,e.end
                ease = ease_funcs[e.easingType] if e.easingType < len(ease_funcs) else ease_funcs[0]
                for i in range(split_event_length):
                    se_st = st + i * (et - st) / split_event_length
                    se_et = st + (i + 1) * (et - st) / split_event_length
                    se_sv = ease(i / split_event_length) * (ev - sv) + sv
                    se_ev = ease((i + 1) / split_event_length) * (ev - sv) + sv
                    moves.append({
                        "type":"y",
                        "st":se_st,
                        "et":se_et,
                        "sv":se_sv,
                        "ev":se_ev
                    })
    
    moves.sort(key=lambda x:x["st"])
    max_time = max([moves["et"] for moves in moves])
    time_split_block_size = 1 / 10 / T
    block_num = int(max_time / time_split_block_size)
    for i in trange(block_num,desc="processing move events"):
        se_st = i * time_split_block_size
        se_et = (i + 1) * time_split_block_size
        se_sv_x,se_sv_y = get_moves_state(moves,se_st)
        se_ev_x,se_ev_y = get_moves_state(moves,se_et)
        phi_judgeLine["judgeLineMoveEvents"].append({
            "startTime": se_st,
            "endTime": se_et,
            "start": (se_sv_x + 675) / (675 * 2),
            "end": (se_ev_x + 675) / (675 * 2),
            "start2": (se_sv_y + 450) / (450 * 2),
            "end2": (se_ev_y + 450) / (450 * 2)
        })
                    
    phi_data["judgeLineList"].append(phi_judgeLine)

with open(argv[2],"w",encoding="utf-8") as f:
    f.write(json.dumps(phi_data,ensure_ascii=False))