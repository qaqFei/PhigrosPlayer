from __future__ import annotations
from dataclasses import dataclass
import typing

class _low_python_version_use_dataclass:
    def __init__(self,**kw) -> None:
        for key,val in zip(kw.keys(),kw.values()):
            setattr(self,key,val)

@dataclass
class note:
    type:typing.Literal[1,2,3,4]
    time:int|float
    positionX:int|float
    holdTime:int|float
    speed:int|float
    floorPosition:int|float
    clicked:bool
    morebets:bool
    id:int
    rendered:bool

    def __eq__(self,oth):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        note_t = {1:"t",2:"d",3:"h",4:"f"}[self.type]
        return f"{self.master.id}+{self.id}{note_t}"

@dataclass
class speedEvent:
    startTime:int|float
    endTime:int|float
    value:int|float
    floorPosition:int|float|None

@dataclass
class judgeLineMoveEvent:
    startTime:int|float
    endTime:int|float
    start:int|float
    end:int|float
    start2:int|float
    end2:int|float

@dataclass
class judgeLineRotateEvent:
    startTime:int|float
    endTime:int|float
    start:int|float
    end:int|float

@dataclass
class judgeLineDisappearEvent:
    startTime:int|float
    endTime:int|float
    start:int|float
    end:int|float

@dataclass
class judgeLine:
    id:int
    bpm:int|float
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
    offset:int|float
    judgeLineList:list[judgeLine]

    def cal_note_num(self):
        self.note_num = 0
        for judgeLine in self.judgeLineList:
            for _ in judgeLine.notesAbove:
                self.note_num += 1
            for _ in judgeLine.notesBelow:
                self.note_num += 1
    
    def cal_score(self,combo:int) -> str:
        score = int((combo / self.note_num) * 1e6 + 0.5)
        return f"{score:>7}".replace(" ","0")

del typing,dataclass