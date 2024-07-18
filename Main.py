from threading import Thread
from ctypes import windll
from os import chdir,environ,listdir,popen,system,mkdir ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = str()
from os.path import exists,abspath,dirname
from sys import argv
from time import time,sleep
from shutil import rmtree
from tempfile import gettempdir
from ntpath import basename
from random import randint
import typing
import json
import base64
import importlib.util

from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from pygame import mixer
import cv2
import numpy
import webcvapis

import PlaySound # using at eval.
import Chart_Objects_Phi
import Chart_Functions_Phi
import Const
import Find_Files
import ConsoleWindow
import Tool_Functions
import dialog
import Phigros_Tips
import default_extend
import Image_open
import info_loader
import version
import ppr_help

if len(argv) == 1:
    print(ppr_help.HELP_EN)
    windll.kernel32.ExitProcess(0)
    
version.print_hello()
Thread(target=version.check_new_version, daemon=True).start()

if "--hideconsole" in argv:
    ConsoleWindow.Hide()

hidemouse = "--hidemouse" in argv

selfdir = dirname(argv[0])
if selfdir == "": selfdir = abspath(".")
chdir(selfdir)

Kill_PlayThread_Flag = False

if not exists("./7z.exe") or not exists("./7z.dll"):
    print("7z.exe or 7z.dll Not Found.")
    windll.kernel32.ExitProcess(1)

if not (exists("./rpe2phi.py") or exists("./rpe2phi.exe")):
    print("rpe2phi.py or rpe2phi.exe Not Found.")
    windll.kernel32.ExitProcess(1)
rpe2phi_prgm = ".\\rpe2phi.exe" if exists("./rpe2phi.exe") else ".\\rpe2phi.py"

if not (exists("./Main.py") or exists("./Main.exe")):
    print("Please change this file name to Main.py or Main.exe.")
    windll.kernel32.ExitProcess(1)
self_fp = "./Main.exe" if exists("./Main.exe") else "./Main.py"

temp_dir = f"{gettempdir()}\\phigros_chart_temp_{time()}"
for item in [item for item in listdir(gettempdir()) if item.startswith("phigros_chart_temp_")]:
    item = f"{gettempdir()}\\{item}"
    try:
        rmtree(item)
        print(f"Remove Temp Dir: {item}")
    except Exception as e:
        print(f"Warning: {e}")
print(f"Temp Dir: {temp_dir}")

Image.open = Image_open.open

enable_clicksound = "--noclicksound" not in argv
debug = "--debug" in argv
show_holdbody = "--holdbody" in argv
show_judgeline = "--nojudgeline" not in argv
debug_noshow_transparent_judgeline = "--debug-noshow-transparent-judgeline" in argv
judgeline_notransparent = "--judgeline-notransparent" in argv
clickeffect_randomblock = "--noclickeffect-randomblock" not in argv
loop = "--loop" in argv
lfdaot = "--lfdaot" in argv
lfdoat_file = "--lfdaot-file" in argv
render_range_more = "--render-range-more" in argv
render_range_more_scale = 2.0 if "--render-range-more-scale" not in argv else eval(argv[argv.index("--render-range-more-scale")+1])
lfdaot_render_video = "--lfdaot-render-video" in argv
extend_file = argv[argv.index("--extend") + 1] if "--extend" in argv else "./default_extend.py"
no_mixer_reset_chart_time = "--no-mixer-reset-chart-time" in argv
noautoplay = "--noautoplay" in argv
rtacc = "--rtacc" in argv

if lfdaot and noautoplay:
    noautoplay = False
    print("Warning: if use --lfdaot, you cannot use --noautoplay.")

extend_file_spec = importlib.util.spec_from_file_location("extend", extend_file)
extend = importlib.util.module_from_spec(extend_file_spec)
extend_file_spec.loader.exec_module(extend)
extend_object:default_extend.PhigrosPlayer_Extend = extend.PhigrosPlayer_Extend(
    lambda *args, **kwargs: globals(*args, **kwargs)
)

if len(argv) < 2 or not exists(argv[1]):
    argv = [argv[0]] + [dialog.openfile()] + argv[0:]
    if argv[1] == "":
        windll.kernel32.ExitProcess(1)

print("Init Pygame Mixer...")
mixer.init()
mixer.music.set_volume(0.85)

print("Unpack Chart...")
popen(f".\\7z.exe e \"{argv[1]}\" -o\"{temp_dir}\" >> nul").read()

print("Loading All Files of Chart...")
chart_files = Find_Files.Get_All_Files(temp_dir)
chart_files_dict = {
    "charts": [],
    "images": [],
    "audio": [],
}
for item in chart_files:
    try:
        chart_files_dict["images"].append([item,Image.open(item).convert("RGB")])
        print(f"Add Resource (image): {item.replace(f"{temp_dir}\\", "")}")
    except Exception:
        try:
            mixer.music.load(item)
            chart_files_dict["audio"].append(item)
            print(f"Add Resource (audio): {item.replace(f"{temp_dir}\\", "")}")
        except Exception:
            try:
                with open(item, "r", encoding="utf-8") as f:
                    chart_files_dict["charts"].append([item, json.load(f)])
                    print(f"Add Resource (chart): {item.replace(f"{temp_dir}\\", "")}")
            except Exception:
                name = item.replace(f"{temp_dir}\\", "")
                if name not in ["info.csv"]:
                    print(f"Warning: Unknown Resource Type. Path = {name}")
                    
if len(chart_files_dict["charts"]) == 0:
    print("No Chart File Found.")
    windll.kernel32.ExitProcess(1)
if len(chart_files_dict["audio"]) == 0:
    print("No Audio File Found.")
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
    phigros_chart = chart_files_dict["charts"][phigros_chart_index][1]
else:
    phigros_chart = chart_files_dict["charts"][phigros_chart_index][1]
phigros_chart_filepath = chart_files_dict["charts"][phigros_chart_index][0]

