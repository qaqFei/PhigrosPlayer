from sys import argv
import json
import math

import Chart_Functions_Phi

chart_fp = argv[1]
autojs_fp = argv[2]

with open(chart_fp, "r") as f:
    chart_obj = Chart_Functions_Phi.Load_Chart_Object(json.load(f))
    
def rotate_point(x,y,θ,r) -> float:
    xo = r * math.cos(math.radians(θ))
    yo = r * math.sin(math.radians(θ))
    return x + xo,y + yo

def press(x, y, dur, t):
    tasks_py.append(("call", "press_async", (x, y, dur), t))

def sleep(dur):
    tasks_py.append(("sleep", dur))

js = "\
setScreenMetrics(1920, 1080);\
press(1920 / 2, 1080 / 2, 1);\
st_ms = new Date().getTime();\
press_async = async function(x, y, dur) {press(x, y, dur);};\
"
tasks = []
tasks_py = []

for judgeLine in chart_obj.judgeLineList:
    for note in judgeLine.notesAbove + judgeLine.notesBelow:
        note_time = note.time * (1.875 / judgeLine.bpm)
        x, y = judgeLine.get_datavar_move(note.time, 1920, 1080)
        rotate = judgeLine.get_datavar_rotate(note.time)
        x, y = rotate_point(
            x, y, -rotate,
            note.positionX * (1080 * 0.05625)
        )
        press(x, y, 1, note_time * 1000)

async_js_func_code = ""

for task in tasks_py:
    match task[0]:
        case "call":
            pass
        case "sleep":
            pass