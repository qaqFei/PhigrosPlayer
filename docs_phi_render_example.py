from sys import argv
from threading import Thread
from ctypes import windll
from random import randint
from time import time, sleep
import math
import json
import typing

from PIL import Image
from win32api import GetWindowLong, SetWindowLong
import win32con

import web_canvas
import Chart_Objects_Phi

if len(argv) < 2:
    print("Usage: python docs_phi_render_example.py <PhigrosChartFile>")
    raise SystemExit

def get_effect_random_blocks() -> typing.Tuple[int,int,int,int]:
    return tuple((randint(1,90) for _ in range(4)))

def linear_interpolation(
    t:float,
    st:float,
    et:float,
    sv:float,
    ev:float
) -> float:
    if t == st: return sv
    return (t - st) / (et - st) * (ev - sv) + sv

def rotate_point(x,y,θ,r) -> float:
    xo = r * math.cos(math.radians(θ))
    yo = r * math.sin(math.radians(θ))
    return x + xo,y + yo

def Init_Phigros_ChartObject():
    global chart_object
    with open(argv[1], "r") as f: #加载谱面对象
        phigros_chart = json.load(f)
        chart_object = Chart_Objects_Phi.Phigros_Chart(
            formatVersion = phigros_chart["formatVersion"],
            offset = phigros_chart["offset"],
            judgeLineList = [
                Chart_Objects_Phi.judgeLine(
                    id = index,
                    bpm = judgeLine_item["bpm"],
                    notesAbove = [
                        Chart_Objects_Phi.note(
                            type = notesAbove_item["type"],
                            time = notesAbove_item["time"],
                            positionX = notesAbove_item["positionX"],
                            holdTime = notesAbove_item["holdTime"],
                            speed = notesAbove_item["speed"],
                            floorPosition = notesAbove_item["floorPosition"],
                            effect_random_blocks = get_effect_random_blocks()
                        )
                        for notesAbove_item in judgeLine_item["notesAbove"]
                    ],
                    notesBelow = [
                        Chart_Objects_Phi.note(
                            type = notesBelow_item["type"],
                            time = notesBelow_item["time"],
                            positionX = notesBelow_item["positionX"],
                            holdTime = notesBelow_item["holdTime"],
                            speed = notesBelow_item["speed"],
                            floorPosition = notesBelow_item["floorPosition"],
                            effect_random_blocks = get_effect_random_blocks()
                        )
                        for notesBelow_item in judgeLine_item["notesBelow"]
                    ],
                    speedEvents = [
                        Chart_Objects_Phi.speedEvent(
                            startTime = speedEvent_item["startTime"],
                            endTime = speedEvent_item["endTime"],
                            value = speedEvent_item["value"],
                            floorPosition = None
                        )
                        for speedEvent_item in judgeLine_item["speedEvents"]
                    ],
                    judgeLineMoveEvents=[
                        Chart_Objects_Phi.judgeLineMoveEvent(
                            startTime = judgeLineMoveEvent_item["startTime"],
                            endTime = judgeLineMoveEvent_item["endTime"],
                            start = judgeLineMoveEvent_item["start"],
                            end = judgeLineMoveEvent_item["end"],
                            start2 = judgeLineMoveEvent_item["start2"],
                            end2 = judgeLineMoveEvent_item["end2"]
                        )
                        for judgeLineMoveEvent_item in judgeLine_item["judgeLineMoveEvents"]
                    ],
                    judgeLineRotateEvents=[
                        Chart_Objects_Phi.judgeLineRotateEvent(
                            startTime = judgeLineRotateEvent_item["startTime"],
                            endTime = judgeLineRotateEvent_item["endTime"],
                            start = judgeLineRotateEvent_item["start"],
                            end = judgeLineRotateEvent_item["end"]
                        )
                        for judgeLineRotateEvent_item in judgeLine_item["judgeLineRotateEvents"]
                    ],
                    judgeLineDisappearEvents=[
                        Chart_Objects_Phi.judgeLineDisappearEvent(
                            startTime = judgeLineDisappearEvent_item["startTime"],
                            endTime = judgeLineDisappearEvent_item["endTime"],
                            start = judgeLineDisappearEvent_item["start"],
                            end = judgeLineDisappearEvent_item["end"]
                        )
                        for judgeLineDisappearEvent_item in judgeLine_item["judgeLineDisappearEvents"]
                    ]
                )
                for index,judgeLine_item in enumerate(phigros_chart["judgeLineList"])
            ]
        )
        
        #初始化
        for judgeLine in chart_object.judgeLineList:
            #为每个事件排序
            judgeLine.judgeLineMoveEvents.sort(key = lambda x:x.startTime)
            judgeLine.judgeLineRotateEvents.sort(key = lambda x:x.startTime)
            judgeLine.judgeLineDisappearEvents.sort(key = lambda x:x.startTime)
            
            #计算事件单位
            judgeLine.T = 1.875 / judgeLine.bpm
            
            #初始化每个SpeedEvent的floorPosition
            speed_event_floorPosition = 0.0
            for se in judgeLine.speedEvents:
                se.floorPosition = speed_event_floorPosition
                speed_event_floorPosition += (
                    (se.endTime - se.startTime)
                    / judgeLine.T
                    * (se.value)
                )
            
            #为每个Note设置master
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                note.master = judgeLine
            
        #初始化每个Hold的长度
        chart_object.init_holdlength(PHIGROS_Y)
    
