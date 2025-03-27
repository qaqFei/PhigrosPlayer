import typing
import json
import logging
from dataclasses import dataclass, field

import const
import rpe_easing
import light_tool_funcs

type eventValueType = float|str|tuple[float, float, float]

class ChartFormat:
    unset = object()
    phi = object()
    rpe = object()
    pec = object()
    pbc = object()
    
    notetype_map: dict[object, dict[int, int]] = {
        phi: {1: 1, 2: 2, 3: 3, 4: 4}, # standard
        rpe: ...
    }
    
    @staticmethod
    def load_phi(data: dict):
        def _time_coverter(json_line: dict, t: float):
            return t * (1.875 / json_line.get("bpm", 140.0))
        
        def _pos_coverter_x(x: float):
            return x * const.PGR_UW
        
        def _pos_coverter_y(y: float):
            return y * const.PGR_UH
        
        def _put_note(*, json_line: dict, line: JudgeLine, json_note: dict, isAbove: bool):
            if not isinstance(json_note, dict):
                logging.warning(f"Invalid note type: {type(json_note)}")
                return
            
            note_type = ChartFormat.notetype_map[result.type].get(json_note.get("type", 1), const.NOTE_TYPE.TAP)
            speed = json_note.get("speed", 0.0)
            
            note = Note(
                type = note_type,
                time = _time_coverter(json_line, json_note.get("time", 0.0)),
                holdTime = _time_coverter(json_line, json_note.get("holdTime", 0.0)),
                positionX = _pos_coverter_x(json_note.get("positionX", 0.0)),
                speed = _pos_coverter_y(speed) if note_type == const.NOTE_TYPE.HOLD else speed,
                isAbove = isAbove
            )
            
            line.notes.append(note)
        
        def _put_events(es: list[LineEvent], json_es: list[dict], converter: typing.Callable[[float], float], startkey: str = "start", endkey: str = "end"):
            for json_e in json_es:
                if not isinstance(json_e, dict):
                    logging.warning(f"Invalid event type: {type(json_e)}")
                    continue
                
                es.append(LineEvent(
                    startTime = _time_coverter(json_line, json_e.get("startTime", 0.0)),
                    endTime = _time_coverter(json_line, json_e.get("endTime", 0.0)),
                    start = converter(json_e.get(startkey, 0.0)),
                    end = converter(json_e.get(endkey, 0.0))
                ))
        
        formatVersion = data.get("formatVersion", 0)
        if formatVersion not in (1, 2, 3):
            logging.warning(f"Unsupported phi chart format version: {formatVersion}")
            formatVersion = 3
        
        if formatVersion == 2:
            data = light_tool_funcs.SaveAsNewFormat(data)
        
        result = CommonChart()
        result.type = ChartFormat.phi
        
        result.offset = data.get("offset", 0.0)
        
        for json_line in data.get("judgeLineList", []):
            json_line: dict
            
            line = JudgeLine()
            
            for json_note in json_line.get("notesAbove", []):
                _put_note(
                    json_line = json_line,
                    line = line,
                    json_note = json_note,
                    isAbove = True
                )
            
            for json_note in json_line.get("notesBelow", []):
                _put_note(
                    json_line = json_line,
                    line = line,
                    json_note = json_note,
                    isAbove = False
                )
            
            if formatVersion == 1:
                for json_e in json_line.get("judgeLineMoveEvents", []):
                    json_e["start"], json_e["start2"] = light_tool_funcs.unpack_pos(json_e.get("start", 0))
                    json_e["end"], json_e["end2"] = light_tool_funcs.unpack_pos(json_e.get("end", 0))
            
            elayer = EventLayerItem()
            _put_events(elayer.alphaEvents, json_line.get("judgeLineDisappearEvents", []), lambda x: x)
            _put_events(elayer.moveXEvents, json_line.get("judgeLineMoveEvents", []), lambda x: x)
            _put_events(elayer.moveYEvents, json_line.get("judgeLineMoveEvents", []), lambda y: 1.0 - y, "start2", "end2")
            _put_events(elayer.rotateEvents, json_line.get("judgeLineRotateEvents", []), lambda r: -r)
            _put_events(elayer.speedEvents, json_line.get("speedEvents", []), _pos_coverter_y, "value", "value")
            line.eventLayers.append(elayer)
            
            result.lines.append(line)
            
        return result
    
    @staticmethod
    def load_rpe(data: dict):
        ...
    
    @staticmethod
    def load_pec(data: str):
        ...

    @staticmethod
    def load_pbc(data: bytes):
        ...

@dataclass
class Note:
    type: int
    time: float
    holdTime: float
    positionX: float
    speed: float
    
    isAbove: bool
    isFake: bool = False
    yOffset: float = 0.0
    visibleTime: typing.Optional[float] = None
    width: float = 1.0
    alpha: float = 1.0
    hitsound: typing.Optional[str] = None

@dataclass
class LineEvent:
    startTime: float
    endTime: float
    start: eventValueType
    end: eventValueType
    ease: typing.Callable[[float], float] = rpe_easing.ease_funcs[0]
    
    isFill: bool = False

@dataclass
class EventLayerItem:
    alphaEvents: list[LineEvent] = field(default_factory=list)
    moveXEvents: list[LineEvent] = field(default_factory=list)
    moveYEvents: list[LineEvent] = field(default_factory=list)
    rotateEvents: list[LineEvent] = field(default_factory=list)
    speedEvents: list[LineEvent] = field(default_factory=list)
    
    def init_fill(self):
        ...

@dataclass
class ExtendEventsItem:
    colorEvents: list[LineEvent] = field(default_factory=list)
    scaleXEvents: list[LineEvent] = field(default_factory=list)
    scaleYEvents: list[LineEvent] = field(default_factory=list)
    textEvents: list[LineEvent] = field(default_factory=list)
    gifEvents: list[LineEvent] = field(default_factory=list)

@dataclass
class JudgeLine:
    notes: list[Note] = field(default_factory=list)
    eventLayers: list[EventLayerItem] = field(default_factory=list)
    extendEvents: ExtendEventsItem = field(default_factory=ExtendEventsItem)
    
    isTextureLine: bool = False
    texture: typing.Optional[str] = None
    
    isAttachUI: bool = False
    attachUI: typing.Optional[str] = None
    
    enableCover: bool = True

@dataclass
class CommonChartOptions:
    holdIndependentSpeed: bool = True
    holdCoverAtHead: bool = True
    rpeVersion: int = -1

@dataclass
class CommonChart:
    offset: float = 0.0
    lines: list[JudgeLine] = field(default_factory=list)
    
    options: CommonChartOptions = field(default_factory=CommonChartOptions)
    type: object = field(default=lambda: ChartFormat.unset)

def load(data: bytes):
    def _unknow_type():
        raise ValueError("Unknown chart type")
    
    try:
        str_data = data.decode("utf-8")
    except Exception:
        return ChartFormat.load_pbc(data)
    
    try:
        json_data = json.loads(data)
        
        if not isinstance(json_data, dict):
            _unknow_type()
            
        if "formatVersion" in json_data:
            return ChartFormat.load_phi(json_data)
        
        elif "META" in json_data:
            return ChartFormat.load_rpe(json_data)
        
        else:
            _unknow_type()
        
    except json.JSONDecodeError:
        return ChartFormat.load_pec(str_data)