if len(chart_files_dict["images"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["images"]):
        name = chart_file[0].split("/")[-1].split("\\")[-1]
        print(f"{index + 1}. {name}")
    chart_image_index = int(input("请选择谱面图片: ")) - 1
    chart_image:Image.Image = chart_files_dict["images"][chart_image_index][1]
else:
    chart_image:Image.Image = chart_files_dict["images"][chart_image_index][1]
chart_image_filepath = chart_files_dict["images"][chart_image_index][0]

if len(chart_files_dict["audio"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["audio"]):
        name = chart_file.split("/")[-1].split("\\")[-1]
        print(f"{index + 1}. {name}")
    audio_file_index = int(input("请选择音频文件: ")) - 1
    audio_file = chart_files_dict["audio"][audio_file_index]
else:
    audio_file = chart_files_dict["audio"][audio_file_index]
    
mixer.music.load(audio_file)
audio_length = mixer.Sound(audio_file).get_length()
all_inforamtion = {}
print("Loading Chart Information...")

ChartInfoLoader = info_loader.InfoLoader([f"{temp_dir}\\info.csv", f"{temp_dir}\\info.txt", f"{temp_dir}\\info.yml"])
chart_information = ChartInfoLoader.get(basename(phigros_chart_filepath), basename(audio_file), basename(chart_image_filepath))

if "formatVersion" in phigros_chart:
    CHART_TYPE = Const.CHART_TYPE.PHI
elif "META" in phigros_chart:
    CHART_TYPE = Const.CHART_TYPE.REP
else:
    print("This is what format chart???")
    windll.kernel32.ExitProcess(1)
    
print("Loading Chart Information Successfully.")
print("Inforamtions: ")
for k,v in chart_information.items():
    print(f"              {k}: {v}")

del chart_files,chart_files_dict

clickeffect_cache = []
note_id = -1
def LoadChartObject():
    global phigros_chart_obj
    if CHART_TYPE == Const.CHART_TYPE.PHI:
        phigros_chart_obj = Chart_Functions_Phi.Load_Chart_Object(phigros_chart)
    elif CHART_TYPE == Const.CHART_TYPE.REP:
        temp_rpe_fdir = f"{gettempdir()}/qfppr_cctemp_{time() + randint(0, 2 << 31)}"
        try: mkdir(temp_rpe_fdir)
        except Exception: pass
        temp_rpe_fp = f"{temp_rpe_fdir}\\{basename(phigros_chart_filepath)}"
        temp_7z_fp = f"{temp_rpe_fdir}\\{basename(phigros_chart_filepath)}.7z"
        info_fp = f"{temp_dir}\\info.txt" if exists(f"{temp_dir}\\info.txt") else f"{temp_dir}\\info.csv" if exists(f"{temp_dir}\\info.csv") else f"{temp_dir}\\info.yml" if exists(f"{temp_dir}\\info.yml") else None
        print("running rpe2phi...")
        popen(f"{rpe2phi_prgm} {phigros_chart_filepath} {temp_rpe_fp}{f" --extra \"{temp_dir}\\extra.json\"" if exists(f"{temp_dir}\\extra.json") else ""}").read() # if call read function, we will wait still the program finish.
        popen(
            f"\
                .\\7z.exe a -t7z \"{temp_7z_fp}\"\
                \"{temp_rpe_fp}\" \"{chart_image_filepath}\" \"{audio_file}\"\
            " + f" \"{info_fp}\"" if info_fp is not None else "" + " -mmt"
        ).read()
        print("rpe2phi finished, restart...")
        system(f"start {self_fp} {temp_7z_fp} " + " ".join(map(lambda x: f"\"{x}\"", argv[2:]))) # restart!
        windll.kernel32.ExitProcess(0)
LoadChartObject()
extend_object.chart_loaded(phigros_chart_obj)

def Load_Resource():
    global ClickEffect_Size, Note_width
    global note_max_width, note_max_height
    global note_max_width_half, note_max_height_half
    global animation_image
    global WaitLoading,LoadSuccess
    
    print("Loading Resource...")
    WaitLoading = mixer.Sound("./Resources/WaitLoading.mp3")
    LoadSuccess = mixer.Sound("./Resources/LoadSuccess.wav")
    Thread(target=WaitLoading_FadeIn, daemon = True).start()
    LoadSuccess.set_volume(0.75)
    WaitLoading.play(-1)
    Note_width_raw = (0.125 * w + 0.2 * h) / 2
    Note_width = (Note_width_raw) * (eval(argv[argv.index("--scale-note") + 1]) if "--scale-note" in argv else 1.0)
    ClickEffect_Size = Note_width * 1.375
    Resource = {
        "Notes":{
            "Tap": Image.open("./Resources/Notes/Tap.png"),
            "Tap_dub": Image.open("./Resources/Notes/Tap_dub.png"),
            "Drag": Image.open("./Resources/Notes/Drag.png"),
            "Drag_dub": Image.open("./Resources/Notes/Drag_dub.png"),
            "Flick": Image.open("./Resources/Notes/Flick.png"),
            "Flick_dub": Image.open("./Resources/Notes/Flick_dub.png"),
            "Hold_Head": Image.open("./Resources/Notes/Hold_Head.png"),
            "Hold_Head_dub": Image.open("./Resources/Notes/Hold_Head_dub.png"),
            "Hold_End": Image.open("./Resources/Notes/Hold_End.png"),
            "Hold_End_dub": Image.open("./Resources/Notes/Hold_End_dub.png"),
            "Hold_Body": Image.open("./Resources/Notes/Hold_Body.png"),
            "Hold_Body_dub": Image.open("./Resources/Notes/Hold_Body_dub.png"),
            "Tap_Bad": Image.open("./Resources/Notes/Tap_Bad.png")
        },
        "Note_Click_Effect":{
            "Perfect":[
                Image.open(f"./Resources/Note_Click_Effect/Perfect/{i + 1}.png")
                for i in range(30)
            ],
            "Good":[
                Image.open(f"./Resources/Note_Click_Effect/Good/{i + 1}.png")
                for i in range(30)
            ]
        },
        "Levels":{
            "AP": Image.open("./Resources/Levels/AP.png"),
            "FC": Image.open("./Resources/Levels/FC.png"),
            "V": Image.open("./Resources/Levels/V.png"),
            "S": Image.open("./Resources/Levels/S.png"),
            "A": Image.open("./Resources/Levels/A.png"),
            "B": Image.open("./Resources/Levels/B.png"),
            "C": Image.open("./Resources/Levels/C.png"),
            "F": Image.open("./Resources/Levels/F.png")
        },
        "Note_Click_Audio":{
            "Tap": open("./Resources/Note_Click_Audio/Tap.wav", "rb").read(),
            "Drag": open("./Resources/Note_Click_Audio/Drag.wav", "rb").read(),
            "Hold": open("./Resources/Note_Click_Audio/Hold.wav", "rb").read(),
            "Flick": open("./Resources/Note_Click_Audio/Flick.wav", "rb").read()
        },
        "Start": Image.open("./Resources/Start.png"),
        "Button_Left": Image.open("./Resources/Button_Left.png"),
        "Button_Right": None,
        "Retry": Image.open("./Resources/Retry.png"),
        "Arrow_Right": Image.open("./Resources/Arrow_Right.png"),
        "Over": mixer.Sound("./Resources/Over.wav")
    }
    
    Resource["Button_Right"] = Resource["Button_Left"].transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    
    animation_image = chart_image.copy()
    animation_image = animation_image.convert("RGBA")
    animation_image_imdraw = ImageDraw.Draw(animation_image)
    animation_image_imdraw.polygon(
        [
            (0,0),
            (0,animation_image.height),
            (animation_image.width * 0.1,0),
            (0,0)
        ],
        fill = "#00000000"
    )
    animation_image_imdraw.polygon(
        [
            (animation_image.width,0),
            (animation_image.width,animation_image.height),
            (animation_image.width * (1 - 0.1),animation_image.height),
            (animation_image.width,0)
        ],
        fill = "#00000000"
    )
    
    for k,v in Resource["Notes"].items(): # Resize Notes (if Notes is too big) and reg them
        if v.width > Note_width:
            Resource["Notes"][k] = v.resize((int(Note_width),int(Note_width / v.width * v.height)))
        root.reg_img(Resource["Notes"][k], f"Note_{k}")
    
    for i in range(30): # reg click effect
        root.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
        root.reg_img(Resource["Note_Click_Effect"]["Good"][i], f"Note_Click_Effect_Good_{i + 1}")
        
    for k,v in Resource["Levels"].items(): # reg levels img
        root.reg_img(v, f"Level_{k}")
        
    root.reg_img(Resource["Start"],"Start")
    root.reg_img(animation_image,"begin_animation_image")
    root.reg_img(Resource["Button_Left"],"Button_Left")
    root.reg_img(Resource["Button_Right"],"Button_Right")
    root.reg_img(Resource["Retry"],"Retry")
    root.reg_img(Resource["Arrow_Right"],"Arrow_Right")
    
    with open("./Resources/font.ttf","rb") as f:
        root.reg_res(f.read(),"PhigrosFont")
    root.load_allimg()
    root.run_js_code("color_block_img_ele = Start_img; body_ele.appendChild(color_block_img_ele);")
    root.run_js_code(f"loadFont('PhigrosFont',\"{root.get_resource_path("PhigrosFont")}\");")
    while not root.run_js_code("font_loaded;"):
        sleep(0.1)
    
    root.shutdown_fileserver()
    print("Loading Resource Successfully.")
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
    note_max_width_half = note_max_width / 2
    note_max_height_half = note_max_height / 2
    return Resource

def Format_Time(t:typing.Union[int,float]) -> str:
    if t < 0.0: t = 0.0
    m,s = t // 60,t % 60
    m,s = int(m), int(s)
    return f"{m}:{s:>2}".replace(" ", "0")

def WaitLoading_FadeIn():
    for i in range(50):
        WaitLoading.set_volume((i + 1) / 100)
        sleep(2 / 50)

def Show_Start():
    WaitLoading.fadeout(450)
    root.run_js_code("show_in_animation();")
    sleep(1.25)
    draw_background()
    draw_ui(animationing = True)
    root.run_js_wait_code()
    sleep(0.5)
    root.run_js_code("show_out_animation();")
    sleep(1.25)
    Thread(target = PlayerStart_Phi,daemon = True).start()

def draw_ui(
    process:float = 0.0,
    score:str = "0000000",
    combo_state:bool = False,
    combo:int = 0,
    now_time:str = "0:00/0:00",
    acc:str = "100.00%",
    clear:bool = True,
    background:bool = True,
    animationing:bool = False,
    dy:float = 0.0
):
    if clear:
        root.clear_canvas(wait_execute = True)
    if background:
        draw_background()
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,{- h / 7 + dy});",add_code_array=True)
    
    root.create_rectangle(
        0, 0,
        w * process, h / 125,
        fillStyle = "rgba(145, 145, 145, 0.85)",
        wait_execute = True
    )
    
    root.create_rectangle(
        w * process - w * 0.002, 0,
        w * process, h / 125,
        fillStyle = "rgba(255, 255, 255, 0.9)",
        wait_execute = True
    )
    
    root.create_text(
        text = score,
        x = w * 0.988,
        y = h * 0.045,
        textAlign = "right",
        textBaseline = "middle",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{((w + h) / 75 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    if rtacc:
        root.create_text(
            text = acc,
            x = w * 0.988,
            y = h * 0.08,
            textAlign = "right",
            textBaseline = "middle",
            strokeStyle = "white",
            fillStyle = "white",
            font = f"{((w + h) / 145 / 0.75)}px PhigrosFont",
            wait_execute = True
        )
    
    if combo_state:
        root.create_text(
            text = f"{combo}",
            x = w / 2,
            y = h * 0.05,
            textAlign = "center",
            textBaseline = "middle",
            strokeStyle = "white",
            fillStyle = "white",
            font = f"{((w + h) / 75 / 0.75)}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            text=("Autoplay" if not noautoplay else "Combo") if "--combotips" not in argv else argv[argv.index("--combotips") + 1],
            x = w / 2,
            y = h * 0.095,
            textAlign = "center",
            textBaseline = "middle",
            strokeStyle = "white",
            fillStyle = "white",
            font = f"{((w + h) / 100 / 0.75)}px PhigrosFont",
            wait_execute = True
        )
        
    root.create_text(
        text = now_time,
        x = 0,
        y = h * 0.01,
        textAlign = "left",
        textBaseline = "top",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{((w + h) / 175 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,-2 * {- h / 7 + dy});",add_code_array=True)
    
    root.create_text(
        text = chart_information["Name"],
        x = w * 0.0125,
        y = h * 0.976,
        textAlign = "left",
        textBaseline = "bottom",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{((w + h) / 125 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        text = chart_information["Level"],
        x = w * 0.9875,
        y = h * 0.976,
        textAlign = "right",
        textBaseline = "bottom",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{((w + h) / 125 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        text = "PhigrosPlayer - by qaqFei - github.com/qaqFei/PhigrosPlayer - MIT License",
        x = w * 0.9875,
        y = h * 0.995,
        textAlign = "right",
        textBaseline = "bottom",
        strokeStyle = "rgba(255, 255, 255, 0.5)",
        fillStyle = "rgba(255, 255, 255, 0.5)",
        font = f"{((w + h) / 275 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,{- h / 7 + dy});",add_code_array=True)

def draw_background():
    root.create_image(
        "background",
        0, 0,
        w, h, 
        wait_execute = True
    )

def Note_CanRender(
    x:float,y:float,
    hold_points:typing.Union[typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ], None] = None
) -> bool:
    if hold_points is None: # type != HOLD
        if (
            (0 < x < w and 0 < y < h) or
            (0 < x - note_max_width_half < w and 0 < y - note_max_height_half < h) or 
            (0 < x - note_max_width_half < w and 0 < y + note_max_height_half < h) or
            (0 < x + note_max_width_half < w and 0 < y - note_max_height_half < h) or
            (0 < x + note_max_width_half < w and 0 < y + note_max_height_half < h)
        ):
            return True
        return False
    else:
        if any((point_in_screen(point) for point in hold_points)):
            return True
        return any(batch_is_intersect(
            [
                (hold_points[0], hold_points[1]),
                (hold_points[1], hold_points[2]),
                (hold_points[2], hold_points[3]),
                (hold_points[3], hold_points[0])
            ],
            [
                ((0, 0), (w, 0)), ((0, 0), (0, h)),
                ((w, 0), (w, h)), ((0, h), (w, h))
            ]
        ))

def batch_is_intersect(
    lines_group_1:typing.List[typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ]],
    lines_group_2:typing.List[typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ]]
) -> typing.Generator[bool,None,None]:
    for i in lines_group_1:
        for j in lines_group_2:
            yield is_intersect(i,j)

def is_intersect(
    line_1:typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ],
    line_2:typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ]
) -> bool:
    if (
        max(line_1[0][0],line_1[1][0]) < min(line_2[0][0],line_2[1][0]) or
        max(line_2[0][0],line_2[1][0]) < min(line_1[0][0],line_1[1][0]) or
        max(line_1[0][1],line_1[1][1]) < min(line_2[0][1],line_2[1][1]) or
        max(line_2[0][1],line_2[1][1]) < min(line_1[0][1],line_1[1][1])
    ):
        return False
    else:
        return True

def judgeLine_can_render(
    judgeLine_DrawPos:typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ]
) -> bool:
    return any(batch_is_intersect([[[judgeLine_DrawPos[0],judgeLine_DrawPos[1]],[judgeLine_DrawPos[2],judgeLine_DrawPos[3]]]],[[(0,0),(w,0)],[(0,0),(0,h)],[(w,0),(w,h)],[(0,h),(w,h)]]))

def point_in_screen(point:typing.Tuple[float,float]) -> bool:
    return 0 < point[0] < w and 0 < point[1] < h

def get_stringscore(score:float) -> str:
    score_integer = int(score + 0.5)
    return f"{score_integer:>7}".replace(" ","0")

class PhigrosPlayManager:
    def __init__(self, noteCount:int):
        self.events: list[typing.Literal["P", "G", "B", "M"]] = []
        self.event_offsets: list[float] = [] # the note click offset (s)
        self.noteCount: int = noteCount
    
    def addEvent(self, event:typing.Literal["P", "G", "B", "M"], offset:float|None = None): # Perfect, Good, Bad, Miss
        self.events.append(event)
        if offset is not None: # offset is only good judge.
            self.event_offsets.append(offset)
    
    def getJudgelineColor(self) -> tuple[int]:
        if "B" in self.events or "M" in self.events:
            return (255, 255, 255) # White
        if "G" in self.events:
            return (162, 238, 255) # FC
        return (254, 255, 169) # AP

    def getCombo(self) -> int:
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                return cut
        return cut
    
    def getAcc(self) -> float: # 实时 Acc
        if not self.events: return 1.0
        acc = 0.0
        allcut = len(self.events)
        for e in self.events:
            if e == "P":
                acc += 1.0 / allcut
            elif e == "G":
                acc += 0.65 / allcut
        return acc
    
    def getAccOfAll(self) -> float:
        acc = 0.0
        for e in self.events:
            if e == "P":
                acc += 1.0 / self.noteCount
            elif e == "G":
                acc += 0.65 / self.noteCount
        return acc
    
    def getMaxCombo(self) -> int:
        r = 0
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                r = max(r, cut)
                cut = 0
        return max(r, cut)
    
    def getScore(self) -> float:
        return self.getAccOfAll() * 900000 + self.getMaxCombo() / self.noteCount * 100000
    
    def getPerfectCount(self) -> int:
        return self.events.count("P")
    
    def getGoodCount(self) -> int:
        return self.events.count("G")
    
    def getBadCount(self) -> int:
        return self.events.count("B")
    
    def getMissCount(self) -> int:
        return self.events.count("M")
    
    def getEarlyCount(self) -> int:
        return len(list(filter(lambda x: x > 0, self.event_offsets)))
    
    def getLateCount(self) -> int:
        return len(list(filter(lambda x: x < 0, self.event_offsets)))
    
    def getLevelString(self) -> typing.Literal["AP", "FC", "V", "S", "A", "B", "C", "F"]:
        score = self.getScore()
        if self.getPerfectCount() == self.noteCount: return "AP"
        elif self.getBadCount() == 0 and self.getMissCount() == 0: return "FC"
        
        if 0 <= score < 700000:
            return "F"
        elif 700000 <= score < 820000:
            return "C"
        elif 820000 <= score < 880000:
            return "B"
        elif 880000 <= score < 920000:
            return "A"
        elif 920000 <= score < 960000:
            return "S"
        elif 960000 <= score < 1000000:
            return "V"
        elif 1000000 <= score:
            return "AP"

def PlayChart_ThreadFunction():
    global PhigrosPlayManagerObject, Kill_PlayThread_Flag, PlayChart_NowTime
    PlayChart_NowTime = - float("inf")
    PhigrosPlayManagerObject = PhigrosPlayManager(phigros_chart_obj.note_num)
    KeyDownCount = 0
    keymap = {chr(i):False for i in range(97, 123)}
    notes = [i for line in phigros_chart_obj.judgeLineList for i in line.notesAbove + line.notesBelow if not i.fake]
    
    def _KeyDown(key:str):
        nonlocal KeyDownCount
        key = key.lower()
        if len(key) != 1: return
        if not (97 <= ord(key) <= 122): return
        if keymap[key]: return
        keymap[key] = True
        KeyDownCount += 1
        
        can_judge_notes = [(i, offset) for i in notes if (
            not i.player_clicked and
            i.type in (Const.Note.TAP, Const.Note.HOLD) and
            abs((offset := (i.time * i.master.T - PlayChart_NowTime))) <= (0.2 if i.type == Const.Note.TAP else 0.16)
        )]
        can_use_safedrag = [(i, offset) for i in notes if (
            i.type == Const.Note.DRAG and
            not i.player_drag_judge_safe_used and
            abs((offset := (i.time * i.master.T - PlayChart_NowTime))) <= 0.16
        )]
        
        can_judge_notes.sort(key = lambda x: abs(x[1]))
        can_use_safedrag.sort(key = lambda x: abs(x[1]))
        
        if can_judge_notes:
            n, offset = can_judge_notes[0]
            abs_offset = abs(offset)
            if 0.0 <= abs_offset <= 0.08:
                n.state = Const.NOTE_STATE.PERFECT
                if n.type == Const.Note.HOLD:
                    n.player_holdjudged = True
                    n.player_holdclickstate = n.state
                else: # TAP
                    PhigrosPlayManagerObject.addEvent("P")
            elif 0.08 < abs_offset <= 0.16:
                n.state = Const.NOTE_STATE.GOOD
                if n.type == Const.Note.HOLD:
                    n.player_holdjudged = True
                    n.player_holdclickstate = n.state
                else: # TAP
                    PhigrosPlayManagerObject.addEvent("G", offset)
            elif 0.16 < abs_offset <= 0.2: # only tap
                if can_use_safedrag: # not empty
                    drag, drag_offset = can_use_safedrag[0]
                    if not drag.player_will_click:
                        drag.player_will_click = True
                        drag.player_click_offset = drag_offset
                    drag.player_drag_judge_safe_used = True
                    return None
                
                n.player_badtime = PlayChart_NowTime
                n.state = Const.NOTE_STATE.BAD
                PhigrosPlayManagerObject.addEvent("B")
                
            if n.state != Const.NOTE_STATE.MISS:
                n.player_click_offset = offset
                n.player_clicked = True
    
    def _KeyUp(key:str):
        nonlocal KeyDownCount
        key = key.lower()
        if len(key) != 1: return
        if not (97 <= ord(key) <= 122): return
        if KeyDownCount > 0: KeyDownCount -= 1
        keymap[key] = False
    
    root.jsapi.set_attr("PhigrosPlay_KeyDown", _KeyDown)
    root.jsapi.set_attr("PhigrosPlay_KeyUp", _KeyUp)
    root.run_js_code("_PhigrosPlay_KeyDown = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyDown', e.key);});")
    root.run_js_code("_PhigrosPlay_KeyUp = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyUp', e.key);});")
    root.run_js_code("window.addEventListener('keydown', _PhigrosPlay_KeyDown);")
    root.run_js_code("window.addEventListener('keyup', _PhigrosPlay_KeyUp);")
    
    while True:
        keydown = KeyDownCount > 0
        
        for note in notes:
            note_time_sec = note.time * note.master.T
            
            if ( # (Drag / Flick) judge
                keydown and
                not note.player_clicked and
                note.type in (Const.Note.FLICK, Const.Note.DRAG) and
                abs((cktime := note_time_sec - PlayChart_NowTime)) <= 0.16 # +- 160ms
            ):
                note.player_will_click = True
                
                if cktime <= 0.0: #late
                    note.player_click_offset = cktime
            
            if ( # if Drag / Flick it`s time to click and judged, click it and update it.
                note.player_will_click and 
                not note.player_clicked and 
                note_time_sec <= PlayChart_NowTime
            ):
                note.player_clicked = True
                note.state = Const.NOTE_STATE.PERFECT
                PhigrosPlayManagerObject.addEvent("P")
            
            if ( # play click sound
                note.player_clicked and
                not note.player_click_sound_played and
                note.state in (Const.NOTE_STATE.PERFECT, Const.NOTE_STATE.GOOD)
            ):
                Thread(target=PlaySound.Play, args=(Resource["Note_Click_Audio"][note.type_string],)).start()
                note.player_click_sound_played = True
            
            if ( # miss judge
                not note.player_clicked and
                not note.player_missed and
                note_time_sec - PlayChart_NowTime < - 0.2
            ):
                note.player_missed = True
                PhigrosPlayManagerObject.addEvent("M")
            
            if ( # hold hold judge
                note.type == Const.Note.HOLD and 
                note.player_clicked and
                note.state != Const.NOTE_STATE.MISS and
                note.hold_endtime - 0.2 >= PlayChart_NowTime
            ):
                if note.player_last_testholdismiss_time + 0.16 <= time():
                    if keydown:
                        note.player_last_testholdismiss_time = time()
                    else:
                        note.player_holdmiss_time = PlayChart_NowTime
                        note.state = Const.NOTE_STATE.MISS
                        note.player_missed = True
                        PhigrosPlayManagerObject.addEvent("M")
            
            if ( # hold end add event to manager judge
                note.type == Const.Note.HOLD and
                note.player_holdjudged and # if judged is true, hold state is perfect/good/ miss(miss at clicking)
                not note.player_holdjudged_tomanager and
                note.player_holdjudge_tomanager_time <= PlayChart_NowTime
            ):
                note.player_holdjudged_tomanager = True
                if note.state == Const.NOTE_STATE.PERFECT: PhigrosPlayManagerObject.addEvent("P")
                elif note.state == Const.NOTE_STATE.GOOD: PhigrosPlayManagerObject.addEvent("G", note.player_click_offset)
                else: pass # note state is miss at clicking
            
        if Kill_PlayThread_Flag:
            root.run_js_code("window.removeEventListener('keydown', _PhigrosPlay_KeyDown);")
            root.run_js_code("window.removeEventListener('keyup', _PhigrosPlay_KeyUp);")
            root.run_js_code("delete _PhigrosPlay_KeyDown; delete _PhigrosPlay_KeyUp;")
            delattr(root.jsapi, "PhigrosPlay_KeyDown")
            delattr(root.jsapi, "PhigrosPlay_KeyUp")
            Kill_PlayThread_Flag = False
            return
        sleep(1 / 480)

def GetFrameRenderTask_Phi(
    now_t:float,
    judgeLine_Configs:Chart_Objects_Phi.judgeLine_Configs,
    show_start_time:float
):
    global PlayChart_NowTime; PlayChart_NowTime = now_t
    
    GetFrameRenderTask_Phi_CallTime = time() # use in some extend
    Render_JudgeLine_Count = 0
    Render_Note_Count = 0
    Render_ClickEffect_Count = 0
    
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    Chart_Functions_Phi.Update_JudgeLine_Configs(judgeLine_Configs, now_t)
    Task(root.clear_canvas, wait_execute = True)
    Task(draw_background)
    
    if render_range_more:
        fr_x = w / 2 - w / render_range_more_scale / 2
        fr_y = h / 2 - h / render_range_more_scale / 2
    
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.translate({fr_x},{fr_y});",
            add_code_array = True
        )
    
    extra_render_task = phigros_chart_obj.get_datavar_extra(now_t) if phigros_chart_obj.Extra_Enable else []
    
    for judgeLine_cfg in judgeLine_Configs.Configs:
        judgeLine:Chart_Objects_Phi.judgeLine = judgeLine_cfg.line
        this_judgeLine_T = judgeLine.T
        judgeLine_note_dy = Chart_Objects_Phi.getFloorPosition(judgeLine, judgeLine_cfg.time) * PHIGROS_Y
        judgeLine_DrawPos = (
            *Tool_Functions.rotate_point(*judgeLine_cfg.pos, -judgeLine_cfg.rotate, 5.76 * h),
            *Tool_Functions.rotate_point(*judgeLine_cfg.pos, -judgeLine_cfg.rotate + 180, 5.76 * h)
        )
        negative_alpha = judgeLine_cfg.disappear < 0.0
        judgeLine_color = (*judgeLine.get_datavar_color(judgeLine_cfg.time, (254, 255, 169) if not noautoplay else PhigrosPlayManagerObject.getJudgelineColor()), judgeLine_cfg.disappear if not judgeline_notransparent else 1.0)
        judgeLine_webCanvas_color = f"rgba{judgeLine_color}"
        if judgeLine_color[-1] > 0.0 and show_judgeline:
            if judgeLine_can_render(judgeLine_DrawPos) or render_range_more:
                if render_range_more:
                    Task(
                        root.run_js_code,
                        f"ctx.scale({1.0 / render_range_more_scale},{1.0 / render_range_more_scale});",
                        add_code_array = True
                    )
                    
                if judgeLine.TextJudgeLine:
                    Task(
                        root.create_text,
                        *judgeLine_cfg.pos,
                        text = judgeLine.get_datavar_text(judgeLine_cfg.time),
                        font = f"{(w + h) / 75 * 1.35}px PhigrosFont",
                        textAlign = "center",
                        textBaseline = "middle",
                        strokeStyle = judgeLine_webCanvas_color,
                        fillStyle = judgeLine_webCanvas_color,
                        wait_execute = True
                    )
                elif judgeLine.EnableTexture:
                    xscale, yscale = judgeLine.get_datavar_scale(judgeLine_cfg.time)
                    Task(
                        root.run_js_code,
                        f"ctx.drawRotateImage(\
                            {root.get_img_jsvarname(f"JudgeLine_Texture_{judgeLine.id}")},\
                            {judgeLine_cfg.pos[0]},\
                            {judgeLine_cfg.pos[1]},\
                            {judgeLine.TexturePillowObject.width * 0.75 * xscale},\
                            {judgeLine.TexturePillowObject.height * 0.75 * yscale},\
                            {- judgeLine_cfg.rotate},\
                            {judgeLine_cfg.disappear}\
                        );",
                        add_code_array = True
                    )
                else:
                    Task(
                        root.create_line,
                        *judgeLine_DrawPos,
                        lineWidth = JUDGELINE_WIDTH,
                        strokeStyle = judgeLine_webCanvas_color,
                        wait_execute = True
                    )
                
                if debug:
                    Task(
                        root.create_text,
                        *Tool_Functions.rotate_point(*judgeLine_cfg.pos, 90 - judgeLine_cfg.rotate - 180, (w + h) / 75),
                        text = f"{judgeLine.id}",
                        font = f"{(w + h) / 85 / 0.75}px PhigrosFont",
                        textAlign = "center",
                        textBaseline = "middle",
                        strokeStyle = "rgba(254, 255, 169, 0.5)",
                        fillStyle = "rgba(254, 255, 169, 0.5)",
                        wait_execute = True
                    )
                    
                    Task(
                        root.create_rectangle,
                        judgeLine_cfg.pos[0] - (w + h) / 250,
                        judgeLine_cfg.pos[1] - (w + h) / 250,
                        judgeLine_cfg.pos[0] + (w + h) / 250,
                        judgeLine_cfg.pos[1] + (w + h) / 250,
                        fillStyle = "rgb(238, 130, 238)",
                        wait_execute = True
                    )
                    
                Render_JudgeLine_Count += 1
                if render_range_more:
                    Task(
                        root.run_js_code,
                        f"ctx.scale({render_range_more_scale},{render_range_more_scale});",
                        add_code_array = True
                    )
        
        def process(notes_list:typing.List[Chart_Objects_Phi.note], t:typing.Literal[1, -1]): # above => t = 1, below => t = -1
            nonlocal Render_Note_Count
            for note_item in notes_list:
                this_note_sectime = note_item.time * this_judgeLine_T
                this_noteitem_clicked = this_note_sectime < now_t
                this_note_ishold = note_item.type == Const.Note.HOLD
                
                if this_noteitem_clicked and not note_item.clicked:
                    note_item.clicked = True
                    if enable_clicksound and not note_item.fake and not noautoplay:
                        Task.ExTask.append((
                            "thread-call",
                            "PlaySound.Play",
                            f'(Resource["Note_Click_Audio"]["{note_item.type_string}"],)' #use eval to get data tip:this string -> eval(string):tpule (arg to run thread-call)
                        ))
                    
                if not this_note_ishold and this_noteitem_clicked:
                    continue
                elif this_note_ishold and now_t > note_item.hold_endtime:
                    continue
                elif noautoplay and note_item.state == Const.NOTE_STATE.BAD:
                    continue
                elif noautoplay and not this_note_ishold and note_item.player_clicked:
                    continue
                
                note_now_floorPosition = note_item.floorPosition * PHIGROS_Y - (
                        judgeLine_note_dy
                        if not (this_note_ishold and note_item.clicked) else (
                        Chart_Objects_Phi.getFloorPosition(
                            judgeLine,note_item.time
                        ) * PHIGROS_Y + Tool_Functions.linear_interpolation(note_item.hold_endtime - now_t, 0, note_item.hold_length_sec, note_item.hold_length_px, 0)
                    )
                )
                
                if note_now_floorPosition > h * 2 and not render_range_more:
                    continue
                
                rotatenote_at_judgeLine_pos = Tool_Functions.rotate_point(
                    *judgeLine_cfg.pos,-judgeLine_cfg.rotate,note_item.positionX * PHIGROS_X
                )
                judgeLine_to_note_rotate_deg = (-90 if t == 1 else 90) - judgeLine_cfg.rotate
                x,y = Tool_Functions.rotate_point(
                    *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_deg,note_now_floorPosition
                )
                
                if this_note_ishold:
                    note_hold_draw_length = note_now_floorPosition + note_item.hold_length_px
                    if note_hold_draw_length >= 0:
                        holdend_x,holdend_y = Tool_Functions.rotate_point(
                            *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_deg,note_hold_draw_length
                        )
                    else:
                        holdend_x,holdend_y = rotatenote_at_judgeLine_pos
                    if note_now_floorPosition >= 0:
                        holdhead_pos = x, y
                    else:
                        holdhead_pos = rotatenote_at_judgeLine_pos
                    holdbody_range = (
                        Tool_Functions.rotate_point(*holdhead_pos,judgeLine_to_note_rotate_deg - 90,Note_width / 2),
                        Tool_Functions.rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_deg - 90,Note_width / 2),
                        Tool_Functions.rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_deg + 90,Note_width / 2),
                        Tool_Functions.rotate_point(*holdhead_pos,judgeLine_to_note_rotate_deg + 90,Note_width / 2),
                    )
                    
                if not render_range_more:
                    note_iscan_render = (
                        Note_CanRender(x, y)
                        if not this_note_ishold
                        else Note_CanRender(x, y, holdbody_range)
                    )
                else:
                    note_iscan_render = (
                        Note_CanRender(
                            x / render_range_more_scale + fr_x,
                            y / render_range_more_scale + fr_y
                        )
                        if not this_note_ishold
                        else Note_CanRender(
                            x / render_range_more_scale + fr_x,
                            y / render_range_more_scale + fr_y,[
                            (holdbody_range[0][0] / render_range_more_scale + fr_x,holdbody_range[0][1] / render_range_more_scale + fr_y),
                            (holdbody_range[1][0] / render_range_more_scale + fr_x,holdbody_range[1][1] / render_range_more_scale + fr_y),
                            (holdbody_range[2][0] / render_range_more_scale + fr_x,holdbody_range[2][1] / render_range_more_scale + fr_y),
                            (holdbody_range[3][0] / render_range_more_scale + fr_x,holdbody_range[3][1] / render_range_more_scale + fr_y)
                        ])
                    )
                
                if (
                    note_iscan_render and 
                    not negative_alpha and
                    abs(now_t - this_note_sectime) < note_item.VisibleTime
                ): # if judgeline`s alpha value < 0.0, we will not render the notes of judgeline.
                    judgeLine_rotate = (judgeLine_to_note_rotate_deg + 90) % 360
                    dub_text = "_dub" if note_item.morebets else ""
                    if not this_note_ishold:
                        this_note_img_keyname = f"{note_item.type_string}{dub_text}"
                        this_note_img = Resource["Notes"][this_note_img_keyname]
                        this_note_imgname = f"Note_{this_note_img_keyname}"
                    else:
                        this_note_img_keyname = f"{note_item.type_string}_Head{dub_text}"
                        this_note_img = Resource["Notes"][this_note_img_keyname]
                        this_note_imgname = f"Note_{this_note_img_keyname}"
                        
                        this_note_img_body_keyname = f"{note_item.type_string}_Body{dub_text}"
                        this_note_imgname_body = f"Note_{this_note_img_body_keyname}"
                        
                        this_note_img_end_keyname = f"{note_item.type_string}_End{dub_text}"
                        this_note_img_end = Resource["Notes"][this_note_img_end_keyname]
                        this_note_imgname_end = f"Note_{this_note_img_end_keyname}"
                    
                    fix_scale = Const.NOTE_DUB_FIXSCALE if note_item.morebets else 1.0 # because the note img if has morebets frame, the note will be look small, so we will `*` a fix scale to fix the frame size make the note look is small.
                        
                    if this_note_ishold:
                        if note_item.clicked:
                            holdbody_x,holdbody_y = rotatenote_at_judgeLine_pos
                            holdbody_length = note_hold_draw_length - this_note_img_end.height / 2
                        else:
                            holdbody_x,holdbody_y = Tool_Functions.rotate_point(
                                *holdhead_pos,judgeLine_to_note_rotate_deg,this_note_img.height / 2
                            )
                            holdbody_length = note_item.hold_length_px - this_note_img.height / 2 - this_note_img_end.height / 2
                        
                        miss_alpha_change = 0.5 if noautoplay and note_item.player_missed else 1.0
                        
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(this_note_imgname_end)},\
                                {holdend_x},\
                                {holdend_y},\
                                {Note_width * note_item.width * fix_scale},\
                                {Note_width / this_note_img_end.width * this_note_img_end.height},\
                                {judgeLine_rotate},\
                                {note_item.alpha * miss_alpha_change}\
                            );",
                            add_code_array = True
                        )
                        
                        if holdbody_length > 0.0:
                            Task(
                                root.run_js_code,
                                f"ctx.drawAnchorESRotateImage(\
                                    {root.get_img_jsvarname(this_note_imgname_body)},\
                                    {holdbody_x},\
                                    {holdbody_y},\
                                    {Note_width * note_item.width * fix_scale},\
                                    {holdbody_length},\
                                    {judgeLine_rotate},\
                                    {note_item.alpha * miss_alpha_change}\
                                );",
                                add_code_array = True
                            )
                        
                    if not (this_note_ishold and this_note_sectime < now_t):
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(this_note_imgname)},\
                                {x},\
                                {y},\
                                {Note_width * note_item.width * fix_scale},\
                                {Note_width / this_note_img.width * this_note_img.height},\
                                {judgeLine_rotate},\
                                {note_item.alpha}\
                            );",
                            add_code_array = True #eq wait_exec true
                        )
                    
                    Render_Note_Count += 1
        process(judgeLine.notesAbove,1)
        process(judgeLine.notesBelow,-1)

    
    effect_time = 0.5
    miss_effect_time = 0.2
    bad_effect_time = 0.5
    def process_effect_base(x:float, y:float, p:float, effect_random_blocks, perfect:bool):
        nonlocal Render_ClickEffect_Count
        Render_ClickEffect_Count += 1
        color = (254, 255, 169) if perfect else (162, 238, 255)
        imn = "Note_Click_Effect_" + ("Perfect" if perfect else "Good")
        if clickeffect_randomblock:
            for i, deg in enumerate(effect_random_blocks):
                block_alpha = (1.0 - p) * 0.85
                if block_alpha <= 0.0:
                    continue
                effect_random_point = Tool_Functions.rotate_point(
                    x, y, deg + i * 90,
                    ClickEffect_Size * Tool_Functions.ease_out(p) / 1.25
                )
                block_size = EFFECT_RANDOM_BLOCK_SIZE
                if p > 0.65:
                    block_size -= (p - 0.65) * EFFECT_RANDOM_BLOCK_SIZE
                Task(
                    root.create_rectangle,
                    effect_random_point[0] - block_size,
                    effect_random_point[1] - block_size,
                    effect_random_point[0] + block_size,
                    effect_random_point[1] + block_size,
                    fillStyle = f"rgba{color + (block_alpha, )}",
                    wait_execute = True
                )
        Task(
            root.create_image,
            f"{imn}_{int(p * (30 - 1)) + 1}",
            x - ClickEffect_Size / 2,
            y - ClickEffect_Size / 2,
            ClickEffect_Size,ClickEffect_Size,
            wait_execute = True
        )
        
    def process_effect(
        note:Chart_Objects_Phi.note,
        t:float,
        effect_random_blocks,
        perfect:bool,
        offset:float
    ):
        p = (now_t - t * note.master.T) / effect_time
        if not (0.0 <= p <= 1.0): return None
        offset /= note.master.T
        will_show_effect_pos = judgeLine.get_datavar_move(t, w, h)
        will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
        pos = Tool_Functions.rotate_point(
            *will_show_effect_pos,
            -will_show_effect_rotate,
            note.positionX * PHIGROS_X
        )
        process_effect_base(*pos, p, effect_random_blocks, perfect)
    
    def process_miss(
        note:Chart_Objects_Phi.note
    ):
        t = now_t / note.master.T
        p = (now_t - note.time * note.master.T) / miss_effect_time
        will_show_effect_pos = judgeLine.get_datavar_move(t, w, h)
        will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
        pos = Tool_Functions.rotate_point(
            *will_show_effect_pos,
            -will_show_effect_rotate,
            note.positionX * PHIGROS_X
        )
        floorp = note.floorPosition - Chart_Objects_Phi.getFloorPosition(note.master, t)
        x,y = Tool_Functions.rotate_point(
            *pos,
            (-90 if note.above else 90) - will_show_effect_rotate,
            floorp * PHIGROS_Y
        )
        img_keyname = f"{note.type_string}{"_dub" if note.morebets else ""}"
        this_note_img = Resource["Notes"][img_keyname]
        this_note_imgname = f"Note_{img_keyname}"
        Task(
            root.run_js_code,
            f"crc2d_enable_rrm = false; ctx.drawRotateImage(\
                {root.get_img_jsvarname(this_note_imgname)},\
                {x},\
                {y},\
                {Note_width * note.width},\
                {Note_width / this_note_img.width * this_note_img.height},\
                {- will_show_effect_rotate},\
                {note.alpha * (1 - p ** 0.5)}\
            ); crc2d_enable_rrm = true;",
            add_code_array = True
        )
    
    def process_bad(
        note:Chart_Objects_Phi.note
    ):
        t = note.player_badtime / note.master.T
        p = (now_t - note.player_badtime) / bad_effect_time
        will_show_effect_pos = judgeLine.get_datavar_move(t, w, h)
        will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
        pos = Tool_Functions.rotate_point(
            *will_show_effect_pos,
            -will_show_effect_rotate,
            note.positionX * PHIGROS_X
        )
        floorp = note.floorPosition - Chart_Objects_Phi.getFloorPosition(note.master, t)
        x,y = Tool_Functions.rotate_point(
            *pos,
            (-90 if note.above else 90) - will_show_effect_rotate,
            floorp * PHIGROS_Y
        )
        this_note_img = Resource["Notes"]["Tap_Bad"]
        Task(
            root.run_js_code,
            f"crc2d_enable_rrm = false; ctx.drawRotateImage(\
                {root.get_img_jsvarname("Note_Tap_Bad")},\
                {x},\
                {y},\
                {Note_width * note.width * (Const.NOTE_DUB_FIXSCALE if note.morebets else 1.0)},\
                {Note_width / this_note_img.width * this_note_img.height},\
                {- will_show_effect_rotate},\
                {note.alpha * (1 - p ** 3)}\
            ); crc2d_enable_rrm = true;",
            add_code_array = True
        )
        
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.scale({1.0 / render_range_more_scale},{1.0 / render_range_more_scale});",
            add_code_array = True
        )
        
    for judgeLine in phigros_chart_obj.judgeLineList:
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            note_time = note.time * judgeLine.T
            note_ishold = note.type == Const.Note.HOLD
            if not note_ishold and note.show_effected:
                continue
            elif note.fake:
                continue
            
            if not noautoplay:
                if note_time <= now_t:
                    if now_t - note_time <= effect_time:
                        process_effect(
                            note,
                            note.time,
                            note.effect_random_blocks,
                            True,
                            0.0
                        )
                    else:
                        note.show_effected = True
                    
                    if note_ishold:
                        efct_et = note.hold_endtime + effect_time
                        if efct_et >= now_t:
                            for temp_time,hold_effect_random_blocks in note.effect_times:
                                if temp_time < now_t:
                                    if now_t - temp_time <= effect_time:
                                        process_effect(
                                            note,
                                            temp_time / judgeLine.T,
                                            hold_effect_random_blocks,
                                            True,
                                            0.0
                                        )
            else: # noautoplay
                if note.player_holdjudged or (note.state == Const.NOTE_STATE.PERFECT or note.state == Const.NOTE_STATE.GOOD and note.player_clicked):
                    if note_time - note.player_click_offset <= now_t:
                        if now_t - (note_time - note.player_click_offset) <= effect_time:
                            process_effect(
                                note,
                                note.time - note.player_click_offset / note.master.T,
                                note.effect_random_blocks,
                                note.state == Const.NOTE_STATE.PERFECT if note.type != Const.Note.HOLD else note.player_holdclickstate == Const.NOTE_STATE.PERFECT,
                                note.player_click_offset
                            )
                        else:
                            note.show_effected = True
                elif note.state == Const.NOTE_STATE.MISS:
                    if 0.0 <= now_t - note_time <= miss_effect_time and note.type != Const.Note.HOLD:
                        process_miss(note)
                elif note.state == Const.NOTE_STATE.BAD:
                    if 0.0 <= now_t - note.player_badtime <= bad_effect_time:
                        process_bad(note)
                        
                if note_ishold and note.player_holdjudged and note.player_holdclickstate != Const.NOTE_STATE.MISS:
                    efct_et = note.player_holdmiss_time + effect_time
                    if efct_et >= now_t:
                        for temp_time, hold_effect_random_blocks in note.effect_times:
                            if temp_time < now_t:
                                if now_t - temp_time <= effect_time:
                                    if temp_time + effect_time <= efct_et:
                                        process_effect(
                                            note,
                                            temp_time / judgeLine.T,
                                            hold_effect_random_blocks,
                                            note.player_holdclickstate == Const.NOTE_STATE.PERFECT,
                                            0.0
                                        )
                    
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.scale({render_range_more_scale},{render_range_more_scale});",
            add_code_array = True
        )
    
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.translate(-{fr_x},-{fr_y});",
            add_code_array = True
        )
    
    if render_range_more:
        line_poses = [
            # (fr_x,fr_y),
            (fr_x + w / render_range_more_scale,fr_y),
            (fr_x + w / render_range_more_scale,fr_y + h / render_range_more_scale),
            (fr_x,fr_y + h / render_range_more_scale),
            (fr_x,fr_y)
        ]
        Task(
            root.run_js_code,
            f"ctx.lineWidth = {JUDGELINE_WIDTH / render_range_more_scale}; ctx.strokeStyle = \"{Const.RENDER_RANGE_MORE_FRAME_LINE_COLOR}\"; ctx.beginPath(); ctx.moveTo({fr_x},{fr_y});",
            add_code_array = True
        )
        for line_pos in line_poses:
            Task(
                root.run_js_code,
                f"ctx.lineTo({line_pos[0]},{line_pos[1]});",
                add_code_array = True
            )
        Task(
            root.run_js_code,
            "ctx.closePath(); ctx.stroke();",
            add_code_array = True
        )
    
    def do_extra(item:dict):
        print(item)
        
        match item["shader"]:
            case "chromatic":
                power = int(item["vars"]["power"] * (w + h) / 5)
                Task(
                    root.run_js_code,
                    f"rcf.Chromatic({power}, {power}, 0, 0, -{power}, -{power});",
                    add_code_array = True
                )
            
            case "circleBlur":
                pass
            
            case "fisheye":
                pass
            
            case "glitch":
                pass
            
            case "grayscale":
                factor = item["vars"]["factor"]
                Task(
                    root.run_js_code,
                    f"rcf.Grayscale({factor});",
                    add_code_array = True
                )
            
            case "noise":
                pass
            
            case "pixel":
                size = item["vars"]["size"]
                Task(
                    root.run_js_code,
                    f"rcf.Pixel({size});",
                    add_code_array = True
                )
            
            case "radialBlur":
                centerX = item["vars"]["centerX"]
                centerY = item["vars"]["centerY"]
                offset = item["vars"]["power"]
                sampleCount = item["vars"]["sampleCount"] * 4
                Task(
                    root.run_js_code,
                    f"rcf.RadialBlur({centerX}, {centerY}, {offset}, {sampleCount});",
                    add_code_array = True
                )
            
            case "shockwave":
                pass
            
            case "vignette":
                pass
            
            case _:
                print(f"Unknown shader: {item["shader"]}")
    
    for extra_item in extra_render_task:
        if not extra_item["global"]:
            do_extra(extra_item)
        
    combo = Chart_Functions_Phi.Cal_Combo(now_t) if not noautoplay else PhigrosPlayManagerObject.getCombo()
    time_text = f"{Format_Time(now_t)}/{Format_Time(audio_length)}"
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = get_stringscore((combo * (1000000 / phigros_chart_obj.note_num)) if phigros_chart_obj.note_num != 0 else 1000000) if not noautoplay else get_stringscore(PhigrosPlayManagerObject.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        now_time = time_text,
        acc = "100.00%" if not noautoplay else f"{(PhigrosPlayManagerObject.getAcc() * 100):.2f}%",
        clear = False,
        background = False
    )
    
    for extra_item in extra_render_task:
        if extra_item["global"]:
            do_extra(extra_item)
    
    if now_t >= audio_length:
        Task.ExTask.append(("break",))
    
    if not lfdaot: # 2 "if" layer is more readable
        if not no_mixer_reset_chart_time:
            this_music_pos = mixer.music.get_pos() % (audio_length * 1000)
            offset_judge_range = (1000 / 60) * 4
            if abs(music_offset := this_music_pos - (time() - show_start_time) * 1000) >= offset_judge_range:
                if abs(music_offset) <= audio_length * 1000 * 0.75:
                    Task.ExTask.append(("set","show_start_time",show_start_time - music_offset / 1000))
                    print(f"Warning: mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset)}ms)")
    
    Task(root.run_js_wait_code)
    
    extend_object.update(locals())
        
    return Task

