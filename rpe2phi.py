#i can't write this file, because i don't know rpe format... how can tell me?????????  welcome to my github to create a issue. thank you very much!!!
from sys import argv
from dataclasses import dataclass
import json
import math
import typing

import Chart_Functions_Rep
import Chart_Objects_Rep

with open(argv[1],"r",encoding="utf-8") as f:
    rpe_obj = Chart_Functions_Rep.Load_Chart_Object(json.load(f))

ease_funcs = [
  lambda t: t, # linear - 1
  lambda t: math.sin((t * math.pi) / 2), # out sine - 2
  lambda t: 1 - math.cos((t * math.pi) / 2), # in sine - 3
  lambda t: 1 - (1 - t) * (1 - t), # out quad - 4
  lambda t: t ** 2, # in quad - 5
  lambda t: -(math.cos(math.pi * t) - 1) / 2, # io sine - 6
  lambda t: 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2, # io quad - 7
  lambda t: 1 - (1 - t) ** 3, # out cubic - 8
  lambda t: t ** 3, # in cubic - 9
  lambda t: 1 - (1 - t) ** 4, # out quart - 10
  lambda t: t ** 4, # in quart - 11
  lambda t: 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2, # io cubic - 12
  lambda t: 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2, # io quart - 13
  lambda t: 1 - (1 - t) ** 5, # out quint - 14
  lambda t: t ** 5, # in quint - 15
  lambda t: 1 if t == 1 else 1 - 2 ** (-10 * t), # out expo - 16
  lambda t: 0 if t == 0 else 2 ** (10 * t - 10), # in expo - 17
  lambda t: (1 - (t - 1) ** 2) ** 0.5, # out circ - 18
  lambda t: 1 - (1 - t ** 2) ** 0.5, # in circ - 19
  lambda t: 1 + 2.70158 * ((t - 1) ** 3) + 1.70158 * ((t - 1) ** 2), # out back - 20
  lambda t: 2.70158 * (t ** 3) - 1.70158 * (t ** 2), # in back - 21
  lambda t: (1 - (1 - (2 * t) ** 2) ** 0.5) / 2 if t < 0.5 else (((1 - (-2 * t + 2) ** 2) ** 0.5) + 1) / 2, # io circ - 22
  lambda t: ((2 * t) ** 2 * ((2.5949095 + 1) * 2 * t - 2.5949095)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) / 2, # io back - 23
  lambda t: 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1), # out elastic - 24
  lambda t: 0 if t == 0 else (1 if t == 1 else - 2 ** (10 * t - 10) * math.sin((t * 10 - 10.75) * (2 * math.pi / 3))), # in elastic - 25
  lambda t: 7.5625 * (t ** 2) if (t < 1 / 2.75) else (7.5625 * (t - (1.5 / 2.75)) * (t - (1.5 / 2.75)) + 0.75 if (t < 2 / 2.75) else (7.5625 * (t - (2.25 / 2.75)) * (t - (2.25 / 2.75)) + 0.9375 if (t < 2.5 / 2.75) else (7.5625 * (t - (2.625 / 2.75)) * (t - (2.625 / 2.75)) + 0.984375))), # out bounce - 26
  lambda t: 1 - ease_funcs[26 - 1](1 - t), # in bounce - 27
  lambda t: (1 - ease_funcs[26 - 1](1 - 2 * t)) / 2 if t < 0.5 else (1 + ease_funcs[26 - 1](2 * t - 1)) / 2, # io bounce - 28
  lambda t: 0 if t == 0 else (1 if t == 0 else (-2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 if t < 0.5 else (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 + 1) # io elastic - 29
]

@dataclass
class Move:
    type: typing.Literal["x", "y"]
    st: float
    et: float
    sv: float
    ev: float

@dataclass
class PhiMove:
    st: float
    et: float
    sv_x: float
    sv_y: float
    ev_x: float
    ev_y: float

phi_data = {
    "formatVersion": 3,
    "offset": 0,
    "judgeLineList" :[]
}

split_event_length = 50
T = 1.875 / rpe_obj.BPMList[0].bpm

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

def linear_interpolation(
    t:float,
    st:float,
    et:float,
    sv:float,
    ev:float
) -> float:
    if t == st: return sv
    return (t - st) / (et - st) * (ev - sv) + sv

def get_phimove_state(t):
    x, y = 0, 0
    for move in moves:
        if move.st <= t <= move.et:
            if move.type == "x":
                x = linear_interpolation(t, move.st, move.et, move.sv, move.ev)
            elif move.type == "y":
                y = linear_interpolation(t, move.st, move.et, move.sv, move.ev)
    return (x + 675) / 1350, (y + 450) / 900

def get_floor_position(t):
    v = 0.0
    for e in phi_judgeLine["speedEvents"]:
        if e["startTime"] <= t <= e["endTime"]:
            v += (t - e["startTime"]) * T * e["value"]
        elif e["endTime"] <= t:
            v += (e["endTime"] - e["startTime"]) * T * e["value"]
    return v

for rpe_judgeLine in rpe_obj.JudgeLineList:
    phi_judgeLine = {
        "bpm": rpe_obj.BPMList[0].bpm,
        "notesAbove": [],
        "notesBelow": [],
        "speedEvents": [],
        "judgeLineMoveEvents": [],
        "judgeLineRotateEvents": [],
        "judgeLineDisappearEvents": []
    }
    
    moves:typing.List[Move] = []
    
    for eventLayer in rpe_judgeLine.eventLayers:
        if eventLayer.alphaEvents is not None:
            for e in eventLayer.alphaEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = (255 & e.start) / 255
                ev = (255 & e.end) / 255
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    phi_judgeLine["judgeLineDisappearEvents"].append(
                        {
                            "startTime": ist / T,
                            "endTime": iet / T,
                            "start": isv,
                            "end": iev
                        }
                    )
        
        if eventLayer.rotateEvents is not None:
            for e in eventLayer.rotateEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = - e.start
                ev = - e.end
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    phi_judgeLine["judgeLineRotateEvents"].append(
                        {
                            "startTime": ist / T,
                            "endTime": iet / T,
                            "start": isv,
                            "end": iev
                        }
                    )
        
        if eventLayer.moveXEvents is not None:
            for e in eventLayer.moveXEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = e.start
                ev = e.end
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    moves.append(
                        Move(
                            type = "x",
                            st = ist / T,
                            et = iet / T,
                            sv = isv,
                            ev = iev
                        )
                    )
        
        if eventLayer.moveYEvents is not None:
            for e in eventLayer.moveYEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = e.start
                ev = e.end
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    moves.append(
                        Move(
                            type = "y",
                            st = ist / T,
                            et = iet / T,
                            sv = isv,
                            ev = iev
                        )
                    )
        
        if eventLayer.speedEvents is not None:
            for e in eventLayer.speedEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                v = (e.start + e.end) / 2 # normal, e.start == e.end is True
                phi_judgeLine["speedEvents"].append(
                    {
                        "startTime": st / T,
                        "endTime": et / T,
                        "value": (v * 120) / 900 / 0.6
                    }
                )
    
    for note in rpe_judgeLine.notes: # has bugsssssssss
        st = getReal(note.startTime)
        et = getReal(note.endTime)
        phi_judgeLine["notesAbove"]
        item = {
            "type": note.type,
            "time": st / T,
            "holdTime": (et - st) / T,
            "positionX": note.positionX / 1350 / 0.05625,
            "floorPosition": get_floor_position(st / T)
        }
        if note.above:
            phi_judgeLine["notesAbove"].append(item)
        else:
            phi_judgeLine["notesBelow"].append(item)
    
    moves.sort(key=lambda x: x.st)
    phimoves = []
    max_movet = max([i.et for i in moves])
    t = 0.0
    t_step = 1 / split_event_length / T
    while t <= max_movet:
        next_t = t + t_step
        state_now = get_phimove_state(t)
        state_next = get_phimove_state(next_t)
        phi_judgeLine["judgeLineMoveEvents"].append(
            {
                "startTime": t,
                "endTime": next_t,
                "start": state_now[0],
                "end": state_next[0],
                "start2": state_now[1],
                "end2": state_next[1]
            }
        )
        t += t_step
                    
    phi_data["judgeLineList"].append(phi_judgeLine)

with open(argv[2],"w",encoding="utf-8") as f:
    f.write(json.dumps(phi_data,ensure_ascii=False))