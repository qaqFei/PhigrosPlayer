from __future__ import annotations
from dataclasses import dataclass
import typing

import rpe_easing
import Tool_Functions
import Const

@dataclass
class note:
    time: float
    type: typing.Literal[1, 2, 3, 4]
    holdtime: float
    positionX: float
    speed: float # noly hold
    fake: bool
    above: bool
    
    morebets: bool = False
    
    def __post_init__(self):
        self.type_string = {
            Const.Note.TAP: "Tap",
            Const.Note.DRAG: "Drag",
            Const.Note.HOLD: "Hold",
            Const.Note.FLICK: "Flick"
        }[self.type]
    
@dataclass
class speedEvent:
    startTime: float
    endTime: float
    value: float

@dataclass
class alphaEvent:
    startTime: float
    endTime: float
    start: float
    end: float
    easingType: int

@dataclass
class moveEvent:
    startTime: float
    endTime: float
    startX: float
    startY: float
    endX: float
    endY: float
    easingType: int

@dataclass
class rotateEvent:
    startTime: float
    endTime: float
    start: float
    end: float
    easingType: int

@dataclass
class judgeLine:
    bpm: float
    notes: list[note]
    speedEvents: list[speedEvent]
    alphaEvents: list[alphaEvent]
    moveEvents: list[moveEvent]
    rotateEvents: list[rotateEvent]
    
    def getAlpha(self, t: float) -> float:
        for e in self.alphaEvents:
            if e.startTime <= t <= e.endTime:
                return Tool_Functions.easing_interpolation(
                    t, e.startTime, e.endTime,
                    e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1]
                )
        return 0.0
    
    def getMove(self, t: float) -> tuple[float, float]:
        for e in self.moveEvents:
            if e.startTime <= t <= e.endTime:
                return (
                    Tool_Functions.easing_interpolation(
                        t, e.startTime, e.endTime,
                        e.startX, e.endX, rpe_easing.ease_funcs[e.easingType - 1]
                    ),
                    1.0 - Tool_Functions.easing_interpolation(
                        t, e.startTime, e.endTime,
                        e.startY, e.endY, rpe_easing.ease_funcs[e.easingType - 1]
                    )
                )
        return 0.0, 0.0

    def getRotate(self, t: float) -> float:
        for e in self.rotateEvents:
            if e.startTime <= t <= e.endTime:
                return Tool_Functions.easing_interpolation(
                    t, e.startTime, e.endTime,
                    e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1]
                )
        return 0.0
    
    def _getFloorPosition(self, lineTime: float):
        fp = 0.0
        bTime = 1 / self.bpm
        for e in self.speedEvents:
            if e.startTime <= lineTime <= e.endTime:
                fp += (lineTime - e.startTime) * bTime * e.value
            elif e.endTime < lineTime:
                fp += (e.endTime - e.startTime) * bTime * e.value
        return fp
    
    def getNoteFloorPosition(self, lineTime: float, note: note):
        return self._getFloorPosition(note.time) - self._getFloorPosition(lineTime)

@dataclass
class Chart:
    lines: list[judgeLine]