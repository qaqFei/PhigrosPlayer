from threading import Thread
from ctypes import windll
from os import chdir,environ,listdir,popen ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from os.path import exists,abspath,dirname
from sys import argv
from time import time,sleep
from shutil import rmtree
from tempfile import gettempdir
import typing
import csv
import json
import base64

from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from win32gui import GetWindowLong,SetWindowLong
from pygame import mixer
import win32con
import cv2
import numpy

import Chart_Objects_Phi
import Chart_Functions_Phi
import Const
import Find_Files
import PlaySound
import ConsoleWindow
import web_canvas
import Tool_Functions
import dialog
import Phigros_Tips

if "-hideconsole" in argv:
    ConsoleWindow.Hide()

if "-noclicksound" in argv:
    PlaySound.Play = lambda *args,**kwargs:None

hidemouse = "-hidemouse" in argv

selfdir = dirname(argv[0])
if selfdir == "": selfdir = "."
chdir(selfdir)

if not exists(".\\7z.exe") or not exists(".\\7z.dll"):
    print("7z.exe or 7z.dll Not Found.")
    windll.kernel32.ExitProcess(1)

temp_dir = f"{gettempdir()}\\phigros_chart_temp_{time()}"
for item in [item for item in listdir(gettempdir()) if item.startswith("phigros_chart_temp_")]:
    item = f"{gettempdir()}\\{item}"
    try:
        rmtree(item)
        print(f"Remove Temp Dir: {item}")
    except Exception as e:
        print(f"Warning: {e}")
print(f"Temp Dir: {temp_dir}")

Image._open = Image.open
Image.open = lambda fp,mode = "r",formats = None: [print(f"Loading Resource: {fp} ...") if temp_dir not in fp else None,Image._open(fp,mode,formats)][1]

debug = "-debug" in argv
show_holdbody = "-holdbody" in argv
show_judgeline = "-nojudgeline" not in argv
debug_noshow_transparent_judgeline = "-debug-noshow-transparent-judgeline" in argv
judgeline_notransparent = "-judgeline-notransparent" in argv
clickeffect_randomblock = "-noclickeffect-randomblock" not in argv
loop = "-loop" in argv
lfdaot = "-lfdaot" in argv
lfdoat_file = "-lfdaot-file" in argv
render_range_more = "-render-range-more" in argv
render_range_more_scale = 2.0 if "-render-range-more-scale" not in argv else eval(argv[argv.index("-render-range-more-scale")+1])
lfdaot_render_video = "-lfdaot-render-video" in argv

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
    "charts":[],
    "images":[],
    "audio":[],
}
for item in chart_files:
    try:
        chart_files_dict["images"].append([item,Image.open(item).convert("RGB")])
        name = item.replace(temp_dir+"\\","")
        print(f"Add Resource (image): {name}")
    except Exception:
        try:
            mixer.music.load(item)
            chart_files_dict["audio"].append(item)
            name = item.replace(temp_dir+"\\","")
            print(f"Add Resource (audio): {name}")
        except Exception:
            try:
                with open(item,"r",encoding="utf-8") as f:
                    chart_files_dict["charts"].append([item,json.load(f)])
                    name = item.replace(temp_dir+"\\","")
                    print(f"Add Resource (chart): {name}")
            except Exception:
                name = item.replace(temp_dir+"\\","")
                if name not in ["info.csv"]:
                    print(f"Warning: Unknown Resource Type. Path = {name}")
if len(chart_files_dict["charts"]) == 0:
    print("No Chart File Found.")
    windll.kernel32.ExitProcess(1)
if len(chart_files_dict["audio"]) == 0:
    print("No Audio File Found.")
    windll.kernel32.ExitProcess(1)
if len(chart_files_dict["images"]) == 0:
    chart_files_dict["images"].append(["default",Image.new("RGB",(16,9),"#0078d7")])
