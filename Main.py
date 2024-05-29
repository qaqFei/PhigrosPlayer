from threading import Thread
from ctypes import windll
from os import chdir,environ,listdir,popen ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from os.path import exists,abspath,dirname
from sys import argv
from time import time,sleep
from json import loads
from queue import Queue
from shutil import rmtree
from tempfile import gettempdir
import typing
import csv

from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from win32gui import GetWindowLong,SetWindowLong
from pygame import mixer
import win32con
import win32ui

import Chart_Objects_Phi
# import Chart_Objects_Rep
import Chart_Functions_Phi
import Chart_Functions_Rep
import Const
import Find_Files
import PlaySound
import ConsoleWindow
import web_canvas
import Tool_Functions

if "-hideconsole" in argv:
    ConsoleWindow.Hide()

hidemouse = "-hidemouse" in argv

selfdir = dirname(argv[0])
if selfdir == "": selfdir = "."
chdir(selfdir)

if exists(".//__pycache__"):
    try: rmtree(".//__pycache__")
    except Exception: pass

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

if len(argv) < 2 or not exists(argv[1]):
    dlg = win32ui.CreateFileDialog(1)
    dlg.DoModal()
    argv = [argv[0]] + [dlg.GetPathName()] + argv[0:]
    if argv[1] == "":
        windll.kernel32.ExitProcess(1)

print("Loading Font...")
def remove_font():
    while windll.gdi32.RemoveFontResourceW(".\\font.ttf"): pass
remove_font()
windll.gdi32.AddFontResourceW(".\\font.ttf")

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
                    chart_files_dict["charts"].append([item,loads(f.read())])
                    name = item.replace(temp_dir+"\\","")
                    print(f"Add Resource (chart): {name}")
            except Exception:
                name = item.replace(temp_dir+"\\","")
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
    "Level":"Unknow",
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
    chart_image = chart_files_dict["images"][chart_image_index][1]
else:
    chart_image = chart_files_dict["images"][chart_image_index][1]
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
    info_csv_map = {
        name:None for name in "Chart,Music,Image,AspectRatio,ScaleRatio,GlobalAlpha,Name,Level,Illustrator,Designer".split(",")
    }
    with open(f"{temp_dir}\\info.csv","r",encoding="utf-8") as f:
        reader = csv.reader(f)
        for index,row in enumerate(reader):
            if index == 0:
                for index_csv_map,item in enumerate(row):
                    if item in info_csv_map:
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
    raise SystemExit
    
print("Loading Chart Information Successfully.")
print("Inforamtions: ")
print("              Name:",chart_information["Name"])
print("              Artist:",chart_information["Artist"])
print("              Level:",chart_information["Level"])
print("              Charter:",chart_information["Charter"])
print("              BackgroundDim:",chart_information["BackgroundDim"])


del chart_files,chart_files_dict

def loger():
    while True:
        while not loger_queue.empty():
            print(loger_queue.get())
        sleep(0.01)

loger_queue = Queue()
clickeffect_cache = []
note_id = -1

match CHART_TYPE:
    case Const.CHART_TYPE.PHI:
        phigros_chart_obj = Chart_Functions_Phi.Load_Chart_Object(phigros_chart)
    case Const.CHART_TYPE.REP:
        rep_chart_obj = Chart_Functions_Rep.Load_Chart_Object(phigros_chart)

