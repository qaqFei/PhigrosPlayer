import typing
import math
import base64
import random
from sys import argv
from threading import Thread
from os import listdir, environ
from os.path import isfile
from dataclasses import dataclass

import numba
import numpy
import cv2
from PIL import Image, ImageDraw

import const
import rpe_easing

note_id = -1
random_block_num = 4
if "--random-block-num" in argv:
    random_block_num = eval(argv[argv.index("--random-block-num") + 1])

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
    return tuple(((random.uniform(0.0, 360.0), random.uniform(-0.25, 1.15)) for _ in range(random_block_num)))

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
) -> typing.Generator[bool, None, None]:
    for i in lines_group_1:
        for j in lines_group_2:
            yield is_intersect(i, j)

def Note_CanRender(
    w: int, h: int,
    note_max_size_half: float,
    x: float, y: float,
    hold_points: tuple[
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
        tuple[float, float]
    ] | None = None
) -> bool: # note 宽度不会比窗口大的... 一定不会的... 相信我...!!                                                    好吧, 其实我就是想~~偷懒和~~节约性能...  note当线看能简单一些
    if hold_points is None: # type != HOLD                                                                                         ↑↑↑↑↑↑↑↑↑ (划掉... (markdown))
        return (
            (0 < x < w and 0 < y < h) or
            (0 < x - note_max_size_half < w and 0 < y - note_max_size_half < h) or 
            (0 < x - note_max_size_half < w and 0 < y + note_max_size_half < h) or
            (0 < x + note_max_size_half < w and 0 < y - note_max_size_half < h) or
            (0 < x + note_max_size_half < w and 0 < y + note_max_size_half < h)
        )
    else:
        if any((point_in_screen(point, w, h) for point in hold_points)):
            return True
        return any(batch_is_intersect(
            [
                (hold_points[0], hold_points[1]),
                (hold_points[1], hold_points[2]),
                (hold_points[2], hold_points[3]),
                (hold_points[3], hold_points[0])
            ],
            [
                ((0, 0), (w, 0)), ((0, 0), (0, h)),
                ((w, 0), (w, h)), ((0, h), (w, h))
            ]
        ))

def lineInScreen(w: int|float, h: int|float, line: tuple[int|float, ...]):
    return any(batch_is_intersect(
        [
            ((line[0], line[1]), (line[2], line[3]))
        ],
        [
            ((0, 0), (w, 0)), ((0, 0), (0, h)),
            ((w, 0), (w, h)), ((0, h), (w, h))
        ]
    ))

def TextureLine_CanRender(
    w: int, h: int,
    texture_max_size_half: float,
    x: float, y: float
) -> bool:
    tl = x - texture_max_size_half
    tr = x + texture_max_size_half
    tt = y - texture_max_size_half
    tb = y + texture_max_size_half
    sl, sr, st, sb = 0, w, 0, h
    return (
        (sl <= tl <= sr and st <= tt <= sb) or
        (sl <= tl <= sr and st <= tb <= sb) or
        (sl <= tr <= sr and st <= tt <= sb) or
        (sl <= tr <= sr and st <= tb <= sb) or
        (tl <= sl <= tr and tt <= st <= tb) or
        (tl <= sl <= tr and tt <= sb <= tb) or
        (tl <= sr <= tr and tt <= st <= tb) or
        (tl <= sr <= tr and tt <= sb <= tb)
    )
    
def point_in_screen(point: tuple[float, float], w: int, h: int) -> bool:
    return 0 < point[0] < w and 0 < point[1] < h

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
    return (x + 675) / 1350, 1.0 - (y + 450) / 900

def aconrpepos(x: float, y: float):
    return (x * 1350 - 675), (1.0 - y) * 900 - 450

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
    def nproxy_tstring(self, n: typing.Any) -> str: ...
    
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
            psound: typing.Callable[[str], typing.Any]
        ) -> None:
        
        self.pp = pplm_proxy
        self.ppps = ppps
        self.enable_cksound = enable_cksound
        self.psound = psound
        
        self.pc_clicks: list[PPLM_PC_ClickEvent] = []
        self.pc_clickings: int = 0
        self.clickeffects: const.ClickEffectType = []
    
    def pc_click(self, t: float) -> None:
        self.pc_clickings += 1
        self.pc_clicks.append(PPLM_PC_ClickEvent(time=t))
        
    def pc_release(self, t: float) -> None:
        self.pc_clickings += 1
    
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
                    self.psound(self.pp.nproxy_tstring(i))
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
            
            if self.pp.nproxy_stime(i) - t < - const.NOTE_JUDGE_RANGE.MISS * 2:
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
           
if environ.get("ENABLE_JIT", ""):
    numbajit_funcs = [
        rotate_point,
        unpack_pos,
        linear_interpolation,
        is_intersect,
        TextureLine_CanRender,
        point_in_screen,
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
    TextureLine_CanRender(1920, 1080, 23.1, 3.1, 4.3)
    point_in_screen((204.2, 1.3), 1920, 1080)
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