import typing
import math
import base64
import random
import logging
import time
from sys import argv
from threading import Thread
from os import listdir, environ
from os.path import isfile, abspath
from dataclasses import dataclass

import numpy
import cv2
from PIL import Image, ImageDraw

import const
import rpe_easing
import binfile

note_id = -1
random_block_num = eval(argv[argv.index("--random-block-num") + 1]) if "--random-block-num" in argv else 4

def rotate_point(x, y, θ, r) -> tuple[float, float]:
    xo = r * math.cos(math.radians(θ))
    yo = r * math.sin(math.radians(θ))
    return x + xo, y + yo

def Get_A_New_NoteId():
    global note_id
    note_id += 1
    return note_id

def unpack_pos(number: int) -> tuple[int, int]:
    return (number - number % 1000) // 1000, number % 1000

def get_effect_random_blocks() -> tuple[tuple[float, float], ...]:
    return tuple(
        (random.uniform(0.0, 360.0), random.uniform(-0.15, 0.3))
        for _ in range(random_block_num)
    )

def linear_interpolation(
    t: float,
    st: float, et: float,
    sv: float, ev: float
) -> float:
    if t == st: return sv
    return (t - st) / (et - st) * (ev - sv) + sv

def easing_interpolation(
    t: float,
    st: float, et: float,
    sv: float, ev: float,
    f: typing.Callable[[float], float]
):
    if t == st: return sv
    return f((t - st) / (et - st)) * (ev - sv) + sv

bae_bs = 2.15
class begin_animation_eases_class:
    @staticmethod
    def im_ease(x):
        if x <= (1 / bae_bs): return 0.0
        x -= (1 / bae_bs); x /= (1 - (1 / bae_bs))
        a = max(0, 1.4 * x - 0.25) + 0.3
        b = min(a, 1.0)
        return b ** 7
    
    @staticmethod
    def background_ease(x):
        x *= 4
        if x >= 1.0: return 1.0
        if x <= 0.0: return 0.0
        return 1 - (abs(x - 1)) ** 3
    
    @staticmethod
    def tip_alpha_ease(x): #emm... linear
        return min(max(0.0, 3 * x - 0.25), 1.0)
    
    @staticmethod
    def info_data_ease(x):
        if x >= 1.0: return 1.0
        if x <= 0.0: return 0.0
        return 1 - (1 - x) ** 3
    
    @staticmethod
    def background_block_color_alpha_ease(x):
        if x >= 1.0: return 1.0
        if x <= 0.0: return 0.0
        return (1 - x ** 2) ** 0.5

class finish_animation_eases_class:
    @staticmethod
    def all_ease(x):
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        k = 1 - x
        return 1 - k ** 10
    
    @staticmethod
    def score_alpha_ease(x):
        k = 0.125
        x -= k
        x *= (1 / (1 - k))
        x *= 5.0
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return x ** 2

    @staticmethod
    def level_size_ease(x):
        k = 3.0
        return max(0.5 - (k * max(x - 1 / 6, 0.0)) ** 4, 0.0) + 1.0
    
    @staticmethod
    def level_alpha_ease(x):
        k = 0.25
        x -= k
        x *= (1 / (1 - k))
        x *= 5.0
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return x ** 2
    
    @staticmethod
    def playdata_alpha_ease(x):
        k = 0.25
        x -= k
        x *= (1 / (1 - k))
        x *= 5.0
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return x ** 2
    
    @staticmethod
    def button_ease(x):
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return 1 - (1 - x) ** 3

begin_animation_eases = begin_animation_eases_class()
finish_animation_eases = finish_animation_eases_class()

def is_intersect(
    line_1: tuple[
        tuple[float, float],
        tuple[float, float]
    ],
    line_2: tuple[
        tuple[float, float],
        tuple[float, float]
    ]
) -> bool:
    return not (
        max(line_1[0][0], line_1[1][0]) < min(line_2[0][0], line_2[1][0]) or
        max(line_2[0][0], line_2[1][0]) < min(line_1[0][0], line_1[1][0]) or
        max(line_1[0][1], line_1[1][1]) < min(line_2[0][1], line_2[1][1]) or
        max(line_2[0][1], line_2[1][1]) < min(line_1[0][1], line_1[1][1])
    )

def batch_is_intersect(
    lines_group_1: list[tuple[
        tuple[float, float],
        tuple[float, float]
    ]],
    lines_group_2: list[tuple[
        tuple[float, float],
        tuple[float, float]
    ]]
):
    for i in lines_group_1:
        for j in lines_group_2:
            yield is_intersect(i, j)

def pointInPolygon(ploygon: list[tuple[float, float]], point: tuple[float, float]):
    n = len(ploygon)
    j = n - 1
    res = False
    for i in range(n):
        if (
            (ploygon[i][1] > point[1]) != (ploygon[j][1] > point[1])
            and point[0] < (ploygon[j][0] - ploygon[i][0]) * (point[1] - ploygon[i][1]) / (ploygon[j][1] - ploygon[i][1]) + ploygon[i][0]
        ):
            res = not res
        j = i
    return res

def getScreenRect(w: int, h: int):
    return [
        ((0, 0), (w, 0)), ((0, 0), (0, h)),
        ((w, 0), (w, h)), ((0, h), (w, h))
    ]

def getScreenPoints(w: int, h: int):
    return [(0, 0), (w, 0), (w, h), (0, h)]

