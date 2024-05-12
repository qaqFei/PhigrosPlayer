from tkinter import Tk,Toplevel,Canvas
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

from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
from pygame import mixer
from cv2 import VideoWriter
from numpy import asarray

import Chart_Objects
import Find_Files
import Const

mixer.init()
note_id = -1

if exists(".//__pycache__"):
    try: rmtree(".//__pycache__")
    except Exception: pass

if len(argv) < 3:
    print("Create_Video.py <output_file> <input_file>")
    raise SystemExit

if not exists(".\\7z.exe") or not exists(".\\7z.dll"):
    print("7z.exe or 7z.dll Not Found.")
    raise SystemExit

temp_dir = f"{gettempdir()}\\phigros_chart_temp_{time()}"
for item in [item for item in listdir(gettempdir()) if item.startswith("phigros_chart_temp_")]:
    item = f"{gettempdir()}\\{item}"
    try:
        rmtree(item)
        print(f"Remove Temp Dir: {item}")
    except Exception as e:
        print(f"Warning: {e}")
print(f"Temp Dir: {temp_dir}")

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
        except Exception as e:
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

def unpack_pos(number:int) -> tuple[int,int]:
    return (number - number % 1000) // 1000,number % 1000

def is_nan(x) -> bool:
    return x != x

def is_will_process_char(char:str) -> bool:
    if len(char) != 1: return False
    if ord("a") <= ord(char.lower()) <= ord("z"): return True
    return False

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
    ImageDraw.Draw(Resource["ProcessBar"]).rectangle((w * 0.998,0,w,int(h / 125)),fill=(255,)*3)
    print("Loading Resource Successfully.")
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

def merge_image(base:Image.Image,img:Image.Image):
    base.paste(img,(0,0),mask=img.split()[-1])

def get_cv_video_writer_array_by_pil_image(im:Image.Image):
    return asarray(im.resize((w,h)))[:,:,::-1]

fps = 45
w,h = 1920,1080
SSAA_Scale = 1
judgeLine_width = h * 0.0075 * SSAA_Scale
PHIGROS_X,PHIGROS_Y = 0.05625 * w,0.6 * h
JUDGELINE_COLOR = (254,255,169)
Resource = Load_Resource()
video_writer = VideoWriter(
    argv[2],
    VideoWriter.fourcc(*"mp4v"),
    fps,
    (w,h),True
)
background = ImageEnhance.Brightness(chart_image.resize((int(w * SSAA_Scale),int(h * SSAA_Scale))).filter(ImageFilter.GaussianBlur((w + h) * SSAA_Scale / 300))).enhance(1.0 - chart_information["BackgroundDim"])
background_draw = ImageDraw.Draw(background)
pil_font_1 = ImageFont.truetype("./font.ttf",size=int((w + h) * SSAA_Scale / 175 / 0.75)) #pt -> px (pt / 0.75 = px)
pil_font_2 = ImageFont.truetype("./font.ttf",size=int((w + h) * SSAA_Scale / 125 / 0.75))
pil_font_3 = ImageFont.truetype("./font.ttf",size=int((w + h) * SSAA_Scale / 100 / 0.75))
pil_font_4 = ImageFont.truetype("./font.ttf",size=int((w + h) * SSAA_Scale / 70 / 0.75))
pil_font_5 = ImageFont.truetype("./font.ttf",size=int((w + h) * SSAA_Scale / 75 / 0.75))
begin_animation_time = 1.25
begin_animation_gr = Get_Animation_Gr(fps,begin_animation_time)[0]
get_bbox_draw = ImageDraw.Draw(background)

score_draw_bbox = get_bbox_draw.textbbox((0,0),text="0000000",font=pil_font_5)
score_draw_bbox_size = (score_draw_bbox[2] - score_draw_bbox[0],score_draw_bbox[3] - score_draw_bbox[1])
score_draw_kwargs = {
    "xy":(
        w * SSAA_Scale * 0.99 - score_draw_bbox_size[0],
        h * SSAA_Scale * 0.005
    ),
    "fill":"white",
    "font":pil_font_5
}

