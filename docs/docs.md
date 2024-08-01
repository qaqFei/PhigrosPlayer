# PhigrosPlayer 文档

## Inno_AppId.txt 文件
- 用于Inno Setup打包安装程序包的GUID

## WebView2_Runtime_Setup.exe 文件
- 在未安装 `WebView` 时, 可供安装的在线安装包。

## Phigros 谱面文件渲染计算
我们先定义一些数据类型：
``` python
from __future__ import annotations
from dataclasses import dataclass

__all__ = (
    "Phigros_Chart",
    "judgeLine",
    "note",
    "speedEvent",
    "judgeLineMoveEvent",
    "judgeLineRotateEvent",
    "judgeLineDisappearEvent"
)

@dataclass
class Phigros_Chart:
    formatVersion:int
    offset:typing.Union[int,float]
    judgeLineList:list[judgeLine]

@dataclass
class judgeLine:
    bpm:typing.Union[int,float]
    notesAbove:list[note]
    notesBelow:list[note]
    speedEvents:list[speedEvent]
    judgeLineMoveEvents:list[judgeLineMoveEvent]
    judgeLineRotateEvents:list[judgeLineRotateEvent]
    judgeLineDisappearEvents:list[judgeLineDisappearEvent]

@dataclass
class note:
    type:typing.Literal[1,2,3,4]
    time:typing.Union[int,float]
    positionX:typing.Union[int,float]
    holdTime:typing.Union[int,float]
    speed:typing.Union[int,float]
    floorPosition:typing.Union[int,float]

@dataclass
class speedEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    value:typing.Union[int,float]
    floorPosition:typing.Union[typing.Union[int,float],None]

@dataclass
class judgeLineMoveEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]
    start2:typing.Union[int,float]
    end2:typing.Union[int,float]

@dataclass
class judgeLineRotateEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]

@dataclass
class judgeLineDisappearEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]
```

------

一些关于谱面的概念:
- 对于谱面的时间的现实时间的转化: `sec = t * (1.875 / bpm)`

------

定义的一些概念:
- `PHIGROS_X` & `PHIGROS_Y` 假设此时屏幕大小为`w,h`
则: `PHIGROS_X, PHIGROS_Y = 0.05625 * w,0.6 * h`

------

对于谱面数据对象的含义：
- `class note`
    - `type:typing.Literal[1,2,3,4]` `note`的类型:
    `Tap = 1,  Drag = 2, Hold = 3, Flick = 4`
    - `time:typing.Union[int,float]` `note`打击时的时间
        - 对于 `Hold` 音符, 表示打击开始时的时间
    - `positionX:typing.Union[int,float]` `note`对于判定线的横向坐标, 单位为`PHIGROS_X`
    - `holdTime:typing.Union[int,float]` `Hold` 音符的打击时长
        - 转化成秒的方法也是 `sec = t * (1.875 / bpm)`
        - 音符的长度如何计算?
            ```python
            self: note
            
            length_sec = self.holdTime * (1.875 / bpm)
            length_px = self.speed * length_sec * PHIGROS_Y
            ```
        - 结束时间: 
          ```python
          self: note
          
          hold_endtime = (self.time + self.holdTime) * (1.875 / bpm)
          ```
    - `speed:typing.Union[int,float]` `note` 的速度
        - 用处仅在 `Hold` 音符的长度和打击时速度的计算
        - 对于还未打击的音符, 速度以对`speedEvent`插值的到的实时速度值为准
    - `floorPosition:typing.Union[int,float]` 在谱面时间为`0`时, `note` 对于判定线的高度, 单位为`PHIGROS_Y`
        - 作用仅为方便计算、

- `class speedEvent`
    - `startTime:typing.Union[int,float]` 事件开始时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `endTime:typing.Union[int,float]` 事件结束时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `value:typing.Union[int,float]` 在事件开始时间到结束时间范围内的速度值, 单位为 `PHIGROS_Y / s`
    - `floorPosition:typing.Union[typing.Union[int,float],None]` 对于一些谱面, 速度事件拥有`floorPosition`属性, 该属性表示该速度事件在开始时判定线已走过的长度, 仅用于方便计算
      即:
        ```python
        ThisEvent: speedEvent
        NextEvent: speedEvent
      
        NextEvent.floorPosition = ThisEvent.floorPosition + (
            (ThisEvent.endTime - ThisEvent.startTime)
            * (1.875 / bpm)
            * ThisEvent.value
        )
        ```

- `class judgeLineMoveEvent`
    - `startTime:typing.Union[int,float]` 事件开始时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `endTime:typing.Union[int,float]` 事件结束时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `start:typing.Union[int,float]` 事件开始时的`x`坐标 范围: `0.0 ~ 1.0`
    - `end:typing.Union[int,float]` 事件结束时的`x`坐标 范围: `0.0 ~ 1.0`
    - `start2:typing.Union[int,float]` 事件开始时的`y`坐标 范围: `0.0 ~ 1.0`
    - `end2:typing.Union[int,float]` 事件结束时的`y`坐标 范围: `0.0 ~ 1.0`

- `class judgeLineRotateEvent` tip: 为逆时针旋转
    - `startTime:typing.Union[int,float]` 事件开始时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `endTime:typing.Union[int,float]` 事件结束时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `start:typing.Union[int,float]` 事件开始时的旋转度数
    - `end:typing.Union[int,float]` 事件结束时的旋转度数

- `class judgeLineDisappearEvent` tip: `alpha` 为 0 则完全透明
    - `startTime:typing.Union[int,float]` 事件开始时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `endTime:typing.Union[int,float]` 事件结束时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `start:typing.Union[int,float]` 事件开始时的`alpha`值
    - `end:typing.Union[int,float]` 事件结束时的`alpha`值

- `class judgeLine`
    - `bpm:typing.Union[int,float]` 判定线的`bpm`值
    - `notesAbove:list[note]` 判定线的正面`note`列表
    - `notesBelow:list[note]` 判定线的反面`note`列表
    - `speedEvents:list[speedEvent]` 判定线的速度事件列表
    - `judgeLineMoveEvents:list[judgeLineMoveEvent]` 判定线的移动事件列表
    - `judgeLineRotateEvents:list[judgeLineRotateEvent]` 判定线的旋转事件列表
    - `judgeLineDisappearEvents:list[judgeLineDisappearEvent]` 判定线的`alpha`事件列表

------