def polygon2lines(p: list[tuple[float, float]]):
    return [(p[i], p[i + 1]) for i in range(-1, len(p) - 1)]

def polygonIntersect(p1: list[tuple[float, float]], p2: list[tuple[float, float]]):
    return (
        any(batch_is_intersect(polygon2lines(p1), polygon2lines(p2)))
        or any(pointInPolygon(p1, i) for i in p2)
        or any(pointInPolygon(p2, i) for i in p1)
    )

def linesInScreen(w: int, h: int, lines: list[tuple[float, float]]):
    return any(batch_is_intersect(
        lines, getScreenRect(w, h)
    )) or any(pointInScreen(j, w, h) for i in lines for j in i)

def polygonInScreen(w: int, h: int, polygon: list[tuple[float, float]]):
    return polygonIntersect(getScreenPoints(w, h), polygon)

def noteCanRender(
    w: int, h: int,
    note_max_size_half: float,
    x: float, y: float,
    hold_points: tuple[
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
        tuple[float, float]
    ] | None = None
) -> bool: # is type == hold, note_max_size_half is useless
    if hold_points is None: # type != hold
        lt = (x - note_max_size_half, y - note_max_size_half)
        rt = (x + note_max_size_half, y - note_max_size_half)
        rb = (x + note_max_size_half, y + note_max_size_half)
        lb = (x - note_max_size_half, y + note_max_size_half)
    else:
        lt, rt, rb, lb = hold_points
    
    return polygonInScreen(w, h, [lt, rt, rb, lb])

def lineInScreen(w: int|float, h: int|float, line: tuple[float]):
    return linesInScreen(w, h, [((*line[:2], ), (*line[2:], ), )])

def TextureLine_CanRender(
    w: int, h: int,
    texture_max_size_half: float,
    x: float, y: float
) -> bool:
    lt = (x - texture_max_size_half, y - texture_max_size_half)
    rt = (x + texture_max_size_half, y - texture_max_size_half)
    rb = (x + texture_max_size_half, y + texture_max_size_half)
    lb = (x - texture_max_size_half, y + texture_max_size_half)
    
    return polygonInScreen(w, h, [lt, rt, rb, lb])
    
def pointInScreen(point: tuple[float, float], w: int, h: int) -> bool:
    return 0 <= point[0] <= w and 0 <= point[1] <= h

def noteLineOutOfScreen(
    x: float, y: float,
    noteAtJudgeLinePos: tuple[float, float],
    fp: float,
    lineRotate: float,
    lineLength: float,
    lineToNoteRotate: float,
    w: int, h: int,
    note_max_size_half: float
):
    plpttdllotne_line = (
        *rotate_point(x, y, lineRotate, lineLength / 2),
        *rotate_point(x, y, lineRotate + 180, lineLength / 2)
    )
    
    plpttdllotne_cpoint_addfp = rotate_point(
        *noteAtJudgeLinePos,
        lineToNoteRotate,
        fp + 1.0 # add 1.0 px
    )
    
    moved_line = tuple(map(lambda x, y: x + y, plpttdllotne_line, (note_max_size_half, ) * 4))
    
    return (
        not lineInScreen(
            w + note_max_size_half * 2,
            h + note_max_size_half * 2,
            moved_line
        ) and (
            getLineLength(*plpttdllotne_cpoint_addfp, w / 2, h / 2)
            - getLineLength(x, y, w / 2, h / 2)
        ) > 0.0
    )

def ThreadFunc(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs, daemon=True)
        t.start()
        t.join()
    return wrapper

def NoJoinThreadFunc(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs, daemon=True)
        t.start()
    return wrapper

def conrpepos(x: float, y: float):
    return (
        (x + const.RPE_WIDTH / 2) / const.RPE_WIDTH,
        1.0 - (y + const.RPE_HEIGHT / 2) / const.RPE_HEIGHT
    )

def aconrpepos(x: float, y: float):
    return (
        x * const.RPE_WIDTH - const.RPE_WIDTH / 2,
        (1.0 - y) * const.RPE_HEIGHT - const.RPE_HEIGHT / 2
    )

def conimgsize(w: int, h: int, sw: int, sh: int):
    rw = w / const.RPE_WIDTH * sw
    return rw, rw / w * h

# thanks for HLMC (https://github.com/2278535805)
def rpe_text_tween(sv: str, ev: str, t: float, isfill: bool) -> str:
    if "%P%" in sv and "%P%" in ev:
        sv, ev = sv.replace("%P%", ""), ev.replace("%P%", "")
        if isfill: return sv
        
        try: sv, ev = float(sv), float(ev)
        except ValueError: return "0"
        
        v = sv + t * (ev - sv)
        return f"{v:.0f}" if int(sv) == sv and int(ev) == ev else f"{v:.3f}"
            
    elif not sv and not ev:
        return ""
    elif not ev:
        return rpe_text_tween(ev, sv.replace("%P%", ""), 1.0 - t, isfill)
    elif not sv:
        return ev[:int(t * len(ev))]
    
    else:
        xl, yl = len(sv), len(ev)
        ml = min(xl, yl)
        if sv[:ml] == ev[:ml]:
            take_num = int(round((yl - xl) * t)) + xl
            return sv + ev[xl:take_num]
        else:
            return sv.replace("%P%", "")
        
