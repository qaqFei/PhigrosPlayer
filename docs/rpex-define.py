
from __future__ import annotations

import math
import typing
from dataclasses import dataclass, field

number = int | float

def easing(t: number, sv: number, ev: number, st: number, et: number, ef: typing.Callable[[number], number]) -> number:
    return sv + (ev - sv) * ef((t - st) / (et - st))

@dataclass
class RpexChart:
    formatVersion: int = 1
    enableSahder: bool = False
    offset: int = 0

    easingDefinitions: list[EasingDefinitionItem] = field(default_factory=list)
    shaderDefinitions: list[shaderDefinitionItem] = field(default_factory=list)
    textureDefinitions: list[TextureDefinitionItem] = field(default_factory=list)
    audioDefinitions: list[AudioDefinitionItem] = field(default_factory=list)
    noteAnimationDefinitions: list[NoteAnimationDefinitionItem] = field(default_factory=list)

    bpmList: list[BpmItem] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)

    def __post_init__(self):
        for i, f in enumerate(EASING_FUNCS):
            self.easingDefinitions.append(EasingDefinitionItem(i + 1, False, None, f))

@dataclass
class Beat:
    v1: number = 0
    v2: number = 0
    v3: number = 1

    def __post_init__(self):
        self.value = self.v1 + self.v2 / self.v3
    
    def __hash__(self):
        return hash(self.value)
    
    def __eq__(self, other: object):
        return self.value == other.value if isinstance(other, type(self)) else NotImplemented
    
    def __setattr__(self, n: str, v: object):
        if n in ("v1", "v2", "v3", "value"):
            raise AttributeError("Beat is immutable")
        return super().__setattr__(n, v)

@dataclass
class EasingDefinitionItem:
    easingType: int = -1
    enableBezier: bool = False
    bezierPoints: list[number]|None = None

    _pyFunction: typing.Callable[[number], number]|None = None

    def _bezier(self, t: number, p1: number, p2: number) -> number:
        return p1 + (p2 - p1) * t
    
    def getValue(self, x: number) -> number:
        if self.enableBezier:
            points = self.bezierPoints
            while len(points) > 1:
                points = [self._bezier(x, points[i], points[i + 1]) for i in range(len(points) - 1)]
            return points[0]

        elif self._pyFunction is not None:
            return self._pyFunction(x)
        else:
            return x

@dataclass
class shaderDefinitionItem:
    shaderName: str = ""
    isBuiltin: bool = True
    shaderFilePath: str = "/default-unknow.glsl"

@dataclass
class TextureDefinitionItem:
    textureName: str = ""
    textureFilePath: str = "/default-unknow.png"

@dataclass
class AudioDefinitionItem:
    audioName: str = ""
    audioFilePath: str = "/default-unknow.wav"

@dataclass
class NoteAnimationDefinitionItem:
    noteTag: str = ""
    scaleAlphaEvents: list[RpexEvent] = field(default_factory=list)
    scaleRotateEvents: list[RpexEvent] = field(default_factory=list)
    dAlphaEvents: list[RpexEvent] = field(default_factory=list)
    dScaleXEvents: list[RpexEvent] = field(default_factory=list)
    dScaleYEvents: list[RpexEvent] = field(default_factory=list)
    dRotateEvents: list[RpexEvent] = field(default_factory=list)

@dataclass
class BpmItem:
    startBeat: Beat = Beat()
    bpm: number = 120

@dataclass
class Line:
    textureName: str = ""
    bpmfactor: number = 1.0
    lineType: typing.Literal["judgeLine", "textureLine", "textLine", "attachUILine"] = "judgeLine"
    isCover: bool = True
    attachUIName: str = ""
    father: int = -1
    zOrder: int = 0
    notes: list[Note] = field(default_factory=list)

    eventLayers: list[LineEventLayer] = field(default_factory=list)