对于事件：
- 应当连续 即: `es[index].endTime == es[index + 1].startTime`
- 第一个事件的开始时间应当足够的小
- 最后个事件的结束时间应当足够的大

------

事件值的计算:
- 事件皆为线性事件

------
既然, 我们已经了解Phigros谱面的结构和渲染方式, 那就让我们用`Python`编写一个简易的渲染程序吧!

首先, 让我们引入几个模块:
- [WebCanvas](./../web_canvas.py) 这是一个`Python`模块 通过`JavaScript`在`WebView`上创建`Canvas`并绘制内容, 并将其封装为`Python Api`
  文件名: `web_canvas.py`
- [WebCanvas Html](./../web_canvas.html) 这是供`WebCanvas`模块使用的`html`文件 定义了一些`Javascript`函数供调用
  文件名: `web_canvas.html`
- [Chart Objects](./../Chart_Objects_Phi.py) 对于数据类型的定义
  文件名: `Chart_Objects_Phi.py`
- [Const Values](./../Const.py) 常量
  文件名: `Const.py`

其次, 我们需要安装一些模块:
- `pywebview`
- `Pillow`
- `pywin32`

使用脚本安装:
```batch
@echo off
pip install pywebview
pip install Pillow
pip install pywin32
```

------
<font color=#FF0000>注意: 该示例中的变量名可能会与[Main.py](./../Main.py)中的变量名一致, 但含义不同</font>

让我们开始一步步地编写吧, 但是我们不做任何的异常处理, 且只兼容`formatVersion`为3的谱面(最为常见), 最终的文件: [Python Phigros Chart Render Example](./Python Phigros Chart Render Example/Python Phigros Chart Render Example.py)

### Step 1
- 让我们导入基本的模块, 并创建一个简单的`WebView`窗口
- 并且定义 `PHIGROS_X` & `PHIGROS_Y`
- 在窗口大小更新时更新 `PHIGROS_X` & `PHIGROS_Y`
```python
from sys import argv
from threading import Thread
from ctypes import windll
import math
import json

from win32api import GetWindowLong, SetWindowLong
import win32con

import web_canvas
import Chart_Objects_Phi

if len(argv) < 2:
    print("Usage: python docs_phi_render_example.py <PhigrosChartFile>")
    raise SystemExit

def Window_Resize_Callback(width,height):
    global w,h
    global PHIGROS_X, PHIGROS_Y
    w, h = width, height
    PHIGROS_X, PHIGROS_Y = 0.05625 * w,0.6 * h  #虽然说更改常量是一件不好的事情

def Init_Window_Style():
    window_hwnd = window.winfo_hwnd()
    window_style = GetWindowLong(window_hwnd,win32con.GWL_STYLE)
    SetWindowLong(window_hwnd,win32con.GWL_STYLE,window_style & ~win32con.WS_SYSMENU)

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
w_legacy,h_legacy = window.winfo_legacywindowwidth(),window.winfo_legacywindowheight()
dw_legacy,dh_legacy = w - w_legacy,h - h_legacy
window.resize(w + dw_legacy,h + dh_legacy)
window.move(int(screen_width / 2 - (w + dw_legacy) / 2),int(screen_height / 2 - (h + dh_legacy) / 2))
del w_legacy,h_legacy,dw_legacy,dh_legacy

PHIGROS_X, PHIGROS_Y = 0.05625 * w,0.6 * h
window.reg_event("resized", Window_Resize_Callback) #注册事件
Init_Window_Style() #使用win32api更改窗口样式
window.loop_to_close()
windll.kernel32.ExitProcess(0)
```

### Step 2
- 加载Phigros谱面为`Python`对象
- 为了渲染打击时随机扩散的方形特效 定义`Python`函数`get_effect_random_blocks`
- 初始化谱面对象
  ```python
  def get_effect_random_blocks() -> typing.Tuple[int,int,int,int]:
      return tuple((randint(1,90) for _ in range(4)))
  ```
```python
from sys import argv
from threading import Thread
from ctypes import windll
from random import randint
import math
import json
import typing

from win32api import GetWindowLong, SetWindowLong
import win32con

import web_canvas
import Chart_Objects_Phi

if len(argv) < 2:
    print("Usage: python docs_phi_render_example.py <PhigrosChartFile>")
    raise SystemExit

def get_effect_random_blocks() -> typing.Tuple[int,int,int,int]:
    return tuple((randint(1,90) for _ in range(4)))

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
            
        #寻找多押
        notes = []
        for judgeLine in chart_object.judgeLineList:
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                notes.append(note)
        note_times = {}
        for note in notes:
            note:Chart_Objects_Phi.note
            if note.time not in note_times:
                note_times[note.time] = 1
            else:
                note_times[note.time] += 1
        for note in notes:
            if note_times[note.time] > 1:
                note.morebets = True
        del notes,note_times

        #初始化每个Hold的长度
        chart_object.init_holdlength(PHIGROS_Y)
    
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
window.reg_event("resized", Window_Resize_Callback) #注册事件
Init_Window_Style() #使用win32api更改窗口样式
Init_Phigros_ChartObject()
window.loop_to_close()
windll.kernel32.ExitProcess(0)
```

### Step 3
- 加载资源到`WebView`
  `WebCanvas.reg_img` 方法:
    - 第一个参数为资源的名称
    - 第二个参数为资源的对象(PIL.Image.Image)
    - 可在`WebCanvas.create_image`地方使用
    - 资源以 `f"{name}_img"` 的变量名存储在`JavaScript`的全局变量中
```python
from sys import argv
from threading import Thread
from ctypes import windll
from random import randint
from time import sleep
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
    window.load_allimg() #加载全部由reg_img注册的资源
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
window.reg_event("resized", Window_Resize_Callback) #注册事件
Init_Window_Style() #使用win32api更改窗口样式

Init_Phigros_ChartObject()
Resource = Load_Resources() #加载资源
window.loop_to_close()
windll.kernel32.ExitProcess(0)
```

### Step 4
- 让我们初步渲染判定线
    - 增加`Main`函数, 用于渲染
- 让我们定义一个函数:
    ```
    def linear_interpolation(
        t:float,
        st:float,
        et:float,
        sv:float,
        ev:float
    ) -> float:
        if t == st: return sv
        return (t - st) / (et - st) * (ev - sv) + sv
    ```
    这个函数用于事件的线性插值
