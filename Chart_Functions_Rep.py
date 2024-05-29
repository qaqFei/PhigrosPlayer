from threading import Thread
import typing

import Chart_Objects_Rep
import Tool_Functions
import Const
import PlaySound

def Init(
    w_:int,h_:int,
    Resource_:dict
):
    global w,h
    global Resource
    
    w,h = w_,h_
    Resource = Resource_

def Get_FrameData(
    rep_obj:Chart_Objects_Rep.Rep_Chart,
    now_t:float,
    Note_CanRender:typing.Callable[[float,float,typing.Union[typing.Tuple[
            typing.Tuple[float,float],
            typing.Tuple[float,float],
            typing.Tuple[float,float],
            typing.Tuple[float,float]
        ],None]],bool]
) -> Chart_Objects_Rep.FrameData:
    raise NotImplementedError

    fd = Chart_Objects_Rep.FrameData(
        bpm = 0.0,
        beat_time = 0.0,
        JudgeLine_Data = [],
        now_t_beat = 0.0,
        Note_Data = []
    )
    
    for BPMEvent in rep_obj.BPMList:
        if BPMEvent.startTime.value <= now_t:
            fd.bpm = BPMEvent.bpm
    
    fd.beat_time = 60 / fd.bpm
    fd.now_t_beat = now_t / fd.beat_time
    
    for JudgeLine in rep_obj.JudgeLineList:
        FrameData_JudgeLine = Chart_Objects_Rep.JudgeLine_FrameData(
            speed = 1.0,
            x = 0.5,
            y = 0.5,
            dy = 0.0,
            EventLayer_Data = None,
            draw_pos = None
        )
        FrameData_EventLayer = Chart_Objects_Rep.EventLayer_FrameData(
            speedValue = None,
            moveXValue = 0.5,moveYValue = 0.5,
            rotateValue = 0.0,alphaValue = -1.0
        )
        Donot_Process = False
        
        for EventLayer in JudgeLine.eventLayers:
            if Donot_Process:
                break
            if EventLayer.speedEvents is not None and FrameData_EventLayer.speedValue is not None:
                for speedEvent in EventLayer.speedEvents:
                    if speedEvent.startTime.value <= fd.now_t_beat <= speedEvent.endTime.value:
                        FrameData_EventLayer.speedValue = speedEvent.Get_Value(speedEvent.Get_EventProcess(fd.now_t_beat))
                        break
            if EventLayer.moveXEvents is not None and FrameData_EventLayer.moveXValue is not None:
                for moveXEvent in EventLayer.moveXEvents:
                    if moveXEvent.startTime.value <= fd.now_t_beat <= moveXEvent.endTime.value:
                        FrameData_EventLayer.moveXValue = (moveXEvent.Get_Value(moveXEvent.Get_EventProcess(fd.now_t_beat)) + 675) / (675 * 2) * w
                        break
            if EventLayer.moveYEvents is not None and FrameData_EventLayer.moveYValue is not None:
                for moveYEvent in EventLayer.moveYEvents:
                    if moveYEvent.startTime.value <= fd.now_t_beat <= moveYEvent.endTime.value:
                        FrameData_EventLayer.moveYValue = h - ((moveYEvent.Get_Value(moveYEvent.Get_EventProcess(fd.now_t_beat)) + 450) / (450 * 2) * h)
                        break
            if EventLayer.rotateEvents is not None and FrameData_EventLayer.rotateValue is not None:
                for rotateEvent in EventLayer.rotateEvents:
                    if rotateEvent.startTime.value <= fd.now_t_beat <= rotateEvent.endTime.value:
                        FrameData_EventLayer.rotateValue = rotateEvent.Get_Value(rotateEvent.Get_EventProcess(fd.now_t_beat))
                        break
            if EventLayer.alphaEvents is not None and FrameData_EventLayer.alphaValue is not None:
                for alphaEvent in EventLayer.alphaEvents:
                    if alphaEvent.startTime.value <= fd.now_t_beat <= alphaEvent.endTime.value:
                        FrameData_EventLayer.alphaValue = alphaEvent.Get_Value(alphaEvent.Get_EventProcess(fd.now_t_beat))
                        if FrameData_EventLayer.alphaValue < 0.0:
                            Donot_Process = True
                        break
        
        FrameData_JudgeLine.EventLayer_Data = FrameData_EventLayer
        if not (FrameData_EventLayer.alphaValue < 0.0):
            if FrameData_EventLayer.alphaValue > 255:
                FrameData_EventLayer.alphaValue = 255 & FrameData_EventLayer.alphaValue
            FrameData_EventLayer.alphaValue /= 255
            
            FrameData_JudgeLine.draw_pos = (
                *Tool_Functions.rotate_point(FrameData_EventLayer.moveXValue,FrameData_EventLayer.moveYValue,FrameData_EventLayer.rotateValue,5.76 * h),
                *Tool_Functions.rotate_point(FrameData_EventLayer.moveXValue,FrameData_EventLayer.moveYValue,FrameData_EventLayer.rotateValue + 180,5.76 * h)
            )
            
            fd.JudgeLine_Data.append(FrameData_JudgeLine)

            dy = JudgeLine.Get_Notedy(fd.bpm,fd.now_t_beat)
            for note in JudgeLine.notes:
                FrameData_Note = Chart_Objects_Rep.Note_FrameData(
                    x = Const.NAN,y = Const.NAN,
                    rotate = 0.0,type = 0,
                    positionX = 0.0,imname = "",
                    im = None
                )
                
                visible = note.startTime.value * fd.beat_time + note.visibleTime > now_t
                if not visible:
                    continue
                
                Note_ClickTime = note.startTime.value * fd.beat_time
                Note_ToClickTime = Note_ClickTime - now_t
                
                if Note_ToClickTime < 0.0:
                    if not note.clicked:
                        note.clicked = True
                        Thread(target=PlaySound.Play,args=(Resource["Note_Click_Audio"][{Const.Note_Rep.TAP:"Tap",Const.Note_Rep.DRAG:"Drag",Const.Note_Rep.HOLD:"Hold",Const.Note_Rep.FLICK:"Flick"}[note.type]],),daemon=True).start()
                    continue
                
                FrameData_Note.positionX = note.positionX / (450 * 2) * w / 2
                FrameData_Note.type = note.type
                Note_FloorPosition = (note.floorPosition - dy) * h
                
                rotatenote_at_judgeLine_pos = Tool_Functions.rotate_point(
                    FrameData_EventLayer.moveXValue,FrameData_EventLayer.moveYValue,FrameData_EventLayer.rotateValue,FrameData_Note.positionX
                )
                judgeLine_to_note_rotate_angle = 90 + FrameData_EventLayer.rotateValue - (180 if note.above == 1 else 0)
                x,y = Tool_Functions.rotate_point(
                    *rotatenote_at_judgeLine_pos,judgeLine_to_note_rotate_angle,Note_FloorPosition
                )
                
                FrameData_Note.x,FrameData_Note.y = x,y
                
                note_type = {
                    Const.Note_Rep.TAP:"Tap",
                    Const.Note_Rep.DRAG:"Drag",
                    Const.Note_Rep.HOLD:"Hold",
                    Const.Note_Rep.FLICK:"Flick"
                }[note.type]
                
                judgeLine_rotate_integer = - int(FrameData_EventLayer.rotateValue) % 360
                if note.type != Const.Note_Rep.HOLD:
                    FrameData_Note.im = Resource["Notes"][note_type + ("_dub" if note.morebets else "")][judgeLine_rotate_integer]
                    FrameData_Note.imname = f"Note_{note_type}" + ("_dub" if note.morebets else "") + f"_{judgeLine_rotate_integer}"
                else:
                    FrameData_Note.im = Resource["Notes"]["Hold"][note_type + "_Head" + ("_dub" if note.morebets else "")][judgeLine_rotate_integer]
                    FrameData_Note.imname = f"Note_{note_type}" + "_Head" + ("_dub" if note.morebets else "") + f"_{judgeLine_rotate_integer}"
                    # this_note_img_end = Resource["Notes"]["Hold"][note_type + "_End"][judgeLine_rotate_integer]
                    # this_note_imgname_end = f"Note_{note_type}" + "_End"+ f"_{judgeLine_rotate_integer}"
                
                if Note_CanRender(x,y):
                    fd.Note_Data.append(FrameData_Note)
    return fd

