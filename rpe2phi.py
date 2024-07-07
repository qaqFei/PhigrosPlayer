# special event will not processing
from sys import argv
from dataclasses import dataclass
from functools import cache
from base64 import b64encode
from os.path import dirname
import json
import typing

import Chart_Functions_Rep
import Chart_Objects_Rep
import rpe_easing
import _rpe2phi_extra

if len(argv) < 2:
    print("Usage: rpe2phi.py <rpe_file> <phi_target_file>")
    raise SystemExit

with open(argv[1],"r",encoding="utf-8") as f:
    rpe_obj = Chart_Functions_Rep.Load_Chart_Object(json.load(f))

ease_funcs = rpe_easing.ease_funcs

linear = ease_funcs[0]

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

@dataclass
class RpeMoveNode:
    type: typing.Literal["st", "et"]
    item: Move
    value: float

@dataclass
class RpeMoveNodeMgr:
    moves: typing.List[Move]
    nodes: typing.List[RpeMoveNode]
    
    def __post_init__(self):
        for e in self.moves:
            self.nodes.append(RpeMoveNode(type="st", item=e, value=e.st))
            self.nodes.append(RpeMoveNode(type="et", item=e, value=e.et))
        self.nodes.sort(key=lambda x: x.value)

extra_fp = argv[argv.index("-extra") + 1] if "-extra" in argv else None
phi_data = {
    "formatVersion": 3,
    "offset": rpe_obj.META.offset / 1000,
    "judgeLineList" :[]
}

split_event_length = 30
T = 1.875 / rpe_obj.BPMList[0].bpm

for index,bpm in enumerate(rpe_obj.BPMList):
    if index != len(rpe_obj.BPMList) - 1:
        next_bpm = rpe_obj.BPMList[index + 1]
        bpm.dur = next_bpm.startTime.value - bpm.startTime.value
    else:
        bpm.dur = float("inf")

@cache
def getReal(b:Chart_Objects_Rep.Beat):
    realtime = 0.0
    for bpm in rpe_obj.BPMList:
        if bpm.startTime.value < b.value:
            if bpm.startTime.value + bpm.dur > b.value:
                realtime += 60 / bpm.bpm * (b.value - bpm.startTime.value)
            else:
                realtime += 60 / bpm.bpm * bpm.dur
    return realtime

@cache
def linear_interpolation(
    t:float,
    st:float,
    et:float,
    sv:float,
    ev:float
) -> float:
    if t == st: return sv
    return (t - st) / (et - st) * (ev - sv) + sv

def get_phimove_state_x_raw(t, last:bool = False): # can`t: find and return, should find all and return the last value. normal it never returns 0.0 (default).
    if not last:
        for move in x_moves:
            if move.st == t or move.et == t:
                return move.sv if move.st == t else move.ev
        return 0.0
    else:
        v = 0.0
        for move in x_moves:
            if move.st == t or move.et == t:
                v = move.sv if move.st == t else move.ev
        return v

def get_phimove_state_y_raw(t, last:bool = False):
    if not last:
        for move in y_moves:
            if move.st == t or move.et == t:
                return move.sv if move.st == t else move.ev
        return 0.0
    else:
        v = 0.0
        for move in y_moves:
            if move.st == t or move.et == t:
                v = move.sv if move.st == t else move.ev
        return v

def get_floor_position(t):
    v = 0.0
    for e in phi_judgeLine["speedEvents"]:
        if e["startTime"] < t < e["endTime"]:
            v += (t - e["startTime"]) * T * e["value"]
        elif e["endTime"] <= t:
            v += (e["endTime"] - e["startTime"]) * T * e["value"]
    return v

@cache
def conv_note(n):
    return {1:1, 2:3, 3:4, 4:2}[n]

