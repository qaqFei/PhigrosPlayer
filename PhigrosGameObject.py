from dataclasses import dataclass
from random import uniform
import typing
import time

from PIL import Image

import Tool_Functions
import Const

@dataclass
class ClickEvent:
    rect: tuple[float, float, float, float]
    callback: typing.Callable[[int, int], typing.Any]
    once: bool
    tag: str|None = None
    
    def __hash__(self) -> int:
        return id(self)

@dataclass
class MoveEvent:
    callback: typing.Callable[[int, int], typing.Any]
    tag: str|None = None
    
    def __hash__(self) -> int:
        return id(self)
    
@dataclass
class ReleaseEvent:
    callback: typing.Callable[[int, int], typing.Any]
    tag: str|None = None

    def __hash__(self) -> int:
        return id(self)

@dataclass
class EventManager:
    def __init__(self) -> None:
        self.clickEvents: list[ClickEvent] = []
        self.moveEvents: list[MoveEvent] = []
        self.releaseEvents: list[ReleaseEvent] = []
    
    def _callClickCallback(self, e: ClickEvent, x: int, y: int) -> None:
        if Tool_Functions.InRect(x, y, e.rect):
            e.callback(x, y)
            if e.once:
                self.unregEvent(e)
    
    def click(self, x: int, y: int) -> None:
        for e in self.clickEvents:
            self._callClickCallback(e, x, y)
    
    def move(self, x: int, y: int) -> None:
        for e in self.moveEvents:
            e.callback(x, y)
    
    def release(self, x: int, y: int) -> None:
        for e in self.releaseEvents:
            e.callback(x, y)
    
    def regClickEvent(self, e: ClickEvent):
        self.clickEvents.append(e)
    
    def regMoveEvent(self, e: MoveEvent):
        self.moveEvents.append(e)

    def regReleaseEvent(self, e: ReleaseEvent):
        self.releaseEvents.append(e)
    
    def regClickEventFs(self, callback: typing.Callable[[int, int], typing.Any], once: bool):
        e = ClickEvent((0, 0, float("inf"), float("inf")), callback, once)
        self.regClickEvent(e)
        return e
    
    def unregEvent(self, e: ClickEvent):
        for elist in [self.clickEvents, self.moveEvents, self.releaseEvents]:
            try:
                elist.remove(e)
            except ValueError:
                pass

@dataclass
class FaculaAnimationManager:
    def __init__(self) -> None:
        self.faculas = []
    
    def main(self):
        self._createFacula()
        self._createFacula()
        while True:
            time.sleep(uniform(0.35, 1.25))
            self._createFacula()
            for facula in self.faculas:
                if facula["endTime"] < time.time():
                    self.faculas.remove(facula)
    
    def getFaculaState(self, facula: dict) -> dict:
        p = (time.time() - facula["startTime"]) / (facula["endTime"] - facula["startTime"]) # cannot use Tool_Functions.linear_interpolation, it will return 0.0, i tkink is jit bug?. or f32 precision problem?
        if p <= 0.2:
            ep = 1.0 - (1.0 - (p / 0.2)) ** 2
        elif p <= 0.8:
            ep = 1.0
        else:
            ep = (1.0 - (p - 0.8) / 0.2) ** 2
        
        return {
            "y": facula["sy"] + (facula["ey"] - facula["sy"]) * p,
            "size": ep * facula["size"],
            "alpha": ep
        }
            
    def _createFacula(self):
        sy = uniform(0.0, 1.0)
        self.faculas.append({
            "startTime": time.time(),
            "endTime": time.time() + uniform(5.0, 7.0),
            "x": uniform(0.05, 0.95),
            "sy": sy,
            "ey": sy - uniform(0.5, 0.7),
            "size": uniform(0.7, 1.3)
        })

@dataclass
class SongDifficlty:
    name: str
    level: str
    chart: str

@dataclass
class Song:
    name: str
    composer: str
    image: str
    preview: str
    difficlty: list[SongDifficlty]

@dataclass
class Chapter:
    name: str
    cn_name: str
    o_name: str
    image: str
    songs: list[Song]
    im: None|Image.Image = None
    
    def __post_init__(self):
        self.chapterId = int(uniform(0.0, 1.0) * (2 << 31))
    
    def __hash__(self):
        return id(self)

