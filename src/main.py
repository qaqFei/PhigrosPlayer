import err_processer as _
import init_logging as _
import fix_workpath as _
import check_edgechromium as _

import json
import sys
import time
import logging
import typing
from threading import Thread
from ctypes import windll
from os import listdir, popen, mkdir, environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
from os.path import exists, isfile, isdir
from shutil import rmtree
from tempfile import gettempdir
from ntpath import basename

import cv2
import requests
from PIL import Image, ImageFilter, ImageEnhance
from pygame import mixer
from pydub import AudioSegment

import webcv
import playsound
import chartobj_phi
import chartobj_rpe
import chartfuncs_phi
import chartfuncs_rpe
import const
import console_window
import tool_funcs
import dialog
import info_loader
import ppr_help
import binfile
import shader
import file_loader
import phicore

if not exists("./7z.exe") or not exists("./7z.dll"):
    logging.fatal("7z.exe or 7z.dll Not Found")
    raise SystemExit

if len(sys.argv) == 1:
    HELP = ppr_help.HELP_EN if windll.kernel32.GetSystemDefaultUILanguage() != 0x804 else ppr_help.HELP_ZH
    print(HELP)
    raise SystemExit
    
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

try: mkdir(temp_dir)
except Exception as e: logging.warning(f"error when create temp dir: {e}")

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
noautoplay = "--noautoplay" in sys.argv
rtacc = "--rtacc" in sys.argv
lowquality = "--lowquality" in sys.argv
lowquality_scale = float(sys.argv[sys.argv.index("--lowquality-scale") + 1]) ** 0.5 if "--lowquality-scale" in sys.argv else 2.0 ** 0.5
showfps = "--showfps" in sys.argv
lfdaot_start_frame_num = int(eval(sys.argv[sys.argv.index("--lfdaot-start-frame-num") + 1])) if "--lfdaot-start-frame-num" in sys.argv else 0
lfdaot_run_frame_num = int(eval(sys.argv[sys.argv.index("--lfdaot-run-frame-num") + 1])) if "--lfdaot-run-frame-num" in sys.argv else float("inf")
speed = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else 1.0
clickeffect_randomblock_roundn = eval(sys.argv[sys.argv.index("--clickeffect-randomblock-roundn") + 1]) if "--clickeffect-randomblock-roundn" in sys.argv else 0.0
noplaychart = "--noplaychart" in sys.argv
clicksound_volume = float(sys.argv[sys.argv.index("--clicksound-volume") + 1]) if "--clicksound-volume" in sys.argv else 1.0
musicsound_volume = float(sys.argv[sys.argv.index("--musicsound-volume") + 1]) if "--musicsound-volume" in sys.argv else 1.0
lowquality_imjscvscale_x = float(sys.argv[sys.argv.index("--lowquality-imjscvscale-x") + 1]) if "--lowquality-imjscvscale-x" in sys.argv else 1.0
lowquality_imjs_maxsize = float(sys.argv[sys.argv.index("--lowquality-imjs-maxsize") + 1]) if "--lowquality-imjs-maxsize" in sys.argv else 256
enable_controls = "--enable-controls" in sys.argv
lfdaot_video_fourcc = sys.argv[sys.argv.index("--lfdaot-video-fourcc") + 1] if "--lfdaot-video-fourcc" in sys.argv else "mp4v"
record_play = "--record-play" in sys.argv
lfdaot_use_recordfile = sys.argv[sys.argv.index("--lfdaot-use-recordfile") + 1] if "--lfdaot-use-recordfile" in sys.argv else None
wl_more_chinese = "--wl-more-chinese" in sys.argv
skip_time = float(sys.argv[sys.argv.index("--skip-time") + 1]) if "--skip-time" in sys.argv else 0.0
enable_jscanvas_bitmap = "--enable-jscanvas-bitmap" in sys.argv
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

if record_play and not noautoplay:
    noautoplay = True
    logging.warning("if use --record-play, you must use --noautoplay")

