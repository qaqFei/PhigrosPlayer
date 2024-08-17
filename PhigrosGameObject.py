from dataclasses import dataclass
from random import uniform
import typing
import time

import Tool_Functions

buttonType = typing.Literal[0, 1, 2] | None

@dataclass
class ClickEvent:
    button: buttonType
    rect: tuple[float, float, float, float]
    callback: typing.Callable[[int, int, buttonType], typing.Any]
    once: bool
    
    def __hash__(self) -> int:
        return id(self)

@dataclass
class EventManager:
    def __init__(self) -> None:
        self.clickEvents: list[ClickEvent] = []
    
    def _callClickCallback(self, e: ClickEvent, x: int, y: int, button: buttonType) -> None:
        if Tool_Functions.InRect(x, y, e.rect) and (e.button is None or e.button == button):
            e.callback(x, y, button)
            if e.once:
                self.unregClickEvent(e)
    
    def click(self, x: int, y: int, button: buttonType) -> None:
        for e in self.clickEvents:
            self._callClickCallback(e, x, y, button)
    
    def regClickEvent(self, e: ClickEvent):
        self.clickEvents.append(e)
    
    def regClickEventFs(self, callback: typing.Callable[[int, int, buttonType], typing.Any], button: buttonType, once: bool):
        e = ClickEvent(button, (0, 0, float("inf"), float("inf")), callback, once)
        self.regClickEvent(e)
        return e
    
    def unregClickEvent(self, e: ClickEvent):
        self.clickEvents.remove(e)

@dataclass
class FaculaAnimationManager:
    def __init__(self) -> None:
        self.faculas = []
        self.stop = False
    
    def main(self):
        self._createFacula()
        self._createFacula()
        while not self.stop:
            time.sleep(uniform(0.05, 1.5))
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
        sy = uniform(0.0, 0.8)
        self.faculas.append({
            "startTime": time.time(),
            "endTime": time.time() + uniform(5.0, 7.0),
            "x": uniform(0.05, 0.95),
            "sy": sy,
            "ey": sy - uniform(0.5, 0.7),
            "size": uniform(0.7, 1.3)
        })