def Load_Resource():
    global ClickEffect_Size,Note_width,note_max_width,note_max_height,note_max_width_half,note_max_height_half
    global WaitLoading,LoadSuccess
    print("Loading Resource...")
    WaitLoading = mixer.Sound("./Resources/WaitLoading.mp3")
    LoadSuccess = mixer.Sound("./Resources/LoadSuccess.wav")
    Thread(target=WaitLoading_FadeIn,daemon=True).start()
    LoadSuccess.set_volume(0.75)
    WaitLoading.play(-1)
    Note_width = int(PHIGROS_X * 1.75)
    Note_height_Tap = int(Note_width / 989 * 100)
    Note_height_Tap_dub = int(Note_width / 1089 * 200)
    Note_height_Drag = int(Note_width / 989 * 60)
    Note_height_Drag_dub = int(Note_width / 1089 * 160)
    Note_height_Flick = int(Note_width / 989 * 200)
    Note_height_Flick_dub = int(Note_width / 1089 * 300)
    Note_height_Hold_Head = int(Note_width / 989 * 50)
    Note_height_Hold_Head_dub = int(Note_width / 1058 * 97)
    Note_height_Hold_End = int(Note_width / 989 * 50)
    ClickEffect_Size = int(Note_width * 1.5)
    Resource = {
        "Notes":{
            "Tap":Image.open("./Resources/Notes/Tap.png").resize((Note_width,Note_height_Tap)),
            "Tap_dub":Image.open("./Resources/Notes/Tap_dub.png").resize((Note_width,Note_height_Tap_dub)),
            "Drag":Image.open("./Resources/Notes/Drag.png").resize((Note_width,Note_height_Drag)),
            "Drag_dub":Image.open("./Resources/Notes/Drag_dub.png").resize((Note_width,Note_height_Drag_dub)),
            "Flick":Image.open("./Resources/Notes/Flick.png").resize((Note_width,Note_height_Flick)),
            "Flick_dub":Image.open("./Resources/Notes/Flick_dub.png").resize((Note_width,Note_height_Flick_dub)),
            "Hold":{
                "Hold_Head":Image.open("./Resources/Notes/Hold_Head.png").resize((Note_width,Note_height_Hold_Head)),
                "Hold_Head_dub":Image.open("./Resources/Notes/Hold_Head_dub.png").resize((Note_width,Note_height_Hold_Head_dub)),
                "Hold_End":Image.open("./Resources/Notes/Hold_End.png").resize((Note_width,Note_height_Hold_End))
            }
        },
        "Note_Click_Effect":{
            "Perfect":[
                Image.open(f"./Resources/Note_Click_Effect/Perfect/{i}.png").resize((ClickEffect_Size,)*2)
                for i in range(1,31)
            ]
        },
        "Note_Click_Audio":{
            "Tap":open("./Resources/Note_Click_Audio/Tap.wav","rb").read(),
            "Drag":open("./Resources/Note_Click_Audio/Drag.wav","rb").read(),
            "Hold":open("./Resources/Note_Click_Audio/Hold.wav","rb").read(),
            "Flick":open("./Resources/Note_Click_Audio/Flick.wav","rb").read()
        },
        "ProcessBar":Image.new("RGB",(w,int(h / 125)),(145,)*3),
        "Start":Image.open("./Resources/Start.png").resize((w,h))
    }
    print("Loading Resource - create processbar ...")
    ImageDraw.Draw(Resource["ProcessBar"]).rectangle((w * 0.998,0,w,int(h / 125)),fill=(255,)*3)
    Resource["ProcessBar"] = Resource["ProcessBar"]
    root.reg_img(Resource["Notes"]["Tap"],"Note_Tap")
    root.reg_img(Resource["Notes"]["Tap_dub"],"Note_Tap_dub")
    root.reg_img(Resource["Notes"]["Drag"],"Note_Drag")
    root.reg_img(Resource["Notes"]["Drag_dub"],"Note_Drag_dub")
    root.reg_img(Resource["Notes"]["Flick"],"Note_Flick")
    root.reg_img(Resource["Notes"]["Flick_dub"],"Note_Flick_dub")
    root.reg_img(Resource["Notes"]["Hold"]["Hold_Head"],"Note_Hold_Head")
    root.reg_img(Resource["Notes"]["Hold"]["Hold_Head_dub"],"Note_Hold_Head_dub")
    root.reg_img(Resource["Notes"]["Hold"]["Hold_End"],"Note_Hold_End")
    for i in range(30):
        root.reg_img(Resource["Note_Click_Effect"]["Perfect"][i],f"Note_Click_Effect_Perfect_{i + 1}")
    root.reg_img(Resource["ProcessBar"],"ProcessBar")
    root.reg_img(Resource["Start"],"Start")
    root.load_allimg()
    root.shutdown_fileserver()
    root.run_js_code("color_block_img_ele = Start_img; body_ele.appendChild(color_block_img_ele);")
    print("Loading Resource Successfully.")
    note_max_width = max(
        [
            Resource["Notes"]["Tap"].width,
            Resource["Notes"]["Tap_dub"].width,
            Resource["Notes"]["Drag"].width,
            Resource["Notes"]["Drag_dub"].width,
            Resource["Notes"]["Flick"].width,
            Resource["Notes"]["Flick_dub"].width,
            Resource["Notes"]["Hold"]["Hold_Head"].width,
            Resource["Notes"]["Hold"]["Hold_Head_dub"].width,
            Resource["Notes"]["Hold"]["Hold_End"].width
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
            Resource["Notes"]["Hold"]["Hold_Head"].height,
            Resource["Notes"]["Hold"]["Hold_Head_dub"].height,
            Resource["Notes"]["Hold"]["Hold_End"].height
        ]
    )
    note_max_width_half = note_max_width / 2
    note_max_height_half = note_max_height / 2
    return Resource

