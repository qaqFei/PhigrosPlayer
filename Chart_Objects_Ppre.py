from __future__ import annotations
from dataclasses import dataclass
import typing

@dataclass
class note:
    time: tuple[int, int, int]
    type: typing.Literal[1, 2, 3, 4]
    holdtime: tuple[int, int, int]
    positionX: float
    fake: bool

@dataclass
class speedEvent:
    startTime: tuple[int, int, int]
    endTime: tuple[int, int, int]
    start: float
    end: float

@dataclass
class alphaEvent:
    startTime: tuple[int, int, int]
    endTime: tuple[int, int, int]
    start: float
    end: float
    easingType: int

@dataclass
class moveEvent:
    startTime: tuple[int, int, int]
    endTime: tuple[int, int, int]
    startX: float
    startY: float
    endX: float
    endY: float
    easingType: int

@dataclass
class rotateEvent:
    startTime: tuple[int, int, int]
    endTime: tuple[int, int, int]
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

@dataclass
class Chart:
    lines: list[judgeLine]