defualt_information = {
    "Name":"Unknow",
    "Artist":"Unknow",
    "Level":"SP Lv.?",
    "Illustrator":"Unknow",
    "Charter":"Unknow",
    "BackgroundDim":0.6
}
phigros_chart_index = 0
chart_image_index = 0
audio_file_index = 0
if len(chart_files_dict["charts"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["charts"]):
        index += 1
        name = chart_file[0].split("/")[-1].split("\\")[-1]
        print(f"{index}. {name}")
    phigros_chart_index = int(input("请选择谱面文件: "))-1
    phigros_chart = chart_files_dict["charts"][phigros_chart_index][1]
else:
    phigros_chart = chart_files_dict["charts"][phigros_chart_index][1]
phigros_chart_filepath = chart_files_dict["charts"][phigros_chart_index][0]
if len(chart_files_dict["images"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["images"]):
        index += 1
        name = chart_file[0].split("/")[-1].split("\\")[-1]
        print(f"{index}. {name}")
    chart_image_index = int(input("请选择谱面图片: "))-1
    chart_image:Image.Image = chart_files_dict["images"][chart_image_index][1]
else:
    chart_image:Image.Image = chart_files_dict["images"][chart_image_index][1]
chart_image_filepath = chart_files_dict["images"][chart_image_index][0]
if len(chart_files_dict["audio"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["audio"]):
        index += 1
        name = chart_file.split("/")[-1].split("\\")[-1]
        print(f"{index}. {name}")
    audio_file_index = int(input("请选择音频文件: "))-1
    audio_file = chart_files_dict["audio"][audio_file_index]
else:
    audio_file = chart_files_dict["audio"][audio_file_index]
mixer.music.load(audio_file)
audio_length = mixer.Sound(audio_file).get_length()
all_inforamtion = {}
print("Loading Chart Information...")
if not exists(f"{temp_dir}\\info.csv"):
    print("No info.csv Found.")
    chart_information = defualt_information
else:
    path_head = f"{temp_dir}\\"
    _process_path = lambda path:abspath(path_head+path)
    _process_path2 = lambda path:abspath(path)
    info_csv_map = {name:None for name in "Chart,Music,Image,Name,Artist,Level,Illustrator,Charter,AspectRatio,NoteScale,GlobalAlpha".split(",")}
    with open(f"{temp_dir}\\info.csv","r",encoding="utf-8") as f:
        reader = csv.reader(f)
        for index,row in enumerate(reader):
            if index == 0:
                for index_csv_map,item in enumerate(row):
                    info_csv_map[item] = index_csv_map
                break
        for row in reader:
            try:
                all_inforamtion[
                    (
                        _process_path(row[info_csv_map["Chart"] if info_csv_map["Chart"] is not None else 0]),
                        _process_path(row[info_csv_map["Music"] if info_csv_map["Music"] is not None else 1]),
                        _process_path(row[info_csv_map["Image"] if info_csv_map["Image"] is not None else 2])
                    )
                ] = {
                    name:row[info_csv_map[name]] for name in info_csv_map.keys() if info_csv_map[name] is not None and info_csv_map[name] < len(row)
                }
            except Exception as e:
                print(f"Warning: {e} in info.csv.")
    now_key = (
        _process_path2(phigros_chart_filepath),
        _process_path2(audio_file),
        _process_path2(chart_image_filepath)
    )
    for keys in all_inforamtion.keys():
        if keys == now_key:
            chart_information = {
                "Name":all_inforamtion[keys]["Name"] if "Name" in all_inforamtion[keys] else "Unknow",
                "Artist":all_inforamtion[keys]["Artist"] if "Artist" in all_inforamtion[keys] else "Unknow",
                "Level":all_inforamtion[keys]["Level"] if "Level" in all_inforamtion[keys] else "SP Lv.?",
                "Illustrator":all_inforamtion[keys]["Illustrator"] if "Illustrator" in all_inforamtion[keys] else "Unknow",
                "Charter":all_inforamtion[keys]["Charter"] if "Charter" in all_inforamtion[keys] else "Unknow",
                "BackgroundDim":float(all_inforamtion[keys]["BackgroundDim"] if "BackgroundDim" in all_inforamtion[keys] else 0.6)
            }
    try:
        chart_information
    except NameError:
        print("info.cvs Found. But cannot find information of this chart.")
        chart_information = defualt_information

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
    global phigros_chart_obj,rep_chart_obj
    if CHART_TYPE == Const.CHART_TYPE.PHI:
        phigros_chart_obj = Chart_Functions_Phi.Load_Chart_Object(phigros_chart)
    elif CHART_TYPE == Const.CHART_TYPE.REP:
        print("Please run rpe2phi.py.")
        windll.kernel32.ExitProcess(0)
LoadChartObject()

def Load_Resource():
    global ClickEffect_Size,Note_width,note_max_width,note_max_height,note_max_width_half,note_max_height_half,animation_image
    global WaitLoading,LoadSuccess
    print("Loading Resource...")
    WaitLoading = mixer.Sound("./Resources/WaitLoading.mp3")
    LoadSuccess = mixer.Sound("./Resources/LoadSuccess.wav")
    Thread(target=WaitLoading_FadeIn,daemon=True).start()
    LoadSuccess.set_volume(0.75)
    WaitLoading.play(-1)
    Note_width = int(PHIGROS_X * 1.75 * (eval(argv[argv.index("-scale-note") + 1]) if "-scale-note" in argv else 1.0))
    ClickEffect_Size = int(Note_width * 1.5)
    Resource = {
        "Notes":{
            "Tap":Image.open("./Resources/Notes/Tap.png"),
            "Tap_dub":Image.open("./Resources/Notes/Tap_dub.png"),
            "Drag":Image.open("./Resources/Notes/Drag.png"),
            "Drag_dub":Image.open("./Resources/Notes/Drag_dub.png"),
            "Flick":Image.open("./Resources/Notes/Flick.png"),
            "Flick_dub":Image.open("./Resources/Notes/Flick_dub.png"),
            "Hold_Head":Image.open("./Resources/Notes/Hold_Head.png"),
            "Hold_Head_dub":Image.open("./Resources/Notes/Hold_Head_dub.png"),
            "Hold_End":Image.open("./Resources/Notes/Hold_End.png"),
            "Hold_End_dub":Image.open("./Resources/Notes/Hold_End_dub.png"),
            "Hold_Body":Image.open("./Resources/Notes/Hold_Body.png"),
            "Hold_Body_dub":Image.open("./Resources/Notes/Hold_Body_dub.png")
        },
        "Note_Click_Effect":{
            "Perfect":[
                Image.open(f"./Resources/Note_Click_Effect/Perfect/{i}.png")
                for i in range(1,31)
            ]
        },
        "Note_Click_Audio":{
            "Tap":open("./Resources/Note_Click_Audio/Tap.wav","rb").read(),
            "Drag":open("./Resources/Note_Click_Audio/Drag.wav","rb").read(),
            "Hold":open("./Resources/Note_Click_Audio/Hold.wav","rb").read(),
            "Flick":open("./Resources/Note_Click_Audio/Flick.wav","rb").read()
        },
        "Start":Image.open("./Resources/Start.png")
    }
    
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
    
    for key,value in Resource["Notes"].items():
        if value.width > Note_width:
            Resource["Notes"][key] = value.resize((Note_width,int(Note_width / value.width * value.height)))
        root.reg_img(Resource["Notes"][key],f"Note_{key}")
    
    for i in range(30):
        root.reg_img(Resource["Note_Click_Effect"]["Perfect"][i],f"Note_Click_Effect_Perfect_{i + 1}")
    root.reg_img(Resource["Start"],"Start")
    root.reg_img(animation_image,"begin_animation_image")
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
    m,s = t // 60,t % 60
    m,s = int(m),int(s)
    return f"{m}:{s:>2}".replace(" ","0")

def WaitLoading_FadeIn():
    for i in range(1,50+1):
        WaitLoading.set_volume(i / 100)
        sleep(2 / 50)

def Show_Start():
    global WaitLoading,LoadSuccess
    WaitLoading.fadeout(450)
    root.run_js_code("show_in_animation();")
    LoadSuccess.play()
    sleep(1.25)
    draw_background()
    draw_ui(animationing=True)
    root.run_js_wait_code()
    sleep(0.5)
    root.run_js_code("show_out_animation();")
    sleep(1.25)
    root.run_js_code("Start_img.remove();")
    Thread(target=PlayerStart_Phi,daemon=True).start()
    del WaitLoading,LoadSuccess

def draw_ui(
    process:float = 0.0,
    score:str = "0000000",
    combo_state:bool = False,
    combo:int = 0,
    now_time:str = "0:00/0:00",
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
        root.run_js_code(f"ctx.translate(0,{- h / 18 + dy});",add_code_array=True)
    
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
        x = w * 0.99,
        y = h * 0.01,
        textBaseline = "top",
        textAlign = "right",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{int((w + h) / 75 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    if combo_state:
        root.create_text(
            text = f"{combo}",
            x = w / 2,
            y = h * 0.01,
            textBaseline = "top",
            textAlign = "center",
            strokeStyle = "white",
            fillStyle = "white",
            font = f"{int((w + h) / 75 / 0.75)}px PhigrosFont",
            wait_execute = True
        )
        
        root.create_text(
            text="Autoplay" if "-combotips" not in argv else argv[argv.index("-combotips") + 1],
            x = w / 2,
            y = h * 0.1,
            textBaseline = "bottom",
            textAlign = "center",
            strokeStyle = "white",
            fillStyle = "white",
            font = f"{int((w + h) / 100 / 0.75)}px PhigrosFont",
            wait_execute = True
        )
        
    root.create_text(
        text = now_time,
        x = 0,
        y = h * 0.01,
        textBaseline = "top",
        textAlign = "left",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{int((w + h) / 175 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,-2 * {- h / 18 + dy});",add_code_array=True)
    
    root.create_text(
        text = chart_information["Name"],
        x = w * 0.01,
        y = h * 0.99,
        textBaseline = "bottom",
        textAlign = "left",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{int((w + h) / 125 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    root.create_text(
        text = chart_information["Level"],
        x = w * 0.99,
        y = h * 0.99,
        textBaseline = "bottom",
        textAlign = "right",
        strokeStyle = "white",
        fillStyle = "white",
        font = f"{int((w + h) / 125 / 0.75)}px PhigrosFont",
        wait_execute = True
    )
    
    if animationing:
        root.run_js_code(f"ctx.translate(0,{- h / 18 + dy});",add_code_array=True)

def draw_background():
    root.create_image("background",0,0,w,h,wait_execute=True)

def Note_CanRender(
        x:float,y:float,
        hold_points:typing.Union[typing.Tuple[
            typing.Tuple[float,float],
            typing.Tuple[float,float],
            typing.Tuple[float,float],
            typing.Tuple[float,float]
        ],None] = None) -> bool:
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
                [hold_points[0],hold_points[1]],
                [hold_points[1],hold_points[2]],
                [hold_points[2],hold_points[3]],
                [hold_points[3],hold_points[0]]
            ],
            [
                [(0,0),(w,0)],[(0,0),(0,h)],
                [(w,0),(w,h)],[(0,h),(w,h)]
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

def GetFrameRenderTask_Phi(
    now_t:float,
    judgeLine_Configs:typing.Dict[
        int,
        typing.Dict[
            str,
            typing.Union[
                Chart_Objects_Phi.judgeLine,
                int,
                float,
                typing.Tuple[
                    typing.Union[int,float],typing.Union[int,float]
                ]
            ]
        ]
    ],
    show_start_time:float
):
    Task = Chart_Objects_Phi.FrameRenderTask([],[])
    Chart_Functions_Phi.Update_JudgeLine_Configs(judgeLine_Configs,now_t)
    Task(root.clear_canvas,wait_execute = True)
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
    for judgeLine_cfg in judgeLine_Configs.values():
        judgeLine:Chart_Objects_Phi.judgeLine = judgeLine_cfg["judgeLine"]
        this_judgeLine_T = judgeLine.T
        judgeLine_note_dy = Chart_Functions_Phi.Cal_judgeLine_NoteDy_ByTime(judgeLine,this_judgeLine_T,judgeLine_cfg["time"])
        judgeLine_DrawPos = (
            *Tool_Functions.rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],5.76 * h),
            *Tool_Functions.rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"] + 180,5.76 * h)
        )
        judgeLine_strokeStyle = (254,255,169,judgeLine_cfg["Disappear"] if not judgeline_notransparent else 1.0)
        if judgeLine_strokeStyle[-1] > 0.0 and show_judgeline:
            if judgeLine_can_render(judgeLine_DrawPos) or render_range_more:
                if render_range_more:
                    Task(
                        root.run_js_code,
                        f"ctx.scale({1.0 / render_range_more_scale},{1.0 / render_range_more_scale});",
                        add_code_array = True
                    )
                Task(
                    root.create_line,
                    *judgeLine_DrawPos,
                    lineWidth = JUDGELINE_WIDTH,
                    strokeStyle=f"rgba{judgeLine_strokeStyle}",
                    wait_execute = True
                )
                if render_range_more:
                    Task(
                        root.run_js_code,
                        f"ctx.scale({render_range_more_scale},{render_range_more_scale});",
                        add_code_array = True
                    )
        
        def process(notes_list:typing.List[Chart_Objects_Phi.note],t:int):
            for note_item in notes_list:
                this_note_sectime = note_item.time * this_judgeLine_T
                this_noteitem_clicked = this_note_sectime < now_t
                this_note_ishold = note_item.type == Const.Note.HOLD
                note_type = {
                    Const.Note.TAP:"Tap",
                    Const.Note.DRAG:"Drag",
                    Const.Note.HOLD:"Hold",
                    Const.Note.FLICK:"Flick"
                }[note_item.type]
                
                if this_noteitem_clicked and not note_item.clicked:
                    note_item.clicked = True
                    Task.ExTask.append((
                        "thread-call",
                        "PlaySound.Play",
                        f'(Resource["Note_Click_Audio"][{repr(note_type)}],)' #use eval to get data tip:this string -> eval(string):tpule (arg to run thread-call)
                    ))
                    
                if not this_note_ishold and this_noteitem_clicked:
                    continue
                elif this_note_ishold and now_t > note_item.hold_endtime:
                    continue
                
                note_now_floorPosition = note_item.floorPosition * PHIGROS_Y - (
                        judgeLine_note_dy
                        if not (this_note_ishold and note_item.clicked) else (
                        Chart_Functions_Phi.Cal_judgeLine_NoteDy_ByTime(
                            judgeLine,this_judgeLine_T,note_item.time
                        ) + note_item.hold_length_px * (1 - ((note_item.hold_endtime - now_t) / note_item.hold_length_sec))
                    )
                )
                
                rotatenote_at_judgeLine_pos = Tool_Functions.rotate_point(
                    *judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],note_item.positionX * PHIGROS_X
                )
                judgeLine_to_note_rotate_deg = - judgeLine_cfg["Rotate"] +( 180 if t == -1 else 0) - 90
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
                        holdhead_pos = x,y
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
                        Note_CanRender(x,y)
                        if not this_note_ishold
                        else Note_CanRender(x,y,holdbody_range)
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
                
                if note_iscan_render:
                    judgeLine_rotate = (judgeLine_to_note_rotate_deg + 90) % 360
                    dub_text = "_dub" if note_item.morebets else ""
                    if note_item.type != Const.Note.HOLD:
                        this_note_img_keyname = f"{note_type}{dub_text}"
                        this_note_img = Resource["Notes"][this_note_img_keyname]
                        this_note_imgname = f"Note_{this_note_img_keyname}"
                    else:
                        this_note_img_keyname = f"{note_type}_Head{dub_text}"
                        this_note_img = Resource["Notes"][this_note_img_keyname]
                        this_note_imgname = f"Note_{this_note_img_keyname}"
                        
                        this_note_img_body_keyname = f"{note_type}_Body{dub_text}"
                        this_note_imgname_body = f"Note_{this_note_img_body_keyname}"
                        
                        this_note_img_end_keyname = f"{note_type}_End{dub_text}"
                        this_note_img_end = Resource["Notes"][this_note_img_end_keyname]
                        this_note_imgname_end = f"Note_{this_note_img_end_keyname}"
                        
                    if not (this_note_ishold and this_note_sectime < now_t):
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(this_note_imgname)},\
                                {x},\
                                {y},\
                                {Note_width},\
                                {Note_width / this_note_img.width * this_note_img.height},\
                                {judgeLine_rotate}\
                            );",
                            add_code_array = True #eq wait_exec true
                        )
                        
                    if this_note_ishold:
                        if note_item.clicked:
                            holdbody_x,holdbody_y = rotatenote_at_judgeLine_pos
                            holdbody_length = note_hold_draw_length - this_note_img_end.height / 2
                        else:
                            holdbody_x,holdbody_y = Tool_Functions.rotate_point(
                                *holdhead_pos,judgeLine_to_note_rotate_deg,this_note_img.height / 2
                            )
                            holdbody_length = note_item.hold_length_px - this_note_img.height / 2 - this_note_img_end.height / 2
                        
                        Task(
                            root.run_js_code,
                            f"ctx.drawRotateImage(\
                                {root.get_img_jsvarname(this_note_imgname_end)},\
                                {holdend_x},\
                                {holdend_y},\
                                {Note_width},\
                                {Note_width / this_note_img_end.width * this_note_img_end.height},\
                                {judgeLine_rotate}\
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
                                    {Note_width},\
                                    {holdbody_length},\
                                    {judgeLine_rotate}\
                                );",
                                add_code_array = True
                            )
        process(judgeLine.notesAbove,1)
        process(judgeLine.notesBelow,-1)

    
    if render_range_more:
        Task(
            root.run_js_code,
            f"ctx.scale({1.0 / render_range_more_scale},{1.0 / render_range_more_scale});",
            add_code_array = True
        )
    effect_time = 0.5
    for judgeLine in phigros_chart_obj.judgeLineList:
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            note_time = note.time * judgeLine.T
            note_ishold = note.type == Const.Note.HOLD
            
            if not note_ishold and note.show_effected:
                continue
            elif note_ishold and note.show_effected_hold:
                continue
            
            if note_time <= now_t:
                def process(et,t,effect_random_blocks):
                    effect_process = (now_t - et) / effect_time
                    will_show_effect_pos = judgeLine.get_datavar_move(t,w,h)
                    will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
                    effect_pos = Tool_Functions.rotate_point(*will_show_effect_pos,-will_show_effect_rotate,note.positionX * PHIGROS_X)
                    if clickeffect_randomblock:
                        for index,random_deg in enumerate(effect_random_blocks):
                            block_alpha = (1.0 - effect_process) * 0.85
                            if block_alpha <= 0.0:
                                continue
                            effect_random_point = Tool_Functions.rotate_point(
                                *effect_pos,random_deg + index * 90,
                                ClickEffect_Size * Tool_Functions.ease_out(effect_process) / 1.25
                            )
                            block_size = EFFECT_RANDOM_BLOCK_SIZE
                            if effect_process > 0.65:
                                block_size -= (effect_process - 0.65) * EFFECT_RANDOM_BLOCK_SIZE
                            Task(
                                root.create_rectangle,
                                effect_random_point[0] - block_size,
                                effect_random_point[1] - block_size,
                                effect_random_point[0] + block_size,
                                effect_random_point[1] + block_size,
                                fillStyle = f"rgba{(254,255,169,block_alpha)}",
                                wait_execute = True
                            )
                    Task(
                        root.create_image,
                        f"Note_Click_Effect_Perfect_{int(effect_process * (30 - 1)) + 1}",
                        effect_pos[0] - ClickEffect_Size / 2,
                        effect_pos[1] - ClickEffect_Size / 2,
                        ClickEffect_Size,ClickEffect_Size,
                        wait_execute = True
                    )
                            
                if now_t - note_time <= effect_time:
                    process(note_time,note.time,note.effect_random_blocks)
                else:
                    note.show_effected = True
                
                if note_ishold:
                    is_processed = False
                    efct_et = note.hold_endtime + effect_time
                    if efct_et >= now_t:
                        for temp_time,hold_effect_random_blocks in note.effect_times:
                            if temp_time < now_t:
                                if now_t - temp_time <= effect_time:
                                    process(temp_time,temp_time / judgeLine.T,hold_effect_random_blocks)
                                    is_processed = True
                    if not is_processed and efct_et < now_t:
                        note.show_effected_hold = True
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

    combo = Chart_Functions_Phi.Cal_Combo(now_t)
    time_text = f"{Format_Time(now_t)}/{Format_Time(audio_length)}"
    Task(
        draw_ui,
        process=now_t / audio_length,
        score=get_stringscore((combo * (1000000 / phigros_chart_obj.note_num)) if phigros_chart_obj.note_num != 0 else 1000000),
        combo_state=combo >= 3,
        combo=combo,
        now_time=time_text,
        clear=False,
        background=False
    )
    
    if not lfdaot:
        if not mixer.music.get_busy():
            Task.ExTask.append(("break",))
        this_music_pos = mixer.music.get_pos() % (audio_length * 1000)
        offset_judge_range = (1000 / 60) * 4
        if abs(music_offset := this_music_pos - (time() - show_start_time) * 1000) >= offset_judge_range:
            Task.ExTask.append(("set","show_start_time",show_start_time - music_offset / 1000))
            print(f"Warning: mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset)}ms)")
    
    Task(root.run_js_wait_code)
        
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
    print("Player Start")
    root.title("Phigros Chart Player")
    def Begin_Animation():
        animation_time = 4.0
        
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
        chart_level_text_font_size = infoframe_width * 0.215 * 0.145 / chart_level_text_width_1px
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
        
        animation_st = time()
        while True:
            now_process = (time() - animation_st) / animation_time
            if now_process >= 1.0:
                break
            
            root.clear_canvas(wait_execute = True)
            all_ease_value = Tool_Functions.begin_animation_eases.im_ease(now_process)
            background_ease_value = Tool_Functions.begin_animation_eases.background_ease(now_process)
            im_size = 1 / 2.5
            
            draw_background()
            
            root.create_polygon(
                [
                    (0,0),
                    (0,h),
                    (background_ease_value * w,h),
                    (w * 0.1 + background_ease_value * w,0),
                    (0,0),
                ],
                strokeStyle = "rgba(0, 0, 0, 0)",
                fillStyle = f"rgba(0, 0, 0, {0.95 * (1 - now_process)})",
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
                font = f"{int(chart_name_font_size)}px PhigrosFont",
                textBaseline = "middle",
                fillStyle = "#FFFFFF",
                wait_execute = True
            )
            
            root.create_text(
                infoframe_x + infoframe_ltr * 2,
                infoframe_y - infoframe_height * 0.31,
                text = chart_artist_text,
                font = f"{int(chart_artist_text_font_size)}px PhigrosFont",
                textBaseline = "middle",
                fillStyle = "#FFFFFF",
                wait_execute = True
            )
            
            root.create_text(
                infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
                infoframe_y - infoframe_height * 1.03 * 0.55,
                text = chart_level_number,
                font = f"{int(chart_level_number_font_size)}px PhigrosFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = "#2F2F2F",
                wait_execute = True
            )
            
            root.create_text(
                infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
                infoframe_y - infoframe_height * 1.03 * 0.31,
                text = chart_level_text,
                font = f"{int(chart_level_text_font_size)}px PhigrosFont",
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
                w * 0.1375, h * 0.5225,
                text = "Chart",
                font = f"{w / 98}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, 235)",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.1375, h * 0.5225 + w / 98 * 1.25,
                text = chart_charter_text,
                font = f"{chart_charter_text_font_size}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, 235)",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.1255, h * 0.5225 + w / 98 * 1.25 + chart_artist_text_font_size * 2.05,
                text = "Illustration",
                font = f"{w / 98}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, 235)",
                wait_execute = True
            )
            
            root.create_text(
                w * 0.1255, h * 0.5225 + w / 98 * 1.25 + chart_artist_text_font_size * 2.05 + w / 98 * 1.25,
                text = chart_illustrator_text,
                font = f"{chart_illustrator_text_font_size}px PhigrosFont",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, 235)",
                wait_execute = True
            )
            
            root.create_image(
                "begin_animation_image",
                w * 0.65 - w * im_size * 0.5, h * 0.5 - h * im_size * 0.5,
                width = w * im_size, height = h * im_size,
                wait_execute = True
            )
            
            root.run_js_code(
                f"ctx.translate(-{all_ease_value * w},0.0);",
                add_code_array = True
            )
            
            root.run_js_wait_code()
    
    def ChartStart_Animation():
        gr,step_time = Tool_Functions.Get_Animation_Gr(60,0.65)
        val = 0.0
        for step in gr:
            st = time()
            val += step
            draw_ui(animationing=True,dy = h / 18 * val)
            root.create_line(
                w / 2 - (val * w / 2),h / 2,
                w / 2 + (val * w / 2),h / 2,
                strokeStyle = Const.JUDGELINE_PERFECT_COLOR,
                lineWidth = JUDGELINE_WIDTH,
                wait_execute = True
            )
            root.run_js_wait_code()
            sleep(step_time - min(time() - st,step_time))
    
    Begin_Animation()
    ChartStart_Animation()
    
    phigros_chart_obj.init_holdlength(PHIGROS_Y)

    show_start_time = time()
    now_t = 0
    judgeLine_Configs = {
        judgeLine_item.__hash__():{
            "judgeLine":judgeLine_item,
            "Rotate":0.0,
            "Disappear":1.0,
            "Pos":(0,0),
            "Speed":1.0,
            "time":None
        }
        for judgeLine_item in phigros_chart_obj.judgeLineList
    }
    
    if not lfdaot:
        mixer.music.play()
        while not mixer.music.get_busy(): pass
    
    if not lfdaot:
        while True:
            now_t = time() - show_start_time
            Task = GetFrameRenderTask_Phi(
                now_t,
                judgeLine_Configs,
                show_start_time
            )
            Task.ExecTask()
            
            break_flag = Chart_Functions_Phi.FrameData_ProcessExTask(
                locals(),
                Task.ExTask,
                lambda x:eval(x)
            )
            
            if break_flag:
                break
    else:
        lfdaot_tasks = {}
        frame_speed = 60
        if "-lfdaot-frame-speed" in argv:
            frame_speed = eval(argv[argv.index("-lfdaot-frame-speed") + 1])
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
                        locals(),
                        ExTask,
                        lambda x:eval(x)
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
        
    if loop:
        LoadChartObject()
        PlayerStart_Phi()
    else:
        root.destroy()

def Re_Init():
    (
        Chart_Functions_Phi.w,
        Chart_Functions_Phi.h,
        Chart_Functions_Phi.PHIGROS_X,
        Chart_Functions_Phi.PHIGROS_Y
    ) = w,h,PHIGROS_X,PHIGROS_Y
    phigros_chart_obj.init_holdlength(PHIGROS_Y)

print("Loading Window...")
# root.iconbitmap(".\\icon.ico")
root = web_canvas.WebCanvas(
    width = 1,height = 1,
    x = 0,y = 0,
    title = "Phigros Chart Player",
    debug = "-debug" in argv,
    resizable = True if not lfdaot else False,
    frameless = "-frameless" in argv
)
if "-window-host" in argv:
    windll.user32.SetParent(root.winfo_hwnd(),eval(argv[argv.index("-window-host") + 1]))
if hidemouse:
    root.run_js_code("hide_mouse();")
if "-fullscreen" in argv:
    w,h = root.winfo_screenwidth(),root.winfo_screenheight()
    root._web.toggle_fullscreen()
else:
    if "-size" not in argv:
        w,h = int(root.winfo_screenwidth() * 0.61803398874989484820458683436564),int(root.winfo_screenheight() * 0.61803398874989484820458683436564)
    else:
        w,h = int(eval(argv[argv.index("-size") + 1])),int(eval(argv[argv.index("-size") + 2]))
    root.resize(w,h)
    w_legacy,h_legacy = root.winfo_legacywindowwidth(),root.winfo_legacywindowheight()
    dw_legacy,dh_legacy = w - w_legacy,h - h_legacy
    del w_legacy,h_legacy
    root.resize(w + dw_legacy,h + dh_legacy)
    root.move(int(root.winfo_screenwidth() / 2 - (w + dw_legacy) / 2),int(root.winfo_screenheight() / 2 - (h + dh_legacy) / 2))
root.reg_event("resized",lambda *args,**kwargs:exec("global w,h,PHIGROS_X,PHIGROS_Y; args = list(args); args[0] -= dw_legacy; args[1] -= dh_legacy; w,h = args; PHIGROS_X,PHIGROS_Y = 0.05625 * w,0.6 * h; Re_Init()"))

if render_range_more:
    root.run_js_code("render_range_more = true;")
    root.run_js_code(f"render_range_more_scale = {render_range_more_scale};")
    
background_image = ImageEnhance.Brightness(chart_image.resize((w,h)).filter(ImageFilter.GaussianBlur((w + h) / 300))).enhance(1.0 - chart_information["BackgroundDim"])
root.reg_img(background_image,"background")
PHIGROS_X,PHIGROS_Y = 0.05625 * w,0.6 * h
JUDGELINE_WIDTH = h * 0.0075
window_hwnd = root.winfo_hwnd()
print(f"Window Hwnd: {window_hwnd}")
window_style = GetWindowLong(window_hwnd,win32con.GWL_STYLE)
SetWindowLong(window_hwnd,win32con.GWL_STYLE,window_style & ~win32con.WS_SYSMENU) ; del window_style
Resource = Load_Resource()
EFFECT_RANDOM_BLOCK_SIZE = Note_width / 12.5
Chart_Functions_Phi.Init(
    phigros_chart_obj_ = phigros_chart_obj,
    PHIGROS_X_ = PHIGROS_X,PHIGROS_Y_ = PHIGROS_Y,
    w_ = w,h_ = h
)
Thread(target=Show_Start,daemon=True).start()
root.loop_to_close()
windll.kernel32.ExitProcess(0)