if record_play and lfdaot:
    record_play = False
    logging.warning("if use --lfdaot, you cannot use --record-play")

if lfdaot_use_recordfile and not lfdaot:
    lfdaot_use_recordfile = None
    logging.warning("if use --lfdaot-use-recordfile, you must use --lfdaot")

if lfdaot_use_recordfile and lfdoat_file:
    lfdaot_use_recordfile = None
    logging.warning("if use --lfdoat-file, you cannot use --lfdaot-use-recordfile")

if lfdaot and skip_time != 0.0:
    skip_time = 0.0
    logging.warning("if use --lfdaot, you cannot use --skip-time")

if "--clickeffect-easing" in sys.argv:
    phicore.clickEffectEasingType = int(sys.argv[sys.argv.index("--clickeffect-easing") + 1])

combotips = ("RECORD" if lfdaot_use_recordfile is not None else (
    "AUTOPLAY" if not noautoplay else "COMBO"
)) if "--combotips" not in sys.argv else sys.argv[sys.argv.index("--combotips") + 1]

mixer.init()

if "--phira-chart" in sys.argv:
    logging.info("Downloading phira chart...")
    pctid = sys.argv[sys.argv.index("--phira-chart") + 1]
    apiresult = requests.get(f"https://api.phira.cn/chart/{pctid}").json()
    if "error" in apiresult:
        logging.error(f"phira api: {apiresult["error"]}")
        raise SystemExit
    
    sys.argv.insert(1, f"{temp_dir}/phira-temp-chart.zip" if "--phira-chart-save" not in sys.argv else sys.argv[sys.argv.index("--phira-chart-save") + 1])
    with open(sys.argv[1], "wb") as f:
        with requests.get(apiresult["file"], stream=True) as reqs:
            for content in reqs.iter_content(chunk_size=1024):
                f.write(content)
    logging.info("Downloaded phira chart.")

logging.info("Unpack Chart...")
popen(f".\\7z.exe x \"{sys.argv[1]}\" -o\"{temp_dir}\" -y >> nul").read()

logging.info("Loading All Files of Chart...")
files_dict = {
    "charts": [],
    "images": [],
    "audio": [],
}
chartimages = {}
cfrfp_procer: typing.Callable[[str], str] = lambda x: x.replace(f"{temp_dir}\\", "")

for item in tool_funcs.Get_All_Files(temp_dir):
    if item.endswith("info.txt") or item.endswith("info.csv") or item.endswith("info.yml") or item.endswith("extra.json"):
        continue
    
    item_rawname = cfrfp_procer(item)
    loadres = file_loader.loadfile(item)
    
    match loadres.filetype:
        case file_loader.FILE_TYPE.CHART:
            files_dict["charts"].append([item, loadres.data])
            
        case file_loader.FILE_TYPE.IMAGE:
            files_dict["images"].append([item, loadres.data])
            
        case file_loader.FILE_TYPE.SONG:
            files_dict["audio"].append(item)
        
        case file_loader.FILE_TYPE.UNKNOW:
            logging.warning(f"\nUnknow resource type. path = {item_rawname} errors: ")
            # for e in loadres.errs: logging.warning(f"\t{repr(e)}")
                    
if not files_dict["charts"]:
    logging.fatal("No Chart File Found")
    raise SystemExit

if not files_dict["audio"]:
    logging.fatal("No Audio File Found")
    raise SystemExit

if not files_dict["images"]:
    logging.warning("No Image File Found")
    files_dict["images"].append(["default", Image.new("RGB", (16, 9), "#0078d7")])

chart_fp: str
chart_json: dict
cimg_fp: str
chart_image: Image.Image
audio_fp: str

chart_index = file_loader.choosefile(
    fns = map(lambda x: x[0], files_dict["charts"]),
    prompt = "请选择谱面文件: ", rawprocer = cfrfp_procer
)
chart_fp, chart_json = files_dict["charts"][chart_index]

if "formatVersion" in chart_json:
    CHART_TYPE = const.CHART_TYPE.PHI
