from tkinter import Tk,Canvas
from threading import Thread
from ctypes import windll
from os import chdir,environ,listdir,popen ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from os.path import exists,abspath,dirname
from sys import argv
from time import time,sleep
from math import cos,sin,radians,pi
from json import loads
from queue import Queue
from shutil import rmtree
from tempfile import gettempdir
import typing
import csv

from PIL import Image,ImageTk,ImageDraw,ImageFilter,ImageEnhance
from win32gui import GetWindowLong,SetWindowLong,SetParent
from pygame import mixer
import win32con
import win32ui

import Chart_Objects
import Const
import Find_Files
import PlaySound
import ConsoleWindow
import psm
import web_canvas


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

if "-clear" in argv:
    windll.kernel32.ExitProcess(0)

debug = "-debug" in argv
show_holdbody = "-holdbody" in argv
show_judgeline = "-nojudgeline" not in argv
debug_noshow_transparent_judgeline = "-debug-noshow-transparent-judgeline" in argv

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
mixer.music.set_volume(0.5)

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
    print("No Image File Found.")
    windll.kernel32.ExitProcess(1)
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
print("Loading Chart Information Successfully.")
print("Inforamtions: ")
print("              Name:",chart_information["Name"])
print("              Artist:",chart_information["Artist"])
print("              Level:",chart_information["Level"])
print("              Charter:",chart_information["Charter"])
print("              BackgroundDim:",chart_information["BackgroundDim"])

del chart_files,chart_files_dict

def Get_Animation_Gr(fps:float,t:float):
    gr_x = int(fps * t) + 1
    gr = [cos(x / gr_x) + 1 for x in range(int(gr_x * pi))]
    gr_sum = sum(gr)
    step_time = t / len(gr)
    return [item / gr_sum for item in gr],step_time

def rotate_point(x,y,θ,r):
    xo = r * cos(radians(θ))
    yo = r * sin(radians(θ))
    return x + xo,y + yo

def Get_A_New_NoteId_By_judgeLine(judgeLine_item:dict):
    if "_note_count" not in judgeLine_item:
        judgeLine_item["_note_count"] = 1
    else:
        judgeLine_item["_note_count"] += 1
    return judgeLine_item["_note_count"] - 1

def Get_A_New_NoteId():
    global note_id
    note_id += 1
    return note_id

def loger():
    while True:
        while not loger_queue.empty():
            print(loger_queue.get())
        sleep(0.01)

def unpack_pos(number:int) -> tuple[int,int]:
    return (number - number % 1000) // 1000,number % 1000

def is_nan(x) -> bool:
    return x != x

def is_will_process_char(char:str) -> bool:
    if len(char) != 1: return False
    if ord("a") <= ord(char.lower()) <= ord("z"): return True
    return False

loger_queue = Queue()
clickeffect_cache = []
note_id = -1

