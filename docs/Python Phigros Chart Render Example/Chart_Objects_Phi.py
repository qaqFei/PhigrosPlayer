from __future__ import annotations
from dataclasses import dataclass
from random import randint
import typing

import Const

def get_effect_random_blocks() -> typing.Tuple[int,int,int,int]:
    return tuple((randint(1,90) for _ in range(4)))

@dataclass
class note:
    type:typing.Literal[1,2,3,4]
    time:typing.Union[int,float]
    positionX:typing.Union[int,float]
    holdTime:typing.Union[int,float]
    speed:typing.Union[int,float]
    floorPosition:typing.Union[int,float]
    effect_random_blocks:typing.Tuple[int,int,int,int]
    clicked:bool = False
    morebets:bool = False
    master:typing.Union[judgeLine,None] = None
    hold_end_clicked:bool = False
    note_last_show_hold_effect_time:float = 0.0
    show_effected = False
    show_effected_hold = False
    
    def __eq__(self,oth:note):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        note_t = {
            Const.Note.TAP:"t",
            Const.Note.DRAG:"d",
            Const.Note.HOLD:"h",
            Const.Note.FLICK:"f"
        }[self.type]
        return f"{self.master.id}+{self.by_judgeLine_id}{note_t}"
    
    def _cal_holdlength(self,PHIGROS_Y):
        self.hold_length_sec = self.holdTime * self.master.T
        self.hold_length_px = (self.speed * self.hold_length_sec) * PHIGROS_Y
        self.hold_endtime = self.time * self.master.T + self.hold_length_sec
        
        #do other... hehehehe
        self.effect_times = []
        hold_starttime = self.time * self.master.T
        hold_effect_blocktime = (1 / self.master.bpm * 30)
        while True:
            hold_starttime += hold_effect_blocktime
            if hold_starttime >= self.hold_endtime:
                break
            self.effect_times.append((hold_starttime,get_effect_random_blocks()))

@dataclass
class speedEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    value:typing.Union[int,float]
    floorPosition:typing.Union[typing.Union[int,float],None]

@dataclass
class judgeLineMoveEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]
    start2:typing.Union[int,float]
    end2:typing.Union[int,float]

@dataclass
class judgeLineRotateEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]

@dataclass
class judgeLineDisappearEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]

@dataclass
class judgeLine:
    id:int
    bpm:typing.Union[int,float]
    notesAbove:list[note]
    notesBelow:list[note]
    speedEvents:list[speedEvent]
    judgeLineMoveEvents:list[judgeLineMoveEvent]
    judgeLineRotateEvents:list[judgeLineRotateEvent]
    judgeLineDisappearEvents:list[judgeLineDisappearEvent]

    def __eq__(self,oth):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        return f"JudgeLine-{self.id}"
    
    def set_master_to_notes(self):
        for note in self.notesAbove:
            note.master = self
        for note in self.notesBelow:
            note.master = self

@dataclass
class Phigros_Chart:
    formatVersion:int
    offset:typing.Union[int,float]
    judgeLineList:list[judgeLine]
    
    def init_holdlength(self,PHIGROS_Y):
        for judgeLine in self.judgeLineList:
            for note in judgeLine.notesAbove:
                note._cal_holdlength(PHIGROS_Y)
            for note in judgeLine.notesBelow:
                note._cal_holdlength(PHIGROS_Y)

del typing,dataclass