def Get_LevelNumber() -> str:
    lv = chart_information["Level"].lower()
    if "lv." in lv:
        return lv.split("lv.")[1]
    elif "lv" in lv:
        return lv.split("lv")[1]
    elif "level" in lv:
        return lv.split("level")[1]
    else:
        return "?"

def Get_LevelText() -> str:
    return chart_information["Level"].split(" ")[0]

def PlayerStart_Phi():
    global show_start_time
    print("Player Start")
    root.title("Phigros Chart Player")
    Resource["Over"].stop()
    def Begin_Animation():
        animation_time = 4.5
        
        chart_name_text = chart_information["Name"]
        chart_name_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_name_text)}).width;") / 50
        chart_level_number = Get_LevelNumber()
        chart_level_number_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_level_number) if len(chart_level_number) >= 2 else "'00'"}).width;") / 50
        if len(chart_level_number) == 1:
            chart_level_number_width_1px /= 1.35
        chart_level_text = Get_LevelText()
        chart_level_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_level_text) if len(chart_level_text) >= 2 else "'00'"}).width;") / 50
        chart_artist_text = chart_information["Artist"]
        chart_artist_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_artist_text)}).width;") / 50
        chart_charter_text = chart_information["Charter"]
        chart_charter_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_charter_text)}).width;") / 50
        chart_illustrator_text = chart_information["Illustrator"]
        chart_illustrator_text_width_1px = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.process_code_string_syntax_tocode(chart_illustrator_text)}).width;") / 50
        tip = Phigros_Tips.get_tip()
        tip_font_size = w * 0.020833 / 1.25
        infoframe_x = w * 0.095
        infoframe_y = h * 0.47
        infoframe_width = 0.3 * w
        infoframe_height = 0.118 * h
        infoframe_ltr = w * 0.01
        infoframe_text_place_width = w * 0.23
        chart_name_font_size = infoframe_text_place_width / chart_name_text_width_1px
        chart_level_number_font_size = infoframe_width * 0.215 * 0.45 / chart_level_number_width_1px
        chart_level_text_font_size = infoframe_width * 0.215 * 0.175 / chart_level_text_width_1px
        chart_artist_text_font_size = infoframe_text_place_width * 0.65 / chart_artist_text_width_1px
        chart_charter_text_font_size = infoframe_text_place_width * 0.65 / chart_charter_text_width_1px
        chart_illustrator_text_font_size = infoframe_text_place_width * 0.65 / chart_illustrator_text_width_1px
        if chart_name_font_size > w * 0.020833:
            chart_name_font_size = w * 0.020833
        if chart_artist_text_font_size > w * 0.020833 * 0.65:
            chart_artist_text_font_size = w * 0.020833 * 0.65
        if chart_charter_text_font_size > w * 0.020833 * 0.65:
            chart_charter_text_font_size = w * 0.020833 * 0.65
        if chart_illustrator_text_font_size > w * 0.020833 * 0.65:
            chart_illustrator_text_font_size = w * 0.020833 * 0.65
        
        LoadSuccess.play()
        animation_st = time()
        while True:
            now_process = (time() - animation_st) / animation_time
            if now_process >= 1.0:
                break
            
            root.clear_canvas(wait_execute = True)
            all_ease_value = Tool_Functions.begin_animation_eases.im_ease(now_process)
            background_ease_value = Tool_Functions.begin_animation_eases.background_ease(now_process) * 1.25
            info_data_ease_value = Tool_Functions.begin_animation_eases.info_data_ease((now_process - 0.2) * 3.25)
            info_data_ease_value_2 = Tool_Functions.begin_animation_eases.info_data_ease((now_process - 0.275) * 3.25)
            im_size = 1 / 2.5
            
            draw_background()
            
            root.create_polygon(
                [
                    (-w * 0.1,0),
                    (-w * 0.1,h),
                    (background_ease_value * w - w * 0.1,h),
                    (background_ease_value * w,0),
                    (-w * 0.1,0)
                ],
                strokeStyle = "rgba(0, 0, 0, 0)",
                fillStyle = f"rgba(0, 0, 0, {0.75 * (1 - now_process)})",
                wait_execute = True
            )
            
            root.run_js_code(
                f"ctx.translate({all_ease_value * w},0.0);",
                add_code_array = True
            )
            
            root.create_polygon(
                [
                    (infoframe_x + infoframe_ltr,infoframe_y - infoframe_height),
                    (infoframe_x + infoframe_ltr + infoframe_width,infoframe_y - infoframe_height),
                    (infoframe_x + infoframe_width,infoframe_y),
                    (infoframe_x,infoframe_y),
                    (infoframe_x + infoframe_ltr,infoframe_y - infoframe_height)
                ],
                strokeStyle = "rgba(0, 0, 0, 0)",
                fillStyle = "rgba(0, 0, 0, 0.75)",
                wait_execute = True
            )
            
            root.create_polygon(
                [
                    (infoframe_x + w * 0.225 + infoframe_ltr,infoframe_y - infoframe_height * 1.03),
                    (infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215,infoframe_y - infoframe_height * 1.03),
                    (infoframe_x + w * 0.225 + infoframe_width * 0.215,infoframe_y + infoframe_height * 0.03),
                    (infoframe_x + w * 0.225,infoframe_y + infoframe_height * 0.03),
                    (infoframe_x + w * 0.225 + infoframe_ltr,infoframe_y - infoframe_height * 1.03)
                ],
                strokeStyle = "rgba(0, 0, 0, 0)",
                fillStyle = "#FFFFFF",
                wait_execute = True
            )
            
            root.create_text(
                infoframe_x + infoframe_ltr * 2,
                infoframe_y - infoframe_height * 0.65,
                text = chart_name_text,
                font = f"{(chart_name_font_size)}px PhigrosFont",
                textBaseline = "middle",
                fillStyle = "#FFFFFF",
                wait_execute = True
            )
            
            root.create_text(
                infoframe_x + infoframe_ltr * 2,
                infoframe_y - infoframe_height * 0.31,
                text = chart_artist_text,
                font = f"{(chart_artist_text_font_size)}px PhigrosFont",
                textBaseline = "middle",
                fillStyle = "#FFFFFF",
                wait_execute = True
            )
            
            root.create_text(
                infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
                infoframe_y - infoframe_height * 1.03 * 0.58,
                text = chart_level_number,
                font = f"{(chart_level_number_font_size)}px PhigrosFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = "#2F2F2F",
                wait_execute = True
            )
            
            root.create_text(
                infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
                infoframe_y - infoframe_height * 1.03 * 0.31,
                text = chart_level_text,
                font = f"{(chart_level_text_font_size)}px PhigrosFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = "#2F2F2F",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.065,
                h * 0.95,
                text = f"Tip: {tip}",
                font = f"{tip_font_size}px PhigrosFont",
                textBaseline = "bottom",
                fillStyle = f"rgba(255, 255, 255, {Tool_Functions.begin_animation_eases.tip_alpha_ease(now_process)})",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.1375 + (1 - info_data_ease_value) * -1 * w * 0.075,
                h * 0.5225,
                text = "Chart",
                font = f"{w / 98}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.1375 + (1 - info_data_ease_value) * -1 * w * 0.075,
                h * 0.5225 + w / 98 * 1.25,
                text = chart_charter_text,
                font = f"{chart_charter_text_font_size}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.1235 + (1 - info_data_ease_value_2) * -1 * w * 0.075,
                h * 0.565 + w / 98 * 1.25,
                text = "Illustration",
                font = f"{w / 98}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.1235 + (1 - info_data_ease_value_2) * -1 * w * 0.075,
                h * 0.565 + w / 98 * 1.25 + w / 98 * 1.25,
                text = chart_illustrator_text,
                font = f"{chart_illustrator_text_font_size}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
                wait_execute = True
            )
            
            root.create_image(
                "begin_animation_image",
                w * 0.65 - w * im_size * 0.5, h * 0.5 - h * im_size * 0.5,
                width = w * im_size,
                height = h * im_size,
                wait_execute = True
            )
            
            root.run_js_code(
                f"ctx.translate(-{all_ease_value * w},0.0);",
                add_code_array = True
            )
            
            root.run_js_wait_code()
    
    def ChartStart_Animation():
        st = time()
        while time() - st < 0.65:
            p = (time() - st) / 0.65
            val = 1 - (1 - p) ** 2
            draw_ui(animationing = True,dy = h / 7 * val)
            root.create_line(
                w / 2 - (val * w / 2),h / 2,
                w / 2 + (val * w / 2),h / 2,
                strokeStyle = Const.JUDGELINE_PERFECT_COLOR,
                lineWidth = JUDGELINE_WIDTH / render_range_more_scale if render_range_more else JUDGELINE_WIDTH,
                wait_execute = True
            )
            root.run_js_wait_code()
            sleep(1 / 240)
    
    Begin_Animation()
    ChartStart_Animation()
    
    phigros_chart_obj.init_notes(PHIGROS_Y)

    show_start_time = time()
    now_t = 0
    judgeLine_Configs = Chart_Objects_Phi.judgeLine_Configs(
        [
            Chart_Objects_Phi.judgeLine_Config_Item(
                line = judgeLine
            )
            for judgeLine in phigros_chart_obj.judgeLineList
        ]
    )
    
    if not lfdaot:
        mixer.music.play()
        while not mixer.music.get_busy(): pass
    
    if not lfdaot:
        if noautoplay:
            Thread(target=PlayChart_ThreadFunction, daemon=True).start()
            while "PhigrosPlayManagerObject" not in globals(): pass # Waiting to load PhigrosPlayManagerObject.
        play_restart_flag = False
        def _f(): nonlocal play_restart_flag; play_restart_flag = True
        root.jsapi.set_attr("Noautoplay_Restart", _f)
        root.run_js_code("_Noautoplay_Restart = (e) => {if (e.altKey && e.ctrlKey && e.repeat && e.key.toLowerCase() == 'r') pywebview.api.call_attr('Noautoplay_Restart');};") # && e.repeat 为了判定长按
        root.run_js_code("window.addEventListener('keydown', _Noautoplay_Restart);")
        while True:
            now_t = time() - show_start_time
            Task = GetFrameRenderTask_Phi(
                now_t,
                judgeLine_Configs,
                show_start_time
            )
            Task.ExecTask()
            
            break_flag = Chart_Functions_Phi.FrameData_ProcessExTask(
                Task.ExTask,
                lambda x: eval(x)
            )
            
            if break_flag:
                break
            
            if play_restart_flag:
                break
        if noautoplay:
            global Kill_PlayThread_Flag
            Kill_PlayThread_Flag = True
            while Kill_PlayThread_Flag: pass
            
        root.run_js_code("window.removeEventListener('keydown', _Noautoplay_Restart);")
        root.run_js_code("delete _Noautoplay_Restart;")
        delattr(root.jsapi, "Noautoplay_Restart")
            
        if play_restart_flag:
            mixer.music.fadeout(250)
            LoadChartObject()
            Thread(target=PlayerStart_Phi, daemon=True).start()
            return None
                
    else:
        lfdaot_tasks = {}
        frame_speed = 60
        if "--lfdaot-frame-speed" in argv:
            frame_speed = eval(argv[argv.index("--lfdaot-frame-speed") + 1])
        frame_count = 0
        frame_time = 1 / frame_speed
        allframe_num = int(audio_length / frame_time) + 1
        
        if lfdaot and not lfdoat_file: #eq if not lfdoat_file
            while True:
                if frame_count * frame_time > audio_length:
                    break
                
                lfdaot_tasks.update({frame_count:GetFrameRenderTask_Phi(
                    frame_count * frame_time,
                    judgeLine_Configs,
                    show_start_time
                )})
                
                frame_count += 1
                
                print(f"\rLoadFrameData: {frame_count} / {allframe_num}",end="")
            
            lfdaot_fp = dialog.savefile(
                fn = "Chart.lfdaot"
            )
            
            if lfdaot_fp != "":
                data = {
                    "meta":{
                        "frame_speed":frame_speed,
                        "frame_num":len(lfdaot_tasks),
                        "render_range_more":render_range_more,
                        "render_range_more_scale":render_range_more_scale,
                        "size":[w,h]
                    },
                    "data":[]
                }
                for Task in lfdaot_tasks.values():
                    Task_data = {
                        "render":[],
                        "ex":[]
                    }
                    for rendertask in Task.RenderTasks:
                        Task_data["render"].append({
                            "func_name":rendertask.func.__code__.co_name,
                            "args":list(rendertask.args),
                            "kwargs":rendertask.kwargs
                        })
                    for ex in Task.ExTask:
                        Task_data["ex"].append(list(ex))
                    data["data"].append(Task_data)
                with open(lfdaot_fp,"w") as f:
                    f.write(json.dumps(data).replace(" ",""))
        else: #-lfdaot-file
            fp = argv[argv.index("-lfdaot-file") + 1]
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
                "draw_background":draw_background,
                "draw_ui":draw_ui
            })
            for index,Task_data in enumerate(data["data"]):
                lfdaot_tasks.update({
                    index:Chart_Objects_Phi.FrameRenderTask(
                        RenderTasks = [
                            Chart_Objects_Phi.RenderTask(
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
                print("Warning: The size of the lfdaot file is not the same as the size of the window.")
        
        if not lfdaot_render_video:
            mixer.music.play()
            while not mixer.music.get_busy(): pass
        
            last_music_play_fcount = None
            while True:
                render_st = time()
                now_t = mixer.music.get_pos() / 1000
                music_play_fcount = int(now_t / frame_time)
                will_process_extask = []
                try:
                    Task:Chart_Objects_Phi.FrameRenderTask = lfdaot_tasks[music_play_fcount]
                except KeyError:
                    continue
                
                if last_music_play_fcount is not None:
                    for fcount in range(last_music_play_fcount,music_play_fcount):
                        try:
                            Task:Chart_Objects_Phi.FrameRenderTask = lfdaot_tasks[fcount]
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
                    break_flag = Chart_Functions_Phi.FrameData_ProcessExTask(
                        ExTask,
                        lambda x: eval(x)
                    )
                    
                    if break_flag:
                        break_flag_top = True
                
                if break_flag_top:
                    break
                
                sleep(max(0,frame_time - (time() - render_st)))
        else: # -lfdaot-render-video
            video_fp = dialog.savefile(
                fn = "lfdaot_render_video.mp4"
            )
            Lfdaot_VideoWriter = cv2.VideoWriter(
                video_fp,
                cv2.VideoWriter.fourcc(*"mp4v"),
                frame_speed,(w,h),
                True
            )
            
            if video_fp != "":
                def uploadFrame(dataUrl):
                    base64_data = dataUrl[dataUrl.find(",") + 1:]
                    img_data = base64.b64decode(base64_data)
                    img_array = numpy.frombuffer(img_data,dtype=numpy.uint8)
                    img = cv2.imdecode(img_array,cv2.IMREAD_COLOR)
                    Lfdaot_VideoWriter.write(img)
                
                root.jsapi.uploadFrame = uploadFrame
                
                for Task in lfdaot_tasks.values():
                    Task.ExecTask()
                    root.run_js_code("uploadFrame();")
                
                root.run_js_code("uploadFrame_addQueue = true;")
                
                while not root.run_js_code("uploadFrame_finish"):
                    sleep(0.1)
                
                Lfdaot_VideoWriter.release()
    
    LevelName = "AP" if not noautoplay else PhigrosPlayManagerObject.getLevelString()
    EarlyCount = 0 if not noautoplay else PhigrosPlayManagerObject.getEarlyCount()
    LateCount = 0 if not noautoplay else PhigrosPlayManagerObject.getLateCount()
    PerfectCount = phigros_chart_obj.note_num if not noautoplay else PhigrosPlayManagerObject.getPerfectCount()
    GoodCount = 0 if not noautoplay else PhigrosPlayManagerObject.getGoodCount()
    BadCount = 0 if not noautoplay else PhigrosPlayManagerObject.getBadCount()
    MissCount = 0 if not noautoplay else PhigrosPlayManagerObject.getMissCount()
    Acc = 1.0 if not noautoplay else PhigrosPlayManagerObject.getAcc()
    ScoreString = "1000000" if not noautoplay else get_stringscore(PhigrosPlayManagerObject.getScore())
    MaxCombo = phigros_chart_obj.note_num if not noautoplay else PhigrosPlayManagerObject.getMaxCombo()
    AccString = f"{(Acc * 100):.2f}%"
    
    def Chart_Finish_Animation_Frame(p:float):
        root.clear_canvas(wait_execute = True)
        im_ease_value = Tool_Functions.finish_animation_eases.all_ease(p)
        im_ease_pos = w * 1.25 * (1 - im_ease_value)
        data_block_1_ease_value = Tool_Functions.finish_animation_eases.all_ease(p - 0.015)
        data_block_1_ease_pos = w * 1.25 * (1 - data_block_1_ease_value)
        data_block_2_ease_value = Tool_Functions.finish_animation_eases.all_ease(p - 0.035)
        data_block_2_ease_pos = w * 1.25 * (1 - data_block_2_ease_value)
        data_block_3_ease_value = Tool_Functions.finish_animation_eases.all_ease(p - 0.055)
        data_block_3_ease_pos = w * 1.25 * (1 - data_block_3_ease_value)
        button_ease_value = Tool_Functions.finish_animation_eases.button_ease(p * 4.5 - 0.95)
        im_size = 0.475
        level_size = 0.125
        level_size *= Tool_Functions.finish_animation_eases.level_size_ease(p)
        button_ease_pos = - w * Const.FINISH_UI_BUTTON_SIZE * (1 - button_ease_value)
        
        draw_background()
        
        root.create_image(
            "begin_animation_image", #emm...
            w * 0.3 - w * im_size * 0.5 + im_ease_pos,
            h * 0.5 - h * im_size * 0.5,
            width = w * im_size,
            height = h * im_size,
            wait_execute = True
        )
        
        root.create_polygon(
            [
                (w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05, h * 0.5 - h * im_size * 0.5),
                (w * 0.25 + w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05, h * 0.5 - h * im_size * 0.5),
                (w * 0.25 + w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.5),
                (w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.5),
                (w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.05, h * 0.5 - h * im_size * 0.5),
            ],
            strokeStyle = "rgba(0, 0, 0, 0)",
            fillStyle = "#00000066",
            wait_execute = True
        )
        
        root.create_polygon(
            [
                (w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545),
                (w * 0.25 + w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545),
                (w * 0.25 + w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545 + h * im_size * 0.205),
                (w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545 + h * im_size * 0.205),
                (w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.545),
            ],
            strokeStyle = "rgba(0, 0, 0, 0)",
            fillStyle = "#00000066",
            wait_execute = True
        )
        
        root.create_polygon(
            [
                (w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205),
                (w * 0.25 + w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205),
                (w * 0.25 + w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205),
                (w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.205 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205),
                (w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25, h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205),
            ],
            strokeStyle = "rgba(0, 0, 0, 0)",
            fillStyle = "#00000066",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.06,
            h * 0.433,
            text = ScoreString,
            font = f"{(w + h) / 42}px PhigrosFont",
            fillStyle = f"rgba(255, 255, 255, {Tool_Functions.finish_animation_eases.score_alpha_ease(p)})",
            wait_execute = True
        )
        
        root.run_js_code(
            f"ctx.globalAlpha = {Tool_Functions.finish_animation_eases.level_alpha_ease(p)};",
            add_code_array = True
        )
        
        root.create_image(
            f"Level_{LevelName}",
            w * 0.25 - w * im_size * 0.4 + data_block_1_ease_pos + w * im_size * 1.6 - level_size * w / 2,
            h * 0.375 - level_size * w / 2,
            width = w * level_size,
            height = w * level_size,
            wait_execute = True
        )
        
        root.run_js_code(
            "ctx.globalAlpha = 1.0;",
            add_code_array = True
        )
        
        root.run_js_code(
            f"ctx.globalAlpha = {Tool_Functions.finish_animation_eases.playdata_alpha_ease(p - 0.02)}",
            add_code_array = True
        )
        
        root.create_text( # Max Combo
            w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 + w * im_size / 45,
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625,
            text = f"{MaxCombo}",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 70}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 + w * im_size / 45,
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625 + (w + h) / 70 / 2 * 1.25,
            text = "Max Combo",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 150}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text( # Accuracy
            w * 0.25 + w * im_size * 0.38 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 45,
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625,
            text = AccString,
            textAlign = "end",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 70}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 + w * im_size * 0.38 + data_block_2_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 45,
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.6625 + (w + h) / 70 / 2 * 1.25,
            text = "Accuracy",
            textAlign = "end",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 150}px PhigrosFont",
            wait_execute = True
        )
        
        root.run_js_code(
            f"ctx.globalAlpha = {Tool_Functions.finish_animation_eases.playdata_alpha_ease(p - 0.04)}",
            add_code_array = True
        )
        
        root.create_text( # Perfect Count
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.125),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
            text = f"{PerfectCount}",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 75}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.125),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
            text = "Perfect",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 185}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text( # Good Count
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.315),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
            text = f"{GoodCount}",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 75}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.315),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
            text = "Good",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 185}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text( # Bad Conut
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.505),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
            text = f"{BadCount}",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 75}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.505),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
            text = "Bad",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 185}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text( # Miss Count
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.695),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2,
            text = f"{MissCount}",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 75}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.695),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 / 2 + (w + h) / 75 / 2 * 1.25,
            text = "Miss",
            textAlign = "center",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 185}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text( # Early Count
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.875),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.375,
            text = "Early",
            textAlign = "start",
            textBaseline = "middle",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 150}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.925),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.375,
            text = f"{EarlyCount}",
            textAlign = "end",
            textBaseline = "middle",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 150}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text( # Late Count
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.85 * 0.875),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.625,
            text = "Late",
            textAlign = "start",
            textBaseline = "middle",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 150}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            w * 0.25 - w * im_size * 0.4 + data_block_3_ease_pos + w * im_size * 1.05 - w * im_size / 10 * 0.5 - w * im_size / 10 * 0.25 + (w * im_size * 0.8 * 0.925),
            h * 0.5 - h * im_size * 0.5 + h * im_size * 0.59 + h * im_size * 0.205 + h * im_size * 0.205 * 0.625,
            text = f"{LateCount}",
            textAlign = "end",
            textBaseline = "middle",
            fillStyle = "#FFFFFF",
            font = f"{(w + h) / 150}px PhigrosFont",
            wait_execute = True
        )
        
        root.run_js_code(
            "ctx.globalAlpha = 1.0;",
            add_code_array = True
        )
        
        Retry_Button_Width = w * Const.FINISH_UI_BUTTON_SIZE
        Retry_Button_Height = w * Const.FINISH_UI_BUTTON_SIZE / 190 * 145
        Retry_imsize = Retry_Button_Height * 0.3
        
        Continue_Button_Width, Continue_Button_Height = Retry_Button_Width, Retry_Button_Height
        Continue_imsize = Retry_imsize
        
        root.create_image( # Retry Button
            "Button_Left",
            button_ease_pos, 0,
            width = Retry_Button_Width,
            height = Retry_Button_Height,
            wait_execute = True
        )
        
        root.create_image(
            "Retry",
            button_ease_pos + w * Const.FINISH_UI_BUTTON_SIZE * 0.3 - Retry_imsize / 2,
            Retry_Button_Height / 2 - (Retry_Button_Height * (8 / 145)) - Retry_imsize / 2,
            width = Retry_imsize,
            height = Retry_imsize,
            wait_execute = True
        )
        
        root.create_image( # Continue Button
            "Button_Right",
            w - button_ease_pos - Continue_Button_Width, h - Continue_Button_Height,
            width = Continue_Button_Width,
            height = Continue_Button_Height,
            wait_execute = True
        )
        
        root.create_image(
            "Arrow_Right",
            w - (button_ease_pos + w * Const.FINISH_UI_BUTTON_SIZE * 0.35 + Continue_imsize / 2),
            h - (Continue_Button_Height / 2 - (Continue_Button_Height * (8 / 145)) * 1.15 + Continue_imsize / 2),
            width = Continue_imsize,
            height = Continue_imsize,
            wait_execute = True
        )
        root.run_js_wait_code()
    
    def Chart_Finish_Animation():
        animation_1_time = 0.75
        animation_1_start_time = time()
        if noautoplay: a1_combo = PhigrosPlayManagerObject.getCombo()
        
        while time() - animation_1_start_time < animation_1_time:
            p = (time() - animation_1_start_time) / animation_1_time
            v = p ** 2
            if not noautoplay:
                draw_ui(
                    process = 1.0,
                    score = ScoreString,
                    combo_state = True,
                    combo = phigros_chart_obj.note_num,
                    now_time = f"{Format_Time(audio_length)}/{Format_Time(audio_length)}",
                    acc = AccString,
                    animationing = True,
                    dy = h / 7 * (1 - v)
                )
            else:
                draw_ui(
                    process = 1.0,
                    score = ScoreString,
                    combo_state = a1_combo >= 3,
                    combo = a1_combo,
                    now_time = f"{Format_Time(audio_length)}/{Format_Time(audio_length)}",
                    acc = AccString,
                    animationing = True,
                    dy = h / 7 * (1 - v)
                )
            root.run_js_wait_code()
        
        mixer.music.fadeout(250)
        sleep(0.25)
        Resource["Over"].play(-1)
    
        animation_2_time = 3.5
        animation_2_start_time = time()
        a2_loop_clicked = False
        a2_continue_clicked = False
        a2_break = False
        
        def whileCheck():
            nonlocal a2_break
            while True:
                if a2_loop_clicked or (loop and (time() - animation_2_start_time) > 2.75):
                    def _f():
                        LoadChartObject()
                        PlayerStart_Phi()
                    Thread(target=_f, daemon=True).start()
                    break
                
                if a2_continue_clicked:
                    root.destroy()
                    break
                    
                sleep(1 / 240)
            
            root.run_js_code("window.removeEventListener('click', _loopClick);")
            root.run_js_code("window.removeEventListener('click', _continueClick);")
            root.run_js_code("delete _loopClick; delete _continueClick;")
            delattr(root.jsapi, "loopClick")
            delattr(root.jsapi, "continueClick")
            a2_break = True
        
        Thread(target=whileCheck, daemon=True).start()
        
        def loopClick(clientX, clientY):
            nonlocal a2_loop_clicked
            if clientX <= w * Const.FINISH_UI_BUTTON_SIZE and clientY <= w * Const.FINISH_UI_BUTTON_SIZE / 190 * 145:
                a2_loop_clicked = True
        
        def continueClick(clientX, clientY):
            nonlocal a2_continue_clicked
            if clientX >= w - w * Const.FINISH_UI_BUTTON_SIZE and clientY >= h - w * Const.FINISH_UI_BUTTON_SIZE / 190 * 145:
                a2_continue_clicked = True
        
        root.jsapi.set_attr("loopClick", loopClick)
        root.jsapi.set_attr("continueClick", continueClick)
        root.run_js_code("_loopClick = (e) => {pywebview.api.call_attr('loopClick', e.clientX, e.clientY);}")
        root.run_js_code("_continueClick = (e) => {pywebview.api.call_attr('continueClick', e.clientX, e.clientY);}")
        root.run_js_code("window.addEventListener('click', _loopClick);")
        root.run_js_code("window.addEventListener('click', _continueClick);")
        
        while time() - animation_2_start_time < animation_2_time and not a2_break:
            p = (time() - animation_2_start_time) / animation_2_time
            Chart_Finish_Animation_Frame(p)
        
        while not a2_break:
            Chart_Finish_Animation_Frame(1.0)
            
    Chart_Finish_Animation()

