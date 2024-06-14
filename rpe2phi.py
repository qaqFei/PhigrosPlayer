#i can't write this file, because i don't know rpe format... how can tell me?????????  welcome to my github to create a issue. thank you very much!!!
from sys import argv
import json
import math

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
    
    for eventLayer in rpe_judgeLine.eventLayers:
        if eventLayer.alphaEvents is not None:
            for e in eventLayer.alphaEvents:
                pass
    
    phi_data["judgeLineList"].append(phi_judgeLine)

with open(argv[2],"w",encoding="utf-8") as f:
    f.write(json.dumps(phi_data,ensure_ascii=False))