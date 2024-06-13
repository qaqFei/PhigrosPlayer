import Chart_Objects_Rep

def Load_Chart_Object(chart):
    rep_chart_obj = Chart_Objects_Rep.Rep_Chart(
        META = Chart_Objects_Rep.MetaData(
            RPEVersion = chart["META"]["RPEVersion"],
            offset = chart["META"]["offset"],
            name = chart["META"]["name"],
            id = chart["META"]["id"],
            song = chart["META"]["song"],
            background = chart["META"]["background"],
            composer = chart["META"]["composer"],
            charter = chart["META"]["charter"],
            level = chart["META"]["level"]
        ),
        BPMList = [
            Chart_Objects_Rep.BPMEvent(
                startTime = Chart_Objects_Rep.Beat(
                    *BPMEvent_item["startTime"]
                ),
                bpm = BPMEvent_item["bpm"]
            )
            for BPMEvent_item in chart["BPMList"]
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
            for judgeLine_item in chart["judgeLineList"]
        ]
    )
    return rep_chart_obj