def Format_Time(t:typing.Union[int,float]) -> str:
    m,s = t // 60,t % 60
    m,s = int(m),int(s)
    return f"{m}:{s:>2}".replace(" ","0")

def Get_judgeLine_Color() -> str:
    return "#feffa9"

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
    draw_ui()
    root.run_js_wait_code()
    sleep(0.5)
    root.run_js_code("show_out_animation();")
    sleep(1.25)
    match CHART_TYPE:
        case Const.CHART_TYPE.PHI:
            Thread(target=PlayerStart_Phi,daemon=True).start()
        case Const.CHART_TYPE.REP:
            Thread(target=PlayerStart_Rep,daemon=True).start()
    del WaitLoading,LoadSuccess

def draw_ui(
    process:float = 0.0,
    score:str = "0000000",
    combo_state:bool = False,
    combo:int = 0,
    now_time:str = "0:00/0:00",
    clear:bool = True,
    background:bool = True
):
    if clear:
        root.clear_canvas(wait_execute=True)
    if background:
        draw_background()
    root.create_image("ProcessBar",-w + w * process,0,w,int(h / 125),wait_execute=True)
    root.create_text(text=score,x=w * 0.99,y=h * 0.01,textBaseline="top",textAlign="right",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 75 / 0.75)}px sans-serif",wait_execute=True)
    if combo_state:
        root.create_text(text=f"{combo}",x=w / 2,y=h * 0.01,textBaseline="top",textAlign="center",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 75 / 0.75)}px sans-serif",wait_execute=True)
        root.create_text(text="Autoplay" if "-combotips" not in argv else argv[argv.index("-combotips") + 1],x=w / 2,y=h * 0.1,textBaseline="bottom",textAlign="center",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 100 / 0.75)}px sans-serif",wait_execute=True)
    root.create_text(text=now_time,x=0,y=h * 0.01,textBaseline="top",textAlign="left",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 175 / 0.75)}px sans-serif",wait_execute=True)
    root.create_text(text=chart_information["Name"],x=w * 0.01,y=h * 0.99,textBaseline="bottom",textAlign="left",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 125 / 0.75)}px sans-serif",wait_execute=True)
    root.create_text(text=chart_information["Level"],x=w * 0.99,y=h * 0.99,textBaseline="bottom",textAlign="right",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 125 / 0.75)}px sans-serif",wait_execute=True)

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

