from __future__ import annotations
from dataclasses import dataclass
from random import randint
from fractions import Fraction
import typing

import rpe_easing
import Tool_Functions
import Const

class _EqByMemory:
    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, type(self)):
            return self is oth
        return False

@dataclass
class note(_EqByMemory):
    time: float
    type: typing.Literal[1, 2, 3, 4]
    holdtime: float
    positionX: float
    speed: float # noly hold
    fake: bool
    above: bool
    
    morebets: bool = False
    clicked: bool = False
    
    def __post_init__(self):
        self.type_string = {
            Const.Note.TAP: "Tap",
            Const.Note.DRAG: "Drag",
            Const.Note.HOLD: "Hold",
            Const.Note.FLICK: "Flick"
        }[self.type]
    
@dataclass
class speedEvent(_EqByMemory):
    startTime: float
    endTime: float
    value: float

@dataclass
class alphaEvent(_EqByMemory):
    startTime: float
    endTime: float
    start: float
    end: float
    easingType: int

@dataclass
class moveEvent(_EqByMemory):
    startTime: float
    endTime: float
    startX: float
    startY: float
    endX: float
    endY: float
    easingType: int

@dataclass
class rotateEvent(_EqByMemory):
    startTime: float
    endTime: float
    start: float
    end: float
    easingType: int

@dataclass
class judgeLine(_EqByMemory):
    bpm: float
    notes: list[note]
    speedEvents: list[speedEvent]
    alphaEvents: list[alphaEvent]
    moveEvents: list[moveEvent]
    rotateEvents: list[rotateEvent]
    
    def getAlpha(self, t: float) -> float:
        for e in self.alphaEvents:
            if e.startTime <= t <= e.endTime:
                return Tool_Functions.easing_interpolation(
                    t, e.startTime, e.endTime,
                    e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1]
                )
        return 0.0
    
    def getMove(self, t: float) -> tuple[float, float]:
        for e in self.moveEvents:
            if e.startTime <= t <= e.endTime:
                return (
                    Tool_Functions.easing_interpolation(
                        t, e.startTime, e.endTime,
                        e.startX, e.endX, rpe_easing.ease_funcs[e.easingType - 1]
                    ),
                    1.0 - Tool_Functions.easing_interpolation(
                        t, e.startTime, e.endTime,
                        e.startY, e.endY, rpe_easing.ease_funcs[e.easingType - 1]
                    )
                )
        return 0.0, 0.0

    def getRotate(self, t: float) -> float:
        for e in self.rotateEvents:
            if e.startTime <= t <= e.endTime:
                return Tool_Functions.easing_interpolation(
                    t, e.startTime, e.endTime,
                    e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1]
                )
        return 0.0
    
    def _getFloorPosition(self, lineTime: float):
        fp = 0.0
        bTime = 60 / self.bpm
        for e in self.speedEvents:
            if e.startTime <= lineTime <= e.endTime:
                fp += (lineTime - e.startTime) * bTime * e.value
            elif e.endTime < lineTime:
                fp += (e.endTime - e.startTime) * bTime * e.value
        return fp
    
    def getNoteFloorPosition(self, lineTime: float, note: note):
        return self._getFloorPosition(note.time) - self._getFloorPosition(lineTime)

