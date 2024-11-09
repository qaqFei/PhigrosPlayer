import fix_workpath as _

import time
import json
from os import environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
from sys import argv
from threading import Thread

from PIL import Image
from pygame import mixer

import phicore
import const
from chartfuncs_phi import Load_Chart_Object as phiload
from chartfuncs_rpe import Load_Chart_Object as rpeload
from chartobj_phi import FrameTaskRecorder, FrameTaskRecorder_Meta
from webcv import FakeCanvas

if len(argv) < 9:
    print("Usage: tool-createLfdaotFile <chart> <audio> <output> <fps> <width> <height> <chartName> <levelName> [start] [run] [maxthreads]")
    raise SystemExit

mixer.init()

chartJsonData = json.load(open(argv[1], "r", encoding="utf-8"))
if "formatVersion" in chartJsonData:
    chartobj = phiload(chartJsonData)
    CHART_TYPE = const.CHART_TYPE.PHI
else:
    chartobj = rpeload(chartJsonData)
    CHART_TYPE = const.CHART_TYPE.RPE

fps = int(argv[4])
root = FakeCanvas()
w, h = int(argv[5]), int(argv[6])

Resources = {
    "Notes":{
        "Tap": Image.open("./resources/Notes/Tap.png"),
        "Tap_dub": Image.open("./resources/Notes/Tap_dub.png"),
        "Drag": Image.open("./resources/Notes/Drag.png"),
        "Drag_dub": Image.open("./resources/Notes/Drag_dub.png"),
        "Flick": Image.open("./resources/Notes/Flick.png"),
        "Flick_dub": Image.open("./resources/Notes/Flick_dub.png"),
        "Hold_Head": Image.open("./resources/Notes/Hold_Head.png"),
        "Hold_Head_dub": Image.open("./resources/Notes/Hold_Head_dub.png"),
        "Hold_End": Image.open("./resources/Notes/Hold_End.png"),
        "Hold_End_dub": Image.open("./resources/Notes/Hold_End_dub.png"),
        "Hold_Body": Image.open("./resources/Notes/Hold_Body.png"),
        "Hold_Body_dub": Image.open("./resources/Notes/Hold_Body_dub.png")
    }, "Note_Click_Audio": None
}
note_max_width = max([Resources["Notes"]["Tap"].width, Resources["Notes"]["Tap_dub"].width, Resources["Notes"]["Drag"].width, Resources["Notes"]["Drag_dub"].width, Resources["Notes"]["Flick"].width, Resources["Notes"]["Flick_dub"].width, Resources["Notes"]["Hold_Head"].width, Resources["Notes"]["Hold_Head_dub"].width, Resources["Notes"]["Hold_End"].width])
note_max_height = max([Resources["Notes"]["Tap"].height, Resources["Notes"]["Tap_dub"].height, Resources["Notes"]["Drag"].height, Resources["Notes"]["Drag_dub"].height, Resources["Notes"]["Flick"].height, Resources["Notes"]["Flick_dub"].height, Resources["Notes"]["Hold_Head"].height, Resources["Notes"]["Hold_Head_dub"].height, Resources["Notes"]["Hold_End"].height])
note_max_size_half = (note_max_width ** 2 + note_max_height ** 2) ** 0.5
audio_length = mixer.Sound(argv[2]).get_length()

sst = time.time()
coreCfg = phicore.PhiCoreConfigure(
    SETTER = lambda k, v: globals().update({k: v}), root = root,
    w = w, h = h, chart_information = {
        "Name": argv[7],
        "Artist": "",
        "Level": argv[8],
        "Illustrator": "",
        "Charter": "",
        "BackgroundDim": 0.6
    },
    chart_obj = chartobj, CHART_TYPE = CHART_TYPE,
    Resource = Resources,
    ClickEffect_Size = (0.125 * w + 0.2 * h) / 2 * 1.375,
    EFFECT_RANDOM_BLOCK_SIZE = (0.125 * w + 0.2 * h) / 2 / 5.5,
    ClickEffectFrameCount = 30,
    PHIGROS_X = w * 0.05625, PHIGROS_Y = h * 0.6,
    Note_width = (0.125 * w + 0.2 * h) / 2,
    JUDGELINE_WIDTH = h * 0.0075,
    note_max_size_half = note_max_size_half,
    audio_length = audio_length,
    raw_audio_length = audio_length,
    show_start_time = sst,
    chart_res = {},
    clickeffect_randomblock = True,
    clickeffect_randomblock_roundn = 0.0,
    LoadSuccess = None,
    enable_clicksound = True,
    rtacc = False,
    noautoplay = False,
    showfps = False,
    lfdaot = True,
    no_mixer_reset_chart_time = False,
    speed = 1.0,
    render_range_more = False,
    render_range_more_scale = 1.0,
    judgeline_notransparent = False,
    debug = False,
    combotips = "AUTOPLAY",
    noplaychart = False,
    clicksound_volume = 1.0,
    musicsound_volume = 1.0,
    enable_controls = False
)
phicore.CoreConfig(coreCfg)

const.NOTE_DUB_FIXSCALE = Resources["Notes"]["Hold_Body_dub"].width / Resources["Notes"]["Hold_Body"].width
lfdaot_start_frame_num = int(argv[9]) if len(argv) >= 10 else 0
lfdaot_run_frame_num = int(argv[10]) if len(argv) >= 11 else float("inf")
lfdaot_tasks = {}
frame_count = lfdaot_start_frame_num
frame_time = 1 / fps
allframe_num = int(audio_length / frame_time) + 1
maxthreads = int(argv[11]) if len(argv) >= 12 else 1
pool = [i for i in range(lfdaot_start_frame_num, (lfdaot_start_frame_num + lfdaot_run_frame_num) if (lfdaot_run_frame_num != float("inf") and lfdaot_run_frame_num <= allframe_num) else allframe_num)]

def _frame(n: int):
    global frame_count
    
    if CHART_TYPE == const.CHART_TYPE.PHI:
        lfdaot_tasks.update({n: phicore.GetFrameRenderTask_Phi(n * frame_time)})
    elif CHART_TYPE == const.CHART_TYPE.RPE:
        lfdaot_tasks.update({n: phicore.GetFrameRenderTask_Rpe(n * frame_time)})
    
    frame_count += 1

def worker():
    while pool:
        _frame(pool.pop())

ts: list[Thread] = []
for _ in range(maxthreads):
    ts.append(Thread(target=worker, daemon=True))
    ts[-1].start()

try:
    while any((t.is_alive() for t in ts)):
        print(f"\r{frame_count} / {allframe_num}", end="")
        time.sleep(1 / 30)
except KeyboardInterrupt:
    pool.clear()

recorder = FrameTaskRecorder(
    meta = FrameTaskRecorder_Meta(
        frame_speed = fps,
        frame_num = len(lfdaot_tasks),
        render_range_more = False,
        render_range_more_scale = 1.0,
        size = (w, h)
    ),
    data = map(lambda x: x[1], sorted(lfdaot_tasks.items(), key=lambda x: x[0]))
)

with open(argv[3], "w", encoding="utf-8") as f:
    f.write(recorder.jsonify())