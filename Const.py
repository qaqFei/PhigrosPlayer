import typing

class Note:
    TAP = 1
    DRAG = 2
    HOLD = 3
    FLICK = 4

class CHART_TYPE:
    PHI = 1
    RPE = 2

class NOTE_STATE:
    PERFECT = 1
    GOOD = 2
    BAD = 3
    MISS = 4

INF = float("inf")
NAN = float("nan")
JUDGELINE_PERFECT_COLOR = "#feffa9"
RENDER_RANGE_MORE_FRAME_LINE_COLOR = "rgba(0, 94, 255, 0.65)"
FINISH_UI_BUTTON_SIZE = 0.095
JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER = 127 / 975
CHAPTER_DIAGONALRECTANGLEDEG = -75

def set_NOTE_DUB_FIXSCALE(scale: float):
    global NOTE_DUB_FIXSCALE
    NOTE_DUB_FIXSCALE = scale

EXTRA_DEFAULTS = { # no using
    "chromatic": {
        "sampleCount": 3,
        "power": 0.01
    },
    "circleBlur": {
        "size": 10.0
    },
    "fisheye": {
        "power": -0.1
    },
    "glitch": {
        "power": 0.3,
        "rate": 0.6,
        "speed": 5.0,
        "blockCount": 30.5,
        "colorRate": 0.01
    },
    "grayscale": {
        "factor": 1.0
    },
    "noise": {
        "seed": 81.0,
        "power": 0.03
    },
    "pixel": {
        "size": 10.0
    },
    "radialBlur": {
        "centerX": 0.5,
        "centerY": 0.5,
        "power": 0.01,
        "sampleCount": 3,
    },
    "shockwave": {
        "progress": 0.2,
        "centerX": 0.5,
        "centerY": 0.5,
        "width": 0.1,
        "distortion": 0.8,
        "expand": 10.0
    },
    "vignette": {
        "color": [0, 0, 0],
        "extend": 0.25,
        "radius": 15.0
    }
}

del typing