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

一些关于谱面的概念:
- 对于谱面的时间的现实时间的转化: `sec = t * (1.875 / bpm)`
  
- 定义的一些概念:
    - `PHIGROS_X` & `PHIGROS_Y` 假设此时屏幕的大小为`w,h`
    则: `PHIGROS_X, PHIGROS_Y = 0.05625 * w, 0.6 * h`

对于谱面数据对象的含义  注: `bpm` 变量为 `note` 所处判定线的 `bpm`：
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
            self:note
            
            length_sec = self.holdTime * (1.875 / bpm)
            length_px = self.speed * length_sec * PHIGROS_Y
            ```
        - 结束时间: 
          ```python
          self:note
          
          hold_endtime = (self.time + self.holdTime) * (1.875 / bpm)
          ```
    - `speed:typing.Union[int,float]` `note` 的速度
        - 用处仅在 `Hold` 音符的长度和打击时速度的计算
        - 对于还未打击的音符, 速度以对`speedEvent`插值的到的实时速度值为准
    - `floorPosition:typing.Union[int,float]` 在谱面时间为`0`时, `note` 对于判定线的高度, 单位为`PHIGROS_Y`
        - 作用仅为方便计算

- `class speedEvent`
    - `startTime:typing.Union[int,float]` 事件开始时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `endTime:typing.Union[int,float]` 事件结束时的时间
      转化为秒: `sec = startTime * (1.875 / bpm)`
    - `value:typing.Union[int,float]` 在事件开始时间到结束时间范围内的速度值, 单位为 `PHIGROS_Y / s`

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

对于事件：
- 应当连续 即: `es[index].endTime == es[index + 1].startTime`
- 第一个事件的开始时间应当足够的小
- 最后个事件的结束时间应当足够的大

事件值的计算:
- 事件皆为线性事件

... 还没写完

## 一些使用技巧
- 在使用命令行参数并要使用一些值时, 可输入 `Python` 的表达式, 也可使用 `Const` 模块的一些值, 如: `Const.INF` 等等...