for line_index, rpe_judgeLine in enumerate(rpe_obj.JudgeLineList):
    print(f"\rProcess JudgeLine: {line_index + 1}", end="")
    
    phi_judgeLine = {
        "bpm": rpe_obj.BPMList[0].bpm,
        "notesAbove": [],
        "notesBelow": [],
        "speedEvents": [],
        "judgeLineMoveEvents": [],
        "judgeLineRotateEvents": [],
        "judgeLineDisappearEvents": [],
        "--QFPPR-JudgeLine-TextJudgeLine": False,
        "--QFPPR-JudgeLine-TextEvents": [],
        "--QFPPR-JudgeLine-EnableTexture": rpe_judgeLine.Texture != "line.png",
        "--QFPPR-JudgeLine-Texture": rpe_judgeLine.Texture,
        "--QFPPR-JudgeLine-ScaleXEvents": [],
        "--QFPPR-JudgeLine-ScaleYEvents": [],
    }
    
    x_moves:typing.List[Move] = []
    y_moves:typing.List[Move] = []
    
    for eventLayer in rpe_judgeLine.eventLayers:
        if eventLayer.alphaEvents is not None:
            for e in eventLayer.alphaEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = (255 & e.start) / 255
                ev = (255 & e.end) / 255
                ef = ease_funcs[e.easingType - 1]
                if ef is linear:
                    phi_judgeLine["judgeLineDisappearEvents"].append(
                        {
                            "startTime": st / T,
                            "endTime": et / T,
                            "start": sv,
                            "end": ev
                        }
                    )
                else:
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
                if ef is linear:
                    phi_judgeLine["judgeLineRotateEvents"].append(
                        {
                            "startTime": st / T,
                            "endTime": et / T,
                            "start": sv,
                            "end": ev
                        }
                    )
                else:
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
                    x_moves.append(
                        Move(
                            type = "x",
                            st = ist / T,
                            et = iet / T,
                            sv = (isv + 675) / 1350,
                            ev = (iev + 675) / 1350
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
                    y_moves.append(
                        Move(
                            type = "y",
                            st = ist / T,
                            et = iet / T,
                            sv = (isv + 450) / 900,
                            ev = (iev + 450) / 900
                        )
                    )
        
        if eventLayer.speedEvents is not None:
            for e in eventLayer.speedEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                if e.start == e.end:
                    phi_judgeLine["speedEvents"].append(
                        {
                            "startTime": st / T,
                            "value": (e.start * 120) / 900 / 0.6
                        }
                    )
                else:
                    for i in range(split_event_length):
                        ist = st + i * (et - st) / split_event_length
                        iet = st + (i + 1) * (et - st) / split_event_length
                        isp = i / split_event_length
                        isv = linear_interpolation(isp, 0.0, 1.0, e.start, e.end)
                        phi_judgeLine["speedEvents"].append(
                            {
                                "startTime": ist / T,
                                "value": (isv * 120) / 900 / 0.6
                            }
                        )
                    phi_judgeLine["speedEvents"].append(
                        {
                            "startTime": (st + ((split_event_length - 1) + 1) * (et - st) / split_event_length) / T,
                            "value": (e.end * 120) / 900 / 0.6
                        }
                    )
                        
    if rpe_judgeLine.extended is not None:
        if rpe_judgeLine.extended.textEvents is not None and len(rpe_judgeLine.extended.textEvents) > 0:
            phi_judgeLine["--QFPPR-JudgeLine-TextJudgeLine"] = True
            for e in rpe_judgeLine.extended.textEvents:
                phi_judgeLine["--QFPPR-JudgeLine-TextEvents"].append({
                    "startTime": getReal(e.startTime) / T,
                    "value": e.start
                })
                if e.start != e.end:
                    phi_judgeLine["--QFPPR-JudgeLine-TextEvents"].append({
                        "startTime": getReal(e.endTime) / T,
                        "value": e.end
                    })
        
        if rpe_judgeLine.extended.scaleXEvents is not None and len(rpe_judgeLine.extended.scaleXEvents) > 0:
            for e in rpe_judgeLine.extended.scaleXEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = e.start
                ev = e.end
                ef = ease_funcs[e.easingType - 1]
                if ef is linear:
                    phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"].append({
                        "startTime": st / T,
                        "endTime": et / T,
                        "start": sv,
                        "end": ev
                    })
                else:
                    for i in range(split_event_length):
                        ist = st + i * (et - st) / split_event_length
                        iet = st + (i + 1) * (et - st) / split_event_length
                        isvp = ef(i / split_event_length)
                        ievp = ef((i + 1) / split_event_length)
                        isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                        iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                        phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"].append({
                            "startTime": ist / T,
                            "endTime": iet / T,
                            "start": isv,
                            "end": iev
                        })
        
        if rpe_judgeLine.extended.scaleYEvents is not None and len(rpe_judgeLine.extended.scaleYEvents) > 0:
            for e in rpe_judgeLine.extended.scaleYEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = e.start
                ev = e.end
                ef = ease_funcs[e.easingType - 1]
                if ef is linear:
                    phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"].append({
                        "startTime": st / T,
                        "endTime": et / T,
                        "start": sv,
                        "end": ev
                    })
                else:
                    for i in range(split_event_length):
                        ist = st + i * (et - st) / split_event_length
                        iet = st + (i + 1) * (et - st) / split_event_length
                        isvp = ef(i / split_event_length)
                        ievp = ef((i + 1) / split_event_length)
                        isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                        iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                        phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"].append({
                            "startTime": ist / T,
                            "endTime": iet / T,
                            "start": isv,
                            "end": iev
                        })
    
    if len(phi_judgeLine["speedEvents"]) > 0:
        phi_judgeLine["speedEvents"].sort(key = lambda x: x["startTime"])
        for index, e in enumerate(phi_judgeLine["speedEvents"]):
            if index != len(phi_judgeLine["speedEvents"]) - 1:
                ne = phi_judgeLine["speedEvents"][index + 1]
                e["endTime"] = ne["startTime"]
            else:
                e["endTime"] = 1000000000
        
    if len(phi_judgeLine["judgeLineDisappearEvents"]) > 0:
        phi_judgeLine["judgeLineDisappearEvents"].append({
            "startTime": -999999,
            "endTime": min(phi_judgeLine["judgeLineDisappearEvents"], key = lambda x: x["startTime"])["startTime"],
            "start": (v := min(phi_judgeLine["judgeLineDisappearEvents"], key = lambda x: x["startTime"])["start"]),
            "end": v
        })
        phi_judgeLine["judgeLineDisappearEvents"].append({
            "startTime": max(phi_judgeLine["judgeLineDisappearEvents"], key = lambda x: x["endTime"])["endTime"],
            "endTime": 1000000000,
            "start": (v := max(phi_judgeLine["judgeLineDisappearEvents"], key = lambda x: x["endTime"])["end"]),
            "end": v
        })
        phi_judgeLine["judgeLineDisappearEvents"].sort(key = lambda x: x["startTime"])
        
        oth_es = []
        for index, e in enumerate(phi_judgeLine["judgeLineDisappearEvents"]):
            if index != len(phi_judgeLine["judgeLineDisappearEvents"]) - 1:
                ne = phi_judgeLine["judgeLineDisappearEvents"][index + 1]
                if e["endTime"] < ne["startTime"]:
                    oth_es.append({
                        "startTime": e["endTime"],
                        "endTime": ne["startTime"],
                        "start": e["end"],
                        "end": e["end"]
                    })
        phi_judgeLine["judgeLineDisappearEvents"] += oth_es
    
    if len(phi_judgeLine["judgeLineRotateEvents"]) > 0:
        phi_judgeLine["judgeLineRotateEvents"].append({
            "startTime": -999999,
            "endTime": min(phi_judgeLine["judgeLineRotateEvents"], key = lambda x: x["startTime"])["startTime"],
            "start": (v := min(phi_judgeLine["judgeLineRotateEvents"], key = lambda x: x["startTime"])["start"]),
            "end": v
        })
        phi_judgeLine["judgeLineRotateEvents"].append({
            "startTime": max(phi_judgeLine["judgeLineRotateEvents"], key = lambda x: x["endTime"])["endTime"],
            "endTime": 1000000000,
            "start": (v := max(phi_judgeLine["judgeLineRotateEvents"], key = lambda x: x["endTime"])["end"]),
            "end": v
        })
        phi_judgeLine["judgeLineRotateEvents"].sort(key = lambda x: x["startTime"])
        
        oth_es = []
        for index, e in enumerate(phi_judgeLine["judgeLineRotateEvents"]):
            if index != len(phi_judgeLine["judgeLineRotateEvents"]) - 1:
                ne = phi_judgeLine["judgeLineRotateEvents"][index + 1]
                if e["endTime"] < ne["startTime"]:
                    oth_es.append({
                        "startTime": e["endTime"],
                        "endTime": ne["startTime"],
                        "start": e["end"],
                        "end": e["end"]
                    })
        phi_judgeLine["judgeLineRotateEvents"] += oth_es
    
    if len(phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"]) > 0:
        phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"].append({
            "startTime": -999999,
            "endTime": min(phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"], key = lambda x: x["startTime"])["startTime"],
            "start": (v := min(phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"], key = lambda x: x["startTime"])["start"]),
            "end": v
        })
        phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"].append({
            "startTime": max(phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"], key = lambda x: x["endTime"])["endTime"],
            "endTime": 1000000000,
            "start": (v := max(phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"], key = lambda x: x["endTime"])["end"]),
            "end": v
        })
        phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"].sort(key = lambda x: x["startTime"])
        
        oth_es = []
        for index, e in enumerate(phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"]):
            if index != len(phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"]) - 1:
                ne = phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"][index + 1]
                if e["endTime"] < ne["startTime"]:
                    oth_es.append({
                        "startTime": e["endTime"],
                        "endTime": ne["startTime"],
                        "start": e["end"],
                        "end": e["end"]
                    })
        phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"] += oth_es
    
    if len(phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"]) > 0:
        phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"].append({
            "startTime": -999999,
            "endTime": min(phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"], key = lambda x: x["startTime"])["startTime"],
            "start": (v := min(phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"], key = lambda x: x["startTime"])["start"]),
            "end": v
        })
        phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"].append({
            "startTime": max(phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"], key = lambda x: x["endTime"])["endTime"],
            "endTime": 1000000000,
            "start": (v := max(phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"], key = lambda x: x["endTime"])["end"]),
            "end": v
        })
        phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"].sort(key = lambda x: x["startTime"])
        
        oth_es = []
        for index, e in enumerate(phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"]):
            if index != len(phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"]) - 1:
                ne = phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"][index + 1]
                if e["endTime"] < ne["startTime"]:
                    oth_es.append({
                        "startTime": e["endTime"],
                        "endTime": ne["startTime"],
                        "start": e["end"],
                        "end": e["end"]
                    })
        phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"] += oth_es

    if len(x_moves) > 0:
        x_moves.sort(key = lambda x: x.st)
        
        oth_es = []
        for index, e in enumerate(x_moves):
            if index != len(x_moves) - 1:
                ne = x_moves[index + 1]
                if e.et < ne.st:
                    oth_es.append(Move(
                        type = "x",
                        st = e.et,
                        et = ne.st,
                        sv = e.ev,
                        ev = e.ev
                    ))
        x_moves += oth_es
        
        x_moves.sort(key = lambda x: x.st)
    
    if len(y_moves) > 0:
        y_moves.sort(key = lambda x: x.st)
        
        oth_es = []
        for index, e in enumerate(y_moves):
            if index != len(y_moves) - 1:
                ne = y_moves[index + 1]
                if e.et < ne.st:
                    oth_es.append(Move(
                        type = "y",
                        st = e.et,
                        et = ne.st,
                        sv = e.ev,
                        ev = e.ev
                    ))
        y_moves += oth_es
        
        y_moves.sort(key = lambda x: x.st)
        
    for note in rpe_judgeLine.notes:
        st = getReal(note.startTime)
        et = getReal(note.endTime)
        phi_judgeLine["notesAbove"]
        item = {
            "type": conv_note(note.type),
            "time": st / T,
            "holdTime": (et - st) / T,
            "positionX": note.positionX / 1350 / 0.05625,
            "speed": ((get_floor_position(et / T) - get_floor_position(st / T)) / ((et - st) / T)) / T if et != st else note.speed,
            "floorPosition": get_floor_position(st / T),
            "--QFPPR-Note-Width": note.width,
            "--QFPPR-Note-Alpha": (255 & note.alpha) / 255,
            "--QFPPR-Note-Fake": bool(note.isFake),
            "--QFPPR-Note-VisibleTime": note.visibleTime
        }
        
        if item["--QFPPR-Note-Width"] == 1.0:
            del item["--QFPPR-Note-Width"]
        
        if item["--QFPPR-Note-Alpha"] == 1.0:
            del item["--QFPPR-Note-Alpha"]
        
        if not item["--QFPPR-Note-Fake"]:
            del item["--QFPPR-Note-Fake"]
        
        if item["--QFPPR-Note-VisibleTime"] >= 999999.0:
            del item["--QFPPR-Note-VisibleTime"]
        
        if note.above == 1:
            phi_judgeLine["notesAbove"].append(item)
        else:
            phi_judgeLine["notesBelow"].append(item)
    
    node_mgr = RpeMoveNodeMgr(x_moves + y_moves, [])
    
    get_phimove_state_x_cache = cache(get_phimove_state_x_raw)
    get_phimove_state_y_cache = cache(get_phimove_state_y_raw)
    
    for index, this_node in enumerate(node_mgr.nodes):
        if index != len(node_mgr.nodes) - 1:
            next_node = node_mgr.nodes[index + 1]
            
            if this_node.value == next_node.value:
                continue
            
            startTime = this_node.value
            endTime = next_node.value
            
            if this_node.item.type == "x":
                start = this_node.item.sv if this_node.type == "st" else this_node.item.ev
                start2 = get_phimove_state_y_cache(startTime, this_node.type == "st")
            else: # y
                start = get_phimove_state_x_cache(startTime, this_node.type == "st")
                start2 = this_node.item.sv if this_node.type == "st" else this_node.item.ev
            
            if next_node.item.type == "x":
                end = next_node.item.sv if next_node.type == "st" else next_node.item.ev
                end2 = get_phimove_state_y_cache(endTime, this_node.type == "et")
            else: # y
                end = get_phimove_state_x_cache(endTime, this_node.type == "et")
                end2 = next_node.item.sv if next_node.type == "st" else next_node.item.ev
            
            phi_judgeLine["judgeLineMoveEvents"].append({
                "startTime": startTime,
                "endTime": endTime,
                "start": start,
                "end": end,
                "start2": start2,
                "end2": end2
            })
            
    if len(phi_judgeLine["judgeLineMoveEvents"]) > 0:
        phi_judgeLine["judgeLineMoveEvents"].sort(key = lambda x: x["endTime"])
        phi_judgeLine["judgeLineMoveEvents"][-1]["endTime"] = 1000000000
        min(phi_judgeLine["judgeLineMoveEvents"], key = lambda x: x["startTime"])["startTime"] = -999999
    
    phi_judgeLine["judgeLineDisappearEvents"].sort(key = lambda x: x["startTime"])
    phi_judgeLine["judgeLineMoveEvents"].sort(key = lambda x: x["startTime"])
    phi_judgeLine["judgeLineRotateEvents"].sort(key = lambda x: x["startTime"])
    phi_judgeLine["--QFPPR-JudgeLine-TextEvents"].sort(key = lambda x: x["startTime"])
    phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"].sort(key = lambda x: x["startTime"])
    phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"].sort(key = lambda x: x["startTime"])
    
    if not phi_judgeLine["--QFPPR-JudgeLine-TextJudgeLine"]:
        del phi_judgeLine["--QFPPR-JudgeLine-TextJudgeLine"]
        del phi_judgeLine["--QFPPR-JudgeLine-TextEvents"]
    
    if not phi_judgeLine["--QFPPR-JudgeLine-EnableTexture"]:
        del phi_judgeLine["--QFPPR-JudgeLine-EnableTexture"]
        del phi_judgeLine["--QFPPR-JudgeLine-Texture"]
    else:
        try:
            with open(f"{dirname(argv[1])}\\{phi_judgeLine["--QFPPR-JudgeLine-Texture"]}", "rb") as Texture_f:
                phi_judgeLine["--QFPPR-JudgeLine-Texture"] = b64encode(Texture_f.read()).decode("utf-8")
        except Exception:
            print(f"Warning: Texture file {phi_judgeLine['--QFPPR-JudgeLine-Texture']} not found.")
    
    if not phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"]:
        del phi_judgeLine["--QFPPR-JudgeLine-ScaleXEvents"]
    
    if not phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"]:
        del phi_judgeLine["--QFPPR-JudgeLine-ScaleYEvents"]
    
    phi_data["judgeLineList"].append(phi_judgeLine)
    

if extra_fp is not None:
    with open(extra_fp, "r", encoding="utf-8") as f:
        phi_data["--QFPPR-Extra-Enable"] = True
        phi_data["--QFPPR-Extra"] = _rpe2phi_extra.process_extra(json.load(f))

with open(argv[2],"w",encoding="utf-8") as f:
    f.write(json.dumps(phi_data,ensure_ascii=False))