- 让我们再定义一个函数:
    ```
    def rotate_point(x,y,θ,r) -> float:
        xo = r * math.cos(math.radians(θ))
        yo = r * math.sin(math.radians(θ))
        return x + xo,y + yo
    ```
    旋转一个点
- 再让我们定义一个值`JUDGELINE_WIDTH`, 为`h * 0.0075`, 判定线的宽度
- 补充:
    - 一些`WebCanvas`中的方法有`wait_execute`或`add_code_array`, 作用为添加到代码执行的队伍中, 不会立刻执行, 只有在调用`WebCanvas.run_js_wait_code` 时才会一并执行
```python
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
    window.load_allimg() #加载全部由reg_img注册的资源
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
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate, h * 5.67), #h * 5.67 是判定线的长度
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate + 180, h * 5.67),
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
```

### Step 5
至此, 我们已经渲染了判定线, 那么, 下一步就是渲染`note`了
- 由于`Hold`的渲染难度相对比其他`note`来说, 更加困难. 所以, 此步仅渲染除了`Hold`的`note`
- 我们需要渲染`note`, 那么我们就需要知道`note`从谱面开始到现在, 所走过的长度, 我们在`chart_object.judgeLineList`的循环中用此方法计算:
  ```python
  note_dy = 0.0 #note走过的距离
  for e in judgeLine.speedEvents:
      if e.startTime <= chart_time <= e.endTime:
          note_dy += (chart_time - e.startTime) * judgeLine.T * e.value
      elif e.endTime <= chart_time:
          note_dy += (e.endTime - e.startTime) * judgeLine.T * e.value
  note_dy_px = note_dy * PHIGROS_Y
  ```
- 首先我们定义一个函数在`Main`内:
  ```python
  def process_note(
      note_item:Chart_Objects_Phi.note,
      note_face_type:typing.Literal["above","below"],
      note_dy_px:float
  ):
      note_type = {
          Const.Note.TAP:"Tap",
          Const.Note.DRAG:"Drag",
          Const.Note.HOLD:"Hold",
          Const.Note.FLICK:"Flick"
      }[note_item.type]
  ```
  随后:
  ```python
  for note in judgeLine.notesAbove:
      process_note(note, "above", note_dy_px)
            
  for note in judgeLine.notesBelow:
      process_note(note, "below", note_dy_px)
  ```

  让我们往`process_note`函数中编写代码:
  - 因为我们目前不渲染`Hold`, 所以(由于判断`note`是不是`Hold`的地方较多, 所以我们定义`is_hold:bool`):
  ```python
  is_hold = note_item.type == Const.Note.HOLD
  if is_hold:
      return None
  ```
  - 计算`note`现在的时间(秒)
  ```python
  this_note_sectime = note_item.time * judgeLine.T
  ```
  - 计算`note`与判定线的距离
  ```python
  note_to_judgeLine_px = note.floorPosition * PHIGROS_Y - note_dy_px
  ```
  - 如果距离为负数, 则无需渲染, `Hold`除外
  ```python
  if not is_hold and this_note_sectime - now_t < 0.0:
      return None
  ```
  - 计算绘制中心坐标
  ```python
  rotatenote_at_judgeLine_pos = rotate_point(
      judgeLine_x, judgeLine_y, -judgeLine_rotate, note_item.positionX * PHIGROS_X
  ) #计算note在判定线上的位置
  judgeLine_to_note_rotate_deg = - judgeLine_rotate + (180 if note_type == "below" else 0) - 90 #note要相对于判定线旋转的角度
  x,y = rotate_point(
      *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_deg,note_to_judgeLine_px
  ) #计算绘制中心坐标
  ```
  - 虽然我们不需要渲染`Hold`, 但我们还是计算`Hold`的基本数据
      - 由于`Hold`在打击时尾速度受`note.speed`的影响, 所以我们对`note_to_judgeLine_px`变量的定义做修改, 并对`note_dy`和`note_dy_px`的计算抽离为一个函数`Cal_judgeLine_NoteDy_ByTime`:
        ```python
        def Cal_judgeLine_NoteDy_ByTime(
            judgeLine:Chart_Objects_Phi.judgeLine,
            time:float
        ) -> float:
            note_dy = 0.0 #note走过的距离
            for e in judgeLine.speedEvents:
                if e.startTime <= time <= e.endTime:
                    note_dy += (time - e.startTime) * judgeLine.T * e.value
                elif e.endTime <= time:
                    note_dy += (e.endTime - e.startTime) * judgeLine.T * e.value
            return note_dy
        ```
        ```python
        note_to_judgeLine_px = note_item.floorPosition * PHIGROS_Y - (
                note_dy_px
                if not (is_hold and note_item.clicked) else ( #是Hold, 且已打击
                Cal_judgeLine_NoteDy_ByTime(
                    judgeLine, note_item.time #计算note开始时的距离
                ) * PHIGROS_Y + note_item.hold_length_px * (1 - ((note_item.hold_endtime - now_t) / note_item.hold_length_sec)) #计算Hold的距离
            )
        )
        ```
      - 让我们计算`Hold`的基本数据:
        ```python
        if is_hold:
            note_hold_draw_length = note_to_judgeLine_px + note_item.hold_length_px #计算Hold尾对于判定线的距离
            if note_hold_draw_length >= 0: #打击未结束时
                holdend_x,holdend_y = rotate_point(
                    *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_hold_draw_length
                ) #计算Hold尾坐标
            else:
                holdend_x,holdend_y = rotatenote_at_judgeLine_pos #Hold尾坐标在判定线上
            if note_to_judgeLine_px >= 0: #未打击时
                holdhead_pos = x,y
            else: #打击未结束时
                holdhead_pos = rotatenote_at_judgeLine_pos
            holdbody_range = ( #Hold的渲染范围
                rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
            )
        ```
  - 此外, 为了节约性能, 我们不渲染在屏幕之外的`note`, 所以我们引入函数`Note_CanRender`及其辅助函数:
  ```python
  def Note_CanRender(
      x:float,y:float,
      hold_points:typing.Union[typing.Tuple[
          typing.Tuple[float,float],
          typing.Tuple[float,float],
          typing.Tuple[float,float],
          typing.Tuple[float,float]
      ],None] = None
  ) -> bool:
      if hold_points is None: #type != HOLD
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
  
  def point_in_screen(point:typing.Tuple[float,float]) -> bool:
      return 0 < point[0] < w and 0 < point[1] < h
  ```
  - 然后调用`Note_CanRender`判断是否要渲染`note`
  ```python
  note_iscan_render = (
      Note_CanRender(x,y)
      if not is_hold
      else Note_CanRender(x,y,holdbody_range)
  )
  ```
  - 然后让我们生成`note`绘制的资源名(在`window.reg_img`时定义的):
  ```python
  if note_iscan_render:
      judgeLine_rotate = (judgeLine_to_note_rotate_deg + 90) % 360 #计算note的旋转角度
      dub_text = "_dub" if note_item.morebets else ""
      if not is_hold:
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
  ```
  - 最后!!! 渲染!
  ```python
  if not (is_hold and this_note_sectime < now_t):
      window.run_js_code(
          f"ctx.drawRotateImage(\
              {window.get_img_jsvarname(this_note_imgname)},\
              {x},\
              {y},\
              {Note_width},\
              {Note_width / this_note_img.width * this_note_img.height},\
              {note_to_judgeLine_rotate}\
          );",
          add_code_array = True
      )
  ```