@dataclass
class Note:
    time: Beat = Beat()
    holdTime: Beat = Beat()
    noteType: typing.Literal[1, 2, 3, 4] = 1
    noteTags: list[str] = field(default_factory=list)
    positionX: number = 0.0
    isAbove: bool = True
    isFake: bool = False
    yOffset: number = 0.0
    visibleTime: number|None = None

    scaleAlpha: number = 1.0
    scaleX: number = 1.0
    scaleY: number = 1.0

    dAlpha: number = 0.0
    dScaleX: number = 0.0
    dScaleY: number = 0.0

@dataclass
class LineEventLayer:
    alphaEvents: list[RpexEvent] = field(default_factory=list)
    rotateEvents: list[RpexEvent] = field(default_factory=list)
    moveXEvents: list[RpexEvent] = field(default_factory=list)
    moveYEvents: list[RpexEvent] = field(default_factory=list)

    scaleXEvents: list[RpexEvent] = field(default_factory=list) # only first layer
    scaleYEvents: list[RpexEvent] = field(default_factory=list) # only first layer
    textEvents: list[RpexEvent] = field(default_factory=list) # only first layer
    colorEvents: list[RpexEvent] = field(default_factory=list) # only first layer

    alphaDefault: number = 0.0
    rotateDefault: number = 0.0
    moveXDefault: number = 0.0
    moveYDefault: number = 0.0
    scaleXDefault: number = 1.0
    scaleYDefault: number = 1.0
    textDefault: str = ""
    colorDefault: list[number, number, number] = field(default_factory=lambda: list([1.0, 1.0, 1.0]))
    
    def getValue(self, t: number, isfirst: bool):
        alpha, rotate, x, y = self.alphaDefault, self.rotateDefault, self.moveXDefault, self.moveYDefault

RpexEventT = typing.TypeVar("RpexEventT")

@dataclass
class RpexEvent(typing.Generic[RpexEventT]):
    startTime: Beat = Beat()
    endTime: Beat = Beat()
    startValue: RpexEventT
    endValue: RpexEventT
    easingType: int|typing.Callable[[number], number] = 1
    
    def getValue(self, t: number) -> RpexEventT:
        assert isinstance(self.easingType, typing.Callable), "easingType must be a function, do you forget to init ?"
        assert type(self.startValue) is type(self.endValue), "startValue and endValue must be the same type"
        
        if isinstance(self.startValue, number):
            return easing(t, self.startTime.value, self.endTime.value, self.startValue, self.endValue, self.easingType)
        elif isinstance(self.startValue, str):
            t = easing(t, 0.0, 1.0, self.startTime.value, self.endTime.value, self.easingType)
            
            if "%P%" in self.startValue and "%P%" in self.endValue:
                try:
                    dig = int(float(self.startValue.split("%P%")[-1]))
                    s, e =  (
                        "".join(self.startValue.split("%P%")[:1]),
                        "".join(self.endValue.split("%P%")[:1])
                    )
                    s, e = float(s), float(e)
                    v = s + (e - s) * t
                    return f"{v:.{dig}f}"
                except ValueError:
                    return "text event value error"
                
            if self.startValue == self.endValue: return self.startValue
            sl, el = len(self.startValue), len(self.endValue)
            if sl > el:
                return self.startValue[:int(sl * t)]
            else:
                return self.endValue[:int(el * t)]
            
        elif isinstance(self.startValue, list):
            return [easing(t, self.startTime.value, self.endTime.value, self.startValue[i], self.endValue[i], self.easingType) for i in range(len(self.startValue))]

