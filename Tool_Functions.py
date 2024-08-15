from random import randint
from sys import argv
from threading import Thread
import typing
import math
import base64

import numba
import numpy
import cv2

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
    return (number - number % 1000) // 1000,number % 1000

def ease_out(x:float) -> float:
    return math.sqrt(1.0 - (1.0 - x) ** 2)

def get_effect_random_blocks() -> tuple[int, ...]:
    return tuple((randint(1, 90) for _ in range(random_block_num)))

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
    t:float,
    st:float,
    et:float,
    sv:float,
    ev:float,
    f:typing.Callable
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
    if (
        max(line_1[0][0], line_1[1][0]) < min(line_2[0][0], line_2[1][0]) or
        max(line_2[0][0], line_2[1][0]) < min(line_1[0][0], line_1[1][0]) or
        max(line_1[0][1], line_1[1][1]) < min(line_2[0][1], line_2[1][1]) or
        max(line_2[0][1], line_2[1][1]) < min(line_1[0][1], line_1[1][1])
    ):
        return False
    else:
        return True

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
    if hold_points is None: # type != HOLD                                                                                         ↑↑↑↑↑↑↑↑↑ (划掉...)
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
    
def judgeLine_can_render(
    judgeLine_DrawPos: typing.Tuple[
        typing.Tuple[float, float],
        typing.Tuple[float, float]
    ], w: int, h: int
) -> bool:
    return any(batch_is_intersect([[[judgeLine_DrawPos[0],judgeLine_DrawPos[1]],[judgeLine_DrawPos[2],judgeLine_DrawPos[3]]]],[[(0,0),(w,0)],[(0,0),(0,h)],[(w,0),(w,h)],[(0,h),(w,h)]]))

@numba.jit
def point_in_screen(point:typing.Tuple[float,float], w: int, h: int) -> bool:
    return 0 < point[0] < w and 0 < point[1] < h

def ThreadFunc(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
        t.join()
    return wrapper

def NoJoinThreadFunc(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wrapper

def conrpepos(x: float, y: float):
    return (x + 675) / 1350, 1.0 - (y + 450) / 900

def Format_Time(t:typing.Union[int,float]) -> str:
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

linear_interpolation(0.5,0.1,0.8,-114.514,314.159)
is_intersect(((0, 0), (114, 514)), ((0, 0), (114, 514)))
TextureLine_CanRender(1920, 1080, 50, 0, 0)
point_in_screen((0, 0), 1920, 1080)