print("Loading Window...")
# root.iconbitmap("./icon.ico")
root = webcvapis.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "Phigros Chart Player",
    debug = "--debug" in argv,
    resizable = False,
    frameless = "-frameless" in argv
)
if "--window-host" in argv:
    windll.user32.SetParent(root.winfo_hwnd(), eval(argv[argv.index("--window-host") + 1]))
if hidemouse:
    root.run_js_code("hide_mouse();")
if "--fullscreen" in argv:
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root._web.toggle_fullscreen()
else:
    if "--size" not in argv:
        w, h = int(root.winfo_screenwidth() * 0.61803398874989484820458683436564), int(root.winfo_screenheight() * 0.61803398874989484820458683436564)
    else:
        w, h = int(eval(argv[argv.index("--size") + 1])), int(eval(argv[argv.index("--size") + 2]))
    root.resize(w, h)
    w_legacy, h_legacy = root.winfo_legacywindowwidth(), root.winfo_legacywindowheight()
    dw_legacy, dh_legacy = w - w_legacy, h - h_legacy
    del w_legacy, h_legacy
    root.resize(w + dw_legacy, h + dh_legacy)
    root.move(int(root.winfo_screenwidth() / 2 - (w + dw_legacy) / 2), int(root.winfo_screenheight() / 2 - (h + dh_legacy) / 2))