def PlayerStart_Phi():
    print("Player Start")
    root.title("Phigros Chart Player")
    def judgeLine_Animation():
        gr,step_time = Tool_Functions.Get_Animation_Gr(60,0.5)
        val = 0.0
        for step in gr:
            st = time()
            val += step
            draw_ui()
            root.create_line(
                w / 2 - (val * w / 2),h / 2,
                w / 2 + (val * w / 2),h / 2,
                strokeStyle = Get_judgeLine_Color(),
                lineWidth = JUDGELINE_WIDTH,
                wait_execute = True
            )
            root.run_js_wait_code()
            sleep(step_time - min(time() - st,step_time))
        
    judgeLine_Animation()
    
    phigros_chart_obj.init_holdlength(PHIGROS_Y)

    show_start_time = time()
    now_t = 0
    T_dws = {judgeLine_item.__hash__():1.875/judgeLine_item.bpm for judgeLine_item in phigros_chart_obj.judgeLineList}
    judgeLine_Configs = {
        judgeLine_item.__hash__():{
            "judgeLine":judgeLine_item,
            "Rotate":0.0,
            "Disappear":1.0,
            "Pos":[0,0],
            "Speed":1.0,
            "Note_dy":0.0,
            "time":None
        }
        for judgeLine_item in phigros_chart_obj.judgeLineList
    }
    mixer.music.play()
    while not mixer.music.get_busy(): pass
    cal_fps_block_size = 10
    last_cal_fps_time = time()
    time_block_render_count = 0
    while True:
        now_t = time() - show_start_time
        Chart_Functions_Phi.Update_JudgeLine_Configs(judgeLine_Configs,T_dws,now_t)
        root.clear_canvas(wait_execute = True)
        draw_background()

        for judgeLine_cfg_key in judgeLine_Configs:
            judgeLine_cfg = judgeLine_Configs[judgeLine_cfg_key]
            judgeLine:Chart_Objects_Phi.judgeLine = judgeLine_cfg["judgeLine"]
            this_judgeLine_T = T_dws[judgeLine_cfg_key]
            judgeLine_cfg["Note_dy"] = Chart_Functions_Phi.Cal_judgeLine_NoteDy(judgeLine_cfg,this_judgeLine_T)
            judgeLine_DrawPos = (
                *Tool_Functions.rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],5.76 * h),
                *Tool_Functions.rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"] + 180,5.76 * h)
            )
            judgeLine_strokeStyle = (254,255,169,judgeLine_cfg["Disappear"] if not judgeline_notransparent else 1.0)
            if judgeLine_strokeStyle[-1] != 0.0 and show_judgeline and judgeLine_can_render(judgeLine_DrawPos):
                root.create_line(
                    *judgeLine_DrawPos,
                    lineWidth = JUDGELINE_WIDTH,
                    strokeStyle=f"rgba{judgeLine_strokeStyle}",
                    wait_execute = True
                )
            
            def process(notes_list:typing.List[Chart_Objects_Phi.note],t:int):
                for note_item in notes_list:
                    this_noteitem_clicked = note_item.time * this_judgeLine_T < now_t
                    if this_noteitem_clicked and not note_item.clicked:
                        note_item.clicked = True
                        Thread(target=PlaySound.Play,args=(Resource["Note_Click_Audio"][{Const.Note.TAP:"Tap",Const.Note.DRAG:"Drag",Const.Note.HOLD:"Hold",Const.Note.FLICK:"Flick"}[note_item.type]],),daemon=True).start()
                    if note_item.type != Const.Note.HOLD and this_noteitem_clicked:
                        continue
                    elif note_item.type == Const.Note.HOLD and now_t > note_item.hold_endtime:
                        continue
                    cfg = {
                        "note":note_item,
                        "now_floorPosition":note_item.floorPosition * PHIGROS_Y - (judgeLine_cfg["Note_dy"] if not (note_item.type == Const.Note.HOLD and note_item.clicked) else (
                            Chart_Functions_Phi.Cal_judgeLine_NoteDy_ByTime(judgeLine,this_judgeLine_T,note_item.time) + note_item.hold_length_px * (1 - ((note_item.hold_endtime - now_t) / note_item.hold_length_sec))
                        ))
                    }
                    rotatenote_at_judgeLine_pos = Tool_Functions.rotate_point(
                        *judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],note_item.positionX * PHIGROS_X
                    )
                    judgeLine_to_note_rotate_angle = 90 - judgeLine_cfg["Rotate"] - (180 if t == 1 else 0)
                    x,y = Tool_Functions.rotate_point(
                        *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_angle,cfg["now_floorPosition"]
                    )
                    if note_item.type == Const.Note.HOLD:
                        note_hold_draw_length = cfg["now_floorPosition"] + note_item.hold_length_px
                        if note_hold_draw_length >= 0:
                            holdend_x,holdend_y = Tool_Functions.rotate_point(
                                *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_angle,note_hold_draw_length
                            )
                        else:
                            holdend_x,holdend_y = rotatenote_at_judgeLine_pos
                        if cfg["now_floorPosition"] >= 0:
                            holdhead_pos = x,y
                        else:
                            holdhead_pos = rotatenote_at_judgeLine_pos
                        holdbody_range = (
                            Tool_Functions.rotate_point(*holdhead_pos,judgeLine_to_note_rotate_angle - 90,Note_width / 2),
                            Tool_Functions.rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_angle - 90,Note_width / 2),
                            Tool_Functions.rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_angle + 90,Note_width / 2),
                            Tool_Functions.rotate_point(*holdhead_pos,judgeLine_to_note_rotate_angle + 90,Note_width / 2),
                        )
                    note_type = {
                        Const.Note.TAP:"Tap",
                        Const.Note.DRAG:"Drag",
                        Const.Note.HOLD:"Hold",
                        Const.Note.FLICK:"Flick"
                    }[note_item.type]
                    if (
                        Note_CanRender(x,y)
                        if note_item.type != Const.Note.HOLD
                        else Note_CanRender(x,y,holdbody_range)
                    ):
                        judgeLine_rotate_integer = - int(judgeLine_cfg["Rotate"]) % 360
                        if note_item.type != Const.Note.HOLD:
                            this_note_img = Resource["Notes"][note_type + ("_dub" if note_item.morebets else "")]
                            this_note_imgname = f"Note_{note_type}" + ("_dub" if note_item.morebets else "")
                        else:
                            this_note_img = Resource["Notes"]["Hold"][note_type + "_Head" + ("_dub" if note_item.morebets else "")]
                            this_note_imgname = f"Note_{note_type}" + "_Head" + ("_dub" if note_item.morebets else "")
                            this_note_img_end = Resource["Notes"]["Hold"][note_type + "_End"]
                            this_note_imgname_end = f"Note_{note_type}" + "_End"
                        if note_item.type == Const.Note.HOLD:
                            root.create_polygon(
                                points=holdbody_range,
                                fillStyle="#0078d7",
                                strokeStyle="#00000000",
                                wait_execute = True
                            )
                            root.run_js_code(
                                f"ctx.drawRotateImage(\
                                    {root.get_img_jsvarname(this_note_imgname_end)},\
                                    {holdend_x},\
                                    {holdend_y},\
                                    {this_note_img_end.width},\
                                    {this_note_img_end.height},\
                                    {judgeLine_rotate_integer}\
                                );",
                                add_code_array = True
                            )
                        if not (note_item.type == Const.Note.HOLD and note_item.time * this_judgeLine_T < now_t):
                            root.run_js_code( #more about this function at js define CanvasRenderingContext2D.prototype.drawRotateImage
                                f"ctx.drawRotateImage(\
                                    {root.get_img_jsvarname(this_note_imgname)},\
                                    {x},\
                                    {y},\
                                    {this_note_img.width},\
                                    {this_note_img.height},\
                                    {judgeLine_rotate_integer}\
                                );",
                                add_code_array = True #eq wait_exec true
                            )
                        note_item.rendered = True
            process(judgeLine.notesAbove,1)
            process(judgeLine.notesBelow,-1)

        effect_time = 0.5
        for judgeLine in phigros_chart_obj.judgeLineList:
            T = 1.875 / judgeLine.bpm
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                note_time = note.time * T
                if note_time <= now_t:
                    
                    def process(et,t,effect_random_blocks):
                        effect_process = (now_t - et) / effect_time
                        effect_img_lst = Resource["Note_Click_Effect"]["Perfect"]
                        effect_img_index = int(effect_process * (len(effect_img_lst) - 1))
                        effect_img = effect_img_lst[effect_img_index]
                        effect_imgname = f"Note_Click_Effect_Perfect_{effect_img_index + 1}"
                        will_show_effect_pos = judgeLine.get_datavar_move(t,w,h)
                        will_show_effect_rotate = judgeLine.get_datavar_rotate(t)
                        if Chart_Functions_Phi.is_nan(will_show_effect_pos): will_show_effect_pos = judgeLine_cfg["Pos"]
                        if Chart_Functions_Phi.is_nan(will_show_effect_rotate): will_show_effect_rotate = judgeLine_cfg["Rotate"]
                        effect_pos = Tool_Functions.rotate_point(*will_show_effect_pos,-will_show_effect_rotate,note.positionX * PHIGROS_X)
                        root.create_image(
                            effect_imgname,
                            effect_pos[0] - effect_img.width / 2,
                            effect_pos[1] - effect_img.height / 2,
                            effect_img.width,effect_img.height,
                            wait_execute = True
                        )
                        if clickeffect_randomblock:
                            for index,random_deg in enumerate(effect_random_blocks):
                                effect_random_point = Tool_Functions.rotate_point(
                                    *effect_pos,random_deg + index * 90,
                                    ClickEffect_Size * Tool_Functions.ease_out(effect_process) / 1.3
                                )
                                root.create_rectangle(
                                    effect_random_point[0] - EFFECT_RANDOM_BLOCK_SIZE,
                                    effect_random_point[1] - EFFECT_RANDOM_BLOCK_SIZE,
                                    effect_random_point[0] + EFFECT_RANDOM_BLOCK_SIZE,
                                    effect_random_point[1] + EFFECT_RANDOM_BLOCK_SIZE,
                                    fillStyle = f"rgb{(254,255,169,1.0 - effect_process)}",
                                    wait_execute = True
                                )
                                
                    if now_t - note_time <= effect_time:
                        process(note_time,note.time,note.effect_random_blocks)
                    
                    if note.type == Const.Note.HOLD:
                        if note.hold_endtime + effect_time >= now_t:
                            for temp_time,hold_effect_random_blocks in note.effect_times:
                                if temp_time < now_t:
                                    if now_t - temp_time <= effect_time:
                                        process(temp_time,temp_time / T,hold_effect_random_blocks)

        combo = Chart_Functions_Phi.Cal_Combo(now_t)
        time_text = f"{Format_Time(now_t)}/{Format_Time(audio_length)}"
        draw_ui(
            process=now_t / audio_length,
            score=get_stringscore(combo * (1000000 / phigros_chart_obj.note_num)),
            combo_state=combo >= 3,
            combo=combo,
            now_time=time_text,
            clear=False,
            background=False
        )
        if not mixer.music.get_busy():
            break
        root.run_js_wait_code()
        time_block_render_count += 1
        this_music_pos = mixer.music.get_pos() % (audio_length * 1000)
        offset_judge_range = 66.666667 #ms
        if abs(music_offset := this_music_pos - (time() - show_start_time) * 1000) >= offset_judge_range:
            show_start_time -= music_offset / 1000
            loger_queue.put(f"Warning: mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset)}ms)")
        if time_block_render_count >= cal_fps_block_size:
            if "-showfps" in argv:
                try:
                    root.title(f"Phigros Chart Player - FPS: {(time_block_render_count / (time() - last_cal_fps_time)) : .2f}")
                except ZeroDivisionError:
                    root.title(f"Phigros Chart Player - FPS: inf")
            last_cal_fps_time,time_block_render_count = time(),0
    if loop:
        PlayerStart_Phi()
    else:
        root.destroy()

