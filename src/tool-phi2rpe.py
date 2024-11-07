import json
from copy import deepcopy
from fractions import Fraction
from sys import argv

if len(argv) < 3:
    print("Usage: tool-phi2rpe <input> <output>")
    raise SystemExit

with open(argv[1], "r", encoding="utf-8") as f:
    phic = json.load(f)

def n2f(x: float):
    x *= 0.03125
    fra = Fraction(x % 1.0).limit_denominator((2 << 30) - 1)
    return [int(x), fra.numerator, fra.denominator]

def f2n(x: list):
    return (x[0] + x[1] / x[2]) / 0.03125

bpms = [i["bpm"] for i in phic["judgeLineList"]]
rpeop = {
    "BPMList": [
        {
            "bpm": (sum(bpms) / len(bpms)) if bpms else 120.0,
            "startTime": [0, 0, 1]
        }
    ],
    "META": {
        "RPEVersion": 140, "background": "",
        "charter": "", "composer": "",
        "id": "", "level": "",
        "name": "", "offset": int(phic["offset"] * 1000), "song": ""
    },
    "judgeLineGroup": ["Default"],
    "judgeLineList": [],
    "multiLineString": "",
    "multiScale": 1.0
}

for line in phic["judgeLineList"]:
    rpel = {
        "Group": 0,
        "Name": "Untitled",
        "Texture": "line.png",
        "bpmfactor": line["bpm"] / rpeop["BPMList"][0]["bpm"],
        "father": -1,
        "isCover": 1,
        "zOrder": 0,
        "notes": [],
        "eventLayers": [
            {
                "alphaEvents": [],
                "moveXEvents": [],
                "moveYEvents": [],
                "rotateEvents": [],
                "speedEvents": []
            },
            *((None, ) * 4)
        ],
        "alphaControl": [{"alpha": 1.0, "easing": 1, "x": 0.0}, {"alpha": 1.0, "easing": 1, "x": 9999999.0}],
        "extended": {"inclineEvents": [{"bezier": 0, "bezierPoints": [0.0, 0.0, 0.0, 0.0], "easingLeft": 0.0, "easingRight": 1.0, "easingType": 0, "end": 0.0, "endTime": [1, 0, 1], "linkgroup": 0, "start": 0.0, "startTime": [0, 0, 1]}]},
        "posControl": [{"easing": 1, "pos": 1.0, "x": 0.0}, {"easing": 1, "pos": 1.0, "x": 9999999.0}],
        "sizeControl": [{"easing": 1, "size": 1.0, "x": 0.0}, {"easing": 1, "size": 1.0, "x": 9999999.0}],
        "skewControl": [{"easing": 1, "skew": 0.0, "x": 0.0}, {"easing": 1, "skew": 0.0, "x": 9999999.0}],
        "yControl": [{"easing": 1, "x": 0.0, "y": 1.0}, {"easing": 1, "x": 9999999.0, "y": 1.0}],
    }
    holds = []
    
    for e in line["speedEvents"]:
        rpel["eventLayers"][0]["speedEvents"].append({
            "linkgroup": 0,
            "startTime": n2f(e["startTime"]),
            "endTime": n2f(e["endTime"]),
            "start": e["value"] * 0.6 * 900 / 120,
            "end": e["value"] * 0.6 * 900 / 120,
        })
    
    for e in line["judgeLineMoveEvents"]:
        rpel["eventLayers"][0]["moveXEvents"].append({
            "linkgroup": 0,
            "bezier": 0,
            "bezierPoints": [0.0, 0.0, 0.0, 0.0],
            "easingLeft": 0.0,
            "easingRight": 1.0,
            "easingType": 1,
            "startTime": n2f(e["startTime"]),
            "endTime": n2f(e["endTime"]),
            "start": e["start"] * 1350 - 675,
            "end": e["end"] * 1350 - 675,
        })
        
        rpel["eventLayers"][0]["moveYEvents"].append({
            "linkgroup": 0,
            "bezier": 0,
            "bezierPoints": [0.0, 0.0, 0.0, 0.0],
            "easingLeft": 0.0,
            "easingRight": 1.0,
            "easingType": 1,
            "startTime": n2f(e["startTime"]),
            "endTime": n2f(e["endTime"]),
            "start": e["start2"] * 900 - 450,
            "end": e["end2"] * 900 - 450,
        })
    
    for e in line["judgeLineRotateEvents"]:
        rpel["eventLayers"][0]["rotateEvents"].append({
            "linkgroup": 0,
            "bezier": 0,
            "bezierPoints": [0.0, 0.0, 0.0, 0.0],
            "easingLeft": 0.0,
            "easingRight": 1.0,
            "easingType": 1,
            "startTime": n2f(e["startTime"]),
            "endTime": n2f(e["endTime"]),
            "start": -e["start"],
            "end": -e["end"],
        })
    
    for e in line["judgeLineDisappearEvents"]:
        rpel["eventLayers"][0]["alphaEvents"].append({
            "linkgroup": 0,
            "bezier": 0,
            "bezierPoints": [0.0, 0.0, 0.0, 0.0],
            "easingLeft": 0.0,
            "easingRight": 1.0,
            "easingType": 1,
            "startTime": n2f(e["startTime"]),
            "endTime": n2f(e["endTime"]),
            "start": int(e["start"] * 255),
            "end": int(e["end"] * 255),
        })
    
    for n in line["notesAbove"]:
        if n["type"] == 3: 
            holds.append((n, 1))
            continue
            
        rpel["notes"].append({
            "above": 1, "alpha": 255, "isFake": 0, "size": 1.0,
            "visibleTime": 999999.0, "yOffset": 0.0,
            
            "type": {1:1, 2:4, 3:2, 4:3}[n["type"]],
            "startTime": n2f(n["time"]),
            "endTime": n2f(n["time"] + n["holdTime"]),
            "positionX": n["positionX"] * 0.05625 * 1350,
            "speed": n["speed"]
        })
        
    for n in line["notesBelow"]:
        if n["type"] == 3: 
            holds.append((n, 0))
            continue
            
        rpel["notes"].append({
            "above": 0, "alpha": 255, "isFake": 0, "size": 1.0,
            "visibleTime": 999999.0, "yOffset": 0.0,
            
            "type": {1:1, 2:4, 3:2, 4:3}[n["type"]],
            "startTime": n2f(n["time"]),
            "endTime": n2f(n["time"] + n["holdTime"]),
            "positionX": n["positionX"] * 0.05625 * 1350,
            "speed": n["speed"]
        })
    
    for n, above in holds:
        fel, fer = n["time"], n["time"] + n["holdTime"]
        sevs = []
        for e in rpel["eventLayers"][0]["speedEvents"]:
            etl, etr = f2n(e["startTime"]), f2n(e["endTime"])
            if (
                fel <= etl <= etr <= fer
                or fel <= etl <= fer <= etr
                or etl <= fel <= fer <= etr
                or etl <= fel <= etr <= fer
            ):
                sevs.append(e["start"]) # start == end
                
        if len(set(sevs)) <= 1:
            rpel["notes"].append({
                "above": above, "alpha": 255, "isFake": 0, "size": 1.0,
                "visibleTime": 999999.0, "yOffset": 0.0,
                
                "type": 2,
                "startTime": n2f(n["time"]),
                "endTime": n2f(n["time"] + n["holdTime"]),
                "positionX": n["positionX"] * 0.05625 * 1350,
                "speed": ((n["speed"] / (sevs[0] * 120 / 900 / 0.6)) if sevs and sevs[0] != 0.0 else 1.0)
            })
        else:
            hnl = deepcopy(rpel)
            
            for e in hnl["eventLayers"][0]["speedEvents"]:
                pts, pte = f2n(e["startTime"]), f2n(e["endTime"])
                if pte == pts:
                    hnl["eventLayers"][0]["speedEvents"].remove(e)
                    continue
                
                if pte <= n["time"]:
                    continue
                else:
                    if pts >= n["time"] + n["holdTime"]:
                        hnl["eventLayers"][0]["speedEvents"].remove(e)
                    else:
                        if n["time"] <= pts <= pte <= n["time"] + n["holdTime"]:
                            hnl["eventLayers"][0]["speedEvents"].remove(e)
                        elif n["time"] <= pts <= n["time"] + n["holdTime"] <= pte:
                            hnl["eventLayers"][0]["speedEvents"].remove(e)
                        elif pte >= n["time"]:
                            e["endTime"] = n2f(n["time"])
                            nv = e["start"] / ((n["time"] - pts) / (pte - pts))
                            e["start"], e["end"] = nv, nv
            
            hnl["notes"].clear()
            hnl["eventLayers"][0]["alphaEvents"].clear()
            hnl["eventLayers"][0]["alphaEvents"].append({
                "linkgroup": 0, "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0], "easingLeft": 0.0,
                "easingRight": 1.0, "easingType": 1,
                "startTime": [0, 0, 1], "endTime": [1, 0, 1],
                "start": 0, "end": 0,
            })
            hnl["eventLayers"][0]["speedEvents"].append({
                "linkgroup": 0,
                "startTime": n2f(n["time"]),
                "endTime": n2f(n["time"] + n["holdTime"]),
                "start": 0.6 * 900 / 120,
                "end": 0.6 * 900 / 120,
            })
            hnl["notes"].append({
                "above": above, "alpha": 255, "isFake": 0, "size": 1.0,
                "visibleTime": 999999.0, "yOffset": 0.0,
                
                "type": 2,
                "startTime": n2f(n["time"]),
                "endTime": n2f(n["time"] + n["holdTime"]),
                "positionX": n["positionX"] * 0.05625 * 1350,
                "speed": n["speed"]
            })
            rpeop["judgeLineList"].append(hnl)
            print(f"add tie line hold: {n["time"]}")
    
    rpeop["judgeLineList"].append(rpel)

json.dump(rpeop, open(argv[2], "w", encoding="utf-8"), indent=4, ensure_ascii=False)