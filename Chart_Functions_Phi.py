from threading import Thread
import typing

import Chart_Objects_Phi
import Const
import Tool_Functions

def Init(
    phigros_chart_obj_:Chart_Objects_Phi.Phigros_Chart,
    PHIGROS_X_:float,PHIGROS_Y_:float,
    w_:int,h_:int
):
    global phigros_chart_obj
    global PHIGROS_X,PHIGROS_Y
    global w,h
    
    phigros_chart_obj = phigros_chart_obj_
    PHIGROS_X,PHIGROS_Y = PHIGROS_X_,PHIGROS_Y_
    w,h = w_,h_

def Cal_Combo(now_time:float) -> int:
    combo = 0
    for judgeLine in phigros_chart_obj.judgeLineList:
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

def Cal_judgeLine_NoteDy_ByTime(judgeLine:Chart_Objects_Phi.judgeLine,time:float) -> float:
    if not judgeLine.speedEvents: return 0.0
    for speed_event in judgeLine.speedEvents:
        if speed_event.startTime <= time <= speed_event.endTime:
            dy = speed_event.floorPosition + (
                time - speed_event.startTime
            ) * judgeLine.T * speed_event.value
            return dy * PHIGROS_Y
    last_speed_event = judgeLine.speedEvents[-1]
    dy = last_speed_event.floorPosition + (time - last_speed_event.endTime) * judgeLine.T * last_speed_event.value
    return dy * PHIGROS_Y

def Update_JudgeLine_Configs(judgeLine_Configs:Chart_Objects_Phi.judgeLine_Configs,now_t:typing.Union[int,float]):
    for judgeLine_cfg in judgeLine_Configs.Configs:
        judgeLine:Chart_Objects_Phi.judgeLine = judgeLine_cfg.line
        judgeLine_cfg.time = now_t / judgeLine.T
        judgeLine_cfg.rotate = judgeLine.get_datavar_rotate(judgeLine_cfg.time)
        judgeLine_cfg.disappear = judgeLine.get_datavar_disappear(judgeLine_cfg.time)
        judgeLine_cfg.pos = judgeLine.get_datavar_move(judgeLine_cfg.time,w,h)

def FrameData_ProcessExTask(ExTask,eval_func):
    break_flag = False
    
    for ext in ExTask:
        if ext[0] == "break":
            break_flag = True
        elif ext[0] == "set":
            eval_func(f"exec('global {ext[1]}; {ext[1]} = {ext[2]}')")
        elif ext[0] == "thread-call":
            Thread(target=eval_func(ext[1]),args=eval_func(ext[2]),daemon=True).start()
        
    return break_flag

def Load_Chart_Object(
    phigros_chart:Const.CHART_JSON_TYPE
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
                        effect_random_blocks = Tool_Functions.get_effect_random_blocks()
                    )
                    for notesAbove_item in judgeLine_item["notesAbove"]
                ],
                notesBelow = [
                    Chart_Objects_Phi.note(
                        type = notesBelow_item["type"],
                        time = notesBelow_item["time"],
                        positionX = notesBelow_item["positionX"],
                        holdTime = notesBelow_item["holdTime"],
                        speed = notesBelow_item["speed"],
                        floorPosition = notesBelow_item["floorPosition"],
                        id = Tool_Functions.Get_A_New_NoteId(),
                        by_judgeLine_id = Tool_Functions.Get_A_New_NoteId_By_judgeLine(judgeLine_item),
                        effect_random_blocks = Tool_Functions.get_effect_random_blocks()
                    )
                    for notesBelow_item in judgeLine_item["notesBelow"]
                ],
                speedEvents = [
                    Chart_Objects_Phi.speedEvent(
                        startTime = speedEvent_item["startTime"],
                        endTime = speedEvent_item["endTime"],
                        value = speedEvent_item["value"]
                    )
                    for speedEvent_item in judgeLine_item["speedEvents"]
                ],
                judgeLineMoveEvents = [
                    Chart_Objects_Phi.judgeLineMoveEvent(
                        startTime = judgeLineMoveEvent_item["startTime"],
                        endTime = judgeLineMoveEvent_item["endTime"],
                        start = judgeLineMoveEvent_item["start"],
                        end = judgeLineMoveEvent_item["end"],
                        start2 = judgeLineMoveEvent_item["start2"],
                        end2 = judgeLineMoveEvent_item["end2"]
                    )
                    for judgeLineMoveEvent_item in judgeLine_item["judgeLineMoveEvents"]
                ] if len(judgeLine_item["judgeLineMoveEvents"]) > 0 and "start2" in judgeLine_item["judgeLineMoveEvents"][0] and "end2" in judgeLine_item["judgeLineMoveEvents"][0] else [
                    Chart_Objects_Phi.judgeLineMoveEvent(
                        startTime = judgeLineMoveEvent_item["startTime"],
                        endTime = judgeLineMoveEvent_item["endTime"],
                        start = Tool_Functions.unpack_pos(judgeLineMoveEvent_item["start"])[0] / 880,
                        end = Tool_Functions.unpack_pos(judgeLineMoveEvent_item["end"])[0] / 880,
                        start2 = Tool_Functions.unpack_pos(judgeLineMoveEvent_item["start"])[1] / 520,
                        end2 = Tool_Functions.unpack_pos(judgeLineMoveEvent_item["end"])[1] / 520
                    )
                    for judgeLineMoveEvent_item in judgeLine_item["judgeLineMoveEvents"]
                ],
                judgeLineRotateEvents = [
                    Chart_Objects_Phi.judgeLineRotateEvent(
                        startTime = judgeLineRotateEvent_item["startTime"],
                        endTime = judgeLineRotateEvent_item["endTime"],
                        start = judgeLineRotateEvent_item["start"],
                        end = judgeLineRotateEvent_item["end"]
                    )
                    for judgeLineRotateEvent_item in judgeLine_item["judgeLineRotateEvents"]
                ],
                judgeLineDisappearEvents = [
                    Chart_Objects_Phi.judgeLineDisappearEvent(
                        startTime = judgeLineDisappearEvent_item["startTime"],
                        endTime = judgeLineDisappearEvent_item["endTime"],
                        start = judgeLineDisappearEvent_item["start"],
                        end = judgeLineDisappearEvent_item["end"]
                    )
                    for judgeLineDisappearEvent_item in judgeLine_item["judgeLineDisappearEvents"]
                ]
            )
            for index,judgeLine_item in enumerate(phigros_chart.get("judgeLineList", []))
        ]
    )
    
    print("Finding Chart More Bets...")
    notes = [item for judgeLine in phigros_chart_obj.judgeLineList for item in judgeLine.notesAbove + judgeLine.notesBelow]
    note_times = {}
    for note in notes:
        if note.time not in note_times:
            note_times[note.time] = (False, note)
        else:
            if not note_times[note.time][0]:
                note_times[note.time][-1].morebets = True
                note_times[note.time] = (True, note)
            note.morebets = True
    del notes,note_times
        
    phigros_chart_obj.init()
    print("Load Chart Object Successfully.")
    return phigros_chart_obj