def PlayerStart_Rep():
    raise NotImplementedError

    print("Player Start")
    root.title("Phigros Chart Player")
    def judgeLine_Animation():
        gr,step_time = Tool_Functions.Get_Animation_Gr(60,0.5)
        val = 0.0
        for step in gr:
            st = time()
            val += step
            draw_ui()
            root.create_line(
                w / 2 - (val * w / 2),h / 2,
                w / 2 + (val * w / 2),h / 2,
                strokeStyle = Get_judgeLine_Color(),
                lineWidth = JUDGELINE_WIDTH,
                wait_execute = True
            )
            root.run_js_wait_code()
            sleep(step_time - min(time() - st,step_time))
    judgeLine_Animation()
    
    show_start_time = time()
    now_t = 0
    mixer.music.play()
    while not mixer.music.get_busy(): pass
    cal_fps_block_size = 10
    last_cal_fps_time = time()
    time_block_render_count = 0
    while True:
        now_t = time() - show_start_time
        root.clear_canvas(wait_execute = True)
        draw_background()
        
        fd = Chart_Functions_Rep.Get_FrameData(rep_chart_obj,now_t,Note_CanRender)
        
        for JudgeLine_Data in fd.JudgeLine_Data:
            judgeLine_strokeStyle = (254,255,169,JudgeLine_Data.EventLayer_Data.alphaValue if not judgeline_notransparent else 1.0)
            if judgeLine_strokeStyle[-1] != 0.0:
                root.create_line(
                    *JudgeLine_Data.draw_pos,
                    lineWidth = JUDGELINE_WIDTH,
                    strokeStyle=f"rgba{judgeLine_strokeStyle}",
                    wait_execute = True
                )
        
        for Note_Data in fd.Note_Data:
            root.create_image(
                Note_Data.imname,
                Note_Data.x - Note_Data.im.width / 2,Note_Data.y - Note_Data.im.height / 2,
                Note_Data.im.width,Note_Data.im.height,
                wait_execute = True
            )
        
        # combo = Chart_Functions_Rep.Cal_Combo(now_t)
        combo = 0
        time_text = f"{Format_Time(now_t)}/{Format_Time(audio_length)}"
        draw_ui(
            process=now_t / audio_length,
            score=get_stringscore(combo * (1000000 / rep_chart_obj.numOfNotes)),
            combo_state=combo >= 3,
            combo=combo,
            now_time=time_text,
            clear=False,
            background=False
        )
        if not mixer.music.get_busy():
            break
        root.run_js_wait_code()
        time_block_render_count += 1
        this_music_pos = mixer.music.get_pos() % (audio_length * 1000)
        offset_judge_range = 66.666667 #ms
        if abs(music_offset := this_music_pos - (time() - show_start_time) * 1000) >= offset_judge_range:
            show_start_time -= music_offset / 1000
            loger_queue.put(f"Warning: mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset)}ms)")
        if time_block_render_count >= cal_fps_block_size:
            if "-showfps" in argv:
                try:
                    root.title(f"Phigros Chart Player - FPS: {(time_block_render_count / (time() - last_cal_fps_time)) : .2f}")
                except ZeroDivisionError:
                    root.title(f"Phigros Chart Player - FPS: inf")
            last_cal_fps_time,time_block_render_count = time(),0
    root.destroy()

