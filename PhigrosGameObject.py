from dataclasses import dataclass
from random import uniform
import typing
import time

from PIL import Image

import Tool_Functions
import Const
import rpe_easing

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
    
    def __post_init__(self):
        self._ease_fast = rpe_easing.ease_funcs[11]
        self._ease_slow = rpe_easing.ease_funcs[12]
        self._atime = 0.65
    
    def getBarWidth(self):
        sv = Const.PHIGROS_SETTING_BAR_WIDTH_MAP[self.aFrom]
        ev = Const.PHIGROS_SETTING_BAR_WIDTH_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self._atime
        p = (time.time() - st) / (et - st)
        p = Tool_Functions.fixOutofRangeP(p)
        p = self._ease_slow(p)
        return p * (ev - sv) + sv
    
    def getLabelWidth(self):
        sv = Const.PHIGROS_SETTING_LABEL_WIDTH_MAP[self.aFrom]
        ev = Const.PHIGROS_SETTING_LABEL_WIDTH_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self._atime
        p = (time.time() - st) / (et - st)
        p = Tool_Functions.fixOutofRangeP(p)
        p = self._ease_fast(p)
        return p * (ev - sv) + sv
    
    def getLabelX(self):
        sv = Const.PHIGROS_SETTING_LABEL_X_MAP[self.aFrom]
        ev = Const.PHIGROS_SETTING_LABEL_X_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self._atime
        p = (time.time() - st) / (et - st)
        p = Tool_Functions.fixOutofRangeP(p)
        p = self._ease_slow(p)
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
            et = self.aSTime + self._atime
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
    
    def getTextScale(self, t: int):
        if t not in (self.aFrom, self.aTo):
            return 1.0
        elif self.aSTime == float("-inf"):
            return 1.175
        else:
            st = self.aSTime
            et = self.aSTime + self._atime
            p = (time.time() - st) / (et - st)
            p = Tool_Functions.fixOutofRangeP(p)
            p = self._ease_slow(p)
            
            return Tool_Functions.linear_interpolation(p, 0.0, 1.0, 1.175, 1.0) if self.aFrom == t else Tool_Functions.linear_interpolation(p, 0.0, 1.0, 1.0, 1.175)
    
    def getShadowRect(self):
        sv = Const.PHIGROS_SETTING_SHADOW_XRECT_MAP[self.aFrom]
        ev = Const.PHIGROS_SETTING_SHADOW_XRECT_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self._atime
        p = (time.time() - st) / (et - st)
        p = Tool_Functions.fixOutofRangeP(p)
        p = self._ease_slow(p)
        return (
            p * (ev[0] - sv[0]) + sv[0],
            p * (ev[1] - sv[1]) + sv[1]
        )
        
    def changeState(self, state: int):
        self.aFrom, self.aTo = self.aTo, state
        self.aSTime = time.time()
    
    def getSettingDx(self, shadowRectLeft: float, w: int, t: int):
        return (Const.PHIGROS_SETTING_SHADOW_XRECT_MAP[t][0] - shadowRectLeft) * w
        
    def render(
        self,
        drawPlaySetting: typing.Callable[[float, float], None],
        drawAccountAndCountSetting: typing.Callable[[float, float], None],
        drawOtherSetting: typing.Callable[[float, float], None],
        shadowRectLeft: float, w: int,
        settingDx: list[float]
    ):
        sp_state = self.aFrom == self.aTo # before user change ui state
        if sp_state:
            self.aFrom = Const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT
            self.aTo = Const.PHIGROS_SETTING_STATE.PLAY
        
        st = self.aSTime
        et = self.aSTime + self._atime
        p = (time.time() - st) / (et - st) if self.aSTime != float("-inf") else 1.0
        p = Tool_Functions.fixOutofRangeP(p)
        p = self._ease_slow(p)
        
        drawPlaySettingDx = self.getSettingDx(shadowRectLeft, w, Const.PHIGROS_SETTING_STATE.PLAY)
        drawAccountAndCountSettingDx = self.getSettingDx(shadowRectLeft, w, Const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT)
        drawOtherSettingDx = self.getSettingDx(shadowRectLeft, w, Const.PHIGROS_SETTING_STATE.OTHER)

        drawPlaySettingAlpha = 0.0 if Const.PHIGROS_SETTING_STATE.PLAY not in (self.aFrom, self.aTo) else ((1.0 - p) if self.aFrom == Const.PHIGROS_SETTING_STATE.PLAY else p)
        drawAccountAndCountSettingAlpha = 0.0 if Const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT not in (self.aFrom, self.aTo) else ((1.0 - p) if self.aFrom == Const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT else p)
        drawOtherSettingAlpha = 0.0 if Const.PHIGROS_SETTING_STATE.OTHER not in (self.aFrom, self.aTo) else ((1.0 - p) if self.aFrom == Const.PHIGROS_SETTING_STATE.OTHER else p)

        drawPlaySetting(drawPlaySettingDx, drawPlaySettingAlpha)
        drawAccountAndCountSetting(drawAccountAndCountSettingDx, drawAccountAndCountSettingAlpha)
        drawOtherSetting(drawOtherSettingDx, drawOtherSettingAlpha)
        settingDx.clear()
        settingDx.extend([drawPlaySettingDx, drawAccountAndCountSettingDx, drawOtherSettingDx])
        
        if sp_state:
            self.aFrom = Const.PHIGROS_SETTING_STATE.PLAY
            self.aTo = Const.PHIGROS_SETTING_STATE.PLAY

@dataclass
class PhiBaseWidget:
    padding_top: float = 0.0
    padding_bottom: float = 0.0
    tonext: float = 0.0
    
@dataclass
class PhiLabel(PhiBaseWidget):
    left_text: str = ""
    right_text: str = ""
    fontsize: float = 1.0
    color: str = "#FFFFFF"
    
@dataclass
class PhiSlider(PhiBaseWidget):
    value: float = 0.0
    number_points: tuple[tuple[float, float]] = ((0.0, 0.0), (1.0, 1.0))
    lr_button: bool = False

@dataclass
class PhiCheckbox(PhiBaseWidget):
    text: str = ""
    fontsize: float = 1.0
    checked: bool = False
    
    check_animation_st: float = float("-inf")