```python
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
import Const

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
        
        #寻找多押
        notes = []
        for judgeLine in chart_object.judgeLineList:
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                notes.append(note)
        note_times = {}
        for note in notes:
            note:Chart_Objects_Phi.note
            if note.time not in note_times:
                note_times[note.time] = 1
            else:
                note_times[note.time] += 1
        for note in notes:
            if note_times[note.time] > 1:
                note.morebets = True
        del notes,note_times
        
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
    window.load_allimg() #加载全部由reg_img注册的资源
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

def Note_CanRender(
    x:float,y:float,
    hold_points:typing.Union[typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ],None] = None
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

def point_in_screen(point:typing.Tuple[float,float]) -> bool:
    return 0 < point[0] < w and 0 < point[1] < h

def Cal_judgeLine_NoteDy_ByTime(
    judgeLine:Chart_Objects_Phi.judgeLine,
    time:float
) -> float:
    note_dy = 0.0 #note走过的距离
    for e in judgeLine.speedEvents:
        if e.startTime <= time <= e.endTime:
            note_dy += (time - e.startTime) * judgeLine.T * e.value
        elif e.endTime <= time:
            note_dy += (e.endTime - e.startTime) * judgeLine.T * e.value
    return note_dy

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
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate, h * 5.67), #h * 5.67 是判定线的长度
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate + 180, h * 5.67),
                    lineWidth = JUDGELINE_WIDTH,
                    strokeStyle = f"rgba{judgeLine_strokeStyle}",
                    wait_execute = True
                )
            
            def process_note(
                note_item:Chart_Objects_Phi.note,
                note_face_type:typing.Literal["above","below"],
                note_dy_px:float
            ):
                this_note_sectime = note_item.time * judgeLine.T
                is_hold = note_item.type == Const.Note.HOLD
                if is_hold:
                    return None
                
                if not is_hold and this_note_sectime - now_t < 0.0:
                    return None

                note_type = {
                    Const.Note.TAP:"Tap",
                    Const.Note.DRAG:"Drag",
                    Const.Note.HOLD:"Hold",
                    Const.Note.FLICK:"Flick"
                }[note_item.type]
                
                note_to_judgeLine_px = note_item.floorPosition * PHIGROS_Y - (
                        note_dy_px
                        if not (is_hold and note_item.clicked) else ( #是Hold, 且已打击
                        Cal_judgeLine_NoteDy_ByTime(
                            judgeLine, note_item.time #计算note开始时的距离
                        ) * PHIGROS_Y + note_item.hold_length_px * (1 - ((note_item.hold_endtime - now_t) / note_item.hold_length_sec)) #计算Hold的距离
                    )
                )
                rotatenote_at_judgeLine_pos = rotate_point(
                    judgeLine_x, judgeLine_y, -judgeLine_rotate, note_item.positionX * PHIGROS_X
                ) #计算note在判定线上的位置
                judgeLine_to_note_rotate_deg = - judgeLine_rotate + (180 if note_face_type == "below" else 0) - 90 #note要相对于判定线旋转的角度
                x,y = rotate_point(
                    *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_to_judgeLine_px
                ) #计算绘制中心坐标
                
                if is_hold:
                    note_hold_draw_length = note_to_judgeLine_px + note_item.hold_length_px #计算Hold尾对于判定线的距离
                    if note_hold_draw_length >= 0: #打击未结束时
                        holdend_x,holdend_y = rotate_point(
                            *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_hold_draw_length
                        ) #计算Hold尾坐标
                    else:
                        holdend_x,holdend_y = rotatenote_at_judgeLine_pos #Hold尾坐标在判定线上
                    if note_to_judgeLine_px >= 0: #未打击时
                        holdhead_pos = x,y
                    else: #打击未结束时
                        holdhead_pos = rotatenote_at_judgeLine_pos
                    holdbody_range = ( #Hold的渲染范围
                        rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                        rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                    )
                
                note_iscan_render = (
                    Note_CanRender(x,y)
                    if not is_hold
                    else Note_CanRender(x,y,holdbody_range)
                )
                
                if note_iscan_render:
                    note_to_judgeLine_rotate = (judgeLine_to_note_rotate_deg + 90) % 360 #计算note的旋转角度
                    dub_text = "_dub" if note_item.morebets else ""
                    if not is_hold:
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
                    
                    if not (is_hold and this_note_sectime < now_t):
                        window.run_js_code(
                            f"ctx.drawRotateImage(\
                                {window.get_img_jsvarname(this_note_imgname)},\
                                {x},\
                                {y},\
                                {Note_width},\
                                {Note_width / this_note_img.width * this_note_img.height},\
                                {note_to_judgeLine_rotate}\
                            );",
                            add_code_array = True
                        )
            
            note_dy = Cal_judgeLine_NoteDy_ByTime(judgeLine, chart_time)
            note_dy_px = note_dy * PHIGROS_Y
            
            for note in judgeLine.notesAbove:
                process_note(note, "above", note_dy_px)
            
            for note in judgeLine.notesBelow:
                process_note(note, "below", note_dy_px)
        
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
```

