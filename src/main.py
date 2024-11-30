import err_processer as _
import init_logging as _
import fix_workpath as _
import check_edgechromium as _

import json
import sys
import time
import logging
from threading import Thread
from ctypes import windll
from os import listdir, popen, environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
from os.path import exists, isfile, isdir
from shutil import rmtree
from tempfile import gettempdir
from ntpath import basename

import cv2
from PIL import Image, ImageFilter, ImageEnhance
from pygame import mixer
from pydub import AudioSegment

import webcv
import playsound
import chartobj_phi
import chartfuncs_phi
import chartfuncs_rpe
import const
import console_window
import tool_funcs
import dialog
import info_loader
import ppr_help
from phicore import *

if not exists("./7z.exe") or not exists("./7z.dll"):
    logging.fatal("7z.exe or 7z.dll Not Found")
    windll.kernel32.ExitProcess(1)

if len(sys.argv) == 1:
    HELP = ppr_help.HELP_EN if windll.kernel32.GetSystemDefaultUILanguage() != 0x804 else ppr_help.HELP_ZH
    print(HELP)
    windll.kernel32.ExitProcess(0)
    
console_window.Hide() if "--hideconsole" in sys.argv else None

for item in [item for item in listdir(gettempdir()) if item.startswith("phigros_chart_temp_")]:
    item = f"{gettempdir()}\\{item}"
    try:
        rmtree(item)
        logging.info(f"Remove Temp Dir: {item}")
    except Exception as e:
        logging.warning(e)
        
temp_dir = f"{gettempdir()}\\phigros_chart_temp_{time.time()}"
logging.info(f"Temp Dir: {temp_dir}")

enable_clicksound = "--noclicksound" not in sys.argv
debug = "--debug" in sys.argv
show_holdbody = "--holdbody" in sys.argv
debug_noshow_transparent_judgeline = "--debug-noshow-transparent-judgeline" in sys.argv
judgeline_notransparent = "--judgeline-notransparent" in sys.argv
clickeffect_randomblock = "--noclickeffect-randomblock" not in sys.argv
loop = "--loop" in sys.argv
lfdaot = "--lfdaot" in sys.argv
lfdoat_file = "--lfdaot-file" in sys.argv
render_range_more = "--render-range-more" in sys.argv
render_range_more_scale = 2.0 if "--render-range-more-scale" not in sys.argv else eval(sys.argv[sys.argv.index("--render-range-more-scale") + 1])
lfdaot_render_video = "--lfdaot-render-video" in sys.argv
no_mixer_reset_chart_time = "--no-mixer-reset-chart-time" in sys.argv
noautoplay = "--noautoplay" in sys.argv
rtacc = "--rtacc" in sys.argv
lowquality = "--lowquality" in sys.argv
user_lowquality = lowquality
lowquality_scale = float(sys.argv[sys.argv.index("--lowquality-scale") + 1]) ** 0.5 if "--lowquality-scale" in sys.argv else 2.0 ** 0.5
showfps = "--showfps" in sys.argv
lfdaot_start_frame_num = int(eval(sys.argv[sys.argv.index("--lfdaot-start-frame-num") + 1])) if "--lfdaot-start-frame-num" in sys.argv else 0
lfdaot_run_frame_num = int(eval(sys.argv[sys.argv.index("--lfdaot-run-frame-num") + 1])) if "--lfdaot-run-frame-num" in sys.argv else float("inf")
speed = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else 1.0
clickeffect_randomblock_roundn = float(eval(sys.argv[sys.argv.index("--clickeffect-randomblock-roundn") + 1])) if "--clickeffect-randomblock-roundn" in sys.argv else 0.0
combotips = ("AUTOPLAY" if not noautoplay else "COMBO") if "--combotips" not in sys.argv else sys.argv[sys.argv.index("--combotips") + 1]
noplaychart = "--noplaychart" in sys.argv
clicksound_volume = float(sys.argv[sys.argv.index("--clicksound-volume") + 1]) if "--clicksound-volume" in sys.argv else 1.0
musicsound_volume = float(sys.argv[sys.argv.index("--musicsound-volume") + 1]) if "--musicsound-volume" in sys.argv else 1.0
lowquality_imjscvscale_x = float(sys.argv[sys.argv.index("--lowquality-imjscvscale-x") + 1]) if "--lowquality-imjscvscale-x" in sys.argv else 1.0
enable_controls = "--enable-controls" in sys.argv
lfdaot_video_fourcc = sys.argv[sys.argv.index("--lfdaot-video-fourcc") + 1] if "--lfdaot-video-fourcc" in sys.argv else "mp4v"
respaths = ["./resources"]

if "--res" in sys.argv:
    respaths.append(sys.argv[sys.argv.index("--res") + 1])

if lfdaot and noautoplay:
    noautoplay = False
    logging.warning("if use --lfdaot, you cannot use --noautoplay")

if showfps and lfdaot and lfdaot_render_video:
    showfps = False
    logging.warning("if use --lfdaot-render-video, you cannot use --showfps")

if lfdaot and speed != 1.0:
    speed = 1.0
    logging.warning("if use --lfdaot, you cannot use --speed")

mixer.init()

logging.info("Unpack Chart...")
popen(f".\\7z.exe x \"{sys.argv[1]}\" -o\"{temp_dir}\" -y >> nul").read()