def Format_Time(t: int|float) -> str:
    if t < 0.0: t = 0.0
    m, s = t // 60, t % 60
    m, s = int(m), int(s)
    return f"{m}:{s:>2}".replace(" ", "0")

def DataUrl2MatLike(dataurl: str) -> cv2.typing.MatLike:
    return cv2.imdecode(
        numpy.frombuffer(
            base64.b64decode(
                dataurl[dataurl.find(",") + 1:]
            ),
            dtype = numpy.uint8
        ),
        cv2.IMREAD_COLOR
    )

def inrect(x: float, y: float, rect: tuple[float, float, float, float]) -> bool:
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]

def easeAlpha(p: float):
    if 0.0 <= p <= 0.4: 
        return 1.0 - (1.0 - 2 * p * (0.5 / 0.4)) ** 2
    elif 0.4 <= p <= 0.8:
        return 1.0
    else:
        return (2.0 - 2.0 * ((p - 0.8) * (0.5 / 0.2) + 0.5)) ** 2

def inDiagonalRectangle(x0: float, y0: float, x1: float, y1: float, power: float, x: float, y: float):
    x += (y - y0) / (y1 - y0) * (x1 - x0) * power
    return x0 + (x1 - x0) * power <= x <= x1 and y0 <= y <= y1

def compute_intersection(
    x0: float, y0: float,
    x1: float, y1: float,
    x2: float, y2: float,
    x3: float, y3: float
):
    a1 = y1 - y0
    b1 = x0 - x1
    c1 = x1 * y0 - x0 * y1
    a2 = y3 - y2
    b2 = x2 - x3
    c2 = x3 * y2 - x2 * y3
    return (b2 * c1 - b1 * c2) / (a1 * b2 - a2 * b1), (a1 * c2 - a2 * c1) / (a1 * b2 - a2 * b1)

def fixorp(p: float):
    return max(0.0, min(1.0, p))

def PhigrosChapterNameAlphaValueTransfrom(p: float):
    if p >= 0.4:
        return 1.0
    return p / 0.4

def PhigrosChapterPlayButtonAlphaValueTransfrom(p: float):
    if p <= 0.6:
        return 0.0
    return (p - 0.6) / 0.4

def PhigrosChapterDataAlphaValueTransfrom(p: float):
    if p <= 0.6:
        return 0.0
    return (p - 0.6) / 0.4

def getDPower(width: float, height: float, deg: float):
    l1 = 0, 0, width, 0
    l2 = 0, height, *rotate_point(0, height, deg, (width ** 2 + height ** 2) ** 0.5)
    return compute_intersection(*l1, *l2)[0] / width

def getSizeByRect(rect: tuple[float, float, float, float]):
    return rect[2] - rect[0], rect[3] - rect[1]