if render_range_more:
    root.run_js_code("render_range_more = true;")
    root.run_js_code(f"render_range_more_scale = {render_range_more_scale};")

for line in phigros_chart_obj.judgeLineList:
    if line.EnableTexture:
        root.reg_img(line.TexturePillowObject, f"JudgeLine_Texture_{line.id}")

background_image_blur = chart_image.resize((w,h)).filter(ImageFilter.GaussianBlur((w + h) / 125))
background_image = ImageEnhance.Brightness(background_image_blur).enhance(1.0 - chart_information["BackgroundDim"])
root.reg_img(background_image,"background")
PHIGROS_X, PHIGROS_Y = 0.05625 * w, 0.6 * h
JUDGELINE_WIDTH = h * 0.0075
Resource = Load_Resource()
EFFECT_RANDOM_BLOCK_SIZE = Note_width / 12.5
Chart_Functions_Phi.Init(
    phigros_chart_obj_ = phigros_chart_obj,
    PHIGROS_X_ = PHIGROS_X, PHIGROS_Y_ = PHIGROS_Y,
    w_ = w, h_ = h
)
extend_object.loaded()
Thread(target=Show_Start,daemon=True).start()
root.loop_to_close()

for item in [item for item in listdir(gettempdir()) if item.startswith("qfppr_cctemp_")]:
    item = f"{gettempdir()}\\{item}"
    try:
        rmtree(item)
        print(f"Remove Temp Dir: {item}")
    except Exception as e:
        print(f"Warning: {e}")

windll.kernel32.ExitProcess(0)