def Load_Resources():
    global ClickEffect_Size,Note_width,note_max_width,note_max_height,note_max_width_half,note_max_height_half
    Note_width = int(PHIGROS_X * 1.75)
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
        }
    }
    
    for key,value in Resource["Notes"].items(): #修改资源尺寸
        if value.width > Note_width:
            Resource["Notes"][key] = value.resize((Note_width,int(Note_width / value.width * value.height)))
        window.reg_img(Resource["Notes"][key],f"Note_{key}") #注册资源
    
    for i in range(30):
        window.reg_img(Resource["Note_Click_Effect"]["Perfect"][i],f"Note_Click_Effect_Perfect_{i + 1}") #注册资源
    with open("./Resources/font.ttf","rb") as f:
        window.reg_res(f.read(),"PhigrosFont") #注册资源
    window.load_allimg() #加载全部由reg_img注册的资源
    window.run_js_code(f"loadFont('PhigrosFont',\"{window.get_resource_path("PhigrosFont")}\");") #加载字体
    while not window.run_js_code("font_loaded;"):
        sleep(0.1)
    window.shutdown_fileserver()
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

def Window_Resize_Callback(width,height):
    global w,h
    global PHIGROS_X, PHIGROS_Y
    w, h = width, height
    PHIGROS_X, PHIGROS_Y = 0.05625 * w,0.6 * h  #虽然说更改常量是一件不好的事情
    chart_object.init_holdlength(PHIGROS_Y)

def Init_Window_Style():
    window_hwnd = window.winfo_hwnd()
    window_style = GetWindowLong(window_hwnd,win32con.GWL_STYLE)
    SetWindowLong(window_hwnd,win32con.GWL_STYLE,window_style & ~win32con.WS_SYSMENU)

def Main():
    render_st = time()
    while True:
        now_t = time() - render_st
        
        #清空WebCanvas 并填充黑色背景
        window.clear_canvas(wait_execute = True)
        window.create_rectangle(
            0, 0,
            w, h,
            strokeStyle = "#00000000",
            fillStyle = "#000000",
            wait_execute = True
        )
        
        for judgeLine in chart_object.judgeLineList:
            chart_time = now_t / judgeLine.T
            
            #渲染判定线
            judgeLine_x, judgeLine_y = w / 2, h / 2 #默认值 防止事件不规范时
            judgeLine_rotate = 0.0
            judgeLine_alpha = 0.0
            
            for e in judgeLine.judgeLineMoveEvents: #计算判定线坐标
                if e.startTime <= chart_time <= e.endTime:
                    judgeLine_x, judgeLine_y = (
                        linear_interpolation(chart_time, e.startTime, e.endTime, e.start, e.end) * w,
                        h - linear_interpolation(chart_time, e.startTime, e.endTime, e.start2, e.end2) * h
                    )
                    break
            
            for e in judgeLine.judgeLineRotateEvents: #计算判定线旋转角度
                if e.startTime <= chart_time <= e.endTime:
                    judgeLine_rotate = linear_interpolation(chart_time, e.startTime, e.endTime, e.start, e.end)
                    break
            
            for e in judgeLine.judgeLineDisappearEvents: #计算判定线透明度
                if e.startTime <= chart_time <= e.endTime:
                    judgeLine_alpha = linear_interpolation(chart_time, e.startTime, e.endTime, e.start, e.end)
                    break
            
            if judgeLine_alpha > 0.0:
                judgeLine_strokeStyle = (254,255,169,judgeLine_alpha) #判定线颜色
                window.create_line(
                    *rotate_point(judgeLine_x, judgeLine_y, judgeLine_rotate, h * 5.67), #h * 5.67 是判定线的长度
                    *rotate_point(judgeLine_x, judgeLine_y, judgeLine_rotate + 180, h * 5.67),
                    lineWidth = JUDGELINE_WIDTH,
                    strokeStyle = f"rgba{judgeLine_strokeStyle}",
                    wait_execute = True
                )
        
        #渲染
        window.run_js_wait_code()

window = web_canvas.WebCanvas( #创建窗口
    width = 1,
    height = 1,
    x = 0,
    y = 0,
    title = "Python Phigros Chart Render Example"
)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
w,h = int(screen_width * 0.65), int(screen_height * 0.65) #定义窗口大小

window.resize(w,h)
w_legacy,h_legacy = window.winfo_legacywindowwidth(), window.winfo_legacywindowheight()
dw_legacy,dh_legacy = w - w_legacy,h - h_legacy
window.resize(w + dw_legacy,h + dh_legacy)
window.move(int(screen_width / 2 - (w + dw_legacy) / 2), int(screen_height / 2 - (h + dh_legacy) / 2))
del w_legacy,h_legacy,dw_legacy,dh_legacy

PHIGROS_X, PHIGROS_Y = 0.05625 * w,0.6 * h
JUDGELINE_WIDTH = h * 0.0075
window.reg_event("resized", Window_Resize_Callback) #注册事件
Init_Window_Style() #使用win32api更改窗口样式

Init_Phigros_ChartObject()
Resource = Load_Resources() #加载资源
Thread(target = Main, daemon = True).start() #开始渲染
window.loop_to_close()
windll.kernel32.ExitProcess(0)