def getCenterPointByRect(rect: tuple[float, float, float, float]):
    return (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2

def sliderValueP(value: float, values: tuple[tuple[float, float]]):
    ranges = [(values[i - 1][0], values[i][0], values[i - 1][1], values[i][1]) for i in range(len(values)) if i != 0]
    for r in ranges:
        if r[2] <= value <= r[3]:
            return (value - r[2]) / (r[3] - r[2]) * (r[1] - r[0]) + r[0]
    return 0.0 if value < values[0][1] else 1.0

def sliderValueValue(p: float, values: tuple[tuple[float, float]]):
    ranges = [(values[i - 1][0], values[i][0], values[i - 1][1], values[i][1]) for i in range(len(values)) if i != 0]
    for r in ranges:
        if r[0] <= p <= r[1]:
            return (p - r[0]) / (r[1] - r[0]) * (r[3] - r[2]) + r[2]
    return ranges[0][2] if p < ranges[0][0] else ranges[-1][3]

def cutAnimationIllImage(im: Image.Image):
    imdraw = ImageDraw.Draw(im)
    imdraw.polygon(
        [
            (0, 0),
            (0, im.height),
            (im.width * 0.1, 0),
            (0, 0)
        ],
        fill = "#00000000"
    )
    imdraw.polygon(
        [
            (im.width, 0),
            (im.width, im.height),
            (im.width * (1 - 0.1), im.height),
            (im.width, 0)
        ],
        fill = "#00000000"
    )
    
def Get_All_Files(path: str) -> list[str]:
    if path[-1] == "/" or path[:-1] == "\\":
        path = path[:-1]
    path = path.replace("/", "\\")
    files = []
    for item in listdir(path):
        if isfile(f"{path}\\{item}"):
            files.append(f"{path}\\{item}")
        else:
            files += Get_All_Files(f"{path}\\{item}")
    return files

def getLineLength(x0: float, y0: float, x1: float, y1: float):
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

def gtpresp(p: str):
    result =  f"./phigros_assets/{p}".replace("\\", "/")
    while "//" in result: result = result.replace("//", "/")
    return result

def indrect(x: float, y: float, rect: tuple[float, float, float, float], dpower: float):
    x += (1.0 - (y - rect[1]) / (rect[3] - rect[1])) * (dpower * (rect[2] - rect[0]))
    return inrect(x, y, rect)

def isfloatable(s: str):
    try: float(s); return True
    except: return False

def isallnum(lst: list[str], l: int|None = None):
    return (len(lst) >= l or l is None) and all(map(lambda x: isfloatable(x), lst))

def createBezierFunction(ps: list[float]) -> typing.Callable[[float], float]:
    return lambda t: sum([ps[i] * (1 - t) ** (len(ps) - i - 1) * t ** i for i in range(len(ps))])

def createCuttingEasingFunction(f: typing.Callable[[float], float], l: float, r: float):
    return lambda t: f(t * (r - l) + l)

def pec2rpe_findevent_bytime(es: list[dict], t: float, default: float):
    if not es: return default
    
    ets = list(map(lambda x: abs(x["endTime"][0] - t), es))
    return es[ets.index(min(ets))]["end"]

def pec2rpe(pec: str):
    Exception=StopAsyncIteration
    errs = []
    peclines = pec.split("\n")
    result = { # if some key and value is not exists, in loading rpe chart, it will be set to default value.
        "META": {},
        "BPMList": [],
        "judgeLineList": []
    }
    
    result["META"]["offset"] = float(peclines.pop(0)) - 150
    
    peclines = list(map(lambda x: x.split(" "), peclines))
    
    pecbpms = list(filter(lambda x: x and x[0] == "bp" and isallnum(x[1:], 2), peclines))
    pecnotes = list(filter(lambda x: x and x[0] in ("n1", "n2", "n3", "n4") and isallnum(x[1:], 5 if x[0] != "n2" else 6), peclines))
    pecnotespeeds = list(filter(lambda x: x and x[0] == "#" and isallnum(x[1:], 1), peclines))
    pecnotesizes = list(filter(lambda x: x and x[0] == "&" and isallnum(x[1:], 1), peclines))
    peccps = list(filter(lambda x: x and x[0] == "cp" and isallnum(x[1:], 4), peclines))
    peccds = list(filter(lambda x: x and x[0] == "cd" and isallnum(x[1:], 3), peclines))
    peccas = list(filter(lambda x: x and x[0] == "ca" and isallnum(x[1:], 3), peclines))
    peccvs = list(filter(lambda x: x and x[0] == "cv" and isallnum(x[1:], 3), peclines))
    peccms = list(filter(lambda x: x and x[0] == "cm" and isallnum(x[1:], 6), peclines))
    peccrs = list(filter(lambda x: x and x[0] == "cr" and isallnum(x[1:], 5), peclines))
    peccfs = list(filter(lambda x: x and x[0] == "cf" and isallnum(x[1:], 4), peclines))
    
    pecbpms.sort(key = lambda x: float(x[1]))
    
    notezip = list(zip(pecnotes, pecnotespeeds, pecnotesizes))
    notezip.sort(key = lambda x: float(x[0][2]))
    
    peccps.sort(key = lambda x: float(x[1]))
    peccds.sort(key = lambda x: float(x[1]))
    peccas.sort(key = lambda x: float(x[1]))
    peccvs.sort(key = lambda x: float(x[1]))
    peccms.sort(key = lambda x: float(x[1]))
    peccrs.sort(key = lambda x: float(x[1]))
    peccfs.sort(key = lambda x: float(x[1]))
    
    rpex = lambda x: (x / 2048 - 0.5) * const.RPE_WIDTH
    rpey = lambda y: (y / 1400 -  0.5) * const.RPE_HEIGHT
    rpes = lambda s: s / 1400 * const.RPE_HEIGHT
    lines = {}
                    
    checkLine = lambda k: [
        (
            lines.update({k: {
                "eventLayers": [{
                    "speedEvents": [],
                    "moveXEvents": [],
                    "moveYEvents": [],
                    "rotateEvents": [],
                    "alphaEvents": []
                }],
                "notes": []
            }}),
            result["judgeLineList"].append(lines[k])
        ) if k not in lines else None,
    ]
    
    for e in pecbpms:
        try:
            result["BPMList"].append({
                "startTime": [float(e[1]), 0, 1],
                "bpm": float(e[2])
            })
        except Exception as e:
            errs.append(e)
    
    for e, sp, si in notezip:
        try:
            et = None
            if e[0] == "n2": et = [float(e.pop(3)), 0, 1]
            ntype = {"n1": 1, "n2": 2, "n3": 3, "n4": 4}[e[0]]
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            x = float(e[3])
            if et is None: et = st.copy()
            above = int(e[4])
            fake = bool(int(e[5]))
            speed = float(sp[1])
            size = float(si[1])
            
            checkLine(k)
            lines[k]["notes"].append({
                "type": ntype,
                "startTime": st,
                "endTime": et,
                "positionX": x / 2048 * const.RPE_WIDTH,
                "above": above,
                "isFake": fake,
                "speed": speed,
                "size": size
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccps:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            x = float(e[3])
            y = float(e[4])
            
            checkLine(k)
            lines[k]["eventLayers"][0]["moveXEvents"].append({
                "startTime": t, "endTime": t,
                "start": rpex(x), "end": rpex(x),
                "easingType": 1
            })
            lines[k]["eventLayers"][0]["moveYEvents"].append({
                "startTime": t, "endTime": t,
                "start": rpey(y), "end": rpey(y),
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)

    for e in peccds:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            v = float(e[3])
            
            checkLine(k)
            lines[k]["eventLayers"][0]["rotateEvents"].append({
                "startTime": t, "endTime": t,
                "start": v, "end": v,
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccas:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            v = float(e[3])

            checkLine(k)
            lines[k]["eventLayers"][0]["alphaEvents"].append({
                "startTime": t, "endTime": t,
                "start": v, "end": v,
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccvs:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            v = float(e[3])

            checkLine(k)
            lines[k]["eventLayers"][0]["speedEvents"].append({
                "startTime": t, "endTime": t,
                "start": rpes(v), "end": rpes(v),
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccms:
        try:
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            et = [float(e[3]), 0, 1]
            ex = float(e[4])
            ey = float(e[5])
            ease = int(e[6])
            
            checkLine(k)
            mxes = lines[k]["eventLayers"][0]["moveXEvents"]
            myes = lines[k]["eventLayers"][0]["moveYEvents"]
            sx = pec2rpe_findevent_bytime(mxes, st[0], rpex(ex))
            sy = pec2rpe_findevent_bytime(myes, st[0], rpey(ey))

            mxes.append({
                "startTime": st, "endTime": et,
                "start": sx, "end": rpex(ex),
                "easingType": ease
            })
            myes.append({
                "startTime": st, "endTime": et,
                "start": sy, "end": rpey(ey),
                "easingType": ease
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccrs:
        try:
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            et = [float(e[3]), 0, 1]
            ev = float(e[4])
            ease = int(e[5])

            checkLine(k)
            res = lines[k]["eventLayers"][0]["rotateEvents"]
            sv = pec2rpe_findevent_bytime(res, st[0], ev)

            res.append({
                "startTime": st, "endTime": et,
                "start": sv, "end": ev,
                "easingType": ease
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccfs:
        try:
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            et = [float(e[3]), 0, 1]
            ev = float(e[4])

            checkLine(k)
            aes = lines[k]["eventLayers"][0]["alphaEvents"]
            sv = pec2rpe_findevent_bytime(aes, st[0], ev)

            aes.append({
                "startTime": st, "endTime": et,
                "start": sv, "end": ev,
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    return result, errs

def checkOffset(now_t: float, raw_audio_length: float, mixer):
    # must not use set_pos to reset music
    offset_judge_range = (1 / 60) * 4
    
    if mixer.music.get_busy() and abs(music_offset := now_t - (mixer.music.get_pos() / 1000)) >= offset_judge_range:
        if abs(music_offset) < raw_audio_length * 1000 * 0.75:
            logging.warning(f"mixer offset > {offset_judge_range}ms, reseted chart time. (offset = {int(music_offset * 1000)}ms)")
            return music_offset
        
    return 0.0

def samefile(a: str, b: str):
    a, b = abspath(a), abspath(b)
    a, b = a.replace("\\", "/"), b.replace("\\", "/")
    while "//" in a: a = a.replace("//", "/")
    while "//" in b: b = b.replace("//", "/")
    return a == b

def findfileinlist(fn: str, lst: list[str]):
    for i, f in enumerate(lst):
        if samefile(fn, f):
            return i
    return None

def fileinlist(fn: str, lst: list[str]):
    return findfileinlist(fn, lst) is not None

class PhigrosPlayPlayStateManager:
    def __init__(self, noteCount: int):
        self.events: list[typing.Literal["P", "G", "B", "M"]] = []
        self.event_offsets: list[float] = [] # the note click offset (s)
        self.noteCount = noteCount
    
    def addEvent(self, event: typing.Literal["P", "G", "B", "M"], offset: float|None = None): # Perfect, Good, Bad, Miss
        self.events.append(event)
        if offset is not None: # offset is only good judge.
            self.event_offsets.append(offset)
    
    def getJudgelineColor(self) -> tuple[int]:
        if "B" in self.events or "M" in self.events:
            return (255, 255, 255) # White
        if "G" in self.events:
            return (162, 238, 255) # FC
        return (255, 255, 170) # AP

    def getCombo(self) -> int:
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                return cut
        return cut
    
    def getAcc(self) -> float: # 实时 Acc
        if not self.events: return 1.0
        acc = 0.0
        allcut = len(self.events)
        for e in self.events:
            if e == "P":
                acc += 1.0 / allcut
            elif e == "G":
                acc += 0.65 / allcut
        return acc
    
    def getAccOfAll(self) -> float:
        acc = 0.0
        for e in self.events:
            if e == "P":
                acc += 1.0 / self.noteCount
            elif e == "G":
                acc += 0.65 / self.noteCount
        return acc
    
    def getMaxCombo(self) -> int:
        r = 0
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                r = max(r, cut)
                cut = 0
        return max(r, cut)
    
    def getScore(self) -> float:
        return self.getAccOfAll() * 900000 + self.getMaxCombo() / self.noteCount * 100000
    
    def getPerfectCount(self) -> int:
        return self.events.count("P")
    
    def getGoodCount(self) -> int:
        return self.events.count("G")
    
    def getBadCount(self) -> int:
        return self.events.count("B")
    
    def getMissCount(self) -> int:
        return self.events.count("M")
    
    def getEarlyCount(self) -> int:
        return len(list(filter(lambda x: x > 0, self.event_offsets)))
    
    def getLateCount(self) -> int:
        return len(list(filter(lambda x: x < 0, self.event_offsets)))
    
    def getLevelString(self) -> typing.Literal["AP", "FC", "V", "S", "A", "B", "C", "F"]:
        score = self.getScore()
        if self.getPerfectCount() == self.noteCount: return "AP"
        elif self.getBadCount() == 0 and self.getMissCount() == 0: return "FC"
        
        if 0 <= score < 700000:
            return "F"
        elif 700000 <= score < 820000:
            return "C"
        elif 820000 <= score < 880000:
            return "B"
        elif 880000 <= score < 920000:
            return "A"
        elif 920000 <= score < 960000:
            return "S"
        elif 960000 <= score < 1000000:
            return "V"
        elif 1000000 <= score:
            return "AP"
        
class PPLM_ProxyBase:
    def __init__(self, cobj: typing.Any) -> None: ...
    
    def get_lines(self) -> list[typing.Any]: ...
    def get_all_pnotes(self) -> list[typing.Any]: ...
    def remove_pnote(self, n: typing.Any) -> None: ...
    
    def nproxy_stime(self, n: typing.Any) -> float: ...
    def nproxy_etime(self, n: typing.Any) -> float: ...
    def nproxy_hcetime(self, n: typing.Any) -> float: ...
    
    def nproxy_typein(self, n: typing.Any, ts: tuple[typing.Any]) -> bool: ...
    def nproxy_typeis(self, n: typing.Any, t: typing.Any) -> bool: ...
    def nproxy_typeisnot(self, n: typing.Any, t: typing.Any) -> bool: return not self.nproxy_typeis(n, t)
    def nproxy_phitype(self, n: typing.Any) -> typing.Any: ...
    
    def nproxy_nowpos(self, n: typing.Any) -> tuple[float, float]: ...
    def nproxy_effects(self, n: typing.Any) -> const.ClickEffectType: ...
    
    def nproxy_get_pclicked(self, n: typing.Any) -> bool: ...
    def nproxy_set_pclicked(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_wclick(self, n: typing.Any) -> bool: ...
    def nproxy_set_wclick(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_pclick_offset(self, n: typing.Any) -> float: ...
    def nproxy_set_pclick_offset(self, n: typing.Any, offset: float) -> None: ...
    
    def nproxy_get_ckstate(self, n: typing.Any) -> typing.Any: ...
    def nproxy_set_ckstate(self, n: typing.Any, state: typing.Any) -> None: ...
    def nproxy_get_ckstate_ishit(self, n: typing.Any) -> bool: ...
    
    def nproxy_get_cksound_played(self, n: typing.Any) -> bool: ...
    def nproxy_set_cksound_played(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_missed(self, n: typing.Any) -> bool: ...
    def nproxy_set_missed(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_holdjudged(self, n: typing.Any) -> bool: ...
    def nproxy_set_holdjudged(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_holdjudged_tomanager(self, n: typing.Any) -> bool: ...
    def nproxy_set_holdjudged_tomanager(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_last_testholdmiss_time(self, n: typing.Any) -> float: ...
    def nproxy_set_last_testholdmiss_time(self, n: typing.Any, time: float) -> None: ...
    
    def nproxy_get_safe_used(self, n: typing.Any) -> bool: ...
    def nproxy_set_safe_used(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_holdclickstate(self, n: typing.Any) -> typing.Any: ...
    def nproxy_set_holdclickstate(self, n: typing.Any, state: typing.Any) -> None: ...
    
    def nproxy_get_pbadtime(self, n: typing.Any) -> float: ...
    def nproxy_set_pbadtime(self, n: typing.Any, time: float) -> None: ...

@dataclass
class PPLM_PC_ClickEvent: time: float
@dataclass
class PPLM_PC_ReleaseEvent: time: float
    
class PhigrosPlayLogicManager:
    def __init__(
            self,
            pplm_proxy: PPLM_ProxyBase,
            ppps: PhigrosPlayPlayStateManager,
            enable_cksound: bool,
            psound: typing.Callable[[str], typing.Any],
            record: bool = False
        ) -> None:
        
        self.pp = pplm_proxy
        self.ppps = ppps
        self.enable_cksound = enable_cksound
        self.psound = psound
        self.record = record
        
        if self.record:
            self.recorder = binfile.PlayRecorderWriter()
        
        self.pc_clicks: list[PPLM_PC_ClickEvent] = []
        self.pc_clickings: int = 0
        self.clickeffects: const.ClickEffectType = []
    
    def pc_click(self, t: float) -> None:
        self.pc_clickings += 1
        self.pc_clicks.append(PPLM_PC_ClickEvent(time=t))
        
        if self.record:
            self.recorder.pc_click(t)
        
    def pc_release(self, t: float) -> None:
        self.pc_clickings -= 1
        
        if self.record:
            self.recorder.pc_release(t)
    
    def pc_update(self, t: float) -> None:
        pnotes = self.pp.get_all_pnotes()
        
        keydown = self.pc_clickings > 0
        
        for i in pnotes.copy():
            if ( # drag / flick range judge
                keydown and
                not self.pp.nproxy_get_wclick(i) and
                self.pp.nproxy_typein(i, (const.Note.DRAG, const.Note.FLICK)) and
                abs((self.pp.nproxy_stime(i) - t)) <= const.NOTE_JUDGE_RANGE.GOOD
            ):
                self.pp.nproxy_set_wclick(i, True)
            
            if ( # drag / flick it is time to judge
                self.pp.nproxy_get_wclick(i) and
                not self.pp.nproxy_get_pclicked(i) and
                self.pp.nproxy_stime(i) <= t
            ):
                self.pp.nproxy_set_pclicked(i, True)
                self.pp.nproxy_set_ckstate(i, const.NOTE_STATE.PERFECT)
                self.ppps.addEvent("P")
                self.clickeffects.append((True, t, *self.pp.nproxy_effects(i).pop(0)[1:]))
            
            if ( # play click sound
                self.pp.nproxy_get_pclicked(i) and
                not self.pp.nproxy_get_cksound_played(i) and
                self.pp.nproxy_get_ckstate_ishit(i)
            ):
                if self.enable_cksound:
                    self.psound(self.pp.nproxy_phitype(i))
                    if self.record:
                        self.recorder.clicksound(t, self.pp.nproxy_phitype(i))
                self.pp.nproxy_set_cksound_played(i, True)
            
            if ( # miss judge
                not self.pp.nproxy_get_pclicked(i) and
                not self.pp.nproxy_get_missed(i) and
                self.pp.nproxy_stime(i) - t < -const.NOTE_JUDGE_RANGE.MISS
            ):
                self.pp.nproxy_set_missed(i, True)
                self.ppps.addEvent("M")
            
            if ( # hold holding judge
                keydown and
                self.pp.nproxy_typeis(i, const.Note.HOLD) and
                self.pp.nproxy_get_pclicked(i) and
                self.pp.nproxy_get_ckstate_ishit(i) and
                self.pp.nproxy_etime(i) - 0.2 >= t
            ):
                self.pp.nproxy_set_last_testholdmiss_time(i, t)
            
            if ( # hold holding miss judge
                not keydown and
                self.pp.nproxy_typeis(i, const.Note.HOLD) and
                self.pp.nproxy_get_pclicked(i) and
                self.pp.nproxy_get_ckstate_ishit(i) and
                self.pp.nproxy_etime(i) - 0.2 >= t and
                self.pp.nproxy_get_last_testholdmiss_time(i) + 0.16 <= t
            ):
                self.pp.nproxy_set_ckstate(i, const.NOTE_STATE.MISS)
                self.pp.nproxy_set_missed(i, True)
                self.ppps.addEvent("M")
            
            if ( # hold add hit event to manager
                self.pp.nproxy_typeis(i, const.Note.HOLD) and
                self.pp.nproxy_get_holdjudged(i) and # if judged is true, hold state is perfect/good/ miss(miss at clicking)
                not self.pp.nproxy_get_holdjudged_tomanager(i) and
                self.pp.nproxy_hcetime(i) <= t
            ):
                self.pp.nproxy_set_holdjudged_tomanager(i, True)
                state = self.pp.nproxy_get_ckstate(i)
                if state == const.NOTE_STATE.PERFECT:
                    self.ppps.addEvent("P")
                elif state == const.NOTE_STATE.GOOD:
                    self.ppps.addEvent("G", self.pp.nproxy_get_pclick_offset(i))
            
            if ( # add hold effects
                self.pp.nproxy_typeis(i, const.Note.HOLD) and
                self.pp.nproxy_get_ckstate_ishit(i) and
                self.pp.nproxy_etime(i) >= t
            ):
                for effect in self.pp.nproxy_effects(i):
                    if effect[0] <= t:
                        self.clickeffects.append((self.pp.nproxy_get_ckstate(i) == const.NOTE_STATE.PERFECT, t, *effect[1:]))
                        self.pp.nproxy_effects(i).remove(effect)
                    else:
                        break
            
            if self.pp.nproxy_typeisnot(i, const.Note.HOLD) and self.pp.nproxy_stime(i) - t < - const.NOTE_JUDGE_RANGE.MISS * 2:
                self.pp.remove_pnote(i)
            elif self.pp.nproxy_typeis(i, const.Note.HOLD) and self.pp.nproxy_etime(i) - t < - const.NOTE_JUDGE_RANGE.MISS * 2:
                self.pp.remove_pnote(i)
            elif self.pp.nproxy_stime(i) > t + const.NOTE_JUDGE_RANGE.BAD * 2:
                break
        
        while self.pc_clicks:
            cke = self.pc_clicks.pop()
            
            can_judge_notes = []
            can_use_safe_notes = []
            
            for i in pnotes:
                if (
                    not self.pp.nproxy_get_pclicked(i) and
                    self.pp.nproxy_typein(i, (const.Note.TAP, const.Note.HOLD)) and
                    abs((offset := (self.pp.nproxy_stime(i) - cke.time))) <= (
                        const.NOTE_JUDGE_RANGE.BAD \
                            if self.pp.nproxy_typeis(i, const.Note.TAP) else \
                                const.NOTE_JUDGE_RANGE.GOOD
                    )
                ):
                    can_judge_notes.append((i, offset))
                
                if (
                    self.pp.nproxy_typein(i, (const.Note.DRAG, const.Note.FLICK)) and
                    not self.pp.nproxy_get_safe_used(i) and
                    abs((offset := (self.pp.nproxy_stime(i) - cke.time))) <= const.NOTE_JUDGE_RANGE.GOOD
                ):
                    can_use_safe_notes.append((i, offset))

                if self.pp.nproxy_stime(i) > cke.time + const.NOTE_JUDGE_RANGE.BAD * 2:
                    break
            
            can_judge_notes.sort(key = lambda x: abs(x[1]))
            can_use_safe_notes.sort(key = lambda x: x[1])
            
            if not can_judge_notes: continue
            
            n, offset = can_judge_notes[0]
            abs_offset = abs(offset)
            
            if 0.0 <= abs_offset <= const.NOTE_JUDGE_RANGE.PERFECT:
                state = const.NOTE_STATE.PERFECT
                
                self.pp.nproxy_set_ckstate(n, state)
                
                if self.pp.nproxy_typeis(n, const.Note.HOLD):
                    self.pp.nproxy_set_holdjudged(n, True)
                    self.pp.nproxy_set_holdclickstate(n, state)
                else:
                    self.ppps.addEvent("P")

            elif const.NOTE_JUDGE_RANGE.PERFECT < abs_offset <= const.NOTE_JUDGE_RANGE.GOOD:
                state = const.NOTE_STATE.GOOD

                self.pp.nproxy_set_ckstate(n, state)
                
                if self.pp.nproxy_typeis(n, const.Note.HOLD):
                    self.pp.nproxy_set_holdjudged(n, True)
                    self.pp.nproxy_set_holdclickstate(n, state)
                else:
                    self.ppps.addEvent("G", offset)
            
            elif const.NOTE_JUDGE_RANGE.GOOD < abs_offset <= const.NOTE_JUDGE_RANGE.BAD: # only tap can goto there
                if can_use_safe_notes:
                    drag, _ = can_use_safe_notes[0]
                    if not self.pp.nproxy_get_wclick(drag):
                        self.pp.nproxy_set_wclick(drag, True)
                    self.pp.nproxy_set_safe_used(drag, True)
                    continue
                
                self.pp.nproxy_set_pbadtime(n, cke.time)
                self.pp.nproxy_set_ckstate(n, const.NOTE_STATE.BAD)
                self.ppps.addEvent("B")
            
            if self.pp.nproxy_get_ckstate(n) != const.NOTE_STATE.MISS:
                self.pp.nproxy_set_pclick_offset(n, offset)
                self.pp.nproxy_set_pclicked(n, True)
            
            if self.pp.nproxy_get_ckstate_ishit(n):
                e = self.pp.nproxy_effects(n).pop(0)
                npos = self.pp.nproxy_nowpos(n)
                self.clickeffects.append((
                    self.pp.nproxy_get_ckstate(n) == const.NOTE_STATE.PERFECT,
                    t,
                    *e[1:-1],
                    eval(f"lambda w, h: ({npos[0]} * w, {npos[1]} * h)") if self.pp.nproxy_typeis(n, const.Note.HOLD) and self.pp.nproxy_stime(n) >= t else e[-1]
                ))

class FramerateCalculator:
    def __init__(self):
        self._frame_count = 0
        self._frame_lastt = time.perf_counter()
        self._frame_checklimit = 25
        self.framerate = -1
    
    def frame(self):
        self._frame_count += 1
        
        if self._frame_count >= self._frame_checklimit:
            uset = time.perf_counter() - self._frame_lastt
            self.framerate = (self._frame_count / uset) if uset else float("inf")
            self._frame_count = 0
            self._frame_lastt = time.perf_counter()
            
            if self.framerate != float("inf"):
                self._frame_checklimit = self.framerate * 0.1

if environ.get("ENABLE_JIT", "0") == "1":
    import numba
    
    numbajit_funcs = [
        rotate_point,
        unpack_pos,
        linear_interpolation,
        is_intersect,
        pointInScreen,
        conrpepos,
        aconrpepos,
        inrect,
        inDiagonalRectangle,
        compute_intersection,
        fixorp,
        PhigrosChapterNameAlphaValueTransfrom,
        PhigrosChapterPlayButtonAlphaValueTransfrom,
        PhigrosChapterDataAlphaValueTransfrom,
        getDPower,
        getSizeByRect,
        getCenterPointByRect,
        getLineLength,
        indrect
    ]

    for f in numbajit_funcs:
        globals()[f.__name__] = numba.jit(f)
    efs = rpe_easing.ease_funcs.copy()
    rpe_easing.ease_funcs.clear()
    rpe_easing.ease_funcs.extend(map(numba.jit, efs))
    (*map(lambda x: x(random.uniform(0.0, 1.0)), rpe_easing.ease_funcs), )

    rotate_point(0.0, 0.0, 90, 1.145)
    unpack_pos(1000 * 11 + 45)
    linear_interpolation(0.5, 0.0, 1.0, 0.0, 1.0)
    is_intersect(((0.0, 0.1), (0.0, 0.2)), ((-0.1, 0.1), (0.0, 0.4)))
    pointInScreen((204.2, 1.3), 1920, 1080)
    aconrpepos(*conrpepos(102.4, 30.3))
    inrect(1.3, 13.4, (0.2, 3.1, 0.4, 1.4))
    inDiagonalRectangle(0.0, 0.0, 123.3, 32.2, 3.2, 0.2, 0.4)
    compute_intersection(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
    fixorp(2.3)
    PhigrosChapterNameAlphaValueTransfrom(0.7)
    PhigrosChapterPlayButtonAlphaValueTransfrom(0.5)
    PhigrosChapterDataAlphaValueTransfrom(0.1)
    getDPower(24, 42, 75)
    getSizeByRect((0.0, 0.0, 1.0, 4.0))
    getCenterPointByRect((0.0, 0.0, 1.0, 1.0))
    getLineLength(0.0, 0.0, 1.0, 1.0)
    indrect(0.0, 3.0, (0.0, 0.0, 1.0, 4.5), 5.3)
    