def get_combo_draw_kwargs(combo:int):
    combo_draw_bbox = get_bbox_draw.textbbox((0,0),text=f"{combo}",font=pil_font_4)
    combo_draw_bbox_size = (combo_draw_bbox[2] - combo_draw_bbox[0],combo_draw_bbox[3] - combo_draw_bbox[1])
    combo_draw_kwargs = {
        "xy":(
            w * SSAA_Scale / 2 - combo_draw_bbox_size[0] / 2,
            h * SSAA_Scale * 0.001 + combo_draw_bbox_size[1] / 2
        ),
        "fill":"white",
        "font":pil_font_4
    }
    return combo_draw_kwargs

autoplay_draw_bbox = get_bbox_draw.textbbox((0,0),text="Autoplay",font=pil_font_3)
autoplay_draw_bbox_size = (autoplay_draw_bbox[2] - autoplay_draw_bbox[0],autoplay_draw_bbox[3] - autoplay_draw_bbox[1])
autoplay_draw_kwargs = {
    "xy":(
        w * SSAA_Scale / 2 - autoplay_draw_bbox_size[0] / 2,
        h * SSAA_Scale * 0.055 + autoplay_draw_bbox_size[1] / 2
    ),
    "fill":"white",
    "font":pil_font_3,
    "text":"Autoplay"
}

time_draw_bbox = get_bbox_draw.textbbox((0,0),text="0:00/0:00",font=pil_font_1)
time_draw_bbox_size = (time_draw_bbox[2] - time_draw_bbox[0],time_draw_bbox[3] - time_draw_bbox[1])
time_draw_kwargs = {
    "xy":(
        0,
        h * SSAA_Scale * 0.00075
    ),
    "fill":"white",
    "font":pil_font_1
}

chart_name_draw_bbox = get_bbox_draw.textbbox((0,0),text=chart_information["Name"],font=pil_font_2)
chart_name_draw_bbox_size = (chart_name_draw_bbox[2] - chart_name_draw_bbox[0],chart_name_draw_bbox[3] - chart_name_draw_bbox[1])
chart_name_draw_kwargs = {
    "xy":(
        w * SSAA_Scale * 0.01,
        h * SSAA_Scale * 0.98 - chart_name_draw_bbox_size[1]
    ),
    "fill":"white",
    "font":pil_font_2,
    "text":chart_information["Name"]
}

level_draw_bbox = get_bbox_draw.textbbox((0,0),text=chart_information["Level"],font=pil_font_2)
level_draw_bbox_size = (level_draw_bbox[2] - level_draw_bbox[0],level_draw_bbox[3] - level_draw_bbox[1])
level_draw_kwargs = {
    "xy":(
        w * SSAA_Scale * 0.99 - level_draw_bbox_size[0],
        h * SSAA_Scale * 0.98 - level_draw_bbox_size[1]
    ),
    "fill":"white",
    "font":pil_font_2,
    "text":chart_information["Level"]
}

before_begin_frame = get_cv_video_writer_array_by_pil_image(background)
for i in range(int(fps / 2)):
    print(f"Before begin animation... {i + 1} / {int(fps / 2)} frame.\r",end="")
    video_writer.write(before_begin_frame)
print()

