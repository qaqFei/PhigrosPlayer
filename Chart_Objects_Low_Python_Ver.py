from __future__ import annotations
from dataclasses import dataclass
import typing

class _low_python_version_use_dataclass:
    def __init__(self,**kw) -> None:
        for key,val in zip(kw.keys(),kw.values()):
            setattr(self,key,val)

def dataclass(cls):return cls

@dataclass
class note(_low_python_version_use_dataclass):
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
class speedEvent(_low_python_version_use_dataclass): ...

@dataclass
class judgeLineMoveEvent(_low_python_version_use_dataclass): ...

@dataclass
class judgeLineRotateEvent(_low_python_version_use_dataclass): ...

@dataclass
class judgeLineDisappearEvent(_low_python_version_use_dataclass): ...

@dataclass
class judgeLine(_low_python_version_use_dataclass):
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
class Phigros_Chart(_low_python_version_use_dataclass):

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