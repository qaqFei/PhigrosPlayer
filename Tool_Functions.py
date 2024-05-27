from math import cos,sin,radians,pi
from random import randint
from sys import argv
import typing

note_id = -1
random_block_num = 4
if "-random-block-num" in argv:
    random_block_num = eval(argv[argv.index("-random-block-num") + 1])

def Get_Animation_Gr(fps:float,t:float):
    gr_x = int(fps * t) + 1
    gr = [cos(x / gr_x) + 1 for x in range(int(gr_x * pi))]
    gr_sum = sum(gr)
    step_time = t / len(gr)
    return [item / gr_sum for item in gr],step_time

def rotate_point(x,y,θ,r):
    xo = r * cos(radians(θ))
    yo = r * sin(radians(θ))
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
    return sin(x * (pi / 2))

def get_effect_random_blocks() -> typing.Tuple[int,int,int,int]:
    return tuple((randint(1,90) for _ in range(random_block_num)))