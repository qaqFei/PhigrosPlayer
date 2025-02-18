import json
from sys import argv

import phi_easing

if len(argv) < 3:
    print("Usage: tool-fv22fv3 <input> <output>")
    raise SystemExit

with open(argv[1], "r", encoding="utf-8") as f:
    fv2 = json.load(f)

def SaveAsNewFormat(chart: dict):
    def GetEaseProgress(easeType: int, progress: float):
        return phi_easing.ease_funcs[easeType](progress) if 0.0 <= progress <= 1.0 else (0.0 if progress < 0.0 else 1.0)
    
    def ToCompatibilityEvents(events: list[dict], ismove: bool):
        result: list[dict] = []
        
        cyevent = {
            "startTime": -999999.0, "endTime": 1e09,
            **(
                {"start": 0.5, "end": 0.5, "start2": 0.5, "end2": 0.5}
                if ismove else {"start": 0.0, "end": 0.0}
            )
        }
        result.append(cyevent)
        
        for k, thise in enumerate(events):
            thise_uen = thise.get("useEndNode", False)
            
            if k == 0:
                cyevent["start"] = thise["start"]
                cyevent["end"] = thise["start"]
                cyevent["endTime"] = thise["startTime"]
                
                if ismove:
                    cyevent["start2"] = thise["start2"]
                    cyevent["end2"] = thise["start2"]
            
            if k < len(events) - 1:
                nexte = events[k + 1]
                
                if thise.get("easeType", 0) == 0 and (not ismove or thise.get("easeType2", 0) == 0):
                    result.append({
                        "startTime": thise["startTime"],
                        "endTime": nexte["startTime"],
                        "start": thise["start"],
                        "end": thise["end"] if thise_uen else nexte["start"],
                        **({
                            "start2": thise["start2"],
                            "end2": thise["end2"] if thise_uen else nexte["start2"],
                        } if ismove else {})
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
                            ) + thise["start"],
                            **({
                                "start2": GetEaseProgress(
                                    thise.get("easeType2", 0),
                                    num2 / (nexte["startTime"] - thise["startTime"])
                                ) * (
                                    (thise["end2"] if thise_uen else nexte["start2"]) - thise["start2"]
                                ) + thise["start2"]
                            } if ismove else {})
                        }
                        
                        if cyevent["startTime"] != thise["startTime"]:
                            result[-1]["endTime"] = cyevent["startTime"]
                            result[-1]["end"] = cyevent["start"]
                            if ismove: result[-1]["end2"] = cyevent["start2"]
                            
                        cyevent["end"] = thise["end"] if thise_uen else nexte["start"]
                        if ismove: cyevent["end2"] = thise["end2"] if thise_uen else nexte["start2"]
                        cyevent["endTime"] = nexte["startTime"]
                            
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
                    "end": thise["start"],
                    **({
                        "start2": thise["start2"],
                        "end2": thise["start2"],
                    } if ismove else {})
                })
        
        for i, e in enumerate(result):
            if not ismove: e.update({"start2": 0.0, "end2": 0.0})
            result[i] = {
                "startTime": e["startTime"],
                "endTime": e["endTime"],
                "start": e["start"],
                "end": e["end"],
                "start2": e["start2"],
                "end2": e["end2"]
            }
        
        return result
    
    compatibilityChart = {
        "formatVersion": 3,
        "offset": chart["offset"],
        "numOfNotes": chart["numOfNotes"],
        "judgeLineList": []
    }
    
    for line in chart["judgeLineList"][:24]:
        cyline = {
            "numOfNotes": line["numOfNotes"],
            "numOfNotesAbove": line["numOfNotesAbove"],
            "numOfNotesBelow": line["numOfNotesBelow"],
            "bpm": line["bpm"],
            "speedEvents": [],
            "notesAbove": [{
                "type": chartNote["type"],
                "time": chartNote["time"],
                "positionX": chartNote["positionX"],
                "holdTime": chartNote["holdTime"],
                "speed": chartNote["speed"] if chartNote["type"] != 3 else chartNote["headSpeed"],
                "floorPosition": chartNote["floorPosition"]
            } for chartNote in line["notesAbove"]],
            "notesBelow": [{
                "type": chartNote["type"],
                "time": chartNote["time"],
                "positionX": chartNote["positionX"],
                "holdTime": chartNote["holdTime"],
                "speed": chartNote["speed"] if chartNote["type"] != 3 else chartNote["headSpeed"],
                "floorPosition": chartNote["floorPosition"]
            } for chartNote in line["notesBelow"]],
            "judgeLineDisappearEvents": [],
            "judgeLineMoveEvents": [],
            "judgeLineRotateEvents": []
        }
        
        if line["speedEvents"]:
            for j, e in enumerate(line["speedEvents"]):
                if j == 0 and e["startTime"] != 0.0:
                    cyline["speedEvents"].append({
                        "startTime": 0.0, "endTime": e["startTime"],
                        "floorPosition": 0.0, "value": 1.0
                    })
                
                cyline["speedEvents"].append({
                    "startTime": e["startTime"],
                    "endTime": line["speedEvents"][j + 1]["startTime"] if j < len(line["speedEvents"]) - 1 else 1e09,
                    "floorPosition": e["floorPosition"],
                    "value": e["value"]
                })
        else:
            cyline["speedEvents"].append({
                "startTime": 0.0, "endTime": 1e09,
                "floorPosition": 0.0, "value": 1.0
            })

        cyline["judgeLineDisappearEvents"] = ToCompatibilityEvents(line["judgeLineDisappearEvents"], False)
        cyline["judgeLineRotateEvents"] = ToCompatibilityEvents(line["judgeLineRotateEvents"], False)
        cyline["judgeLineMoveEvents"] = ToCompatibilityEvents(line["judgeLineMoveEvents"], True)
        
        compatibilityChart["judgeLineList"].append(cyline)

    return compatibilityChart

fv3 = SaveAsNewFormat(fv2)

json.dump(fv3, open(argv[2], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