def Load_Chart_Object(phigros_chart):
    rep_chart_obj = Chart_Objects_Rep.Rep_Chart(
        META = Chart_Objects_Rep.MetaData(
            RPEVersion = phigros_chart["META"]["RPEVersion"],
            offset = phigros_chart["META"]["offset"],
            name = phigros_chart["META"]["name"],
            id = phigros_chart["META"]["id"],
            song = phigros_chart["META"]["song"],
            background = phigros_chart["META"]["background"],
            composer = phigros_chart["META"]["composer"],
            charter = phigros_chart["META"]["charter"],
            level = phigros_chart["META"]["level"]
        ),
        BPMList = [
            Chart_Objects_Rep.BPMEvent(
                startTime = Chart_Objects_Rep.Beat(
                    *BPMEvent_item["startTime"]
                ),
                bpm = BPMEvent_item["bpm"]
            )
            for BPMEvent_item in phigros_chart["BPMList"]
        ],
        JudgeLineList = [
            Chart_Objects_Rep.JudgeLine(
                numOfNotes = judgeLine_item["numOfNotes"],
                isCover = judgeLine_item["isCover"],
                Texture = judgeLine_item["Texture"],
                eventLayers = [
                    Chart_Objects_Rep.EventLayer(
                        speedEvents = [
                            Chart_Objects_Rep.LineEvent(
                                startTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["startTime"]
                                ),
                                endTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["endTime"]
                                ),
                                start = LineEvent_item["start"],
                                end = LineEvent_item["end"],
                                easingType = None
                            )
                            for LineEvent_item in EventLayer_item["speedEvents"]
                        ] if "speedEvents" in EventLayer_item and EventLayer_item["speedEvents"] is not None else None,
                        moveXEvents = [
                            Chart_Objects_Rep.LineEvent(
                                startTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["startTime"]
                                ),
                                endTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["endTime"]
                                ),
                                start = LineEvent_item["start"],
                                end = LineEvent_item["end"],
                                easingType = LineEvent_item["easingType"]
                            ) for LineEvent_item in EventLayer_item["moveXEvents"]
                        ] if "moveXEvents" in EventLayer_item and EventLayer_item["moveXEvents"] is not None else None,
                        moveYEvents = [
                            Chart_Objects_Rep.LineEvent(
                                startTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["startTime"]
                                ),
                                endTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["endTime"]
                                ),
                                start = LineEvent_item["start"],
                                end = LineEvent_item["end"],
                                easingType = LineEvent_item["easingType"]
                            ) for LineEvent_item in EventLayer_item["moveYEvents"]
                        ] if "moveYEvents" in EventLayer_item and EventLayer_item["moveYEvents"] is not None else None,
                        rotateEvents = [
                            Chart_Objects_Rep.LineEvent(
                                startTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["startTime"]
                                ),
                                endTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["endTime"]
                                ),
                                start = LineEvent_item["start"],
                                end = LineEvent_item["end"],
                                easingType = LineEvent_item["easingType"]
                            ) for LineEvent_item in EventLayer_item["rotateEvents"]
                        ] if "rotateEvents" in EventLayer_item and EventLayer_item["rotateEvents"] is not None else None,
                        alphaEvents = [
                            Chart_Objects_Rep.LineEvent(
                                startTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["startTime"]
                                ),
                                endTime = Chart_Objects_Rep.Beat(
                                    *LineEvent_item["endTime"]
                                ),
                                start = LineEvent_item["start"],
                                end = LineEvent_item["end"],
                                easingType = LineEvent_item["easingType"]
                            ) for LineEvent_item in EventLayer_item["alphaEvents"]
                        ] if "alphaEvents" in EventLayer_item and EventLayer_item["alphaEvents"] is not None else None,
                    )
                    for EventLayer_item in judgeLine_item["eventLayers"] if EventLayer_item is not None
                ],
                extended = Chart_Objects_Rep.Extended(
                    scaleXEvents = [
                        Chart_Objects_Rep.LineEvent(
                            startTime = Chart_Objects_Rep.Beat(
                                *LineEvent_item["startTime"]
                            ),
                            endTime = Chart_Objects_Rep.Beat(
                                *LineEvent_item["endTime"]
                            ),
                            start = LineEvent_item["start"],
                            end = LineEvent_item["end"],
                            easingType = LineEvent_item["easingType"]
                        ) for LineEvent_item in judgeLine_item["scaleXEvents"]
                    ] if "scaleXEvents" in judgeLine_item and judgeLine_item["scaleXEvents"] is not None else None,
                    scaleYEvents = [
                        Chart_Objects_Rep.LineEvent(
                            startTime = Chart_Objects_Rep.Beat(
                                *LineEvent_item["startTime"]
                            ),
                            endTime = Chart_Objects_Rep.Beat(
                                *LineEvent_item["endTime"]
                            ),
                            start = LineEvent_item["start"],
                            end = LineEvent_item["end"],
                            easingType = LineEvent_item["easingType"]
                        ) for LineEvent_item in judgeLine_item["scaleYEvents"]
                    ] if "scaleYEvents" in judgeLine_item and judgeLine_item["scaleYEvents"] is not None else None,
                    colorEvents = [
                        Chart_Objects_Rep.LineEvent(
                            startTime = Chart_Objects_Rep.Beat(
                                *LineEvent_item["startTime"]
                            ),
                            endTime = Chart_Objects_Rep.Beat(
                                *LineEvent_item["endTime"]
                            ),
                            start = LineEvent_item["start"],
                            end = LineEvent_item["end"],
                            easingType = LineEvent_item["easingType"]
                        ) for LineEvent_item in judgeLine_item["colorEvents"]
                    ] if "colorEvents" in judgeLine_item and judgeLine_item["colorEvents"] is not None else None,
                ) if "extended" in judgeLine_item and judgeLine_item["extended"] is not None else None,
                notes = [
                    Chart_Objects_Rep.Note(
                        type = Note_item["type"],
                        startTime = Chart_Objects_Rep.Beat(
                            *Note_item["startTime"]
                        ),
                        endTime = Chart_Objects_Rep.Beat(
                            *Note_item["endTime"]
                        ),
                        positionX = Note_item["positionX"],
                        above = Note_item["above"],
                        isFake = Note_item["isFake"],
                        speed = Note_item["speed"],
                        yOffset = Note_item["yOffset"],
                        visibleTime = Note_item["visibleTime"]
                    )
                    for Note_item in judgeLine_item["notes"]
                ] if "notes" in judgeLine_item else []
            )
            for judgeLine_item in phigros_chart["judgeLineList"]
        ]
    )
    rep_chart_obj.Init()
    return rep_chart_obj