def Re_Init():
    match CHART_TYPE:
        case Const.CHART_TYPE.PHI:
            (
                Chart_Functions_Phi.w,
                Chart_Functions_Phi.h,
                Chart_Functions_Phi.PHIGROS_X,
                Chart_Functions_Phi.PHIGROS_Y
            ) = w,h,PHIGROS_X,PHIGROS_Y
            phigros_chart_obj.init_holdlength(PHIGROS_Y)
        case Const.CHART_TYPE.REP:
            (
                Chart_Functions_Rep.w,
                Chart_Functions_Rep.h
            ) = w,h

print("Loading Window...")
# root.iconbitmap(".\\icon.ico")
root = web_canvas.WebCanvas(
    width=1,height=1,
    x=0,y=0,
    title="Phigros Chart Player",
    debug="-debug" in argv
)
if hidemouse:
    root.run_js_code("hide_mouse();")
root.reg_event("closed",remove_font)
if "-fullscreen" in argv:
    w,h = root.winfo_screenwidth(),root.winfo_screenheight()
    root._web.toggle_fullscreen()
else:
    w,h = int(root.winfo_screenwidth() * 0.61803398874989484820458683436564),int(root.winfo_screenheight() * 0.61803398874989484820458683436564)
    root.resize(w,h)
    w_legacy,h_legacy = root.winfo_legacywindowwidth(),root.winfo_legacywindowheight()
    dw_legacy,dh_legacy = w - w_legacy,h - h_legacy
    del w_legacy,h_legacy
    root.resize(w + dw_legacy,h + dh_legacy)
    root.move(int(root.winfo_screenwidth() / 2 - (w + dw_legacy) / 2),int(root.winfo_screenheight() / 2 - (h + dh_legacy) / 2))
