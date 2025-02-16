import json
from sys import argv

import phi_easing
import const
import light_tool_funcs

if len(argv) < 3:
    print("Usage: tool-fv22fv3 <input> <output>")
    raise SystemExit

with open(argv[1], "r", encoding="utf-8") as f:
    fv2 = json.load(f)

def fv2events2fv3(es: list[dict], isspeed: bool, ismove: bool):
    es.sort(key=lambda e: e["startTime"])
    nes = []
    for i, e in enumerate(es):
        useEndNode = e.get("useEndNode", True)
        easeFunc = phi_easing.ease_funcs[e.get("easeType", 0)]
        easeFunc2 = phi_easing.ease_funcs[e.get("easeType2", 0)]
        
        if i != len(es) - 1:
            if not useEndNode:
                e["end"] = es[i + 1]["start"]
            e["endTime"] = es[i + 1]["startTime"]
        else:
            if not useEndNode:
                e["end"] = e["start"]
            e["endTime"] = const.PGR_INF
            easeFunc = phi_easing.ease_funcs[0]
            easeFunc2 = phi_easing.ease_funcs[0]
        
        if isspeed:
            nes.append({
                "startTime": e["startTime"],
                "endTime": e["endTime"],
                "value": e["value"]
            })
            continue
        
        if ismove and easeFunc is phi_easing.ease_funcs[0] and easeFunc2 is phi_easing.ease_funcs[0]:
            nes.append({
                "startTime": e["startTime"],
                "endTime": e["endTime"],
                "start": e["start"],
                "end": e["end"],
                "start2": e["start2"],
                "end2": e["end2"]
            })
            continue
        
        if not ismove and easeFunc is phi_easing.ease_funcs[0]:
            nes.append({
                "startTime": e["startTime"],
                "endTime": e["endTime"],
                "start": e["start"],
                "end": e["end"]
            })
            continue
        
        nowt = e["startTime"]
        splitUnit = 1
        while nowt <= e["endTime"]:
            v = light_tool_funcs.easing_interpolation(nowt, e["startTime"], e["endTime"], e["start"], e["end"], easeFunc)
            if ismove: v2 = light_tool_funcs.easing_interpolation(nowt, e["startTime"], e["endTime"], e["start2"], e["end2"], easeFunc2)
            nv = light_tool_funcs.easing_interpolation(nowt + splitUnit, e["startTime"], e["endTime"], e["start"], e["end"], easeFunc)
            if ismove: nv2 = light_tool_funcs.easing_interpolation(nowt + splitUnit, e["startTime"], e["endTime"], e["start2"], e["end2"], easeFunc2)
            
            if ismove:
                nes.append({
                    "startTime": nowt,
                    "endTime": nowt + splitUnit,
                    "start": v,
                    "end": nv,
                    "start2": v2,
                    "end2": nv2
                })
            else:
                nes.append({
                    "startTime": nowt,
                    "endTime": nowt + splitUnit,
                    "start": v,
                    "end": nv
                })
            
            nowt += splitUnit
        
        if nowt != e["endTime"]:
            nes.append({
                "startTime": nowt,
                "endTime": e["endTime"],
                "start": e["end"],
                "end": e["end"],
                "start2": e["end2"],
                "end2": e["end2"]
            } if ismove else {
                "startTime": nowt,
                "endTime": e["endTime"],
                "start": e["end"],
                "end": e["end"]
            })
    
    return nes

def convertLine(fv2line: dict):
    fv2line["speedEvents"] = fv2events2fv3(fv2line["speedEvents"], True, False)
    
    fv2line["notesAbove"] = list(map(lambda n: {
        "type": n["type"],
        "time": n["time"],
        "positionX": n["positionX"],
        "holdTime": n["holdTime"],
        "speed": n["speed"],
        "floorPosition": n["floorPosition"]
    }, fv2line["notesAbove"]))
    
    fv2line["notesBelow"] = list(map(lambda n: {
        "type": n["type"],
        "time": n["time"],
        "positionX": n["positionX"],
        "holdTime": n["holdTime"],
        "speed": n["speed"],
        "floorPosition": n["floorPosition"]
    }, fv2line["notesBelow"]))
    
    fv2line["judgeLineDisappearEvents"] = fv2events2fv3(fv2line["judgeLineDisappearEvents"], False, False)
    fv2line["judgeLineRotateEvents"] = fv2events2fv3(fv2line["judgeLineRotateEvents"], False, False)
    fv2line["judgeLineMoveEvents"] = fv2events2fv3(fv2line["judgeLineMoveEvents"], False, True)
    
    return fv2line

fv3 = {
    "formatVersion": 3,
    "offset": fv2["offset"],
    "judgeLineList": list(map(convertLine, fv2["judgeLineList"]))
}

json.dump(fv3, open(argv[2], "w", encoding="utf-8"), ensure_ascii=False)