def Load_Chart_Object():
    global phigros_chart_obj
    print("Loading Chart Object...")
    phigros_chart_obj = Chart_Objects.Phigros_Chart(
        formatVersion=phigros_chart["formatVersion"],
        offset=phigros_chart["offset"],
        judgeLineList=[
            Chart_Objects.judgeLine(
                id=index,
                bpm=judgeLine_item["bpm"],
                notesAbove=[
                    Chart_Objects.note(
                        type=notesAbove_item["type"],
                        time=notesAbove_item["time"],
                        positionX=notesAbove_item["positionX"],
                        holdTime=notesAbove_item["holdTime"],
                        speed=notesAbove_item["speed"],
                        floorPosition=notesAbove_item["floorPosition"],
                        clicked=False,
                        morebets=False,
                        id=Get_A_New_NoteId(),
                        by_judgeLine_id=Get_A_New_NoteId_By_judgeLine(judgeLine_item),
                        rendered=False
                    )
                    for notesAbove_item in judgeLine_item["notesAbove"]
                ],
                notesBelow=[
                    Chart_Objects.note(
                        type=notesBelow_item["type"],
                        time=notesBelow_item["time"],
                        positionX=notesBelow_item["positionX"],
                        holdTime=notesBelow_item["holdTime"],
                        speed=notesBelow_item["speed"],
                        floorPosition=notesBelow_item["floorPosition"],
                        clicked=False,
                        morebets=False,
                        id=Get_A_New_NoteId(),
                        by_judgeLine_id=Get_A_New_NoteId_By_judgeLine(judgeLine_item),
                        rendered=False
                    )
                    for notesBelow_item in judgeLine_item["notesBelow"]
                ],
                speedEvents=[
                    Chart_Objects.speedEvent(
                        startTime=speedEvent_item["startTime"],
                        endTime=speedEvent_item["endTime"],
                        value=speedEvent_item["value"],
                        floorPosition=speedEvent_item["floorPosition"] if "floorPosition" in speedEvent_item else None
                    )
                    for speedEvent_item in judgeLine_item["speedEvents"]
                ],
                judgeLineMoveEvents=[
                    Chart_Objects.judgeLineMoveEvent(
                        startTime=judgeLineMoveEvent_item["startTime"],
                        endTime=judgeLineMoveEvent_item["endTime"],
                        start=judgeLineMoveEvent_item["start"],
                        end=judgeLineMoveEvent_item["end"],
                        start2=judgeLineMoveEvent_item["start2"],
                        end2=judgeLineMoveEvent_item["end2"]
                    )
                    for judgeLineMoveEvent_item in judgeLine_item["judgeLineMoveEvents"]
                ] if len(judgeLine_item["judgeLineMoveEvents"]) > 0 and "start2" in judgeLine_item["judgeLineMoveEvents"][0] and "end2" in judgeLine_item["judgeLineMoveEvents"][0] else [
                    Chart_Objects.judgeLineMoveEvent(
                        startTime=judgeLineMoveEvent_item["startTime"],
                        endTime=judgeLineMoveEvent_item["endTime"],
                        start=unpack_pos(judgeLineMoveEvent_item["start"])[0] / 880,
                        end=unpack_pos(judgeLineMoveEvent_item["end"])[0] / 880,
                        start2=unpack_pos(judgeLineMoveEvent_item["start"])[1] / 520,
                        end2=unpack_pos(judgeLineMoveEvent_item["end"])[1] / 520
                    )
                    for judgeLineMoveEvent_item in judgeLine_item["judgeLineMoveEvents"]
                ],
                judgeLineRotateEvents=[
                    Chart_Objects.judgeLineRotateEvent(
                        startTime=judgeLineRotateEvent_item["startTime"],
                        endTime=judgeLineRotateEvent_item["endTime"],
                        start=judgeLineRotateEvent_item["start"],
                        end=judgeLineRotateEvent_item["end"]
                    )
                    for judgeLineRotateEvent_item in judgeLine_item["judgeLineRotateEvents"]
                ],
                judgeLineDisappearEvents=[
                    Chart_Objects.judgeLineDisappearEvent(
                        startTime=judgeLineDisappearEvent_item["startTime"],
                        endTime=judgeLineDisappearEvent_item["endTime"],
                        start=judgeLineDisappearEvent_item["start"],
                        end=judgeLineDisappearEvent_item["end"]
                    )
                    for judgeLineDisappearEvent_item in judgeLine_item["judgeLineDisappearEvents"]
                ]
            )
            for index,judgeLine_item in enumerate(phigros_chart["judgeLineList"])
        ]
    )
    for judgeLine in phigros_chart_obj.judgeLineList:
        judgeLine.set_master_to_notes()
    phigros_chart_obj.cal_note_num()
    print("Finding Chart More Bets...")
    notes = []
    for judgeLine in phigros_chart_obj.judgeLineList:
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            notes.append(note)
    note_times = {}
    for note in notes:
        note:Chart_Objects.note
        if note.time not in note_times:
            note_times[note.time] = 1
        else:
            note_times[note.time] += 1
    for note in notes:
        if note_times[note.time] > 1:
            note.morebets = True
    del notes,note_times
    print("Load Chart Object Successfully.")

Load_Chart_Object()

def rotate_image(im:Image.Image,angle:float) -> Image.Image:
    imsize = int((im.width ** 2 + im.height ** 2) ** 0.5) + 1
    new_im = Image.new("RGBA",(imsize,)*2,(0,0,0,0))
    new_im.paste(im,(
        int(imsize / 2 - im.width / 2),
        int(imsize / 2 - im.height / 2)
    ))
    return new_im.rotate(angle)

def get_all_angle_img(im:Image.Image,w:int,h:int) -> dict[int,Image.Image]:
    return {
        angle:rotate_image(im,angle).resize((int((w ** 2 + h ** 2) ** 0.5),)*2) for angle in range(0,360)
    }