elif "META" in chart_json:
    CHART_TYPE = const.CHART_TYPE.RPE
else:
    logging.fatal("This is what format chart ???")
    raise SystemExit

def LoadChartObject(first: bool = False):
    global chart_obj
    
    if CHART_TYPE == const.CHART_TYPE.PHI:
        chart_obj = chartfuncs_phi.Load_Chart_Object(chart_json)
    elif CHART_TYPE == const.CHART_TYPE.RPE:
        chart_obj = chartfuncs_rpe.Load_Chart_Object(chart_json)
        
        chart_obj.META.RPEVersion = (
            sys.argv[sys.argv.index("--rpeversion") + 1]
            if "--rpeversion" in sys.argv
            else chart_obj.META.RPEVersion
        )
    
    if not first:
        updateCoreConfig()
        
LoadChartObject(True)

cimg_index = file_loader.choosefile(
    fns = map(lambda x: x[0], files_dict["images"]),
    prompt = "请选择背景图片: ", rawprocer = cfrfp_procer,
    default = chart_obj.META.background if CHART_TYPE == const.CHART_TYPE.RPE else None
)
cimg_fp, chart_image = files_dict["images"][cimg_index]
chart_image = chart_image.convert("RGB")

audio_index = file_loader.choosefile(
    fns = files_dict["audio"],
    prompt = "请选择音频文件: ", rawprocer = cfrfp_procer,
    default = chart_obj.META.song if CHART_TYPE == const.CHART_TYPE.RPE else None
)
audio_fp = files_dict["audio"][audio_index]

raw_audio_fp = audio_fp
if speed != 1.0:
    logging.info(f"Processing audio, rate = {speed}")
    seg: AudioSegment = AudioSegment.from_file(audio_fp)
    seg = seg._spawn(seg.raw_data, overrides = {
        "frame_rate": int(seg.frame_rate * speed)
    }).set_frame_rate(seg.frame_rate)
    audio_fp = f"{temp_dir}/ppr_temp_audio_{time.time()}.mp3"
    seg.export(audio_fp, format="mp3")

mixer.music.load(audio_fp)
raw_audio_length = mixer.Sound(audio_fp).get_length()
audio_length = raw_audio_length + (chart_obj.META.offset / 1000 if CHART_TYPE == const.CHART_TYPE.RPE else 0.0)
all_inforamtion = {}
logging.info("Loading Chart Information...")

ChartInfoLoader = info_loader.InfoLoader([f"{temp_dir}\\info.csv", f"{temp_dir}\\info.txt", f"{temp_dir}\\info.yml"])
chart_information = ChartInfoLoader.get(basename(chart_fp), basename(raw_audio_fp), basename(cimg_fp))

if CHART_TYPE == const.CHART_TYPE.RPE and chart_information is ChartInfoLoader.default_info:
    chart_information["Name"] = chart_obj.META.name
    chart_information["Artist"] = chart_obj.META.composer
    chart_information["Level"] = chart_obj.META.level
    chart_information["Charter"] = chart_obj.META.charter

logging.info("Loading Chart Information Successfully")
logging.info("Inforamtions: ")
for k,v in chart_information.items():
    logging.info(f"              {k}: {v}")

if exists(f"{temp_dir}\\extra.json"):
    try:
        logging.info("found extra.json, loading...")
        extra = chartfuncs_rpe.loadextra(json.load(open(f"{temp_dir}\\extra.json", "r", encoding="utf-8")), "--enable-shader" in sys.argv)
        logging.info("loading extra.json successfully")
    except SystemExit as e:
        logging.error("loading extra.json failed")
        
if "extra" not in globals():
    extra = chartfuncs_rpe.loadextra({}, False)

if extra.enable and not (lfdaot and lfdaot_render_video):
    logging.warning(f"if you want to enable shader, please render a video.")
    extra.enable = False
    
if extra.enable:
    logging.warning("extra effect item`s global value is also true, false value is not supported.")
    logging.warning("if you want to enable shader, you cannot use jit.")
    shader.hookMathFuncs()