### Step 6
- 让我们开始渲染`Hold`吧!
  - 我们要计算`Hold`身的坐标的长度:
  ```python
  if is_hold:
    if note_item.clicked:
        holdbody_x,holdbody_y = rotatenote_at_judgeLine_pos
        holdbody_length = note_hold_draw_length - this_note_img_end.height / 2
    else:
        holdbody_x,holdbody_y = rotate_point(
            *holdhead_pos,judgeLine_to_note_rotate_deg,this_note_img.height / 2
        )
        holdbody_length = note_item.hold_length_px - this_note_img.height / 2 - this_note_img_end.height / 2
  ```
  - 绘制`Hold`尾和`Hold`身:
  ```python
  window.run_js_code(
      f"ctx.drawRotateImage(\
          {window.get_img_jsvarname(this_note_imgname_end)},\
          {holdend_x},\
          {holdend_y},\
          {Note_width},\
          {Note_width / this_note_img_end.width * this_note_img_end.height},\
          {note_to_judgeLine_rotate}\
      );",
      add_code_array = True
  )
      
  if holdbody_length > 0.0:
      window.run_js_code(
          f"ctx.drawAnchorESRotateImage(\
              {window.get_img_jsvarname(this_note_imgname_body)},\
              {holdbody_x},\
              {holdbody_y},\
              {Note_width},\
              {holdbody_length},\
              {note_to_judgeLine_rotate}\
          );",
          add_code_array = True
      )
  ```
  - 删除跳过`Hold`渲染的判断语句
```python
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
import Const

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
        
        #寻找多押
        notes = []
        for judgeLine in chart_object.judgeLineList:
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                notes.append(note)
        note_times = {}
        for note in notes:
            note:Chart_Objects_Phi.note
            if note.time not in note_times:
                note_times[note.time] = 1
            else:
                note_times[note.time] += 1
        for note in notes:
            if note_times[note.time] > 1:
                note.morebets = True
        del notes,note_times
        
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
    window.load_allimg() #加载全部由reg_img注册的资源
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

def Note_CanRender(
    x:float,y:float,
    hold_points:typing.Union[typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ],None] = None
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

def point_in_screen(point:typing.Tuple[float,float]) -> bool:
    return 0 < point[0] < w and 0 < point[1] < h

def Cal_judgeLine_NoteDy_ByTime(
    judgeLine:Chart_Objects_Phi.judgeLine,
    time:float
) -> float:
    note_dy = 0.0 #note走过的距离
    for e in judgeLine.speedEvents:
        if e.startTime <= time <= e.endTime:
            note_dy += (time - e.startTime) * judgeLine.T * e.value
        elif e.endTime <= time:
            note_dy += (e.endTime - e.startTime) * judgeLine.T * e.value
    return note_dy

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
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate, h * 5.67), #h * 5.67 是判定线的长度
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate + 180, h * 5.67),
                    lineWidth = JUDGELINE_WIDTH,
                    strokeStyle = f"rgba{judgeLine_strokeStyle}",
                    wait_execute = True
                )
            
            def process_note(
                note_item:Chart_Objects_Phi.note,
                note_face_type:typing.Literal["above","below"],
                note_dy_px:float
            ):
                this_note_sectime = note_item.time * judgeLine.T
                this_noteitem_clicked = this_note_sectime < now_t
                is_hold = note_item.type == Const.Note.HOLD
                
                if not note_item.clicked and this_noteitem_clicked:
                    note_item.clicked = True #更新clicked状态
                
                if not is_hold and note_item.clicked:
                    return None
                elif is_hold and now_t > note_item.hold_endtime:
                    return None

                note_type = {
                    Const.Note.TAP:"Tap",
                    Const.Note.DRAG:"Drag",
                    Const.Note.HOLD:"Hold",
                    Const.Note.FLICK:"Flick"
                }[note_item.type]
                
                note_to_judgeLine_px = note_item.floorPosition * PHIGROS_Y - (
                        note_dy_px
                        if not (is_hold and note_item.clicked) else ( #是Hold, 且已打击
                        Cal_judgeLine_NoteDy_ByTime(
                            judgeLine, note_item.time #计算note开始时的距离
                        ) * PHIGROS_Y + note_item.hold_length_px * (1 - ((note_item.hold_endtime - now_t) / note_item.hold_length_sec)) #计算Hold的距离
                    )
                )
                rotatenote_at_judgeLine_pos = rotate_point(
                    judgeLine_x, judgeLine_y, -judgeLine_rotate, note_item.positionX * PHIGROS_X
                ) #计算note在判定线上的位置
                judgeLine_to_note_rotate_deg = - judgeLine_rotate + (180 if note_face_type == "below" else 0) - 90 #note要相对于判定线旋转的角度
                x,y = rotate_point(
                    *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_to_judgeLine_px
                ) #计算绘制中心坐标
                
                if is_hold:
                    note_hold_draw_length = note_to_judgeLine_px + note_item.hold_length_px #计算Hold尾对于判定线的距离
                    if note_hold_draw_length >= 0: #打击未结束时
                        holdend_x,holdend_y = rotate_point(
                            *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_hold_draw_length
                        ) #计算Hold尾坐标
                    else:
                        holdend_x,holdend_y = rotatenote_at_judgeLine_pos #Hold尾坐标在判定线上
                    if note_to_judgeLine_px >= 0: #未打击时
                        holdhead_pos = x,y
                    else: #打击未结束时
                        holdhead_pos = rotatenote_at_judgeLine_pos
                    holdbody_range = ( #Hold的渲染范围
                        rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                        rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                    )
                    
                note_iscan_render = (
                    Note_CanRender(x,y)
                    if not is_hold
                    else Note_CanRender(x,y,holdbody_range)
                )
                
                if note_iscan_render:
                    note_to_judgeLine_rotate = (judgeLine_to_note_rotate_deg + 90) % 360 #计算note的旋转角度
                    dub_text = "_dub" if note_item.morebets else ""
                    if not is_hold:
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
                    
                    if not (is_hold and this_note_sectime < now_t):
                        window.run_js_code(
                            f"ctx.drawRotateImage(\
                                {window.get_img_jsvarname(this_note_imgname)},\
                                {x},\
                                {y},\
                                {Note_width},\
                                {Note_width / this_note_img.width * this_note_img.height},\
                                {note_to_judgeLine_rotate}\
                            );",
                            add_code_array = True
                        )
                    
                    if is_hold:
                        if note_item.clicked:
                            holdbody_x,holdbody_y = rotatenote_at_judgeLine_pos
                            holdbody_length = note_hold_draw_length - this_note_img_end.height / 2
                        else:
                            holdbody_x,holdbody_y = rotate_point(
                                *holdhead_pos,judgeLine_to_note_rotate_deg,this_note_img.height / 2
                            )
                            holdbody_length = note_item.hold_length_px - this_note_img.height / 2 - this_note_img_end.height / 2
                    
                        window.run_js_code(
                            f"ctx.drawRotateImage(\
                                {window.get_img_jsvarname(this_note_imgname_end)},\
                                {holdend_x},\
                                {holdend_y},\
                                {Note_width},\
                                {Note_width / this_note_img_end.width * this_note_img_end.height},\
                                {note_to_judgeLine_rotate}\
                            );",
                            add_code_array = True
                        )
                            
                        if holdbody_length > 0.0:
                            window.run_js_code(
                                f"ctx.drawAnchorESRotateImage(\
                                    {window.get_img_jsvarname(this_note_imgname_body)},\
                                    {holdbody_x},\
                                    {holdbody_y},\
                                    {Note_width},\
                                    {holdbody_length},\
                                    {note_to_judgeLine_rotate}\
                                );",
                                add_code_array = True
                            )
            note_dy = Cal_judgeLine_NoteDy_ByTime(judgeLine, chart_time)
            note_dy_px = note_dy * PHIGROS_Y
            
            for note in judgeLine.notesAbove:
                process_note(note, "above", note_dy_px)
            
            for note in judgeLine.notesBelow:
                process_note(note, "below", note_dy_px)
        
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
```