begin_animation_range_size = int(fps * begin_animation_time)
for i in range(begin_animation_range_size):
    begin_animation_process = (i + 1) / begin_animation_range_size
    this_frame = background.copy()
    this_frame_draw = ImageDraw.Draw(this_frame)
    gr_value = sum(begin_animation_gr[:int(len(begin_animation_gr) * begin_animation_process)])
    begin_animation_judgeLine_length_half = w / 2 * gr_value #SSAA in draw
    this_frame_draw.line(
        (
            ((w / 2 - begin_animation_judgeLine_length_half) * SSAA_Scale,(h / 2) * SSAA_Scale),
            ((w / 2 + begin_animation_judgeLine_length_half) * SSAA_Scale,(h / 2) * SSAA_Scale)
        ),
        width=int(judgeLine_width),
        fill=JUDGELINE_COLOR
    )
    this_frame_draw.text(**score_draw_kwargs,text="0000000")
    # this_frame_draw.text(**combo_draw_kwargs,text="0")
    # this_frame_draw.text(**autoplay_draw_kwargs)
    this_frame_draw.text(**time_draw_kwargs,text="0:00/0:00")
    this_frame_draw.text(**chart_name_draw_kwargs)
    this_frame_draw.text(**level_draw_kwargs)
    print(f"Begin animation... {i + 1} / {begin_animation_range_size} frame.\r",end="")
    video_writer.write(get_cv_video_writer_array_by_pil_image(this_frame))

print()
del this_frame_draw

frame_count = 0
max_frame_count = int(audio_length * fps)
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

while True:
    try:
        frame_count += 1
        combo = 0
        now_time = frame_count / fps
        this_frame = background.copy()
        this_frame_draw = ImageDraw.Draw(this_frame)
        judgeLine_image = Image.new("RGBA",(int(w * SSAA_Scale),int(h * SSAA_Scale)),(0,0,0,0))
        notes_image = judgeLine_image.copy()

        judgeLine_image_draw = ImageDraw.Draw(judgeLine_image,"RGBA")
        Update_JudgeLine_Configs(
            judgeLine_Configs,
            {
                judgeLine_item.__hash__():1.875/judgeLine_item.bpm
                for judgeLine_item in phigros_chart_obj.judgeLineList
            },now_time)
        
        for judgeLine_cfg_key in sorted(judgeLine_Configs,key=lambda x:judgeLine_Configs[x]["Disappear"]):
            judgeLine_cfg = judgeLine_Configs[judgeLine_cfg_key]
            judgeLine:Chart_Objects.judgeLine = judgeLine_cfg["judgeLine"]
            this_judgeLine_T = 1.875 / judgeLine.bpm
            judgeLine_cfg["Note_dy"] = Cal_judgeLine_NoteDy(judgeLine_cfg,this_judgeLine_T)
            judgeLine_DrawPos = [
                *rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],5.76 * h),
                *rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"] + 180,5.76 * h)
            ]
            judgeLine_DrawPos = [int(item * SSAA_Scale) for item in judgeLine_DrawPos]
            draw_cfg = {
                "fill":JUDGELINE_COLOR + (int(255 * judgeLine_cfg["Disappear"]),),
                "width":int(judgeLine_width),
            }
            if judgeLine_cfg["Disappear"] > 0:
                judgeLine_image_draw.line(
                    judgeLine_DrawPos,**draw_cfg
                )
        
        for judgeLine in phigros_chart_obj.judgeLineList:
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                if note.time * (1.875 / judgeLine.bpm) <= now_time:
                    combo += 1

        merge_image(this_frame,judgeLine_image)
        merge_image(this_frame,notes_image)
        score_text = f"{int((combo / phigros_chart_obj.note_num) + 0.5):>7}".replace(" ","0")
        this_frame_draw.text(**score_draw_kwargs,text=score_text)
        if combo >= 3:
            this_frame_draw.text(**get_combo_draw_kwargs(combo),text=f"{combo}")
            this_frame_draw.text(**autoplay_draw_kwargs)
        this_frame_draw.text(**time_draw_kwargs,text=f"{Format_Time(now_time)}/{Format_Time(audio_length)}")
        this_frame_draw.text(**chart_name_draw_kwargs)
        this_frame_draw.text(**level_draw_kwargs)
        video_writer.write(get_cv_video_writer_array_by_pil_image(this_frame))
        print(f"{frame_count} / {max_frame_count} frame.\r",end="")
        if now_time >= audio_length:
            break
    except KeyboardInterrupt:
        break

video_writer.release()