logging.info("Loading All Files of Chart...")
chart_files = tool_funcs.Get_All_Files(temp_dir)
chart_files_dict = {
    "charts": [],
    "images": [],
    "audio": [],
}
for item in chart_files:
    if item.endswith("info.txt") or item.endswith("info.csv") or item.endswith("info.yml") or item.endswith("extra.json"):
        continue
    
    try:
        chart_files_dict["images"].append([item, Image.open(item).convert("RGB")])
        logging.info(f"Add Resource (image): {item.replace(f"{temp_dir}\\", "")}")
    except Exception:
        try:
            mixer.music.load(item)
            chart_files_dict["audio"].append(item)
            logging.info(f"Add Resource (audio): {item.replace(f"{temp_dir}\\", "")}")
        except Exception:
            try:
                with open(item, "r", encoding="utf-8") as f:
                    chart_text = f.read()
                    chart_files_dict["charts"].append([item, json.loads(chart_text)])
                    logging.info(f"Add Resource (chart): {item.replace(f"{temp_dir}\\", "")}")
            except Exception as e:
                if isinstance(e, json.decoder.JSONDecodeError) and (chart_text.startswith("175") or chart_text.startswith("0")): # pec chart
                    rpeJson = { # if some key and value is not exists, in loading rpe chart, it will be set to default value.
                        "META": {},
                        "BPMList": [],
                        "judgeLineList": []
                    }
                    judgeLines = {}
                    checkLineExists = lambda k: [judgeLines.update({k: {
                        "eventLayers": [{
                            "speedEvents": [],
                            "moveXEvents": [],
                            "moveYEvents": [],
                            "rotateEvents": [],
                            "alphaEvents": []
                        }],
                        "notes": []
                    }}), rpeJson["judgeLineList"].append(judgeLines[k]),
                        waitAddEventMove.update({k: {}}),
                        waitAddEventRotate.update({k: {}}),
                        waitAddEventAlpha.update({k: {}})
                    ] if k not in judgeLines else None
                    waitAddEventMove = {}
                    waitAddEventRotate = {}
                    waitAddEventAlpha = {}
                    textlines = list(filter(lambda x: x, chart_text.split("\n")))
                    eventLevelDict = {
                        "bp": 0,
                        "cp": 1, "cd": 1, "ca": 1,
                        "cm": 2, "cr": 2, "cf": 2, "cv": 3,
                        "n1": 4, "n2": 4, "n3": 4, "n4": 4, "&": 4, "#": 4
                    }
                    textlines.sort(key = lambda x: (eventLevelDict[x.split(" ")[0]] if x.split(" ")[0] in eventLevelDict else -1))
                    for i, textline in enumerate(textlines):
                        tokens = textline.split(" ")
                        try:
                            match tokens[0]:
                                case "bp":
                                    rpeJson["BPMList"].append({
                                        "startTime": [float(tokens[1]), 0, 1],
                                        "bpm": float(tokens[2])
                                    })
                                case "cp":
                                    checkLineExists(tokens[1])
                                    waitAddEventMove[tokens[1]][float(tokens[2])] = {
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "startX": (float(tokens[3]) / 2048 - 0.5) * 1350,
                                        "startY": (float(tokens[4]) / 1400 - 0.5) * 900
                                    }
                                case "cm":
                                    checkLineExists(tokens[1])
                                    line = judgeLines[tokens[1]]
                                    try: startEvent = waitAddEventMove[tokens[1]][float(tokens[2])]
                                    except KeyError: startEvent = {
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "startX": (float(tokens[4]) / 2048 - 0.5) * 1350,
                                        "startY": (float(tokens[5]) / 1400 - 0.5) * 900
                                    }
                                    line["eventLayers"][0]["moveXEvents"].append({
                                        "startTime": startEvent["startTime"],
                                        "endTime": [float(tokens[3]), 0, 1],
                                        "start": startEvent["startX"],
                                        "end": (float(tokens[4]) / 2048 - 0.5) * 1350,
                                        "easingType": int(float(tokens[6]))
                                    })
                                    line["eventLayers"][0]["moveYEvents"].append({
                                        "startTime": startEvent["startTime"],
                                        "endTime": [float(tokens[3]), 0, 1],
                                        "start": startEvent["startY"],
                                        "end": (float(tokens[5]) / 1400 - 0.5) * 900,
                                        "easingType": int(float(tokens[6]))
                                    })
                                case "cd":
                                    checkLineExists(tokens[1])
                                    waitAddEventRotate[tokens[1]][float(tokens[2])] = {
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "start": float(tokens[3]),
                                    }
                                case "cr":
                                    checkLineExists(tokens[1])
                                    line = judgeLines[tokens[1]]
                                    try: startEvent = waitAddEventRotate[tokens[1]][float(tokens[2])]
                                    except KeyError: startEvent = {
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "start": float(tokens[4])
                                    }
                                    line["eventLayers"][0]["rotateEvents"].append({
                                        "startTime": startEvent["startTime"],
                                        "endTime": [float(tokens[3]), 0, 1],
                                        "start": startEvent["start"],
                                        "end": float(tokens[4]),
                                        "easingType": int(float(tokens[5]))
                                    })
                                case "ca":
                                    checkLineExists(tokens[1])
                                    waitAddEventAlpha[tokens[1]][float(tokens[2])] = {
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "start": float(tokens[3]),
                                    }
                                case "cf":
                                    checkLineExists(tokens[1])
                                    line = judgeLines[tokens[1]]
                                    try: startEvent = waitAddEventAlpha[tokens[1]][float(tokens[2])]
                                    except KeyError: startEvent = {
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "start": float(tokens[4])
                                    }
                                    line["eventLayers"][0]["alphaEvents"].append({
                                        "startTime": startEvent["startTime"],
                                        "endTime": [float(tokens[3]), 0, 1],
                                        "start": startEvent["start"],
                                        "end": float(tokens[4]),
                                        "easingType": 1
                                    })
                                case "cv":
                                    checkLineExists(tokens[1])
                                    line = judgeLines[tokens[1]]
                                    line["eventLayers"][0]["speedEvents"].append({
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "start": float(tokens[3]) * 0.5844193793466191, # 1 / 1.7111
                                        "end": float(tokens[3]) * 0.5844193793466191,
                                        "easingType": 1
                                    })
                                case "n1" | "n2" | "n3" | "n4":
                                    checkLineExists(tokens[1])
                                    line = judgeLines[tokens[1]]
                                    ntls = [textlines[i + 1], textlines[i + 2]]
                                    ntl1 = ntls[0] if "#" in ntls[0] else ntls[1]
                                    ntl2 = ntls[1] if "&" in ntls[1] else ntls[0]
                                    if tokens[0] == "n2":
                                        et = [float(tokens[3]), 0, 1]
                                        del tokens[3]
                                    line["notes"].append({
                                        "type": {"n1": 1, "n2": 2, "n3": 3, "n4": 4}[tokens[0]],
                                        "startTime": [float(tokens[2]), 0, 1],
                                        "endTime": [float(tokens[2]), 0, 1] if tokens[0] != "n2" else et,
                                        "positionX": float(tokens[3]) / 2048 * 1350,
                                        "above": int(float(tokens[4])),
                                        "isFake": bool(int(float(tokens[5]))),
                                        "speed": float(ntl1.replace(" ", "").replace("#", "")),
                                        "size": float(ntl2.replace(" ", "").replace("&", ""))
                                    })
                        except Exception as e:
                            logging.warning(f"In pec2rpe: {repr(e)}")
                    for line in rpeJson["judgeLineList"]:
                        for i, e in enumerate(line["eventLayers"][0]["speedEvents"]):
                            if i != len(line["eventLayers"][0]["speedEvents"]) - 1:
                                e["endTime"] = line["eventLayers"][0]["speedEvents"][i + 1]["startTime"]
                            else:
                                e["endTime"] = [e["startTime"][0] + 31250000, 0, 1]
                    chart_files_dict["charts"].append([item, rpeJson])
                else:
                    logging.warning(f"Unknown Resource Type. Path = {item.replace(f"{temp_dir}\\", "")}, Error = {e}")
                    