logging.info(f"enable_shader: {extra.enable}")

def getResPath(path: str, file: bool = True):
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

def Load_Resource():
    global noteWidth
    global note_max_width, note_max_height
    global note_max_size_half
    global animation_image
    global WaitLoading, LoadSuccess
    global chart_res
    global ClickEffectFrameCount
    global cksmanager
    
    logging.info("Loading Resource...")
    WaitLoading = mixer.Sound(getResPath("/WaitLoading.mp3"))
    LoadSuccess = mixer.Sound(getResPath("/LoadSuccess.wav"))
    Thread(target=WaitLoading_FadeIn, daemon = True).start()
    LoadSuccess.set_volume(0.75)
    WaitLoading.play(-1)
    noteWidth_raw = (0.125 * w + 0.2 * h) / 2
    noteWidth = (noteWidth_raw) * (eval(sys.argv[sys.argv.index("--scale-note") + 1]) if "--scale-note" in sys.argv else 1.0)
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
            const.Note.TAP: playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Tap.wav"))),
            const.Note.DRAG: playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Drag.wav"))),
            const.Note.HOLD: playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Hold.wav"))),
            const.Note.FLICK: playsound.directSound(loadAudio(getResPath("/Note_Click_Audio/Flick.wav")))
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
    
    for k, v in Resource["Notes"].items():
        respacker.reg_img(Resource["Notes"][k], f"Note_{k}")
    
    for i in range(ClickEffectFrameCount): # reg click effect
        respacker.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
        respacker.reg_img(Resource["Note_Click_Effect"]["Good"][i], f"Note_Click_Effect_Good_{i + 1}")
        
    for k,v in Resource["Levels"].items(): # reg levels img
        respacker.reg_img(v, f"Level_{k}")
        
    respacker.reg_img(Resource["le_warn"], "le_warn")
    respacker.reg_img(chart_image, "begin_animation_image")
    respacker.reg_img(finish_animation_image, "finish_animation_image")
    respacker.reg_img(Resource["Button_Left"], "Button_Left")
    respacker.reg_img(Resource["Button_Right"], "Button_Right")
    respacker.reg_img(Resource["Retry"], "Retry")
    respacker.reg_img(Resource["Arrow_Right"], "Arrow_Right")
    respacker.reg_img(Resource["PauseImg"], "PauseImg")
    
    chart_res = {}
    
    if CHART_TYPE == const.CHART_TYPE.RPE:
        imfns: list[str] = list(map(lambda x: x[0], files_dict["images"]))
        imobjs: list[Image.Image] = list(map(lambda x: x[1], files_dict["images"]))
        
        for line in chart_obj.judgeLineList:
            if line.Texture != "line.png":
                paths = [
                    f"{temp_dir}\\{line.Texture}",
                    f"{temp_dir}\\{line.Texture}.png",
                    f"{temp_dir}\\{line.Texture}.jpg",
                    f"{temp_dir}\\{line.Texture}.jpeg"
                ]
                
                for p in paths:
                    if tool_funcs.fileinlist(p, imfns):
                        texture_index = tool_funcs.findfileinlist(p, imfns)
                        texture: Image.Image = imobjs[texture_index]
                        chart_res[line.Texture] = (texture.convert("RGBA"), texture.size)
                        logging.info(f"Loaded line texture {line.Texture}")
                        break
                else:
                    logging.warning(f"Cannot find texture {line.Texture}")
                    texture = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
                    chart_res[line.Texture] = (texture, texture.size)
                    
                respacker.reg_img(chart_res[line.Texture][0], f"lineTexture_{chart_obj.judgeLineList.index(line)}")
    
    with open(getResPath("/font.ttf"), "rb") as f:
        root.reg_res(f.read(),"PhigrosFont")
    respacker.load(*respacker.pack())
    
    root.wait_jspromise(f"loadFont('PhigrosFont',\"{root.get_resource_path("PhigrosFont")}\");")
    root.unreg_res("PhigrosFont")
    
    root.file_server.shutdown()
    note_max_width = noteWidth * const.NOTE_DUB_FIXSCALE
    note_max_height = max(
        [
            note_max_width / Resource["Notes"]["Tap"].width * Resource["Notes"]["Tap"].height,
            note_max_width / Resource["Notes"]["Tap_dub"].width * Resource["Notes"]["Tap_dub"].height,
            note_max_width / Resource["Notes"]["Drag"].width * Resource["Notes"]["Drag"].height,
            note_max_width / Resource["Notes"]["Drag_dub"].width * Resource["Notes"]["Drag_dub"].height,
            note_max_width / Resource["Notes"]["Flick"].width * Resource["Notes"]["Flick"].height,
            note_max_width / Resource["Notes"]["Flick_dub"].width * Resource["Notes"]["Flick_dub"].height,
            note_max_width / Resource["Notes"]["Hold_Head"].width * Resource["Notes"]["Hold_Head"].height,
            note_max_width / Resource["Notes"]["Hold_Head_dub"].width * Resource["Notes"]["Hold_Head_dub"].height,
            note_max_width / Resource["Notes"]["Hold_End"].width * Resource["Notes"]["Hold_End"].height
        ]
    )
    note_max_size_half = ((note_max_width ** 2 + note_max_height ** 2) ** 0.5) / 2
    
    # shaders = {
    #     "chromatic": open("./shaders/chromatic.glsl", "r", encoding="utf-8").read(),
    #     "circleBlur": open("./shaders/circle_blur.glsl", "r", encoding="utf-8").read(),
    #     "fisheye": open("./shaders/fisheye.glsl", "r", encoding="utf-8").read(),
    #     "glitch": open("./shaders/glitch.glsl", "r", encoding="utf-8").read(),
    #     "grayscale": open("./shaders/grayscale.glsl", "r", encoding="utf-8").read(),
    #     "noise": open("./shaders/noise.glsl", "r", encoding="utf-8").read(),
    #     "pixel": open("./shaders/pixel.glsl", "r", encoding="utf-8").read(),
    #     "radialBlur": open("./shaders/radial_blur.glsl", "r", encoding="utf-8").read(),
    #     "shockwave": open("./shaders/shockwave.glsl", "r", encoding="utf-8").read(),
    #     "vignette": open("./shaders/vignette.glsl", "r", encoding="utf-8").read()
    # }
    
    # how to load shaders to webgl and use them???
    ... # TODO
    
    if CHART_TYPE == const.CHART_TYPE.RPE:
        for line in chart_obj.judgeLineList:
            for note in line.notes:
                if note.hitsound_reskey not in Resource["Note_Click_Audio"]:
                    try:
                        Resource["Note_Click_Audio"][note.hitsound_reskey] = playsound.directSound(loadAudio(f"{temp_dir}\\{note.hitsound}"))
                        logging.info(f"Loaded note hitsound {note.hitsound}")
                    except Exception as e:
                        logging.warning(f"Cannot load note hitsound {note.hitsound} for note due to {e}")
    
    cksmanager = phicore.ClickSoundManager(Resource["Note_Click_Audio"])
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
        phicore.draw_background()
        phicore.draw_ui(animationing=True)
        p = (time.time() - animationst) / 1.0
        dle_warn((tool_funcs.fixorp(p) - 1.0) ** 4)
        root.run_js_wait_code()
    
    time.sleep(0.25)
    root.clear_canvas(wait_execute=True)
    phicore.draw_background()
    phicore.draw_ui(animationing=True)
    root.run_js_wait_code()
    Thread(target=PlayerStart, daemon=True).start()