def Load_Resource():
    global ClickEffect_Size,Note_width
    print("Loading Resource...")
    Note_width = int(PHIGROS_X * 1.5)
    Note_height_Tap = int(Note_width / 989 * 100)
    Note_height_Tap_dub = int(Note_width / 1089 * 200)
    Note_height_Drag = int(Note_width / 989 * 60)
    Note_height_Drag_dub = int(Note_width / 1089 * 160)
    Note_height_Flick = int(Note_width / 989 * 200)
    Note_height_Flick_dub = int(Note_width / 1089 * 300)
    Note_height_Hold_Head = int(Note_width / 989 * 50)
    Note_height_Hold_Head_dub = int(Note_width / 1058 * 97)
    Note_height_Hold_End = int(Note_width / 989 * 50)
    ClickEffect_Size = int(Note_width*1.5)
    Resource = {
        "Notes_Base":{
            "Tap":Image.open("./Resources/Notes/Tap.png"),
            "Tap_dub":Image.open("./Resources/Notes/Tap_dub.png"),
            "Drag":Image.open("./Resources/Notes/Drag.png"),
            "Drag_dub":Image.open("./Resources/Notes/Drag_dub.png"),
            "Flick":Image.open("./Resources/Notes/Flick.png"),
            "Flick_dub":Image.open("./Resources/Notes/Flick_dub.png"),
            "Hold":{
                "Hold_Head":Image.open("./Resources/Notes/Hold_Head.png"),
                "Hold_Head_dub":Image.open("./Resources/Notes/Hold_Head_dub.png"),
                "Hold_End":Image.open("./Resources/Notes/Hold_End.png")
            }
        },
        "Note_Click_Effect":{
            "Perfect":[
                Image.open(f"./Resources/Note_Click_Effect/Perfect/{i}.png").resize((ClickEffect_Size,)*2)
                for i in range(1,31)
            ],
            "Good":[
                Image.open(f"./Resources/Note_Click_Effect/Good/{i}.png").resize((ClickEffect_Size,)*2)
                for i in range(1,31)
            ]
        },
        "Note_Click_Audio":{
            "1":open("./Resources/Note_Click_Audio/Tap.wav","rb").read(),
            "2":open("./Resources/Note_Click_Audio/Drag.wav","rb").read(),
            "3":open("./Resources/Note_Click_Audio/Hold.wav","rb").read(),
            "4":open("./Resources/Note_Click_Audio/Flick.wav","rb").read()
        },
        "ProcessBar":Image.new("RGB",(w,int(h / 125)),(145,)*3),
        "Start":Image.open("./Resources/Start.png").resize((w,h))
    }
    res_note_base_small_x = 4
    print("Loading Resource - resize note ...")
    Resource["Notes_Base"] = {
        "Tap":Resource["Notes_Base"]["Tap"].resize((int(Resource["Notes_Base"]["Tap"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Tap"].height / res_note_base_small_x))),
        "Tap_dub":Resource["Notes_Base"]["Tap_dub"].resize((int(Resource["Notes_Base"]["Tap_dub"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Tap_dub"].height / res_note_base_small_x))),
        "Drag":Resource["Notes_Base"]["Drag"].resize((int(Resource["Notes_Base"]["Drag"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Drag"].height / res_note_base_small_x))),
        "Drag_dub":Resource["Notes_Base"]["Drag_dub"].resize((int(Resource["Notes_Base"]["Drag_dub"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Drag_dub"].height / res_note_base_small_x))),
        "Flick":Resource["Notes_Base"]["Flick"].resize((int(Resource["Notes_Base"]["Flick"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Flick"].height / res_note_base_small_x))),
        "Flick_dub":Resource["Notes_Base"]["Flick_dub"].resize((int(Resource["Notes_Base"]["Flick_dub"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Flick_dub"].height / res_note_base_small_x))),
        "Hold":{
            "Hold_Head":Resource["Notes_Base"]["Hold"]["Hold_Head"].resize((int(Resource["Notes_Base"]["Hold"]["Hold_Head"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Hold"]["Hold_Head"].height / res_note_base_small_x))),
            "Hold_Head_dub":Resource["Notes_Base"]["Hold"]["Hold_Head_dub"].resize((int(Resource["Notes_Base"]["Hold"]["Hold_Head_dub"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Hold"]["Hold_Head_dub"].height / res_note_base_small_x))),
            "Hold_End":Resource["Notes_Base"]["Hold"]["Hold_End"].resize((int(Resource["Notes_Base"]["Hold"]["Hold_End"].width / res_note_base_small_x),int(Resource["Notes_Base"]["Hold"]["Hold_End"].height / res_note_base_small_x)))
        }
    }
    print("Loading Resource - rotate note ...")
    Resource["Notes"] = {
        "Tap":get_all_angle_img(Resource["Notes_Base"]["Tap"],Note_width,Note_height_Tap),
        "Tap_dub":get_all_angle_img(Resource["Notes_Base"]["Tap_dub"],Note_width,Note_height_Tap_dub),
        "Drag":get_all_angle_img(Resource["Notes_Base"]["Drag"],Note_width,Note_height_Drag),
        "Drag_dub":get_all_angle_img(Resource["Notes_Base"]["Drag_dub"],Note_width,Note_height_Drag_dub),
        "Flick":get_all_angle_img(Resource["Notes_Base"]["Flick"],Note_width,Note_height_Flick),
        "Flick_dub":get_all_angle_img(Resource["Notes_Base"]["Flick_dub"],Note_width,Note_height_Flick_dub),
        "Hold":{
            "Hold_Head":get_all_angle_img(Resource["Notes_Base"]["Hold"]["Hold_Head"],Note_width,Note_height_Hold_Head),
            "Hold_Head_dub":get_all_angle_img(Resource["Notes_Base"]["Hold"]["Hold_Head_dub"],Note_width,Note_height_Hold_Head_dub),
            "Hold_End":get_all_angle_img(Resource["Notes_Base"]["Hold"]["Hold_End"],Note_width,Note_height_Hold_End)
        }
    }
    print("Loading Resource - create processbar ...")
    ImageDraw.Draw(Resource["ProcessBar"]).rectangle((w * 0.998,0,w,int(h / 125)),fill=(255,)*3)
    Resource["ProcessBar"] = Resource["ProcessBar"]
    for i in range(0,360):
        root.reg_img(Resource["Notes"]["Tap"][i],f"Note_Tap_{i}")
        root.reg_img(Resource["Notes"]["Tap_dub"][i],f"Note_Tap_dub_{i}")
        root.reg_img(Resource["Notes"]["Drag"][i],f"Note_Drag_{i}")
        root.reg_img(Resource["Notes"]["Drag_dub"][i],f"Note_Drag_dub_{i}")
        root.reg_img(Resource["Notes"]["Flick"][i],f"Note_Flick_{i}")
        root.reg_img(Resource["Notes"]["Flick_dub"][i],f"Note_Flick_dub_{i}")
        root.reg_img(Resource["Notes"]["Hold"]["Hold_Head"][i],f"Note_Hold_Head_{i}")
        root.reg_img(Resource["Notes"]["Hold"]["Hold_Head_dub"][i],f"Note_Hold_Head_dub_{i}")
        root.reg_img(Resource["Notes"]["Hold"]["Hold_End"][i],f"Note_Hold_End_{i}")
    for i in range(30):
        root.reg_img(Resource["Note_Click_Effect"]["Perfect"][i],f"Note_Click_Effect_Perfect_{i + 1}")
        root.reg_img(Resource["Note_Click_Effect"]["Good"][i],f"Note_Click_Effect_Good_{i + 1}")
    root.reg_img(Resource["ProcessBar"],"ProcessBar")
    root.reg_img(Resource["Start"],"Start")
    root.load_allimg()
    print("Loading Resource Successfully.")
    # if not hidemouse: root.configure(cursor="arrow")
    # if not hidemouse: show_start.configure(cursor="arrow")
    root.deiconify()
    return Resource

def Update_JudgeLine_Configs(judgeLine_Configs,T_dws,now_t:typing.Union[int,float]):
    for judgeLine_cfg_key in judgeLine_Configs:
        judgeLine_cfg = judgeLine_Configs[judgeLine_cfg_key]
        judgeLine_cfg["time"] = now_t / T_dws[judgeLine_cfg_key]
        judgeLine:Chart_Objects.judgeLine = judgeLine_cfg["judgeLine"]
        rotate_var = judgeLine.get_datavar_rotate(judgeLine_cfg["time"])
        disappear_var = judgeLine.get_datavar_disappear(judgeLine_cfg["time"])
        move_var = judgeLine.get_datavar_move(judgeLine_cfg["time"],w,h)
        speed_var = judgeLine.get_datavar_speed(judgeLine_cfg["time"])
        if not is_nan(rotate_var): judgeLine_cfg["Rotate"] = rotate_var
        if not is_nan(disappear_var): judgeLine_cfg["Disappear"] = disappear_var
        if not is_nan(move_var): judgeLine_cfg["Pos"] = move_var
        if not is_nan(speed_var): judgeLine_cfg["Speed"] = speed_var

def Format_Time(t:typing.Union[int,float]) -> str:
    m,s = t // 60,t % 60
    m,s = int(m),int(s)
    return f"{m}:{s:>2}".replace(" ","0")

def Cal_judgeLine_NoteDy(judgeLine_cfg,T:float) -> float:
    judgeLine:Chart_Objects.judgeLine = judgeLine_cfg["judgeLine"]
    if judgeLine.speedEvents == []: return 0
    return Cal_judgeLine_NoteDy_ByTime(judgeLine,T,judgeLine_cfg["time"])

def Cal_judgeLine_NoteDy_ByTime(judgeLine:Chart_Objects.judgeLine,T:float,time:float) -> float:
    dy = 0
    if judgeLine.speedEvents[0].floorPosition is not None:
        for speed_event in judgeLine.speedEvents:
            if speed_event.startTime <= time <= speed_event.endTime:
                dy = speed_event.floorPosition * PHIGROS_Y + (
                    time - speed_event.startTime
                ) * T * speed_event.value * PHIGROS_Y
                return dy
        last_speed_event = sorted(judgeLine.speedEvents,key=lambda x:x.startTime)[-1]
        dy = last_speed_event.floorPosition * PHIGROS_Y + (time - last_speed_event.endTime) * T * last_speed_event.value * PHIGROS_Y
        return dy
    else:
        for speed_event in judgeLine.speedEvents:
            if speed_event.startTime < time and speed_event.endTime < time:
                dy += (speed_event.endTime - speed_event.startTime) * T * speed_event.value * PHIGROS_Y
            elif speed_event.startTime <= time <= speed_event.endTime:
                dy += (time - speed_event.startTime) * T * speed_event.value * PHIGROS_Y
            else:
                pass
        return dy

def Get_judgeLine_Color() -> str:
    return score_manager.get_judgeLine_color()

def Show_Start():
    global res_start_tk
    res_start_tk = ImageTk.PhotoImage(Resource["Start"])
    show_start.overrideredirect(True)
    show_start_cv = Canvas(show_start,width=w,height=h,bg="white",highlightthickness=0)
    show_start_cv.create_image(0,0,image=res_start_tk,anchor="nw")
    show_start_cv.pack()
    show_start.update()
    show_start_hwnd = int(show_start.frame(),16)
    Style = GetWindowLong(show_start_hwnd,win32con.GWL_STYLE)
    Style = Style &~win32con.WS_CAPTION &~win32con.WS_SYSMENU &~win32con.WS_SIZEBOX | win32con.WS_CHILD
    SetWindowLong(show_start_hwnd,win32con.GWL_STYLE,Style) ; del Style
    SetParent(show_start_hwnd,window_hwnd)
    show_start.geometry("+0+0")
    gr,step_time = Get_Animation_Gr(60,1.25)
    alpha = 0.0
    for step in gr:
        alpha += step
        show_start.attributes("-alpha",alpha)
        sleep(step_time)
    draw_background()
    draw_ui()
    root.run_js_wait_code()
    sleep(0.5)
    for step in gr:
        alpha -= step
        show_start.attributes("-alpha",alpha)
        sleep(step_time)
    def _f():
        SetParent(show_start_hwnd,0)
        show_start.destroy()
    Thread(target=_f,daemon=True).start()
    Thread(target=PlayerStart,daemon=True).start()

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
    root.create_image("ProcessBar",-w + w * process,0,Resource["ProcessBar"].width,Resource["ProcessBar"].height,wait_execute=True)
    root.create_text(text=score,x=w * 0.99,y=h * 0.01,textBaseline="top",textAlign="right",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 75 / 0.75)}px sans-serif",wait_execute=True)
    if combo_state:
        root.create_text(text=f"{combo}",x=w / 2,y=h * 0.01,textBaseline="top",textAlign="center",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 75 / 0.75)}px sans-serif",wait_execute=True)
        root.create_text(text="Autoplay" if "-combotips" not in argv else argv[argv.index("-combotips") + 1],x=w / 2,y=h * 0.1,textBaseline="bottom",textAlign="center",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 100 / 0.75)}px sans-serif",wait_execute=True)
    root.create_text(text=now_time,x=0,y=h * 0.01,textBaseline="top",textAlign="left",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 175 / 0.75)}px sans-serif",wait_execute=True)
    root.create_text(text=chart_information["Name"],x=w * 0.01,y=h * 0.99,textBaseline="bottom",textAlign="left",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 125 / 0.75)}px sans-serif",wait_execute=True)
    root.create_text(text=chart_information["Level"],x=w * 0.99,y=h * 0.99,textBaseline="bottom",textAlign="right",strokeStyle="white",fillStyle="white",font=f"{int((w + h) / 125 / 0.75)}px sans-serif",wait_execute=True)

def draw_background():
    root.create_image("background",0,0,w,h,wait_execute=True)

def Cal_Combo(now_time:float) -> int:
    combo = 0
    for judgeLine in phigros_chart_obj.judgeLineList:
        T = 1.875 / judgeLine.bpm
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            if note.time * T <= now_time and note.type != Const.Note.HOLD:
                combo += 1
            elif note.type == Const.Note.HOLD and note.hold_endtime <= now_time:
                combo += 1
    return combo

def PlayerStart(again:bool=False,again_window:typing.Union[None,Tk]=None):
    global score_manager
    print("Player Start")
    root.title("Phigros Chart Player")
    score_manager = psm.Manager(phigros_chart_obj.note_num)
    def judgeLine_Animation():
        gr,step_time = Get_Animation_Gr(60,0.5)
        val = 0.0
        for step in gr:
            st = time()
            val += step
            draw_ui()
            root.create_line(
                w / 2 - (val * w / 2),h / 2,
                w / 2 + (val * w / 2),h / 2,
                strokeStyle=Get_judgeLine_Color(),
                lineWidth=h * 0.0075,
                wait_execute=True
            )
            root.run_js_wait_code()
            sleep(step_time - min(time() - st,step_time))
    if again:
        again_window.overrideredirect(True)
        again_window.update()
        again_toplevel_hwnd = int(again_window.frame(),16)
        Style = GetWindowLong(again_toplevel_hwnd,win32con.GWL_STYLE)
        Style = Style &~win32con.WS_CAPTION &~win32con.WS_SYSMENU &~win32con.WS_SIZEBOX | win32con.WS_CHILD
        SetWindowLong(again_toplevel_hwnd,win32con.GWL_STYLE,Style) ; del Style
        SetParent(again_toplevel_hwnd,window_hwnd)
        again_window.geometry("+0+0")
        again_window.deiconify()
        root.focus_force()
        gr,step_time = Get_Animation_Gr(60,0.75)
        alpha = 0.0
        for step in gr:
            alpha += step
            again_window.attributes("-alpha",alpha)
            sleep(step_time)
        root.clear_canvas()
        sleep(0.2)
        Thread(target=judgeLine_Animation,daemon=True).start()
        for step in gr:
            alpha -= step
            again_window.attributes("-alpha",alpha)
            sleep(step_time)
        again_window.destroy()
    else:
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
    fps = 60
    cal_fps_block_size = fps / 15 if fps != float("inf") else 60 / 15
    last_cal_fps_time = time()
    time_block_render_count = 0
    while True:
        st = time()
        now_t = time() - show_start_time
        Update_JudgeLine_Configs(judgeLine_Configs,T_dws,now_t)
        root.clear_canvas(wait_execute=True)
        draw_background()

        for judgeLine_cfg_key in judgeLine_Configs:
            judgeLine_cfg = judgeLine_Configs[judgeLine_cfg_key]
            judgeLine:Chart_Objects.judgeLine = judgeLine_cfg["judgeLine"]
            this_judgeLine_T = T_dws[judgeLine_cfg_key]
            judgeLine_cfg["Note_dy"] = Cal_judgeLine_NoteDy(judgeLine_cfg,this_judgeLine_T)
            judgeLine_DrawPos = [
                *rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],5.76 * h),
                *rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"] + 180,5.76 * h)
            ]
            judgeLine_strokeStyle = (254,255,169,judgeLine_cfg["Disappear"])
            root.create_line(
                *judgeLine_DrawPos,
                lineWidth = h * 0.0075,
                strokeStyle=f"rgba{judgeLine_strokeStyle}",
                wait_execute = True
            )
            
            def process(notes_list:list[Chart_Objects.note],t:int):
                for note_item in notes_list:
                    this_noteitem_clicked = note_item.time * this_judgeLine_T < now_t
                    if this_noteitem_clicked and not note_item.clicked:
                        note_item.clicked = True
                        Thread(target=PlaySound.Play,args=(Resource["Note_Click_Audio"][str(note_item.type)],),daemon=True).start()
                    if note_item.type != Const.Note.HOLD and this_noteitem_clicked:
                        continue
                    elif note_item.type == Const.Note.HOLD and now_t > note_item.hold_endtime:
                        continue
                    cfg = {
                        "note":note_item,
                        "now_floorPosition":note_item.floorPosition * PHIGROS_Y - (judgeLine_cfg["Note_dy"] if not (note_item.type == Const.Note.HOLD and note_item.clicked) else (
                            Cal_judgeLine_NoteDy_ByTime(judgeLine,this_judgeLine_T,note_item.time) + note_item.hold_length_px * (1 - ((note_item.hold_endtime - now_t) / note_item.hold_length_sec))
                        ))
                    }
                    rotatenote_at_judgeLine_pos = rotate_point(
                        *judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],note_item.positionX * PHIGROS_X
                    )
                    judgeLine_to_note_rotate_angle = 90 - judgeLine_cfg["Rotate"] - (180 if t == 1 else 0)
                    x,y = rotate_point(
                        *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_angle,cfg["now_floorPosition"]
                    )
                    if note_item.type == Const.Note.HOLD:
                        if cfg["now_floorPosition"] + note_item.hold_length_px >= 0:
                            holdend_x,holdend_y = rotate_point(
                                *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_angle,cfg["now_floorPosition"] + note_item.hold_length_px
                            )
                        else:
                            holdend_x,holdend_y = rotatenote_at_judgeLine_pos
                        if cfg["now_floorPosition"] >= 0:
                            holdhead_pos = x,y
                        else:
                            holdhead_pos = rotatenote_at_judgeLine_pos
                        holdbody_range = [
                            rotate_point(*holdhead_pos,judgeLine_to_note_rotate_angle - 90,Note_width / 2),
                            rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_angle - 90,Note_width / 2),
                            rotate_point(holdend_x,holdend_y,judgeLine_to_note_rotate_angle + 90,Note_width / 2),
                            rotate_point(*holdhead_pos,judgeLine_to_note_rotate_angle + 90,Note_width / 2),
                        ]
                    note_type = {
                        Const.Note.TAP:"Tap",
                        Const.Note.DRAG:"Drag",
                        Const.Note.HOLD:"Hold",
                        Const.Note.FLICK:"Flick"
                    }[note_item.type]
                    render_range = 1.2
                    if (
                            -w * (render_range - 1.0) < x < render_range * w
                            and -h * (render_range - 1.0) < y < render_range * h
                        ) or note_item.rendered:
                        judgeLine_rotate_integer = int(judgeLine_cfg["Rotate"]) % 360
                        if note_item.type != Const.Note.HOLD:
                            this_note_img = Resource["Notes"][note_type + ("_dub" if note_item.morebets else "")][judgeLine_rotate_integer]
                            this_note_imgname = f"Note_{note_type}" + ("_dub" if note_item.morebets else "") + f"_{judgeLine_rotate_integer}"
                        else:
                            this_note_img = Resource["Notes"]["Hold"][note_type + "_Head" + ("_dub" if note_item.morebets else "")][judgeLine_rotate_integer]
                            this_note_imgname = f"Note_{note_type}" + "_Head" + ("_dub" if note_item.morebets else "") + f"_{judgeLine_rotate_integer}"
                            this_note_img_end = Resource["Notes"]["Hold"][note_type + "_End"][judgeLine_rotate_integer]
                            this_note_imgname_end = f"Note_{note_type}" + "_End"+ f"_{judgeLine_rotate_integer}"
                        if not (note_item.type == Const.Note.HOLD and note_item.time * this_judgeLine_T < now_t):
                            root.create_image(
                                this_note_imgname,
                                x - this_note_img.width / 2,
                                y - this_note_img.height / 2,
                                this_note_img.width,this_note_img.height,
                                wait_execute = True
                            )
                        if note_item.type == Const.Note.HOLD:
                            root.create_image(
                                this_note_imgname_end,
                                holdend_x - this_note_img_end.width / 2,
                                holdend_y - this_note_img_end.height / 2,
                                this_note_img_end.width,this_note_img_end.height,
                                wait_execute = True
                            )
                            root.create_polygon(
                                points=holdbody_range,
                                fillStyle="#0078d7",
                                strokeStyle="#00000000",
                                wait_execute = True
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
                    if now_t - note_time <= effect_time:
                        effect_process = (now_t - note_time) / effect_time
                        effect_img_lst = Resource["Note_Click_Effect"]["Perfect"]
                        effect_img_index = int(effect_process * (len(effect_img_lst) - 1))
                        effect_img = effect_img_lst[effect_img_index]
                        effect_imgname = f"Note_Click_Effect_Perfect_{effect_img_index + 1}"
                        will_show_effect_pos = judgeLine.get_datavar_move(note.time,w,h)
                        will_show_effect_rotate = judgeLine.get_datavar_rotate(note.time)
                        if is_nan(will_show_effect_pos): will_show_effect_pos = judgeLine_cfg["Pos"]
                        if is_nan(will_show_effect_rotate): will_show_effect_rotate = judgeLine_cfg["Rotate"]
                        effect_pos = rotate_point(*will_show_effect_pos,-will_show_effect_rotate,note.positionX * PHIGROS_X)
                        root.create_image(
                            effect_imgname,
                            effect_pos[0] - effect_img.width / 2,
                            effect_pos[1] - effect_img.height / 2,
                            effect_img.width,effect_img.height,
                            wait_execute = True
                        )
                    if note.type == Const.Note.HOLD:
                        if note.hold_endtime + effect_time >= now_t:
                            effect_times = []
                            temp_time = note_time
                            hold_effect_blocktime = (1 / judgeLine.bpm * 30)
                            while True:
                                temp_time += hold_effect_blocktime
                                if temp_time >= note.hold_endtime:
                                    break
                                effect_times.append(temp_time)
                            for temp_time in effect_times:
                                if temp_time < now_t:
                                    if now_t - temp_time <= effect_time:
                                        effect_process = (now_t - temp_time) / effect_time
                                        effect_img_lst = Resource["Note_Click_Effect"]["Perfect"]
                                        effect_img_index = int(effect_process * (len(effect_img_lst) - 1))
                                        effect_img = effect_img_lst[effect_img_index]
                                        effect_imgname = f"Note_Click_Effect_Perfect_{effect_img_index + 1}"
                                        will_show_effect_pos = judgeLine.get_datavar_move(temp_time / T,w,h)
                                        will_show_effect_rotate = judgeLine.get_datavar_rotate(temp_time / T)
                                        if is_nan(will_show_effect_pos): will_show_effect_pos = judgeLine_cfg["Pos"]
                                        if is_nan(will_show_effect_rotate): will_show_effect_rotate = judgeLine_cfg["Rotate"]
                                        effect_pos = rotate_point(*will_show_effect_pos,-will_show_effect_rotate,note.positionX * PHIGROS_X)
                                        root.create_image(
                                            effect_imgname,
                                            effect_pos[0] - effect_img.width / 2,
                                            effect_pos[1] - effect_img.height / 2,
                                            effect_img.width,effect_img.height,
                                            wait_execute = True
                                        )

        combo = Cal_Combo(now_t)
        process = int((now_t / audio_length) * w)
        time_text = f"{Format_Time(now_t)}/{Format_Time(audio_length)}"
        draw_ui(
            process=process,
            score=score_manager.get_stringscore(combo * (1000000 / phigros_chart_obj.note_num)),
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
        if abs(music_offset := this_music_pos - now_t * 1000) >= offset_judge_range:
            show_start_time -= music_offset / 1000
            loger_queue.put(f"Warning: mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset)}ms)")
        if time_block_render_count >= cal_fps_block_size:
            if "-showfps" in argv:
                try:
                    root.title(f"Phigros Chart Player - FPS: {(time_block_render_count / (time() - last_cal_fps_time)) : .2f}")
                except ZeroDivisionError:
                    root.title(f"Phigros Chart Player - FPS: inf")
            last_cal_fps_time,time_block_render_count = time(),0
        sleep(1 / fps - min(time() - st,1 / fps))

print("Loading Window...")
# root.iconbitmap(".\\icon.ico")
# if not hidemouse: root.configure(cursor="watch")
root = web_canvas.WebCanvas(
    width=1,height=1,
    x=0,y=0,
    title="Phigros Chart Player",
    hidden=True,debug="-debug" in argv
)
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
background_image = ImageEnhance.Brightness(chart_image.resize((w,h)).filter(ImageFilter.GaussianBlur((w + h) / 300))).enhance(1.0 - chart_information["BackgroundDim"])
root.reg_img(background_image,"background")
PHIGROS_X,PHIGROS_Y = 0.05625 * w,0.6 * h
window_hwnd = root.winfo_hwnd()
print(f"Window Hwnd: {window_hwnd}")
window_style = GetWindowLong(window_hwnd,win32con.GWL_STYLE)
SetWindowLong(window_hwnd,win32con.GWL_STYLE,window_style & ~win32con.WS_SYSMENU) ; del window_style
show_start = Tk()
show_start.geometry(f"{w}x{h}+99999+99999")
show_start.protocol("WM_DELETE_WINDOW",lambda:[show_start.destroy(),root.destroy(),remove_font()])
if not hidemouse: show_start.configure(cursor="watch")
Resource = Load_Resource()
Thread(target=Show_Start,daemon=True).start()
Thread(target=loger,daemon=True).start()
show_start.mainloop()
root.loop_to_close()
windll.kernel32.ExitProcess(0)