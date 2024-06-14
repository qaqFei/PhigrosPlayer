from random import randint
from sys import argv
import typing
import math

import numba

note_id = -1
random_block_num = 4
if "-random-block-num" in argv:
    random_block_num = eval(argv[argv.index("-random-block-num") + 1])

def Get_Animation_Gr(fps:float,t:float):
    gr_x = int(fps * t) + 1
    gr = [math.cos(x / gr_x) + 1 for x in range(int(gr_x * math.pi))]
    gr_sum = sum(gr)
    step_time = t / len(gr)
    return [item / gr_sum for item in gr],step_time

def rotate_point(x,y,θ,r) -> float:
    xo = r * math.cos(math.radians(θ))
    yo = r * math.sin(math.radians(θ))
    return x + xo,y + yo

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

def unpack_pos(number:int) -> tuple[int,int]:
    return (number - number % 1000) // 1000,number % 1000

def ease_out(x:float) -> float:
    return math.sqrt(1.0 - (1.0 - x) ** 2)

def get_effect_random_blocks() -> typing.Tuple[int,int,int,int]:
    return tuple((randint(1,90) for _ in range(random_block_num)))

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

class begin_animation_eases:
    def im_ease(x):
        a = max(0, 1.4 * x - 0.25)
        b = min(a, 1.0)
        return b ** 3
    
    def background_ease(x):
        k = 4
        a = max(0, x)
        b = min(a, 1 / k)
        return (k ** 2 * b) ** 2 / (k ** 2)

linear_interpolation(0.5,0.1,0.8,-114.514,314.159)