@dataclass
class Chart(_EqByMemory):
    lines: list[judgeLine]
    
    def saveAsPpre(self) -> dict:
        data = {
            "lines": []
        }
        
        for line in self.lines:
            lineData = {
                "bpm": line.bpm,
                "notes": [{
                    "type": note.type,
                    "time": note.time,
                    "holdtime": note.holdtime,
                    "positionX": note.positionX,
                    "speed": note.speed,
                    "fake": note.fake,
                    "above": note.above
                } for note in line.notes],
                "speedEvents": [{
                    "startTime": se.startTime,
                    "endTime": se.endTime,
                    "value": se.value
                } for se in line.speedEvents],
                "alphaEvents": [{
                    "startTime": ae.startTime,
                    "endTime": ae.endTime,
                    "start": ae.start,
                    "end": ae.end,
                    "easingType": ae.easingType
                } for ae in line.alphaEvents],
                "moveEvents": [{
                    "startTime": me.startTime,
                    "endTime": me.endTime,
                    "startX": me.startX,
                    "startY": me.startY,
                    "endX": me.endX,
                    "endY": me.endY,
                    "easingType": me.easingType
                } for me in line.moveEvents],
                "rotateEvents": [{
                    "startTime": re.startTime,
                    "endTime": re.endTime,
                    "start": re.start,
                    "end": re.end,
                    "easingType": re.easingType
                } for re in line.rotateEvents],
            }
            
            data["lines"].append(lineData)
        
        return data

    def _getRpeBeat(self, t: float) -> list:
        t = t if t >= 0.0 else 0.0
        f = Fraction(t % (abs(t) / t)).limit_denominator((2 << 31) - 2) if t != 0 else Fraction(0)
        return [int(t), f.numerator, f.denominator]
        
    def saveAsRpe(self) -> dict:
        if not self.lines:
            GlobalBpm = sum([i.bpm for i in self.lines]) / len(self.lines)
        else:
            GlobalBpm = 140.0
        data = {
            "BPMList": [ { "bpm": GlobalBpm, "startTime": [0, 0, 1] } ],
            "META": {
                "RPEVersion": 130,
                "background": "BACKGROUND",
                "charter": "CHARTER",
                "composer": "COMPOSER",
                "id": f"{randint(0, 2 << 31)}",
                "level": "LEVEL",
                "name": "NAME",
                "offset": 0,
                "song": "SONG"
            },
            "judgeLineGroup" : [ "Default" ],
            "judgeLineList": []
        }
        
        for line in self.lines:
            lineData = {
                "Group" : 0,
                "Name" : "Untitled",
                "Texture" : "line.png",
                "alphaControl" : [
                    {
                        "alpha" : 1.0,
                        "easing" : 1,
                        "x" : 0.0
                    },
                    {
                        "alpha" : 1.0,
                        "easing" : 1,
                        "x" : 9999999.0
                    }
                ],
                "bpmfactor" : 1.0,
                "eventLayers": [{"alphaEvents": [], "moveXEvents": [], "moveYEvents": [], "rotateEvents": [], "speedEvents": []}],
                "extended" : {
                    "inclineEvents" : [
                    {
                        "bezier" : 0,
                        "bezierPoints" : [ 0.0, 0.0, 0.0, 0.0 ],
                        "easingLeft" : 0.0,
                        "easingRight" : 1.0,
                        "easingType" : 0,
                        "end" : 0.0,
                        "endTime" : [ 1, 0, 1 ],
                        "linkgroup" : 0,
                        "start" : 0.0,
                        "startTime" : [ 0, 0, 1 ]
                    }
                    ]
                },
                "father" : -1,
                "isCover" : 1,
                "notes": [],
                "numOfNotes": len(line.notes),
                "posControl" : [
                    {
                        "easing" : 1,
                        "pos" : 1.0,
                        "x" : 0.0
                    },
                    {
                        "easing" : 1,
                        "pos" : 1.0,
                        "x" : 9999999.0
                    }
                ],
                "sizeControl" : [
                    {
                        "easing" : 1,
                        "size" : 1.0,
                        "x" : 0.0
                    },
                    {
                        "easing" : 1,
                        "size" : 1.0,
                        "x" : 9999999.0
                    }
                ],
                "skewControl" : [
                    {
                        "easing" : 1,
                        "skew" : 0.0,
                        "x" : 0.0
                    },
                    {
                        "easing" : 1,
                        "skew" : 0.0,
                        "x" : 9999999.0
                    }
                ],
                "yControl" : [
                    {
                        "easing" : 1,
                        "x" : 0.0,
                        "y" : 1.0
                    },
                    {
                        "easing" : 1,
                        "x" : 9999999.0,
                        "y" : 1.0
                    }
                ],
                "zOrder" : 0
            }
            
            for e in line.speedEvents:
                lineData["eventLayers"][0]["speedEvents"].append({
                    "start": e.value * 0.6 * 900 / 120,
                    "end": e.value * 0.6 * 900 / 120,
                    "startTime": self._getRpeBeat(e.startTime * (60 / line.bpm) / (60 / GlobalBpm)),
                    "endTime": self._getRpeBeat(e.endTime * (60 / line.bpm) / (60 / GlobalBpm)),
                    "linkgroup": 0
                })
            
            for e in line.alphaEvents:
                lineData["eventLayers"][0]["alphaEvents"].append({
                    "bezier": 0,
                    "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                    "easingLeft": 0.0,
                    "easingRight": 1.0,
                    "easingType": e.easingType,
                    "end": int(e.end * 255),
                    "endTime": self._getRpeBeat(e.endTime * (60 / line.bpm) / (60 / GlobalBpm)),
                    "linkgroup": 0,
                    "start": int(e.start * 255),
                    "startTime": self._getRpeBeat(e.startTime * (60 / line.bpm) / (60 / GlobalBpm))
                })
        
            for e in line.moveEvents:
                lineData["eventLayers"][0]["moveXEvents"].append({
                    "bezier": 0,
                    "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                    "easingLeft": 0.0,
                    "easingRight": 1.0,
                    "easingType": e.easingType,
                    "end": (e.endX - 0.5) * 1350,
                    "endTime": self._getRpeBeat(e.endTime * (60 / line.bpm) / (60 / GlobalBpm)),
                    "linkgroup": 0,
                    "start": (e.startX - 0.5) * 1350,
                    "startTime": self._getRpeBeat(e.startTime * (60 / line.bpm) / (60 / GlobalBpm))
                })
                lineData["eventLayers"][0]["moveYEvents"].append({
                    "bezier": 0,
                    "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                    "easingLeft": 0.0,
                    "easingRight": 1.0,
                    "easingType": e.easingType,
                    "end": (e.endY - 0.5) * 900,
                    "endTime": self._getRpeBeat(e.endTime * (60 / line.bpm) / (60 / GlobalBpm)),
                    "linkgroup": 0,
                    "start": (e.startY - 0.5) * 900,
                    "startTime": self._getRpeBeat(e.startTime * (60 / line.bpm) / (60 / GlobalBpm))
                })
            
            for e in line.rotateEvents:
                lineData["eventLayers"][0]["rotateEvents"].append({
                    "bezier": 0,
                    "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                    "easingLeft": 0.0,
                    "easingRight": 1.0,
                    "easingType": e.easingType,
                    "end": - e.end,
                    "endTime": self._getRpeBeat(e.endTime * (60 / line.bpm) / (60 / GlobalBpm)),
                    "linkgroup": 0,
                    "start": - e.start,
                    "startTime": self._getRpeBeat(e.startTime * (60 / line.bpm) / (60 / GlobalBpm))
                })
            
            for note in line.notes:
                if note.type != Const.Note.HOLD:
                    speed = note.speed
                else:
                    try:
                        speed = note.holdtime * (60 / line.bpm) * note.speed / - line.getNoteFloorPosition(note.time + note.holdtime, note)
                    except Exception as e:
                        speed = 1.0
                lineData["notes"].append({
                    "above": int(not note.above) + 1,
                    "alpha": 255,
                    "endTime": self._getRpeBeat((note.time + note.holdtime) * (60 / line.bpm) / (60 / GlobalBpm)),
                    "isFake": int(note.fake),
                    "positionX": note.positionX / (1 / 0.05625) * 1350,
                    "size": 1.0,
                    "speed": speed,
                    "startTime": self._getRpeBeat(note.time * (60 / line.bpm) / (60 / GlobalBpm)),
                    "type": {1:1, 3:2, 4:3, 2:4}[note.type],
                    "visibleTime": 999999.0,
                    "yOffset": 0.0
                })
            
            data["judgeLineList"].append(lineData)
        
        return data
    
    def saveAsPigeonPhigros(self) -> dict:
        easingSplitNumber = 20
        data = {
            "formatVersion": 3,
            "offset": 0.0,
            "judgeLineList": []
        }
        
        for line in self.lines:
            lineData = {
                "bpm": line.bpm,
                "notesAbove": [],
                "notesBelow": [],
                "speedEvents": [],
                "judgeLineMoveEvents": [],
                "judgeLineRotateEvents": [],
                "judgeLineDisappearEvents": []
            }
            
            for e in line.speedEvents:
                lineData["speedEvents"].append({
                    "startTime": e.startTime * 60 / 1.875,
                    "endTime": e.endTime * 60 / 1.875,
                    "value": e.value
                })
            
            for e in line.alphaEvents:
                if e.easingType == 1:
                    lineData["judgeLineDisappearEvents"].append({
                        "startTime": e.startTime * 60 / 1.875,
                        "endTime": e.endTime * 60 / 1.875,
                        "start": e.start,
                        "end": e.end,
                    })
                else:
                    for i in range(easingSplitNumber):
                        st = e.startTime + i / easingSplitNumber * (e.endTime - e.startTime)
                        et = e.startTime + (i + 1) / easingSplitNumber * (e.endTime - e.startTime)
                        sv = Tool_Functions.easing_interpolation(st, e.startTime, e.endTime, e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1])
                        ev = Tool_Functions.easing_interpolation(et, e.startTime, e.endTime, e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1])
                        lineData["judgeLineDisappearEvents"].append({
                            "startTime": st * 60 / 1.875,
                            "endTime": et * 60 / 1.875,
                            "start": sv,
                            "end": ev,
                        })
            
            for e in line.moveEvents:
                if e.easingType == 1:
                    lineData["judgeLineMoveEvents"].append({
                        "startTime": e.startTime * 60 / 1.875,
                        "endTime": e.endTime * 60 / 1.875,
                        "start": e.startX,
                        "start2": e.startY,
                        "end": e.endX,
                        "end2": e.endY,
                    })
                else:
                    for i in range(easingSplitNumber):
                        st = e.startTime + i / easingSplitNumber * (e.endTime - e.startTime)
                        et = e.startTime + (i + 1) / easingSplitNumber * (e.endTime - e.startTime)
                        svx = Tool_Functions.easing_interpolation(st, e.startTime, e.endTime, e.startX, e.endX, rpe_easing.ease_funcs[e.easingType - 1])
                        evx = Tool_Functions.easing_interpolation(et, e.startTime, e.endTime, e.startX, e.endX, rpe_easing.ease_funcs[e.easingType - 1])
                        svy = Tool_Functions.easing_interpolation(st, e.startTime, e.endTime, e.startY, e.endY, rpe_easing.ease_funcs[e.easingType - 1])
                        evy = Tool_Functions.easing_interpolation(et, e.startTime, e.endTime, e.startY, e.endY, rpe_easing.ease_funcs[e.easingType - 1])
                        lineData["judgeLineMoveEvents"].append({
                            "startTime": st * 60 / 1.875,
                            "endTime": et * 60 / 1.875,
                            "start": svx,
                            "start2": svy,
                            "end": evx,
                            "end2": evy,
                        })

            for e in line.rotateEvents:
                if e.easingType == 1:
                    lineData["judgeLineRotateEvents"].append({
                        "startTime": e.startTime * 60 / 1.875,
                        "endTime": e.endTime * 60 / 1.875,
                        "start": e.start,
                        "end": e.end,
                    })
                else:
                    for i in range(easingSplitNumber):
                        st = e.startTime + i / easingSplitNumber * (e.endTime - e.startTime)
                        et = e.startTime + (i + 1) / easingSplitNumber * (e.endTime - e.startTime)
                        sv = Tool_Functions.easing_interpolation(st, e.startTime, e.endTime, e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1])
                        ev = Tool_Functions.easing_interpolation(et, e.startTime, e.endTime, e.start, e.end, rpe_easing.ease_funcs[e.easingType - 1])
                        lineData["judgeLineRotateEvents"].append({
                            "startTime": st * 60 / 1.875,
                            "endTime": et * 60 / 1.875,
                            "start": sv,
                            "end": ev,
                        })
            
            for note in line.notes:
                noteData = {
                    "time": note.time * 60 / 1.875,
                    "type": note.type,
                    "holdTime": note.holdtime * 60 / 1.875,
                    "positionX": note.positionX,
                    "speed": note.speed,
                    "floorPosition": line.getNoteFloorPosition(0, note)
                }
                if note.above: lineData["notesAbove"].append(noteData)
                else: lineData["notesBelow"].append(noteData)
            data["judgeLineList"].append(lineData)
        
        return data