if len(chart_files_dict["charts"]) == 0:
    logging.fatal("No Chart File Found")
    windll.kernel32.ExitProcess(1)
if len(chart_files_dict["audio"]) == 0:
    logging.fatal("No Audio File Found")
    windll.kernel32.ExitProcess(1)
if len(chart_files_dict["images"]) == 0:
    chart_files_dict["images"].append(["default", Image.new("RGB", (16, 9), "#0078d7")])

phigros_chart_index = 0
chart_image_index = 0
audio_file_index = 0

if len(chart_files_dict["charts"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["charts"]):
        name = chart_file[0].split("/")[-1].split("\\")[-1]
        print(f"{index + 1}. {name}")
    phigros_chart_index = int(input("请选择谱面文件: ")) - 1
    chart_json = chart_files_dict["charts"][phigros_chart_index][1]
else:
    chart_json = chart_files_dict["charts"][phigros_chart_index][1]
phigros_chart_filepath = chart_files_dict["charts"][phigros_chart_index][0]

if "formatVersion" in chart_json:
    CHART_TYPE = const.CHART_TYPE.PHI
elif "META" in chart_json:
    CHART_TYPE = const.CHART_TYPE.RPE
    render_range_more = False
else:
    logging.fatal("This is what format chart???")
    windll.kernel32.ExitProcess(1)

def LoadChartObject(first: bool = False):
    global chart_obj
    if CHART_TYPE == const.CHART_TYPE.PHI:
        chart_obj = chartfuncs_phi.Load_Chart_Object(chart_json)
    elif CHART_TYPE == const.CHART_TYPE.RPE:
        chart_obj = chartfuncs_rpe.Load_Chart_Object(chart_json)
    
    if not first:
        updateCoreConfigure()
LoadChartObject(True)

if len(chart_files_dict["images"]) > 1:
    if CHART_TYPE == const.CHART_TYPE.RPE and chart_obj.META.background in [i[0].split("/")[-1].split("\\")[-1] for i in chart_files_dict["images"]]:
        chart_image_index = [i[0].split("/")[-1].split("\\")[-1] for i in chart_files_dict["images"]].index(chart_obj.META.background)
        chart_image:Image.Image = chart_files_dict["images"][chart_image_index][1]
    else:
        for index, file in enumerate(chart_files_dict["images"]):
            name = file[0].split("/")[-1].split("\\")[-1]
            print(f"{index + 1}. {name}")
        chart_image_index = int(input("请选择谱面图片: ")) - 1
        chart_image:Image.Image = chart_files_dict["images"][chart_image_index][1]
else:
    chart_image:Image.Image = chart_files_dict["images"][chart_image_index][1]
chart_image_filepath = chart_files_dict["images"][chart_image_index][0]

if len(chart_files_dict["audio"]) > 1:
    if CHART_TYPE == const.CHART_TYPE.RPE and chart_obj.META.song in [i.split("/")[-1].split("\\")[-1] for i in chart_files_dict["audio"]]:
        audio_file_index = [i.split("/")[-1].split("\\")[-1] for i in chart_files_dict["audio"]].index(chart_obj.META.song)
        audio_file = chart_files_dict["audio"][audio_file_index]
    else:
        for index, file in enumerate(chart_files_dict["audio"]):
            name = file.split("/")[-1].split("\\")[-1]
            print(f"{index + 1}. {name}")
        audio_file_index = int(input("请选择音频文件: ")) - 1
        audio_file = chart_files_dict["audio"][audio_file_index]
else:
    audio_file = chart_files_dict["audio"][audio_file_index]

raw_audio_file = audio_file
if speed != 1.0:
    logging.info(f"Processing audio, rate = {speed}")
    seg: AudioSegment = AudioSegment.from_file(audio_file)
    seg = seg._spawn(seg.raw_data, overrides = {
        "frame_rate": int(seg.frame_rate * speed)
    }).set_frame_rate(seg.frame_rate)
    audio_file = f"{temp_dir}/ppr_temp_audio_{time.time()}.mp3"
    seg.export(audio_file, format="mp3")

mixer.music.load(audio_file)
raw_audio_length = mixer.Sound(audio_file).get_length()
audio_length = raw_audio_length + (chart_obj.META.offset / 1000 if CHART_TYPE == const.CHART_TYPE.RPE else 0.0)
all_inforamtion = {}
logging.info("Loading Chart Information...")

ChartInfoLoader = info_loader.InfoLoader([f"{temp_dir}\\info.csv", f"{temp_dir}\\info.txt", f"{temp_dir}\\info.yml"])
chart_information = ChartInfoLoader.get(basename(phigros_chart_filepath), basename(raw_audio_file), basename(chart_image_filepath))
    
logging.info("Loading Chart Information Successfully")
logging.info("Inforamtions: ")
for k,v in chart_information.items():
    logging.info(f"              {k}: {v}")
del chart_files, chart_files_dict

extraPath = f"{temp_dir}/extra.json"
extra = {
    "bpm": [ { "time": [ 0, 0, 1 ], "bpm": 1.0 } ],
    "effects": []
}
if exists(extraPath) and isfile(extraPath):
    try:
        with open(extraPath, "r", encoding="utf-8") as f:
            extra.update(json.load(f))
    except Exception as e:
        logging.warning(f"extra.json is not valid, {repr(e)}")

def getResPath(path:str, file: bool = True):
    for rp in reversed(respaths):
        fp = f"{rp}{path}"
        if exists(fp) and (isfile(fp) if file else isdir(fp)):
            return fp
    return f"{respaths[0]}\\{path}"

def putColor(color: tuple|str, im: Image.Image):
    return Image.merge("RGBA", (
        *Image.new("RGB", im.size, color).split(),
        im.split()[-1]
    ))

def loadAudio(path: str):
    seg = AudioSegment.from_file(path)
    fp = f"{temp_dir}/{hash(path)}.wav"
    seg.export(fp, format="wav")
    return open(fp, "rb").read()

def getLowqualityImage(im: Image.Image):
    if user_lowquality and lowquality_scale >= 1.0:
        uw, uh = int(im.width / lowquality_scale / 2), int(im.height / lowquality_scale / 2)
        if uw > 8 and uh > 8:
            return im.resize((uw, uh))
    return im

def Load_Resource():
    global ClickEffect_Size, Note_width
    global note_max_width, note_max_height
    global note_max_size_half
    global animation_image
    global WaitLoading, LoadSuccess
    global chart_res
    global ClickEffectFrameCount
    global shaders
    
    logging.info("Loading Resource...")
    WaitLoading = mixer.Sound(getResPath("/WaitLoading.mp3"))
    LoadSuccess = mixer.Sound(getResPath("/LoadSuccess.wav"))
    Thread(target=WaitLoading_FadeIn, daemon = True).start()
    LoadSuccess.set_volume(0.75)
    WaitLoading.play(-1)
    Note_width_raw = (0.125 * w + 0.2 * h) / 2
    Note_width = (Note_width_raw) * (eval(sys.argv[sys.argv.index("--scale-note") + 1]) if "--scale-note" in sys.argv else 1.0)
    ClickEffect_Size = Note_width * 1.375
    ClickEffectFrameCount = len(listdir(getResPath("/Note_Click_Effect/Frames", False)))
    ClickEffectImages = [Image.open(getResPath(f"/Note_Click_Effect/Frames/{i + 1}.png")) for i in range(ClickEffectFrameCount)]
    Resource = {
        "Notes":{
            "Tap": Image.open(getResPath("/Notes/Tap.png")),
            "Tap_dub": Image.open(getResPath("/Notes/Tap_dub.png")),
            "Drag": Image.open(getResPath("/Notes/Drag.png")),
            "Drag_dub": Image.open(getResPath("/Notes/Drag_dub.png")),
            "Flick": Image.open(getResPath("/Notes/Flick.png")),
            "Flick_dub": Image.open(getResPath("/Notes/Flick_dub.png")),
            "Hold_Head": Image.open(getResPath("/Notes/Hold_Head.png")),
            "Hold_Head_dub": Image.open(getResPath("/Notes/Hold_Head_dub.png")),
            "Hold_End": Image.open(getResPath("/Notes/Hold_End.png")),
            "Hold_End_dub": Image.open(getResPath("/Notes/Hold_End_dub.png")),
            "Hold_Body": Image.open(getResPath("/Notes/Hold_Body.png")),
            "Hold_Body_dub": Image.open(getResPath("/Notes/Hold_Body_dub.png")),
            "Bad": None
        },
        "Note_Click_Effect":{
            "Perfect": list(map(lambda im: putColor((255, 236, 160), im), ClickEffectImages)),
            "Good": list(map(lambda im: putColor((180, 225, 255), im), ClickEffectImages)),
        },
        "Levels":{
            "AP": Image.open(getResPath("/Levels/AP.png")),
            "FC": Image.open(getResPath("/Levels/FC.png")),
            "V": Image.open(getResPath("/Levels/V.png")),
            "S": Image.open(getResPath("/Levels/S.png")),
            "A": Image.open(getResPath("/Levels/A.png")),
            "B": Image.open(getResPath("/Levels/B.png")),
            "C": Image.open(getResPath("/Levels/C.png")),
            "F": Image.open(getResPath("/Levels/F.png"))
        },
        "Note_Click_Audio":{
            "Tap": playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Tap.wav"))),
            "Drag": playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Drag.wav"))),
            "Hold": playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Hold.wav"))),
            "Flick": playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Flick.wav")))
        },
        "le_warn": Image.open(getResPath("/le_warn.png")),
        "Button_Left": Image.open(getResPath("/Button_Left.png")),
        "Button_Right": None,
        "Retry": Image.open(getResPath("/Retry.png")),
        "Arrow_Right": Image.open(getResPath("/Arrow_Right.png")),
        "Over": mixer.Sound(getResPath("/Over.mp3")),
        "Pause": mixer.Sound(getResPath("/Pause.wav")),
        "PauseImg": Image.open(getResPath("/Pause.png"))
    }
    
    respacker = webcv.PILResourcePacker(root)
    
    background_image_blur = chart_image.resize((w, h)).filter(ImageFilter.GaussianBlur((w + h) / 50))
    background_image = ImageEnhance.Brightness(background_image_blur).enhance(1.0 - chart_information["BackgroundDim"])
    respacker.reg_img(background_image, "background")
    
    Resource["Button_Right"] = Resource["Button_Left"].transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    Resource["Notes"]["Bad"] = putColor((90, 60, 70), Resource["Notes"]["Tap"])
    
    finish_animation_image_mask = Image.new("RGBA", (1, 5), (0, 0, 0, 0))
    finish_animation_image_mask.putpixel((0, 4), (0, 0, 0, 204))
    finish_animation_image_mask.putpixel((0, 3), (0, 0, 0, 128))
    finish_animation_image_mask.putpixel((0, 2), (0, 0, 0, 64))
    
    animation_image = chart_image.copy().convert("RGBA")
    tool_funcs.cutAnimationIllImage(animation_image)
    
    finish_animation_image = chart_image.copy().convert("RGBA")
    finish_animation_image_mask = finish_animation_image_mask.resize(finish_animation_image.size)
    finish_animation_image.paste(finish_animation_image_mask, (0, 0), finish_animation_image_mask)
    tool_funcs.cutAnimationIllImage(finish_animation_image)
    
    const.set_NOTE_DUB_FIXSCALE(Resource["Notes"]["Hold_Body_dub"].width / Resource["Notes"]["Hold_Body"].width)
    for k, v in Resource["Notes"].items(): # Resize Notes (if Notes is too big) and reg them
        if v.width > Note_width:
            Resource["Notes"][k] = v.resize((int(Note_width),int(Note_width / v.width * v.height)))
    
    # process lowquality images
    for k,v in Resource["Notes"].items():
        Resource["Notes"][k] = getLowqualityImage(v)
    for k, v in Resource["Note_Click_Effect"].items():
        for i, im in enumerate(v):
            Resource["Note_Click_Effect"][k][i] = getLowqualityImage(im)
    for k, v in Resource["Levels"].items():
        Resource["Levels"][k] = getLowqualityImage(v)
    
    for k, v in Resource["Notes"].items():
        respacker.reg_img(Resource["Notes"][k], f"Note_{k}")
    
    for i in range(ClickEffectFrameCount): # reg click effect
        respacker.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
        respacker.reg_img(Resource["Note_Click_Effect"]["Good"][i], f"Note_Click_Effect_Good_{i + 1}")
        
    for k,v in Resource["Levels"].items(): # reg levels img
        respacker.reg_img(v, f"Level_{k}")
        
    respacker.reg_img(Resource["le_warn"], "le_warn")
    respacker.reg_img(animation_image, "begin_animation_image")
    respacker.reg_img(finish_animation_image, "finish_animation_image")
    respacker.reg_img(Resource["Button_Left"], "Button_Left")
    respacker.reg_img(Resource["Button_Right"], "Button_Right")
    respacker.reg_img(Resource["Retry"], "Retry")
    respacker.reg_img(Resource["Arrow_Right"], "Arrow_Right")
    respacker.reg_img(Resource["PauseImg"], "PauseImg")
    
    chart_res = {}
    if CHART_TYPE == const.CHART_TYPE.RPE:
        for line in chart_obj.JudgeLineList:
            if line.Texture != "line.png":
                paths = [
                    f"{temp_dir}\\{line.Texture}",
                    f"{temp_dir}\\{line.Texture}.png",
                    f"{temp_dir}\\{line.Texture}.jpg",
                    f"{temp_dir}\\{line.Texture}.jpeg",
                    f"./Resource/{line.Texture}",
                    f"./Resource/{line.Texture}.png",
                    f"./Resource/{line.Texture}.jpg",
                    f"./Resource/{line.Texture}.jpeg"
                ]
                for p in paths:
                    if exists(p) and isfile(p):
                        try:
                            texture = Image.open(p).convert("RGBA")
                            size = texture.size
                            if user_lowquality and lowquality_scale >= 1.0:
                                textureWidth, textureHeight = texture.size
                                textureWidth /= lowquality_scale * 2; textureHeight /= lowquality_scale * 2
                                textureWidth, textureHeight = int(textureWidth), int(textureHeight)
                                if textureWidth > 32 and textureHeight > 32:
                                    texture = texture.resize((textureWidth, textureHeight))
                            chart_res[line.Texture] = (texture, size)
                        except Exception as e:
                            logging.error(f"Can't open texture {p} : {e}")
                            continue
                        break
                else:
                    logging.error(f"Can't find texture {line.Texture}")
                    texture = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
                    chart_res[line.Texture] = (texture, texture.size)
                respacker.reg_img(chart_res[line.Texture][0], f"lineTexture_{chart_obj.JudgeLineList.index(line)}")
    
    with open(getResPath("/font.ttf"), "rb") as f:
        root.reg_res(f.read(),"PhigrosFont")
    respacker.load(*respacker.pack())
    
    root.wait_jspromise(f"loadFont('PhigrosFont',\"{root.get_resource_path("PhigrosFont")}\");")
    root.unreg_res("PhigrosFont")
    
    root.file_server.shutdown()
    note_max_width = max(
        [
            Resource["Notes"]["Tap"].width,
            Resource["Notes"]["Tap_dub"].width,
            Resource["Notes"]["Drag"].width,
            Resource["Notes"]["Drag_dub"].width,
            Resource["Notes"]["Flick"].width,
            Resource["Notes"]["Flick_dub"].width,
            Resource["Notes"]["Hold_Head"].width,
            Resource["Notes"]["Hold_Head_dub"].width,
            Resource["Notes"]["Hold_End"].width
        ]
    )
    note_max_height = max(
        [
            Resource["Notes"]["Tap"].height,
            Resource["Notes"]["Tap_dub"].height,
            Resource["Notes"]["Drag"].height,
            Resource["Notes"]["Drag_dub"].height,
            Resource["Notes"]["Flick"].height,
            Resource["Notes"]["Flick_dub"].height,
            Resource["Notes"]["Hold_Head"].height,
            Resource["Notes"]["Hold_Head_dub"].height,
            Resource["Notes"]["Hold_End"].height
        ]
    )
    note_max_size_half = (note_max_width ** 2 + note_max_height ** 2) ** 0.5
    
    logging.info("Loading Shaders...")
    
    shaders = {
        "chromatic": open("./shaders/chromatic.glsl", "r", encoding="utf-8").read(),
        "circleBlur": open("./shaders/circle_blur.glsl", "r", encoding="utf-8").read(),
        "fisheye": open("./shaders/fisheye.glsl", "r", encoding="utf-8").read(),
        "glitch": open("./shaders/glitch.glsl", "r", encoding="utf-8").read(),
        "grayscale": open("./shaders/grayscale.glsl", "r", encoding="utf-8").read(),
        "noise": open("./shaders/noise.glsl", "r", encoding="utf-8").read(),
        "pixel": open("./shaders/pixel.glsl", "r", encoding="utf-8").read(),
        "radialBlur": open("./shaders/radial_blur.glsl", "r", encoding="utf-8").read(),
        "shockwave": open("./shaders/shockwave.glsl", "r", encoding="utf-8").read(),
        "vignette": open("./shaders/vignette.glsl", "r", encoding="utf-8").read()
    }
    
    try:
        for effect in extra["effects"]:
            try:
                shaderName = effect["shader"]
                if shaderName in shaders: continue
                shaderPath = f"{temp_dir}/{shaderName}"
                if exists(shaderPath) and isfile(shaderPath):
                    shaders[shaderName] = open(shaderPath, "r", encoding="utf-8").read()
                else:
                    raise Exception(f"Shader {shaderName} not found")
            except Exception as e:
                logging.error(f"Load Shader {shaderName} Failed")
    except Exception as e:
        logging.error("Load Other Shaders Failed")
    
    extra["effects"] = list(filter(lambda x: x.get("shader", "") in shaders, extra["effects"]))
    
    # how to load shaders to webgl and use them???
    ... # TODO
    
    logging.info("Load Shaders Successfully")
    
    logging.info("Load Resource Successfully")
    return Resource

def WaitLoading_FadeIn():
    for i in range(50):
        WaitLoading.set_volume((i + 1) / 100)
        time.sleep(2 / 50)

def Show_Start():
    WaitLoading.fadeout(450)
    
    def dle_warn(a: float):
        root.run_js_code(
            f"ctx.drawAlphaImage(\
                {root.get_img_jsvarname("le_warn")},\
                0, 0, {w}, {h}, {a}\
            );",
            add_code_array = True
        )
    
    animationst = time.time()
    while time.time() - animationst < 1.0:
        root.clear_canvas(wait_execute=True)
        p = (time.time() - animationst) / 1.0
        dle_warn(1.0 - (1.0 - tool_funcs.fixorp(p)) ** 4)
        root.run_js_wait_code()
    
    time.sleep(0.35)
    
    animationst = time.time()
    while time.time() - animationst < 1.0:
        root.clear_canvas(wait_execute=True)
        draw_background()
        draw_ui(animationing=True)
        p = (time.time() - animationst) / 1.0
        dle_warn((tool_funcs.fixorp(p) - 1.0) ** 4)
        root.run_js_wait_code()
    
    time.sleep(0.25)
    root.clear_canvas(wait_execute=True)
    draw_background()
    draw_ui(animationing=True)
    root.run_js_wait_code()
    Thread(target=PlayerStart, daemon=True).start()

def PlayerStart():
    global show_start_time
    Resource["Over"].stop()
    
    Begin_Animation()
    ChartStart_Animation()

    show_start_time = time.time()
    PhiCoreConfigureObject.show_start_time = show_start_time
    updateCoreConfigure()
    now_t = 0
    
    if not lfdaot:
        mixer.music.play()
        while not mixer.music.get_busy(): pass
    
    if not lfdaot:
        if noautoplay:
            if CHART_TYPE == const.CHART_TYPE.PHI:
                pplm_proxy = chartobj_phi.PPLMPHI_Proxy(chart_obj)
            elif CHART_TYPE == const.CHART_TYPE.RPE:
                pplm_proxy = chartobj_rpe.PPLMRPE_Proxy(chart_obj)
            
            pppsm = tool_funcs.PhigrosPlayPlayStateManager(chart_obj.note_num)
            pplm = tool_funcs.PhigrosPlayLogicManager(pplm_proxy, pppsm, enable_clicksound, print)
            
            root.jsapi.set_attr("PhigrosPlay_KeyDown", lambda t: pplm.pc_click(t - show_start_time))
            root.jsapi.set_attr("PhigrosPlay_KeyUp", lambda t: pplm.pc_release(t - show_start_time))
            root.run_js_code("_PhigrosPlay_KeyDown = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyDown', new Date().getTime() / 1000);});")
            root.run_js_code("_PhigrosPlay_KeyUp = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyUp', new Date().getTime() / 1000);});")
            root.run_js_code("window.addEventListener('keydown', _PhigrosPlay_KeyDown);")
            root.run_js_code("window.addEventListener('keyup', _PhigrosPlay_KeyUp);")
            
        play_restart_flag = False
        pause_flag = False
        pause_st = float("nan")
        
        def _f(): nonlocal play_restart_flag; play_restart_flag = True
        
        @tool_funcs.NoJoinThreadFunc
        def space():
            global show_start_time
            nonlocal pause_flag, pause_st
            
            if not pause_flag:
                pause_flag = True
                mixer.music.pause()
                Resource["Pause"].play()
                pause_st = time.time()
            else:
                mixer.music.unpause()
                show_start_time += time.time() - pause_st
                pause_flag = False
                
        root.jsapi.set_attr("Noautoplay_Restart", _f)
        root.jsapi.set_attr("SpaceClicked", space)
        root.run_js_code("_Noautoplay_Restart = (e) => {if (e.altKey && e.ctrlKey && e.repeat && e.key.toLowerCase() == 'r') pywebview.api.call_attr('Noautoplay_Restart');};") # && e.repeat 为了判定长按
        root.run_js_code("_SpaceClicked = (e) => {if (e.key == ' ' && !e.repeat) pywebview.api.call_attr('SpaceClicked');};")
        root.run_js_code("window.addEventListener('keydown', _Noautoplay_Restart);")
        root.run_js_code("window.addEventListener('keydown', _SpaceClicked);")
        
        while True:
            while pause_flag: time.sleep(1 / 30)
            
            now_t = time.time() - show_start_time
            if CHART_TYPE == const.CHART_TYPE.PHI:
                Task = GetFrameRenderTask_Phi(now_t, pplm = pplm if noautoplay else None)
            elif CHART_TYPE == const.CHART_TYPE.RPE:
                Task = GetFrameRenderTask_Rpe(now_t, pplm = pplm if noautoplay else None)
                
            Task.ExecTask()
            
            break_flag = chartfuncs_phi.FrameData_ProcessExTask(
                Task.ExTask,
                lambda x: eval(x)
            )
            
            if break_flag:
                break
            
            if play_restart_flag:
                break
        
        if noautoplay:
            root.run_js_code("window.removeEventListener('keydown', _PhigrosPlay_KeyDown);")
            root.run_js_code("window.removeEventListener('keyup', _PhigrosPlay_KeyUp);")
        
        root.run_js_code("window.removeEventListener('keydown', _Noautoplay_Restart);")
        root.run_js_code("window.removeEventListener('keydown', _SpaceClicked);")
            
        if play_restart_flag:
            mixer.music.fadeout(250)
            LoadChartObject()
            Thread(target=PlayerStart, daemon=True).start()
            return
    else:
        lfdaot_tasks = {}
        frame_speed = 60
        if "--lfdaot-frame-speed" in sys.argv:
            frame_speed = eval(sys.argv[sys.argv.index("--lfdaot-frame-speed") + 1])
        frame_count = lfdaot_start_frame_num
        frame_time = 1 / frame_speed
        allframe_num = int(audio_length / frame_time) + 1
        
        if lfdaot and not lfdoat_file: #eq if not lfdoat_file
            while True:
                if frame_count * frame_time > audio_length or frame_count - lfdaot_start_frame_num >= lfdaot_run_frame_num:
                    break
                
                if CHART_TYPE == const.CHART_TYPE.PHI:
                    lfdaot_tasks.update({frame_count: GetFrameRenderTask_Phi(frame_count * frame_time)})
                elif CHART_TYPE == const.CHART_TYPE.RPE:
                    lfdaot_tasks.update({frame_count: GetFrameRenderTask_Rpe(frame_count * frame_time)})
                
                frame_count += 1
                
                print(f"\rLoadFrameData: {frame_count} / {allframe_num}", end="")
            
            if "--lfdaot-file-savefp" in sys.argv:
                lfdaot_fp = sys.argv[sys.argv.index("--lfdaot-file-savefp") + 1]
            else:
                lfdaot_fp = dialog.savefile(
                    fn = "Chart.lfdaot"
                )
            
            if lfdaot_fp != "":
                recorder = chartobj_phi.FrameTaskRecorder(
                    meta = chartobj_phi.FrameTaskRecorder_Meta(
                        frame_speed = frame_speed,
                        frame_num = len(lfdaot_tasks),
                        render_range_more = render_range_more,
                        render_range_more_scale = render_range_more_scale,
                        size = (w, h)
                    ),
                    data = lfdaot_tasks.values()
                )
                with open(lfdaot_fp, "w", encoding="utf-8") as f:
                    f.write(recorder.jsonify())
                    
            if "--lfdaot-file-output-autoexit" in sys.argv:
                root.destroy()
                return
        else: #--lfdaot-file
            fp = sys.argv[sys.argv.index("--lfdaot-file") + 1]
            with open(fp,"r",encoding="utf-8") as f:
                data = json.load(f)
            if data["meta"]["render_range_more"]:
                root.run_js_code("render_range_more = true;")
                root.run_js_code(f"render_range_more_scale = {data["meta"]["render_range_more_scale"]};")
            frame_speed = data["meta"]["frame_speed"]
            allframe_num = data["meta"]["frame_num"]
            Task_function_mapping = {
                func_name:getattr(root,func_name)
                for func_name in dir(root)
            }
            Task_function_mapping.update({
                "draw_background": draw_background,
                "draw_ui": draw_ui
            })
            for index,Task_data in enumerate(data["data"]):
                lfdaot_tasks.update({
                    index:chartobj_phi.FrameRenderTask(
                        RenderTasks = [
                            chartobj_phi.RenderTask(
                                func = Task_function_mapping[render_task_data["func_name"]],
                                args = tuple(render_task_data["args"]),
                                kwargs = render_task_data["kwargs"]
                            )
                            for render_task_data in Task_data["render"]
                        ],
                        ExTask = tuple(Task_data["ex"])
                    )
                })
            if data["meta"]["size"] != [w,h]:
                logging.warning("The size of the lfdaot file is not the same as the size of the window")
        
        if not lfdaot_render_video:
            mixer.music.play()
            while not mixer.music.get_busy(): pass
        
            last_music_play_fcount = None
            while True:
                render_st = time.time()
                now_t = mixer.music.get_pos() / 1000
                music_play_fcount = int(now_t / frame_time)
                will_process_extask = []
                try:
                    Task: chartobj_phi.FrameRenderTask = lfdaot_tasks[music_play_fcount]
                except KeyError:
                    continue
                
                if last_music_play_fcount is not None:
                    for fcount in range(last_music_play_fcount,music_play_fcount):
                        try:
                            Task:chartobj_phi.FrameRenderTask = lfdaot_tasks[fcount]
                            if Task.ExTask is not None:
                                will_process_extask.append(Task.ExTask)
                                Task.ExTask = None
                        except KeyError:
                            pass
            
                if not Task.RenderTasks: #empty
                    continue
                
                last_music_play_fcount = music_play_fcount
                
                Task.ExecTask()
                
                break_flag_top = False
                
                if Task.ExTask is not None:
                    will_process_extask.append(Task.ExTask)
                    Task.ExTask = None
                for ExTask in will_process_extask:
                    break_flag = chartfuncs_phi.FrameData_ProcessExTask(
                        ExTask,
                        lambda x: eval(x)
                    )
                    
                    if break_flag:
                        break_flag_top = True
                
                if break_flag_top:
                    break
                
                time.sleep(max(0,frame_time - (time.time() - render_st)))
        else: # --lfdaot-render-video
            if "--lfdaot-render-video-savefp" in sys.argv:
                video_fp = sys.argv[sys.argv.index("--lfdaot-render-video-savefp") + 1]
            else:
                video_fp = dialog.savefile(
                    fn = "lfdaot_render_video.mp4"
                )
            writer = cv2.VideoWriter(
                video_fp,
                cv2.VideoWriter.fourcc(*lfdaot_video_fourcc),
                frame_speed, (w, h),
                True
            )
            
            if video_fp != "":
                root.jsapi.uploadFrame = lambda dataUrl: writer.write(tool_funcs.DataUrl2MatLike(dataUrl))
                
                for Task in lfdaot_tasks.values():
                    Task.ExecTask()
                    root.run_js_code("uploadFrame();")
                
                root.run_js_code("uploadFrame_addQueue = true;")
                
                while not root.run_js_code("uploadFrame_finish;"):
                    time.sleep(0.1)
                root.run_js_code("resetUploadFrameFlags();")
                
                writer.release()
    
    mixer.music.set_volume(1.0)
    initFinishAnimation(pplm if noautoplay else None)
    
    def Chart_Finish_Animation():
        animation_1_time = 0.75
        a1_combo = pplm.ppps.getCombo() if noautoplay else None
        
        animation_1_start_time = time.time()
        while True:
            p = (time.time() - animation_1_start_time) / animation_1_time
            if p > 1.0: break
            Chart_BeforeFinish_Animation_Frame(p, a1_combo)
        
        time.sleep(0.25)
        Resource["Over"].play(-1)
    
        animation_2_time = 3.5
        animation_2_start_time = time.time()
        a2_loop_clicked = False
        a2_continue_clicked = False
        a2_break = False
        
        def whileCheck():
            nonlocal a2_break
            while True:
                if a2_loop_clicked or (loop and (time.time() - animation_2_start_time) > 2.75):
                    def _f():
                        LoadChartObject()
                        PlayerStart()
                    Thread(target=_f, daemon=True).start()
                    break
                
                if a2_continue_clicked:
                    root.destroy()
                    break
                    
                time.sleep(1 / 240)
            
            root.run_js_code("window.removeEventListener('click', _loopClick);")
            root.run_js_code("window.removeEventListener('click', _continueClick);")
            a2_break = True
        
        Thread(target=whileCheck, daemon=True).start()
        
        def loopClick(clientX, clientY):
            nonlocal a2_loop_clicked
            if clientX <= w * const.FINISH_UI_BUTTON_SIZE and clientY <= w * const.FINISH_UI_BUTTON_SIZE / 190 * 145:
                a2_loop_clicked = True
        
        def continueClick(clientX, clientY):
            nonlocal a2_continue_clicked
            if clientX >= w - w * const.FINISH_UI_BUTTON_SIZE and clientY >= h - w * const.FINISH_UI_BUTTON_SIZE / 190 * 145:
                a2_continue_clicked = True
        
        root.jsapi.set_attr("loopClick", loopClick)
        root.jsapi.set_attr("continueClick", continueClick)
        root.run_js_code("_loopClick = (e) => {pywebview.api.call_attr('loopClick', e.clientX, e.clientY);}")
        root.run_js_code("_continueClick = (e) => {pywebview.api.call_attr('continueClick', e.clientX, e.clientY);}")
        root.run_js_code("window.addEventListener('click', _loopClick);")
        root.run_js_code("window.addEventListener('click', _continueClick);")
        
        while not a2_break:
            p = (time.time() - animation_2_start_time) / animation_2_time
            if p > 1.0: break
            Chart_Finish_Animation_Frame(p)
        
        while not a2_break:
            Chart_Finish_Animation_Frame(1.0)
            
    mixer.music.fadeout(250)
    Chart_Finish_Animation()

def updateCoreConfigure():
    global PhiCoreConfigureObject
    
    PhiCoreConfigureObject = PhiCoreConfigure(
        SETTER = lambda vn, vv: globals().update({vn: vv}),
        root = root, w = w, h = h,
        chart_information = chart_information,
        chart_obj = chart_obj, CHART_TYPE = CHART_TYPE,
        Resource = Resource, ClickEffect_Size = ClickEffect_Size,
        EFFECT_RANDOM_BLOCK_SIZE = EFFECT_RANDOM_BLOCK_SIZE,
        ClickEffectFrameCount = ClickEffectFrameCount,
        PHIGROS_X = PHIGROS_X, PHIGROS_Y = PHIGROS_Y,
        Note_width = Note_width, JUDGELINE_WIDTH = JUDGELINE_WIDTH,
        note_max_size_half = note_max_size_half, audio_length = audio_length,
        raw_audio_length = raw_audio_length, show_start_time = float("nan"),
        chart_res = chart_res, clickeffect_randomblock = clickeffect_randomblock,
        clickeffect_randomblock_roundn = clickeffect_randomblock_roundn,
        LoadSuccess = LoadSuccess,
        enable_clicksound = enable_clicksound, rtacc = rtacc,
        noautoplay = noautoplay, showfps = showfps, lfdaot = lfdaot,
        no_mixer_reset_chart_time = no_mixer_reset_chart_time,
        speed = speed, render_range_more = render_range_more,
        render_range_more_scale = render_range_more_scale,
        judgeline_notransparent = judgeline_notransparent,
        debug = debug, combotips = combotips, noplaychart = noplaychart,
        clicksound_volume = clicksound_volume,
        musicsound_volume = musicsound_volume,
        enable_controls = enable_controls
    )
    CoreConfig(PhiCoreConfigureObject)

logging.info("Loading Window...")
root = webcv.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "PhigrosPlayer - Simulator",
    debug = "--debug" in sys.argv,
    resizable = False,
    frameless = "--frameless" in sys.argv
)
        