def checkOffset(now_t: float):
    global show_start_time
    
    dt = tool_funcs.checkOffset(now_t, raw_audio_length, mixer)
    if dt != 0.0:
        show_start_time += dt
        updateCoreConfig()
                
def PlayerStart():
    global show_start_time, cksmanager
    
    Resource["Over"].stop()
    
    phicore.Begin_Animation()
    phicore.ChartStart_Animation()

    show_start_time = time.time() - skip_time
    PhiCoreConfigObject.show_start_time = show_start_time
    updateCoreConfig()
    now_t = 0
    
    if not lfdaot:
        mixer.music.play()
        mixer.music.set_pos(skip_time)
        while not mixer.music.get_busy(): pass
    
    if not lfdaot:
        if noautoplay:
            if CHART_TYPE == const.CHART_TYPE.PHI:
                pplm_proxy = chartobj_phi.PPLMPHI_Proxy(chart_obj)
            elif CHART_TYPE == const.CHART_TYPE.RPE:
                pplm_proxy = chartobj_rpe.PPLMRPE_Proxy(chart_obj)
            
            pppsm = tool_funcs.PhigrosPlayPlayStateManager(chart_obj.note_num)
            pplm = tool_funcs.PhigrosPlayLogicManager(
                pplm_proxy, pppsm,
                enable_clicksound, lambda nt: Resource["Note_Click_Audio"][nt].play(),
                record_play
            )
            
            root.jsapi.set_attr("PhigrosPlay_KeyDown", lambda t: pplm.pc_click((t - show_start_time) * speed))
            root.jsapi.set_attr("PhigrosPlay_KeyUp", lambda t: pplm.pc_release((t - show_start_time) * speed))
            root.run_js_code("_PhigrosPlay_KeyDown = PhigrosPlay_KeyEvent(() => {pywebview.api.call_attr('PhigrosPlay_KeyDown', new Date().getTime() / 1000)}, false);")
            root.run_js_code("_PhigrosPlay_KeyUp = PhigrosPlay_KeyEvent(() => {pywebview.api.call_attr('PhigrosPlay_KeyUp', new Date().getTime() / 1000)}, false);")
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
            checkOffset(now_t - skip_time)
            if CHART_TYPE == const.CHART_TYPE.PHI:
                Task = phicore.GetFrameRenderTask_Phi(now_t, pplm = pplm if noautoplay else None)
            elif CHART_TYPE == const.CHART_TYPE.RPE:
                Task = phicore.GetFrameRenderTask_Rpe(now_t, pplm = pplm if noautoplay else None)
                
            Task.ExecTask()
            
            break_flag = phicore.FrameData_ProcessExTask(Task.ExTask)
            
            if break_flag:
                break
            
            if play_restart_flag:
                break
        
        if noautoplay:
            root.run_js_code("window.removeEventListener('keydown', _PhigrosPlay_KeyDown);")
            root.run_js_code("window.removeEventListener('keyup', _PhigrosPlay_KeyUp);")
        
        root.run_js_code("window.removeEventListener('keydown', _Noautoplay_Restart);")
        root.run_js_code("window.removeEventListener('keydown', _SpaceClicked);")
        
        if record_play:
            record_fp = dialog.savefile(fn="record.bin")
            with open(record_fp, "wb") as f:
                f.write(pplm.recorder.writer.data)
        
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
            if lfdaot_use_recordfile is not None:
                with open(lfdaot_use_recordfile, "rb") as f:
                    recorder_data = list(binfile.readPlayRecorder(f.read()))
                
                if CHART_TYPE == const.CHART_TYPE.PHI:
                    pplm_proxy = chartobj_phi.PPLMPHI_Proxy(chart_obj)
                elif CHART_TYPE == const.CHART_TYPE.RPE:
                    pplm_proxy = chartobj_rpe.PPLMRPE_Proxy(chart_obj)
                
                pppsm = tool_funcs.PhigrosPlayPlayStateManager(chart_obj.note_num)
                pplm = tool_funcs.PhigrosPlayLogicManager(
                    pplm_proxy, pppsm,
                    enable_clicksound, lambda nt: Resource["Note_Click_Audio"][nt].play(),
                    record_play
                )
            else:
                pplm = None
            
            while True:
                if frame_count * frame_time > audio_length or frame_count - lfdaot_start_frame_num >= lfdaot_run_frame_num:
                    break
                
                now_t = frame_count * frame_time
                
                if pplm is not None:
                    for event in recorder_data.copy():
                        match event[0]:
                            case binfile.PlayRecorderBase.PLAY_CLICKSOUND:
                                continue # emm.?
                                if event[1] <= now_t:
                                    Resource["Note_Click_Audio"][event[2]].play()
                                    recorder_data.remove(event)
                            
                            case binfile.PlayRecorderBase.PC_CLICK:
                                if event[1] <= now_t:
                                    pplm.pc_click(event[1])
                                    recorder_data.remove(event)
                            
                            case binfile.PlayRecorderBase.PC_RELEASE:
                                if event[1] <= now_t:
                                    pplm.pc_release(event[1])
                                    recorder_data.remove(event)

                            case _:
                                logging.warning(f"Unknown event type: {event[0]}")
                
                if CHART_TYPE == const.CHART_TYPE.PHI:
                    lfdaot_tasks.update({frame_count: phicore.GetFrameRenderTask_Phi(now_t, pplm=pplm)})
                elif CHART_TYPE == const.CHART_TYPE.RPE:
                    lfdaot_tasks.update({frame_count: phicore.GetFrameRenderTask_Rpe(now_t, pplm=pplm)})
                
                frame_count += 1
                
                print(f"\rLoadFrameData: {frame_count} / {allframe_num}", end="")
            
            if "--lfdaot-file-savefp" in sys.argv:
                lfdaot_fp = sys.argv[sys.argv.index("--lfdaot-file-savefp") + 1]
            else:
                lfdaot_fp = dialog.savefile(fn="Chart.lfdaot")
            
            recorder = chartobj_phi.FrameTaskRecorder(
                meta = chartobj_phi.FrameTaskRecorder_Meta(
                    frame_speed = frame_speed,
                    frame_num = len(lfdaot_tasks),
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
            frame_speed = data["meta"]["frame_speed"]
            allframe_num = data["meta"]["frame_num"]
            Task_function_mapping = {
                func_name:getattr(root,func_name)
                for func_name in dir(root)
            }
            Task_function_mapping.update({
                "draw_background": phicore.draw_background,
                "draw_ui": phicore.draw_ui
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
                    break_flag = phicore.FrameData_ProcessExTask(ExTask)
                    
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
                frameCount = 0
                
                @tool_funcs.ThreadFunc
                def uploadFrame(dataUrl: str):
                    nonlocal frameCount
                    matlike = tool_funcs.DataUrl2MatLike(dataUrl)
                    
                    if extra.enable:
                        now_t = frameCount / frame_speed
                        shader.time = now_t
                        shader.screenSize = shader.vec2(w, h)
                        try:
                            matlike = shader.processFrame(matlike, extra.getValues(now_t))
                        except Exception as e:
                            logging.fatal(f"Shader error: {repr(e)}")
                            writer.release()
                            raise e from e
                        
                    writer.write(matlike)
                    frameCount += 1
                    
                root.jsapi.uploadFrame = uploadFrame
                
                for Task in lfdaot_tasks.values():
                    Task.ExecTask()
                    root.wait_jspromise("uploadFrame();")
                    
                    if root.run_js_code("lfdaot_render_video_stop;"):
                        break
                
                writer.release()
    
    mixer.music.set_volume(1.0)
    phicore.initFinishAnimation(pplm if noautoplay else None)
    
    def Chart_Finish_Animation():
        animation_1_time = 0.75
        a1_combo = pplm.ppps.getCombo() if noautoplay else None
        
        animation_1_start_time = time.time()
        while True:
            p = (time.time() - animation_1_start_time) / animation_1_time
            if p > 1.0: break
            phicore.Chart_BeforeFinish_Animation_Frame(p, a1_combo)
        
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
            phicore.Chart_Finish_Animation_Frame(p)
        
        while not a2_break:
            phicore.Chart_Finish_Animation_Frame(1.0)
    
    mixer.music.fadeout(250)
    Chart_Finish_Animation()

def updateCoreConfig():
    global PhiCoreConfigObject
    
    PhiCoreConfigObject = phicore.PhiCoreConfig(
        SETTER = lambda vn, vv: globals().update({vn: vv}),
        root = root, w = w, h = h,
        chart_information = chart_information,
        chart_obj = chart_obj, CHART_TYPE = CHART_TYPE,
        Resource = Resource,
        ClickEffectFrameCount = ClickEffectFrameCount,
        PHIGROS_X = PHIGROS_X, PHIGROS_Y = PHIGROS_Y,
        noteWidth = noteWidth, JUDGELINE_WIDTH = JUDGELINE_WIDTH,
        note_max_size_half = note_max_size_half, audio_length = audio_length,
        raw_audio_length = raw_audio_length, show_start_time = float("nan"),
        chart_res = chart_res, clickeffect_randomblock = clickeffect_randomblock,
        clickeffect_randomblock_roundn = clickeffect_randomblock_roundn,
        LoadSuccess = LoadSuccess, cksmanager = cksmanager,
        enable_clicksound = enable_clicksound, rtacc = rtacc,
        noautoplay = noautoplay, showfps = showfps, lfdaot = lfdaot,
        speed = speed, render_range_more = render_range_more,
        render_range_more_scale = render_range_more_scale,
        judgeline_notransparent = judgeline_notransparent,
        debug = debug, combotips = combotips, noplaychart = noplaychart,
        clicksound_volume = clicksound_volume,
        musicsound_volume = musicsound_volume,
        enable_controls = enable_controls
    )
    phicore.CoreConfigure(PhiCoreConfigObject)

logging.info("Loading Window...")
root = webcv.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "PhigrosPlayer - Simulator",
    debug = "--debug" in sys.argv,
    resizable = False,
    frameless = "--frameless" in sys.argv,
    renderdemand = "--renderdemand" in sys.argv,
    renderasync = "--renderasync" in sys.argv,
    jslog = "--enable-jslog" in sys.argv,
    jslog_path = sys.argv[sys.argv.index("--jslog-path")] if "--jslog-path" in sys.argv else "./ppr-jslog-nofmt.js"
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
        
    winw, winh = (
        w if w <= root.winfo_screenwidth() else int(root.winfo_screenwidth() * 0.75),
        h if h <= root.winfo_screenheight() else int(root.winfo_screenheight() * 0.75)
    )
    root.resize(winw, winh)
    w_legacy, h_legacy = root.winfo_legacywindowwidth(), root.winfo_legacywindowheight()
    dw_legacy, dh_legacy = winw - w_legacy, winh - h_legacy
    dw_legacy *= webdpr; dh_legacy *= webdpr
    dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
    del w_legacy, h_legacy
    root.resize(winw + dw_legacy, winh + dh_legacy)
    root.move(int(root.winfo_screenwidth() / 2 - (winw + dw_legacy) / webdpr / 2), int(root.winfo_screenheight() / 2 - (winh + dh_legacy) / webdpr / 2))

root.run_js_code(f"lowquality_imjscvscale_x = {lowquality_imjscvscale_x};")
root.run_js_code(f"lowquality_imjs_maxsize = {lowquality_imjs_maxsize};")
root.run_js_code(f"enable_jscanvas_bitmap = {enable_jscanvas_bitmap};")
root.run_js_code(f"RPEVersion = {chart_obj.META.RPEVersion if CHART_TYPE == const.CHART_TYPE.RPE else -1};")
root.run_js_code(f"resizeCanvas({w}, {h});")
    
PHIGROS_X, PHIGROS_Y = 0.05625 * w, 0.6 * h
JUDGELINE_WIDTH = h * 0.0075
Resource = Load_Resource()

if wl_more_chinese:
    root.run_js_code("setWlMoreChinese();")

updateCoreConfig()

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