print("Creating Canvas...")
root.reg_event("resized",lambda *args,**kwargs:exec("global w,h,PHIGROS_X,PHIGROS_Y; args = list(args); args[0] -= dw_legacy; args[1] -= dh_legacy; w,h = args; PHIGROS_X,PHIGROS_Y = 0.05625 * w,0.6 * h; Re_Init()"))
background_image = ImageEnhance.Brightness(chart_image.resize((w,h)).filter(ImageFilter.GaussianBlur((w + h) / 300))).enhance(1.0 - chart_information["BackgroundDim"])
root.reg_img(background_image,"background")
PHIGROS_X,PHIGROS_Y = 0.05625 * w,0.6 * h
JUDGELINE_WIDTH = h * 0.0075
EFFECT_RANDOM_BLOCK_SIZE = h * 0.013
window_hwnd = root.winfo_hwnd()
print(f"Window Hwnd: {window_hwnd}")
window_style = GetWindowLong(window_hwnd,win32con.GWL_STYLE)
SetWindowLong(window_hwnd,win32con.GWL_STYLE,window_style & ~win32con.WS_SYSMENU) ; del window_style
Resource = Load_Resource()
match CHART_TYPE:
    case Const.CHART_TYPE.PHI:
        Chart_Functions_Phi.Init(
            phigros_chart_obj_ = phigros_chart_obj,
            PHIGROS_X_ = PHIGROS_X,PHIGROS_Y_ = PHIGROS_Y,
            w_ = w,h_ = h
        )
    case Const.CHART_TYPE.REP:
        Chart_Functions_Rep.Init(
            w_ = w,h_ = h,
            Resource_ = Resource
        )
Thread(target=Show_Start,daemon=True).start()
Thread(target=loger,daemon=True).start()
root.loop_to_close()
windll.kernel32.ExitProcess(0)