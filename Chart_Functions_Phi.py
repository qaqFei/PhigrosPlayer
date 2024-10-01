import typing
from threading import Thread

import Chart_Objects_Phi
import Const
import Tool_Functions

def Cal_Combo(now_time:float, chart_obj: Chart_Objects_Phi.Phigros_Chart) -> int:
    combo = 0
    for judgeLine in chart_obj.judgeLineList:
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            if note.time * judgeLine.T <= now_time and note.type != Const.Note.HOLD:
                combo += 1
            elif note.type == Const.Note.HOLD:
                if note.hold_length_sec > 0.2:
                    if note.hold_endtime - 0.2 <= now_time:
                        combo += 1
                elif note.time * judgeLine.T <= now_time:
                    combo += 1
    return combo

def Update_JudgeLine_Configs(judgeLine_Configs: Chart_Objects_Phi.judgeLine_Configs, now_t: float, w: int, h: int):
    for judgeLine_cfg in judgeLine_Configs.Configs:
        judgeLine = judgeLine_cfg.line
        judgeLine_cfg.time = now_t / judgeLine.T
        judgeLine_cfg.rotate = judgeLine.get_datavar_rotate(judgeLine_cfg.time)
        judgeLine_cfg.disappear = judgeLine.get_datavar_disappear(judgeLine_cfg.time)
        judgeLine_cfg.pos = judgeLine.get_datavar_move(judgeLine_cfg.time, w, h)

def FrameData_ProcessExTask(ExTask, eval_func):
    break_flag = False
    
    for ext in ExTask:
        if ext[0] == "break":
            break_flag = True
        elif ext[0] == "thread-call":
            Thread(
                target = eval_func(ext[1]),
                args = eval_func(ext[2]),
                daemon = True
            ).start()
        
    return break_flag

