import logging

import chartobj_rpe

def Load_Chart_Object(chart: dict):
    logging.info("Loading Chart Object, fmt = rpe")
    meta = chart.get("META", {})
    rpe_chart_obj = chartobj_rpe.Rpe_Chart(
        META = chartobj_rpe.MetaData(
            RPEVersion = meta.get("RPEVersion", -1),
            offset = meta.get("offset", 0),
            name = meta.get("name", "Unknow"),
            id = meta.get("id", "-1"),
            song = meta.get("song", "Unknow"),
            background = meta.get("background", "Unknow"),
            composer = meta.get("composer", "Unknow"),
            charter = meta.get("charter", "Unknow"),
            level = meta.get("level", "Unknow"),
        ),
        BPMList = [
            chartobj_rpe.BPMEvent(
                startTime = chartobj_rpe.Beat(
                    *BPMEvent_item.get("startTime", [0, 0, 1])
                ),
                bpm = BPMEvent_item.get("bpm", 140)
            )
            for BPMEvent_item in chart.get("BPMList", [])
        ],
        JudgeLineList = [
            chartobj_rpe.JudgeLine(
                isCover = judgeLine_item.get("isCover", 1),
                Texture = judgeLine_item.get("Texture", "line.png"),
                attachUI = judgeLine_item.get("attachUI", None),
                bpmfactor = judgeLine_item.get("bpmfactor", 1.0),
                father = judgeLine_item.get("father", -1),
                zOrder = judgeLine_item.get("zOrder", 0),
                eventLayers = [
                    chartobj_rpe.EventLayer(
                        speedEvents = [
                            chartobj_rpe.LineEvent(
                                startTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = 1
                            )
                            for LineEvent_item in EventLayer_item.get("speedEvents", [])
                        ] if EventLayer_item.get("speedEvents", []) is not None else [],
                        moveXEvents = [
                            chartobj_rpe.LineEvent(
                                startTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("moveXEvents", [])
                        ] if EventLayer_item.get("moveXEvents", []) is not None else [],
                        moveYEvents = [
                            chartobj_rpe.LineEvent(
                                startTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("moveYEvents", [])
                        ] if EventLayer_item.get("moveYEvents", []) is not None else [],
                        rotateEvents = [
                            chartobj_rpe.LineEvent(
                                startTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("rotateEvents", [])
                        ] if EventLayer_item.get("rotateEvents", []) is not None else [],
                        alphaEvents = [
                            chartobj_rpe.LineEvent(
                                startTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = chartobj_rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("alphaEvents", [])
                        ] if EventLayer_item.get("alphaEvents", []) is not None else []
                    ) if EventLayer_item is not None else chartobj_rpe.EventLayer(speedEvents = [], moveXEvents = [], moveYEvents = [], rotateEvents = [], alphaEvents = [])
                    for EventLayer_item in judgeLine_item.get("eventLayers", [])
                ],
                extended = chartobj_rpe.Extended(
                    scaleXEvents = [
                        chartobj_rpe.LineEvent(
                            startTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", 1.0),
                            end = LineEvent_item.get("end", 1.0),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("scaleXEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("scaleXEvents", []) is not None else [],
                    scaleYEvents = [
                        chartobj_rpe.LineEvent(
                            startTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", 1.0),
                            end = LineEvent_item.get("end", 1.0),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("scaleYEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("scaleYEvents", []) is not None else [],
                    colorEvents = [
                        chartobj_rpe.LineEvent(
                            startTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", [255, 255, 255]),
                            end = LineEvent_item.get("end", [255, 255, 255]),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("colorEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("colorEvents", []) is not None else [],
                    textEvents = [
                        chartobj_rpe.LineEvent(
                            startTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = chartobj_rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", ""),
                            end = LineEvent_item.get("end", ""),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("textEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("textEvents", []) is not None else [],
                ) if judgeLine_item.get("extended", {}) is not None else None,
                notes = [
                    chartobj_rpe.Note(
                        type = Note_item.get("type", 1),
                        startTime = chartobj_rpe.Beat(
                            *Note_item.get("startTime", [0, 0, 1])
                        ),
                        endTime = chartobj_rpe.Beat(
                            *Note_item.get("endTime", [0, 0, 1])
                        ),
                        positionX = Note_item.get("positionX", 0),
                        above = Note_item.get("above", 1),
                        isFake = Note_item.get("isFake", False),
                        speed = Note_item.get("speed", 1.0),
                        yOffset = Note_item.get("yOffset", 0.0),
                        visibleTime = Note_item.get("visibleTime", 999999.0),
                        width = Note_item.get("size", 1.0),
                        alpha = Note_item.get("alpha", 255),
                    )
                    for Note_item in judgeLine_item.get("notes", [])
                ]
            )
            for judgeLine_item in chart.get("judgeLineList", [])
        ]
    )
    
    logging.info("Finding Chart More Bets, fmt = rpe")

    def prcmorebets(notes):
        note_times = {}
        for note in notes:
            if note.startTime.value not in note_times:
                note_times[note.startTime.value] = (False, note)
            else:
                if not note_times[note.startTime.value][0]:
                    note_times[note.startTime.value][-1].morebets = True
                    note_times[note.startTime.value] = (True, note)
                note.morebets = True
    prcmorebets(list(filter(lambda x: x.isFake,[item for line in rpe_chart_obj.JudgeLineList for item in line.notes])))
    prcmorebets(list(filter(lambda x: not x.isFake,[item for line in rpe_chart_obj.JudgeLineList for item in line.notes])))
    
    for line in rpe_chart_obj.JudgeLineList:
        for note in line.notes:
            note.floorPosition = line.GetNoteFloorPosition(0.0, note, rpe_chart_obj)
            if note.ishold:
                note.holdLength = line.GetFloorPosition(0.0, rpe_chart_obj.beat2sec(note.endTime.value, line.bpmfactor), rpe_chart_obj) - note.floorPosition
                
    logging.info("Load Chart Object Successfully, fmt = rpe")
    
    return rpe_chart_obj