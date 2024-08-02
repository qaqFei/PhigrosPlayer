import Chart_Objects_Rpe

def Load_Chart_Object(chart:dict):
    meta = chart.get("META", {})
    rpe_chart_obj = Chart_Objects_Rpe.Rpe_Chart(
        META = Chart_Objects_Rpe.MetaData(
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
            Chart_Objects_Rpe.BPMEvent(
                startTime = Chart_Objects_Rpe.Beat(
                    *BPMEvent_item.get("startTime", [0, 0, 1])
                ),
                bpm = BPMEvent_item.get("bpm", 140)
            )
            for BPMEvent_item in chart.get("BPMList", [])
        ],
        JudgeLineList = [
            Chart_Objects_Rpe.JudgeLine(
                numOfNotes = judgeLine_item.get("numOfNotes", 0),
                isCover = judgeLine_item.get("isCover", 1),
                Texture = judgeLine_item.get("Texture", "line.png"),
                attachUI = judgeLine_item.get("attachUI", None),
                father = judgeLine_item.get("father", -1),
                eventLayers = [
                    Chart_Objects_Rpe.EventLayer(
                        speedEvents = [
                            Chart_Objects_Rpe.LineEvent(
                                startTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = None
                            )
                            for LineEvent_item in EventLayer_item.get("speedEvents", [])
                        ] if EventLayer_item.get("speedEvents", []) is not None else [],
                        moveXEvents = [
                            Chart_Objects_Rpe.LineEvent(
                                startTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("moveXEvents", [])
                        ] if EventLayer_item.get("moveXEvents", []) is not None else [],
                        moveYEvents = [
                            Chart_Objects_Rpe.LineEvent(
                                startTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("moveYEvents", [])
                        ] if EventLayer_item.get("moveYEvents", []) is not None else [],
                        rotateEvents = [
                            Chart_Objects_Rpe.LineEvent(
                                startTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("rotateEvents", [])
                        ] if EventLayer_item.get("rotateEvents", []) is not None else [],
                        alphaEvents = [
                            Chart_Objects_Rpe.LineEvent(
                                startTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("startTime", [0, 0, 1])
                                ),
                                endTime = Chart_Objects_Rpe.Beat(
                                    *LineEvent_item.get("endTime", [0, 0, 1])
                                ),
                                start = LineEvent_item.get("start", 0.0),
                                end = LineEvent_item.get("end", 0.0),
                                easingType = LineEvent_item.get("easingType", 1)
                            ) for LineEvent_item in EventLayer_item.get("alphaEvents", [])
                        ] if EventLayer_item.get("alphaEvents", []) is not None else []
                    ) if EventLayer_item is not None else Chart_Objects_Rpe.EventLayer(speedEvents = [], moveXEvents = [], moveYEvents = [], rotateEvents = [], alphaEvents = [])
                    for EventLayer_item in judgeLine_item.get("eventLayers", [])
                ],
                extended = Chart_Objects_Rpe.Extended(
                    scaleXEvents = [
                        Chart_Objects_Rpe.LineEvent(
                            startTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", 1.0),
                            end = LineEvent_item.get("end", 1.0),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("scaleXEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("scaleXEvents", []) is not None else [],
                    scaleYEvents = [
                        Chart_Objects_Rpe.LineEvent(
                            startTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", 1.0),
                            end = LineEvent_item.get("end", 1.0),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("scaleYEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("scaleYEvents", []) is not None else [],
                    colorEvents = [
                        Chart_Objects_Rpe.LineEvent(
                            startTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", [255, 255, 255]),
                            end = LineEvent_item.get("end", [255, 255, 255]),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("colorEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("colorEvents", []) is not None else [],
                    textEvents = [
                        Chart_Objects_Rpe.LineEvent(
                            startTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("startTime", [0, 0, 1])
                            ),
                            endTime = Chart_Objects_Rpe.Beat(
                                *LineEvent_item.get("endTime", [0, 0, 1])
                            ),
                            start = LineEvent_item.get("start", ""),
                            end = LineEvent_item.get("end", ""),
                            easingType = LineEvent_item.get("easingType", 1)
                        ) for LineEvent_item in judgeLine_item.get("extended", {}).get("textEvents", [])
                    ] if judgeLine_item.get("extended", {}).get("textEvents", []) is not None else [],
                ) if judgeLine_item.get("extended", {}) is not None else None,
                notes = [
                    Chart_Objects_Rpe.Note(
                        type = Note_item.get("type", 1),
                        startTime = Chart_Objects_Rpe.Beat(
                            *Note_item.get("startTime", [0, 0, 1])
                        ),
                        endTime = Chart_Objects_Rpe.Beat(
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
    
    print("Finding Chart More Bets...")
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
                note.holdLength = line.GetFloorPosition(0.0, rpe_chart_obj.beat2sec(note.endTime.value), rpe_chart_obj) - note.floorPosition
    
    return rpe_chart_obj