### Step 7
- 至此, 我们已经完成了判定线, Note和渲染, 让我们完成最后的打击特效渲染吧!
- 在`Init_Phigros_ChartObject`函数中为`note`添加`Hold`打击特效的随机效果度数:
  - `Hold`打击特效间隔的计算方法:`blocktime = 1 / note.master.bpm * 30`, 然后将初始化每个Hold的长度重写在此之前, 并重写其他地方的`init_holdlength`, 即使该`note`不是`Hold`
  ```python
  for note in judgeLine.notesAbove + judgeLine.notesBelow:
      note.hold_length_sec = note.holdTime * note.master.T
      note.hold_length_px = (note.speed * note.hold_length_sec) * PHIGROS_Y
      note.hold_endtime = note.time * note.master.T + note.hold_length_sec
  ```
  ```python
    if note.type == Const.Note.HOLD:
        note.effect_times = []
        hold_starttime = note.time * note.master.T #Hold开始时间
        hold_effect_blocktime = (1 / note.master.bpm * 30) #特效的间隔
        while True: #循环遍历添加
            hold_starttime += hold_effect_blocktime
            if hold_starttime >= note.hold_endtime:
                break
            note.effect_times.append((hold_starttime,get_effect_random_blocks()))
  ```
- 在`process_note`函数调用后:
  - 同时定义`ease_out`函数, 由于随机方块的扩散缓动
    ```
    def ease_out(x:float) -> float:
        return math.sqrt(1.0 - (1.0 - x) ** 2)
    ```
  - 再定义`EFFECT_RANDOM_BLOCK_SIZE`, 打击特效的随机扩散方块的大小:
    ```python
    EFFECT_RANDOM_BLOCK_SIZE = Note_width / 12.5
    ```
  ```python
  effect_time = 0.5
  for note in judgeLine.notesAbove + judgeLine.notesBelow:
      note_time = note.time * judgeLine.T #note的打击时刻
      note_ishold = note.type == Const.Note.HOLD #是否为Hold
      
      if note_time <= now_t: #note已打击
          def process(et,t,effect_random_blocks): #处理函数
              effect_process = (now_t - et) / effect_time #特效的进度
              will_show_effect_pos = judgeLine.get_datavar_move(t,w,h) #判定线的坐标
              will_show_effect_rotate = judgeLine.get_datavar_rotate(t) #判定线的旋转角度
              effect_pos = rotate_point(
                  *will_show_effect_pos,
                  -will_show_effect_rotate,
                  note.positionX * PHIGROS_X
              ) #特效的坐标
              for index,random_deg in enumerate(effect_random_blocks): #绘制随机的方块
                  block_alpha = (1.0 - effect_process) * 0.85 #方块的透明度
                  if block_alpha <= 0.0:
                      continue
                  effect_random_point = rotate_point( #特效点的坐标
                      *effect_pos,
                      random_deg + index * 90,
                      ClickEffect_Size * ease_out(effect_process) / 1.25
                  )
                  block_size = EFFECT_RANDOM_BLOCK_SIZE
                  if effect_process > 0.65: #渐渐缩小
                      block_size -= (effect_process - 0.65) * EFFECT_RANDOM_BLOCK_SIZE
                  window.create_rectangle( #绘制特效的随机方块
                      effect_random_point[0] - block_size,
                      effect_random_point[1] - block_size,
                      effect_random_point[0] + block_size,
                      effect_random_point[1] + block_size,
                      fillStyle = f"rgba{(254,255,169,block_alpha)}",
                      wait_execute = True
                  )
              window.create_image( #绘制特效的图像
                  f"Note_Click_Effect_Perfect_{int(effect_process * (30 - 1)) + 1}",
                  effect_pos[0] - ClickEffect_Size / 2,
                  effect_pos[1] - ClickEffect_Size / 2,
                  ClickEffect_Size,ClickEffect_Size,
                  wait_execute = True
              )
                      
          if now_t - note_time <= effect_time: #特效未结束
              process(note_time, note.time, note.effect_random_blocks)
          
          if note_ishold: #如果是Hold
              efct_et = note.hold_endtime + effect_time #Hold打击特效的结束时间
              if efct_et >= now_t: #如果Hold打击特效未结束
                  for temp_time,hold_effect_random_blocks in note.effect_times: #遍历Hold打击特效
                      if temp_time < now_t: #打击特效已发生
                          if now_t - temp_time <= effect_time: #打击特效未结束
                             process(temp_time, temp_time / judgeLine.T, hold_effect_random_blocks)
  ```