EASING_FUNCS: list[typing.Callable[[number], number]] = [
    lambda t: t, # linear - 1
    lambda t: math.sin((t * math.pi) / 2), # out sine - 2
    lambda t: 1 - math.cos((t * math.pi) / 2), # in sine - 3
    lambda t: 1 - (1 - t) * (1 - t), # out quad - 4
    lambda t: t ** 2, # in quad - 5
    lambda t: -(math.cos(math.pi * t) - 1) / 2, # io sine - 6
    lambda t: 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2, # io quad - 7
    lambda t: 1 - (1 - t) ** 3, # out cubic - 8
    lambda t: t ** 3, # in cubic - 9
    lambda t: 1 - (1 - t) ** 4, # out quart - 10
    lambda t: t ** 4, # in quart - 11
    lambda t: 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2, # io cubic - 12
    lambda t: 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2, # io quart - 13
    lambda t: 1 - (1 - t) ** 5, # out quint - 14
    lambda t: t ** 5, # in quint - 15
    lambda t: 1 if t == 1 else 1 - 2 ** (-10 * t), # out expo - 16
    lambda t: 0 if t == 0 else 2 ** (10 * t - 10), # in expo - 17
    lambda t: (1 - (t - 1) ** 2) ** 0.5, # out circ - 18
    lambda t: 1 - (1 - t ** 2) ** 0.5, # in circ - 19
    lambda t: 1 + 2.70158 * ((t - 1) ** 3) + 1.70158 * ((t - 1) ** 2), # out back - 20
    lambda t: 2.70158 * (t ** 3) - 1.70158 * (t ** 2), # in back - 21
    lambda t: (1 - (1 - (2 * t) ** 2) ** 0.5) / 2 if t < 0.5 else (((1 - (-2 * t + 2) ** 2) ** 0.5) + 1) / 2, # io circ - 22
    lambda t: ((2 * t) ** 2 * ((2.5949095 + 1) * 2 * t - 2.5949095)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) / 2, # io back - 23
    lambda t: 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1), # out elastic - 24
    lambda t: 0 if t == 0 else (1 if t == 1 else - 2 ** (10 * t - 10) * math.sin((t * 10 - 10.75) * (2 * math.pi / 3))), # in elastic - 25
    lambda t: 7.5625 * (t ** 2) if (t < 1 / 2.75) else (7.5625 * (t - (1.5 / 2.75)) * (t - (1.5 / 2.75)) + 0.75 if (t < 2 / 2.75) else (7.5625 * (t - (2.25 / 2.75)) * (t - (2.25 / 2.75)) + 0.9375 if (t < 2.5 / 2.75) else (7.5625 * (t - (2.625 / 2.75)) * (t - (2.625 / 2.75)) + 0.984375))), # out bounce - 26
    lambda t: 1 - (7.5625 * ((1 - t) ** 2) if ((1 - t) < 1 / 2.75) else (7.5625 * ((1 - t) - (1.5 / 2.75)) * ((1 - t) - (1.5 / 2.75)) + 0.75 if ((1 - t) < 2 / 2.75) else (7.5625 * ((1 - t) - (2.25 / 2.75)) * ((1 - t) - (2.25 / 2.75)) + 0.9375 if ((1 - t) < 2.5 / 2.75) else (7.5625 * ((1 - t) - (2.625 / 2.75)) * ((1 - t) - (2.625 / 2.75)) + 0.984375)))), # in bounce - 27
    lambda t: (1 - (7.5625 * ((1 - 2 * t) ** 2) if ((1 - 2 * t) < 1 / 2.75) else (7.5625 * ((1 - 2 * t) - (1.5 / 2.75)) * ((1 - 2 * t) - (1.5 / 2.75)) + 0.75 if ((1 - 2 * t) < 2 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.25 / 2.75)) * ((1 - 2 * t) - (2.25 / 2.75)) + 0.9375 if ((1 - 2 * t) < 2.5 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.625 / 2.75)) * ((1 - 2 * t) - (2.625 / 2.75)) + 0.984375))))) / 2 if t < 0.5 else (1 +(7.5625 * ((2 * t - 1) ** 2) if ((2 * t - 1) < 1 / 2.75) else (7.5625 * ((2 * t - 1) - (1.5 / 2.75)) * ((2 * t - 1) - (1.5 / 2.75)) + 0.75 if ((2 * t - 1) < 2 / 2.75) else (7.5625 * ((2 * t - 1) - (2.25 / 2.75)) * ((2 * t - 1) - (2.25 / 2.75)) + 0.9375 if ((2 * t - 1) < 2.5 / 2.75) else (7.5625 * ((2 * t - 1) - (2.625 / 2.75)) * ((2 * t - 1) - (2.625 / 2.75)) + 0.984375))))) / 2, # io bounce - 28
    lambda t: 0 if t == 0 else (1 if t == 0 else (-2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 if t < 0.5 else (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 + 1) # io elastic - 29
]