webdpr = root.run_js_code("window.devicePixelRatio;")
if webdpr != 1.0:
    lowquality = True
    lowquality_scale *= 1.0 / webdpr # ...?

if lowquality:
    root.run_js_code(f"lowquality_scale = {lowquality_scale};")

if "--window-host" in sys.argv:
    windll.user32.SetParent(root.winfo_hwnd(), eval(sys.argv[sys.argv.index("--window-host") + 1]))
if "--fullscreen" in sys.argv:
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.web.toggle_fullscreen()
else:
    if "--size" not in sys.argv:
        w, h = int(root.winfo_screenwidth() * 0.6), int(root.winfo_screenheight() * 0.6)
    else:
        w, h = int(eval(sys.argv[sys.argv.index("--size") + 1])), int(eval(sys.argv[sys.argv.index("--size") + 2]))
    root.resize(w, h)
    w_legacy, h_legacy = root.winfo_legacywindowwidth(), root.winfo_legacywindowheight()
    dw_legacy, dh_legacy = w - w_legacy, h - h_legacy
    dw_legacy *= webdpr; dh_legacy *= webdpr
    dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
    del w_legacy, h_legacy
    root.resize(w + dw_legacy, h + dh_legacy)
    root.move(int(root.winfo_screenwidth() / 2 - (w + dw_legacy) / webdpr / 2), int(root.winfo_screenheight() / 2 - (h + dh_legacy) / webdpr / 2))

if render_range_more:
    root.run_js_code("render_range_more = true;")
    root.run_js_code(f"render_range_more_scale = {render_range_more_scale};")

root.run_js_code(f"lowquality_imjscvscale_x = {lowquality_imjscvscale_x};")
    
PHIGROS_X, PHIGROS_Y = 0.05625 * w, 0.6 * h
JUDGELINE_WIDTH = h * 0.0075
Resource = Load_Resource()
EFFECT_RANDOM_BLOCK_SIZE = Note_width / 5.5

updateCoreConfigure()

Thread(target=Show_Start, daemon=True).start()
root.wait_for_close()

for item in [item for item in listdir(gettempdir()) if item.startswith("qfppr_cctemp_")]:
    item = f"{gettempdir()}\\{item}"
    try:
        rmtree(item)
        logging.info(f"Remove Temp Dir: {item}")
    except Exception as e:
        logging.warning(e)

windll.kernel32.ExitProcess(0)