- 至此, 我们已经完成了所有
```python
from sys import argv
from threading import Thread
from ctypes import windll
from random import randint
from time import time
import math
import json
import typing

from PIL import Image
from win32api import GetWindowLong, SetWindowLong
import win32con

import web_canvas
import Chart_Objects_Phi
import Const

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

def ease_out(x:float) -> float:
    return math.sqrt(1.0 - (1.0 - x) ** 2)

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
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                note.hold_length_sec = note.holdTime * note.master.T
                note.hold_length_px = (note.speed * note.hold_length_sec) * PHIGROS_Y
                note.hold_endtime = note.time * note.master.T + note.hold_length_sec
                
            #为note添加Hold打击特效的随机效果度数
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                if note.type == Const.Note.HOLD:
                    note.effect_times = []
                    hold_starttime = note.time * note.master.T #Hold开始时间
                    hold_effect_blocktime = (1 / note.master.bpm * 30) #特效的间隔
                    while True: #循环遍历添加
                        hold_starttime += hold_effect_blocktime
                        if hold_starttime >= note.hold_endtime:
                            break
                        note.effect_times.append((hold_starttime,get_effect_random_blocks()))
        
        #寻找多押
        notes = []
        for judgeLine in chart_object.judgeLineList:
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                notes.append(note)
        note_times = {}
        for note in notes:
            note:Chart_Objects_Phi.note
            if note.time not in note_times:
                note_times[note.time] = 1
            else:
                note_times[note.time] += 1
        for note in notes:
            if note_times[note.time] > 1:
                note.morebets = True
        del notes,note_times
    
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
    window.load_allimg() #加载全部由reg_img注册的资源
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
    for judgeLine in chart_object.judgeLineList:
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            note.hold_length_sec = note.holdTime * note.master.T
            note.hold_length_px = (note.speed * note.hold_length_sec) * PHIGROS_Y
            note.hold_endtime = note.time * note.master.T + note.hold_length_sec

def Init_Window_Style():
    window_hwnd = window.winfo_hwnd()
    window_style = GetWindowLong(window_hwnd,win32con.GWL_STYLE)
    SetWindowLong(window_hwnd,win32con.GWL_STYLE,window_style & ~win32con.WS_SYSMENU)

def Note_CanRender(
    x:float,y:float,
    hold_points:typing.Union[typing.Tuple[
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float],
        typing.Tuple[float,float]
    ],None] = None
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

def point_in_screen(point:typing.Tuple[float,float]) -> bool:
    return 0 < point[0] < w and 0 < point[1] < h

def Cal_judgeLine_NoteDy_ByTime(
    judgeLine:Chart_Objects_Phi.judgeLine,
    time:float
) -> float:
    note_dy = 0.0 #note走过的距离
    for e in judgeLine.speedEvents:
        if e.startTime <= time <= e.endTime:
            note_dy += (time - e.startTime) * judgeLine.T * e.value
        elif e.endTime <= time:
            note_dy += (e.endTime - e.startTime) * judgeLine.T * e.value
    return note_dy

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
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate, h * 5.67), #h * 5.67 是判定线的长度
                    *rotate_point(judgeLine_x, judgeLine_y, - judgeLine_rotate + 180, h * 5.67),
                    lineWidth = JUDGELINE_WIDTH,
                    strokeStyle = f"rgba{judgeLine_strokeStyle}",
                    wait_execute = True
                )
            
            def process_note(
                note_item:Chart_Objects_Phi.note,
                note_face_type:typing.Literal["above","below"],
                note_dy_px:float
            ):
                this_note_sectime = note_item.time * judgeLine.T
                this_noteitem_clicked = this_note_sectime < now_t
                is_hold = note_item.type == Const.Note.HOLD
                
                if not note_item.clicked and this_noteitem_clicked:
                    note_item.clicked = True #更新clicked状态
                
                if not is_hold and note_item.clicked:
                    return None
                elif is_hold and now_t > note_item.hold_endtime:
                    return None

                note_type = {
                    Const.Note.TAP:"Tap",
                    Const.Note.DRAG:"Drag",
                    Const.Note.HOLD:"Hold",
                    Const.Note.FLICK:"Flick"
                }[note_item.type]
                
                note_to_judgeLine_px = note_item.floorPosition * PHIGROS_Y - (
                        note_dy_px
                        if not (is_hold and note_item.clicked) else ( #是Hold, 且已打击
                        Cal_judgeLine_NoteDy_ByTime(
                            judgeLine, note_item.time #计算note开始时的距离
                        ) * PHIGROS_Y + note_item.hold_length_px * (1 - ((note_item.hold_endtime - now_t) / note_item.hold_length_sec)) #计算Hold的距离
                    )
                )
                rotatenote_at_judgeLine_pos = rotate_point(
                    judgeLine_x, judgeLine_y, -judgeLine_rotate, note_item.positionX * PHIGROS_X
                ) #计算note在判定线上的位置
                judgeLine_to_note_rotate_deg = - judgeLine_rotate + (180 if note_face_type == "below" else 0) - 90 #note要相对于判定线旋转的角度
                x,y = rotate_point(
                    *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_to_judgeLine_px
                ) #计算绘制中心坐标
                
                if is_hold:
                    note_hold_draw_length = note_to_judgeLine_px + note_item.hold_length_px #计算Hold尾对于判定线的距离
                    if note_hold_draw_length >= 0: #打击未结束时
                        holdend_x,holdend_y = rotate_point(
                            *rotatenote_at_judgeLine_pos, judgeLine_to_note_rotate_deg, note_hold_draw_length
                        ) #计算Hold尾坐标
                    else:
                        holdend_x,holdend_y = rotatenote_at_judgeLine_pos #Hold尾坐标在判定线上
                    if note_to_judgeLine_px >= 0: #未打击时
                        holdhead_pos = x,y
                    else: #打击未结束时
                        holdhead_pos = rotatenote_at_judgeLine_pos
                    holdbody_range = ( #Hold的渲染范围
                        rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg - 90, Note_width / 2),
                        rotate_point(holdend_x, holdend_y, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                        rotate_point(*holdhead_pos, judgeLine_to_note_rotate_deg + 90, Note_width / 2),
                    )
                    
                note_iscan_render = (
                    Note_CanRender(x,y)
                    if not is_hold
                    else Note_CanRender(x,y,holdbody_range)
                )
                
                if note_iscan_render:
                    note_to_judgeLine_rotate = (judgeLine_to_note_rotate_deg + 90) % 360 #计算note的旋转角度
                    dub_text = "_dub" if note_item.morebets else ""
                    if not is_hold:
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
                    
                    if not (is_hold and this_note_sectime < now_t):
                        window.run_js_code(
                            f"ctx.drawRotateImage(\
                                {window.get_img_jsvarname(this_note_imgname)},\
                                {x},\
                                {y},\
                                {Note_width},\
                                {Note_width / this_note_img.width * this_note_img.height},\
                                {note_to_judgeLine_rotate}\
                            );",
                            add_code_array = True
                        )
                    
                    if is_hold:
                        if note_item.clicked:
                            holdbody_x,holdbody_y = rotatenote_at_judgeLine_pos
                            holdbody_length = note_hold_draw_length - this_note_img_end.height / 2
                        else:
                            holdbody_x,holdbody_y = rotate_point(
                                *holdhead_pos,judgeLine_to_note_rotate_deg,this_note_img.height / 2
                            )
                            holdbody_length = note_item.hold_length_px - this_note_img.height / 2 - this_note_img_end.height / 2
                    
                        window.run_js_code(
                            f"ctx.drawRotateImage(\
                                {window.get_img_jsvarname(this_note_imgname_end)},\
                                {holdend_x},\
                                {holdend_y},\
                                {Note_width},\
                                {Note_width / this_note_img_end.width * this_note_img_end.height},\
                                {note_to_judgeLine_rotate}\
                            );",
                            add_code_array = True
                        )
                            
                        if holdbody_length > 0.0:
                            window.run_js_code(
                                f"ctx.drawAnchorESRotateImage(\
                                    {window.get_img_jsvarname(this_note_imgname_body)},\
                                    {holdbody_x},\
                                    {holdbody_y},\
                                    {Note_width},\
                                    {holdbody_length},\
                                    {note_to_judgeLine_rotate}\
                                );",
                                add_code_array = True
                            )
            note_dy = Cal_judgeLine_NoteDy_ByTime(judgeLine, chart_time)
            note_dy_px = note_dy * PHIGROS_Y
            
            for note in judgeLine.notesAbove:
                process_note(note, "above", note_dy_px)
            
            for note in judgeLine.notesBelow:
                process_note(note, "below", note_dy_px)
            
            effect_time = 0.5
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                note_time = note.time * judgeLine.T #note的打击时刻
                note_ishold = note.type == Const.Note.HOLD #是否为Hold
                
                if note_time <= now_t: #note已打击
                    def process(et,t,effect_random_blocks): #处理函数
                        effect_process = (now_t - et) / effect_time #特效的进度
                        
                        will_show_effect_pos = 0.0,0.0 #计算判定线的坐标
                        will_show_effect_rotate = 0.0 #计算判定线的旋转角度
                        for e in judgeLine.judgeLineMoveEvents:
                            if e.startTime <= t <= e.endTime:
                                will_show_effect_pos = (
                                    linear_interpolation(t, e.startTime, e.endTime, e.start, e.end) * w,
                                    h - linear_interpolation(t, e.startTime, e.endTime, e.start2, e.end2) * h
                                )
                                break
                        for e in judgeLine.judgeLineRotateEvents:
                            if e.startTime <= t <= e.endTime:
                                will_show_effect_rotate = linear_interpolation(t, e.startTime, e.endTime, e.start, e.end)
                                break
                        
                        effect_pos = rotate_point(
                            *will_show_effect_pos,
                            -will_show_effect_rotate,
                            note.positionX * PHIGROS_X
                        ) #特效的坐标
                        for index,random_deg in enumerate(effect_random_blocks): #绘制随机的方块
                            block_alpha = (1.0 - effect_process) * 0.85 #方块的透明度
                            if block_alpha <= 0.0:
                                continue
                            effect_random_point = rotate_point( #特效点的坐标
                                *effect_pos,
                                random_deg + index * 90,
                                ClickEffect_Size * ease_out(effect_process) / 1.25
                            )
                            block_size = EFFECT_RANDOM_BLOCK_SIZE
                            if effect_process > 0.65: #渐渐缩小
                                block_size -= (effect_process - 0.65) * EFFECT_RANDOM_BLOCK_SIZE
                            window.create_rectangle( #绘制特效的随机方块
                                effect_random_point[0] - block_size,
                                effect_random_point[1] - block_size,
                                effect_random_point[0] + block_size,
                                effect_random_point[1] + block_size,
                                fillStyle = f"rgba{(254,255,169,block_alpha)}",
                                wait_execute = True
                            )
                        window.create_image( #绘制特效的图像
                            f"Note_Click_Effect_Perfect_{int(effect_process * (30 - 1)) + 1}",
                            effect_pos[0] - ClickEffect_Size / 2,
                            effect_pos[1] - ClickEffect_Size / 2,
                            ClickEffect_Size,ClickEffect_Size,
                            wait_execute = True
                        )
                                
                    if now_t - note_time <= effect_time: #特效未结束
                        process(note_time, note.time, note.effect_random_blocks)
                    
                    if note_ishold: #如果是Hold
                        efct_et = note.hold_endtime + effect_time #Hold打击特效的结束时间
                        if efct_et >= now_t: #如果Hold打击特效未结束
                            for temp_time,hold_effect_random_blocks in note.effect_times: #遍历Hold打击特效
                                if temp_time < now_t: #打击特效已发生
                                    if now_t - temp_time <= effect_time: #打击特效未结束
                                        process(temp_time, temp_time / judgeLine.T, hold_effect_random_blocks)
        
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
EFFECT_RANDOM_BLOCK_SIZE = Note_width / 12.5 #打击特效的随机扩散方块的大小
Thread(target = Main, daemon = True).start() #开始渲染
window.loop_to_close()
windll.kernel32.ExitProcess(0)
```

## PhigrosPlayer Extend / PhigrosPlayer 扩展
- `-extend <python_file>`参数的使用
- `PhigrosPlayer_Extend.update`方法会在每一次计算完成渲染数据时调用 (only phi chart)
- 示例(禁用ui):
  ```python
  import typing

  class PhigrosPlayer_Extend:
      def __init__(
          self,
          get_globals: typing.Callable[[], typing.Any]
      ) -> None:
          self._get_globals = get_globals
      
      def globals(self):
          return self._get_globals()
      
      def update(self, locals_dict):
          task = locals_dict["Task"]
          task.RenderTasks = [i for i in task.RenderTasks if i.func.__name__ != "draw_ui"]
      
      def __getattribute__(self, name: str) -> typing.Any:
          try:
              return object.__getattribute__(self, name)
          except AttributeError:
              return lambda *args, **kwargs: None
  ```

## 些许可能代码会存在误解的地方
- `Chart_Functions_Rep` 和 `Chart_Objects_Rep` 中`Note`的`width`属性为`JSON`数据中的`size`

## 一些使用技巧
- 在使用命令行参数并要使用一些值时, 可输入 `Python` 的表达式, 也可使用 `Const` 模块的一些值, 如: `Const.INF` 等等...