@dataclass
class Chapters:
    items: list[Chapter]
    aFrom: int = -1
    aTo: int = 0
    aSTime: float = float("-inf")

@dataclass
class Setting:
    offset: int = 0 # ms, -400 ~ 600
    scale: float = 1.0 # 1.0 ~ 1.3
    background_dim: float = 1.0 # 0.2 ~ 1.0 (?)
    enable_click_sound: bool = True
    sound_volume: float = 1.0 # 0.0 ~ 1.0
    ui_volume: float = 1.0 # 0.0 ~ 1.0
    click_sound_volume: float = 1.0 # 0.0 ~ 1.0
    moerbets_auxiliary: bool = True
    fcap_indicator: bool = True
    low_quality: bool = False
    
@dataclass
class SettingState:
    aFrom: int = Const.PHIGROS_SETTING_STATE.PLAY
    aTo: int = Const.PHIGROS_SETTING_STATE.PLAY
    aSTime: float = float("-inf")
    
    # cannot use tfunc.lerp, ... dub float overflow.
    
    def __post_init__(self):
        from threading import Thread
        Thread(target=self._i, daemon=True).start()

    def _i(self):
        while 1:
            self.changeState(2)
            time.sleep(1.2)
            self.changeState(1)
            time.sleep(1.2)
            self.changeState(3)
            time.sleep(1.2)
            self.changeState(1)
            time.sleep(1.2)
            self.changeState(2)
            time.sleep(1.2)
            self.changeState(3)
            time.sleep(1.2)
            self.changeState(2)
            time.sleep(1.2)
            self.changeState(1)
            time.sleep(1.2)
    
    def getBarWidth(self):
        sv = Const.PHIGROS_SETTING_BAR_WIDTH_MAP[self.aFrom]
        ev = Const.PHIGROS_SETTING_BAR_WIDTH_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + 0.75
        p = (time.time() - st) / (et - st)
        p = Tool_Functions.fixOutofRangeP(p)
        p = (1.0 - (1.0 - p) ** 3)
        return p * (ev - sv) + sv
    
    def getLabelWidth(self):
        sv = Const.PHIGROS_SETTING_LABEL_WIDTH_MAP[self.aFrom]
        ev = Const.PHIGROS_SETTING_LABEL_WIDTH_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + 0.75
        p = (time.time() - st) / (et - st)
        p = Tool_Functions.fixOutofRangeP(p)
        p = (1.0 - (1.0 - p) ** 4)
        return p * (ev - sv) + sv
    
    def getLabelX(self):
        sv = Const.PHIGROS_SETTING_LABEL_X_MAP[self.aFrom]
        ev = Const.PHIGROS_SETTING_LABEL_X_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + 0.75
        p = (time.time() - st) / (et - st)
        p = Tool_Functions.fixOutofRangeP(p)
        p = (1.0 - (1.0 - p) ** 3)
        return p * (ev - sv) + sv
    
    def _lerFromTextColor(self, p: float):
        return (255 * p, ) * 3
    
    def _lerToTextColor(self, p: float):
        return (255 * (1.0 - p), ) * 3
    
    def getTextColor(self, t: int):
        if t not in (self.aFrom, self.aTo):
            return (255, 255, 255)
        elif self.aSTime == float("-inf"):
            return (0, 0, 0) # aFrom and aTo is 1
        else:
            st = self.aSTime
            et = self.aSTime + 0.75
            p = (time.time() - st) / (et - st)
            p = Tool_Functions.fixOutofRangeP(p)
            
            # 这里奇怪的算法: 为了视觉上好看和还原一点
            absv = abs(self.aFrom - self.aTo) if self.aFrom != self.aTo else 1.0
            absv += 0.5
            absv **= 1.25
            if t == self.aFrom:
                p = 1.0 - (1.0 - p) ** absv
            else:
                p = 1.0 - (1.0 - p) ** (1 / absv)
                
            return self._lerFromTextColor(p) if self.aFrom == t else self._lerToTextColor(p)
    
    def changeState(self, state: int):
        self.aFrom, self.aTo = self.aTo, state
        self.aSTime = time.time()