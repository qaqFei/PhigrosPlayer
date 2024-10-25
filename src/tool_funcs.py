import typing
import math
import base64
import random
from sys import argv
from threading import Thread
from os import listdir
from os.path import isfile

import numba
import numpy
import cv2
from PIL import Image, ImageDraw

note_id = -1
random_block_num = 4
if "--random-block-num" in argv:
    random_block_num = eval(argv[argv.index("--random-block-num") + 1])

def Get_Animation_Gr(fps:float,t:float):
    gr_x = int(fps * t) + 1
    gr = [math.cos(x / gr_x) + 1 for x in range(int(gr_x * math.pi))]
    gr_sum = sum(gr)
    step_time = t / len(gr)
    return [item / gr_sum for item in gr],step_time

def rotate_point(x, y, θ, r) -> tuple[float, float]:
    xo = r * math.cos(math.radians(θ))
    yo = r * math.sin(math.radians(θ))
    return x + xo, y + yo

def Get_A_New_NoteId_By_judgeLine(judgeLine_item:dict):
    if "_note_count" not in judgeLine_item:
        judgeLine_item["_note_count"] = 1
    else:
        judgeLine_item["_note_count"] += 1
    return judgeLine_item["_note_count"] - 1

def Get_A_New_NoteId():
    global note_id
    note_id += 1
    return note_id

def unpack_pos(number:int) -> tuple[int, int]:
    return (number - number % 1000) // 1000, number % 1000

def ease_out(x:float) -> float:
    return math.sqrt(1.0 - (1.0 - x) ** 2)

def get_effect_random_blocks() -> tuple[tuple[float, float], ...]:
    return tuple(((random.uniform(0.0, 360.0), random.uniform(0.0, 1.0)) for _ in range(random_block_num)))

@numba.jit(numba.float32(numba.float32,numba.float32,numba.float32,numba.float32,numba.float32))
def linear_interpolation(
    t:float,
    st:float,
    et:float,
    sv:float,
    ev:float
) -> float:
    if t == st: return sv
    return (t - st) / (et - st) * (ev - sv) + sv

def easing_interpolation(
    t: float, st: float,
    et: float, sv: float,
    ev: float, f: typing.Callable[[float], float]
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

@numba.jit
def is_intersect(
    line_1: typing.Tuple[
        typing.Tuple[float, float],
        typing.Tuple[float, float]
    ],
    line_2: typing.Tuple[
        typing.Tuple[float, float],
        typing.Tuple[float, float]
    ]
) -> bool:
    return not (
        max(line_1[0][0], line_1[1][0]) < min(line_2[0][0], line_2[1][0]) or
        max(line_2[0][0], line_2[1][0]) < min(line_1[0][0], line_1[1][0]) or
        max(line_1[0][1], line_1[1][1]) < min(line_2[0][1], line_2[1][1]) or
        max(line_2[0][1], line_2[1][1]) < min(line_1[0][1], line_1[1][1])
    )

def batch_is_intersect(
    lines_group_1: typing.List[typing.Tuple[
        typing.Tuple[float, float],
        typing.Tuple[float, float]
    ]],
    lines_group_2: typing.List[typing.Tuple[
        typing.Tuple[float, float],
        typing.Tuple[float, float]
    ]]
) -> typing.Generator[bool, None, None]:
    for i in lines_group_1:
        for j in lines_group_2:
            yield is_intersect(i, j)

def Note_CanRender(
    w: int, h: int,
    note_max_size_half: float,
    x: float, y: float,
    hold_points: typing.Union[typing.Tuple[
        typing.Tuple[float, float],
        typing.Tuple[float, float],
        typing.Tuple[float, float],
        typing.Tuple[float, float]
    ], None] = None
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

@numba.jit
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
    
@numba.jit
def point_in_screen(point:typing.Tuple[float,float], w: int, h: int) -> bool:
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

def Format_Time(t:int|float) -> str:
    if t < 0.0: t = 0.0
    m,s = t // 60,t % 60
    m,s = int(m), int(s)
    return f"{m}:{s:>2}".replace(" ", "0")

def DataUrl2MatLike(dataurl: str) -> cv2.typing.MatLike:
    return cv2.imdecode(
        numpy.frombuffer(
            base64.b64decode(
                dataurl[dataurl.find(",") + 1:]
            ),
            dtype=numpy.uint8
        ),
        cv2.IMREAD_COLOR
    )

def InRect(x: float, y: float, rect: tuple[float, float, float, float]) -> bool:
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]

def easeAlpha(p: float):
    if 0.0 <= p <= 0.4: 
        return 1.0 - (1.0 - 2 * p * (0.5 / 0.4)) ** 2
    elif 0.4 <= p <= 0.8:
        return 1.0
    else:
        return (2.0 - 2.0 * ((p - 0.8) * (0.5 / 0.2) + 0.5)) ** 2

def inDiagonalRectangle(x0: float, y0: float, x1: float, y1: float, power: float, x: float, y:float):
    x += (y - y0) / (y1 - y0) * (x1 - x0) * power
    return x0 + (x1 - x0) * power <= x <= x1 and y0 <= y <= y1

def compute_intersection(x0, y0, x1, y1, x2, y2, x3, y3):
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
    
def Get_All_Files(path:str) -> list[str]:
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

linear_interpolation(0.5,0.1,0.8,-114.514,314.159)
is_intersect(((0, 0), (114, 514)), ((0, 0), (114, 514)))
TextureLine_CanRender(1920, 1080, 50, 0, 0)
point_in_screen((0, 0), 1920, 1080)