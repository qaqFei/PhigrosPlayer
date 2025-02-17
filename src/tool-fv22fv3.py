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

def SaveAsNewFormat(chart: dict):
    def GetEaseProgress(easeType: int, progress: float):
        return phi_easing.ease_funcs[easeType](progress) if 0.0 <= progress <= 1.0 else (0.0 if progress < 0.0 else 1.0)
    
    def ToCompatibilityEvents(events: list[dict]):
        result: list[dict] = []
        
        cyevent = {
            "startTime": -999999.0, "endTime": 1e09,
            "start": 0.0, "end": 0.0
        }
        result.append(cyevent)
        
        for k, thise in enumerate(events):
            thise_uen = thise.get("useEndNode", False)
            
            if k == 0:
                cyevent["start"] = thise["start"]
                cyevent["end"] = thise["end"]
                cyevent["endTime"] = thise["startTime"]
            
            if k < len(events) - 1:
                nexte = events[k + 1]
                
                if thise.get("easeType", 0) == 0:
                    result.append({
                        "startTime": thise["startTime"],
                        "endTime": nexte["startTime"],
                        "start": thise["start"],
                        "end": thise["end"] if thise_uen else nexte["start"]
                    })
                else:
                    num2 = 0
                    while num2 + thise["startTime"] < nexte["startTime"]:
                        cyevent = {
                            "startTime": num2 + thise["startTime"],
                            "start": GetEaseProgress(
                                thise.get("easeType", 0),
                                num2 / (nexte["startTime"] - thise["startTime"])
                            ) * (
                                (thise["end"] if thise_uen else nexte["start"]) - thise["start"]
                            ) + thise["start"]
                        }
                        
                        if cyevent["startTime"] != thise["startTime"]:
                            result[len(result) - 1]["endTime"] = cyevent["startTime"]
                            result[len(result) - 1]["end"] = cyevent["start"]
                            
                        cyevent["endTime"] = nexte["startTime"]
                        cyevent["end"] = GetEaseProgress(thise.get("easeType", 0), 1.0) * (
                            (thise["end"] if thise_uen else nexte["start"]) - thise["start"]
                        ) + thise["start"]
                        result.append(cyevent)
                        
                        dt = nexte["startTime"] - thise["startTime"]
                        if dt >= 512.0: num2 += 16
                        elif dt >= 256.0: num2 += 8
                        elif dt >= 256.0: num2 += 4
                        else: num2 += 1
            else:
                result.append({
                    "startTime": thise["startTime"],
                    "endTime": 1e09,
                    "start": thise["start"],
                    "end": thise["start"]
                })
        
        return result
    
    compatibilityChart = {
        "formatVersion": 3,
        "offset": chart["offset"],
        "numOfNotes": chart["numOfNotes"],
        "judgeLineList": []
    }
    
    for i, thisline in enumerate(chart["judgeLineList"][:24]):
        compatibilityJudgeLine = {
            "bpm": thisline["bpm"],
            "numOfNotes": thisline["numOfNotes"],
            "numOfNotesAbove": thisline["numOfNotesAbove"],
            "numOfNotesBelow": thisline["numOfNotesBelow"],
            "notesAbove": [{
                "time": chartNote["time"],
                "type": chartNote["type"],
                "positionX": chartNote["positionX"],
                "holdTime": chartNote["holdTime"],
                "speed": chartNote["speed"] if chartNote["type"] != 3 else chartNote["headSpeed"],
                "floorPosition": chartNote["floorPosition"]
            } for chartNote in thisline["notesAbove"]],
            "notesBelow": [{
                "time": chartNote["time"],
                "type": chartNote["type"],
                "positionX": chartNote["positionX"],
                "holdTime": chartNote["holdTime"],
                "speed": chartNote["speed"] if chartNote["type"] != 3 else chartNote["headSpeed"],
                "floorPosition": chartNote["floorPosition"]
            } for chartNote in thisline["notesBelow"]],
            "speedEvents": [],
            "judgeLineDisappearEvents": [],
            "judgeLineRotateEvents": [],
            "judgeLineMoveEvents": []
        }
        
        if len(thisline["speedEvents"]) > 0:
            for j in range(len(thisline["speedEvents"])):
                speedEvent = thisline["speedEvents"][j]
                if j == 0 and speedEvent["startTime"] != 0.0:
                    compatibilityJudgeLine["speedEvents"].append({
                        "startTime": 0.0, "endTime": speedEvent["startTime"],
                        "floorPosition": 0.0, "value": 1.0
                    })
                
                compatibilityJudgeLine["speedEvents"].append({
                    "startTime": speedEvent["startTime"],
                    "endTime": thisline["speedEvents"][j + 1]["startTime"] if j < len(thisline["speedEvents"]) - 1 else 1e09,
                    "floorPosition": speedEvent["floorPosition"],
                    "value": speedEvent["value"]
                })
        else:
            compatibilityJudgeLine["speedEvents"].append({
                "startTime": 0.0, "endTime": 1e09,
                "floorPosition": 0.0, "value": 1.0
            })

        compatibilityJudgeLine["judgeLineDisappearEvents"] = ToCompatibilityEvents()
        
        compatibilityChart["judgeLineList"].append(compatibilityJudgeLine)

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