def Load_Chart_Object(
    phigros_chart:dict
):
    print("Loading Chart Object...")
    phigros_chart_obj = Chart_Objects_Phi.Phigros_Chart(
        formatVersion = phigros_chart.get("formatVersion", 3),
        offset = phigros_chart.get("offset", 0.0),
        judgeLineList = [
            Chart_Objects_Phi.judgeLine(
                id = index,
                bpm = judgeLine_item.get("bpm", float("inf")),
                notesAbove = [
                    Chart_Objects_Phi.note(
                        type = notesAbove_item.get("type", 1),
                        time = notesAbove_item.get("time", -1.0),
                        positionX = notesAbove_item.get("positionX", 0.0),
                        holdTime = notesAbove_item.get("holdTime", 0.0),
                        speed = notesAbove_item.get("speed", -1.0),
                        floorPosition = notesAbove_item.get("floorPosition", -1.0),
                        id = Tool_Functions.Get_A_New_NoteId(),
                        by_judgeLine_id = Tool_Functions.Get_A_New_NoteId_By_judgeLine(judgeLine_item),
                        effect_random_blocks = Tool_Functions.get_effect_random_blocks(),
                        above = True
                    )
                    for notesAbove_item in judgeLine_item.get("notesAbove", [])
                ],
                notesBelow = [
                    Chart_Objects_Phi.note(
                        type = notesBelow_item.get("type", 1),
                        time = notesBelow_item.get("time", -1.0),
                        positionX = notesBelow_item.get("positionX", 0.0),
                        holdTime = notesBelow_item.get("holdTime", 0.0),
                        speed = notesBelow_item.get("speed", -1.0),
                        floorPosition = notesBelow_item.get("floorPosition", -1.0),
                        id = Tool_Functions.Get_A_New_NoteId(),
                        by_judgeLine_id = Tool_Functions.Get_A_New_NoteId_By_judgeLine(judgeLine_item),
                        effect_random_blocks = Tool_Functions.get_effect_random_blocks(),
                        above = False
                    )
                    for notesBelow_item in judgeLine_item.get("notesBelow", [])
                ],
                speedEvents = [
                    Chart_Objects_Phi.speedEvent(
                        startTime = speedEvent_item.get("startTime", -1.0),
                        endTime = speedEvent_item.get("endTime", -1.0),
                        value = speedEvent_item.get("value", 0.0)
                    )
                    for speedEvent_item in judgeLine_item.get("speedEvents", [])
                ],
                judgeLineMoveEvents = [
                    Chart_Objects_Phi.judgeLineMoveEvent(
                        startTime = judgeLineMoveEvent_item.get("startTime", -1.0),
                        endTime = judgeLineMoveEvent_item.get("endTime", -1.0),
                        start = judgeLineMoveEvent_item.get("start", 0.5),
                        end = judgeLineMoveEvent_item.get("end", 0.5),
                        start2 = judgeLineMoveEvent_item.get("start2", 0.5),
                        end2 = judgeLineMoveEvent_item.get("end2", 0.5)
                    )
                    for judgeLineMoveEvent_item in judgeLine_item.get("judgeLineMoveEvents", [])
                ] if len(judgeLine_item_MoveE := judgeLine_item.get("judgeLineMoveEvents", [])) > 0 and "start2" in judgeLine_item_MoveE[0] and "end2" in judgeLine_item_MoveE[0] else [
                    Chart_Objects_Phi.judgeLineMoveEvent(
                        startTime = judgeLineMoveEvent_item.get("startTime", -1.0),
                        endTime = judgeLineMoveEvent_item.get("endTime", -1.0),
                        start = Tool_Functions.unpack_pos(judgeLineMoveEvent_item.get("start", 0.0))[0] / 880,
                        end = Tool_Functions.unpack_pos(judgeLineMoveEvent_item.get("end", 0.0))[0] / 880,
                        start2 = Tool_Functions.unpack_pos(judgeLineMoveEvent_item.get("start", 0.0))[1] / 520,
                        end2 = Tool_Functions.unpack_pos(judgeLineMoveEvent_item.get("end", 0.0))[1] / 520
                    )
                    for judgeLineMoveEvent_item in judgeLine_item.get("judgeLineMoveEvents", [])
                ],
                judgeLineRotateEvents = [
                    Chart_Objects_Phi.judgeLineRotateEvent(
                        startTime = judgeLineRotateEvent_item.get("startTime", -1.0),
                        endTime = judgeLineRotateEvent_item.get("endTime", -1.0),
                        start = judgeLineRotateEvent_item.get("start", 0.0),
                        end = judgeLineRotateEvent_item.get("end", 0.0)
                    )
                    for judgeLineRotateEvent_item in judgeLine_item.get("judgeLineRotateEvents", [])
                ],
                judgeLineDisappearEvents = [
                    Chart_Objects_Phi.judgeLineDisappearEvent(
                        startTime = judgeLineDisappearEvent_item.get("startTime", -1.0),
                        endTime = judgeLineDisappearEvent_item.get("endTime", -1.0),
                        start = judgeLineDisappearEvent_item.get("start", 0.0),
                        end = judgeLineDisappearEvent_item.get("end", 0.0)
                    )
                    for judgeLineDisappearEvent_item in judgeLine_item.get("judgeLineDisappearEvents", [])
                ]
            )
            for index,judgeLine_item in enumerate(phigros_chart.get("judgeLineList", []))
        ]
    )
    
    print("Finding Chart More Bets...")
    note_times = {}
    for note, judgeLine in [(item, judgeLine) for judgeLine in phigros_chart_obj.judgeLineList for item in judgeLine.notesAbove + judgeLine.notesBelow]:
        t = note.time * (1.875 / judgeLine.bpm)
        if t not in note_times:
            note_times[t] = (False, note)
        else:
            if not note_times[t][0]:
                note_times[t][-1].morebets = True
                note_times[t] = (True, note)
            note.morebets = True
    
    print("Load Chart Object Successfully.")
    return phigros_chart_obj