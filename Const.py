import typing

class Note:
    TAP = 1
    DRAG = 2
    HOLD = 3
    FLICK = 4

class CHART_TYPE: #no random :>
    PHI = 0x6ae92a9
    REP = 0x6cd0b78

INF = float("inf")
NAN = float("nan")
JUDGELINE_PERFECT_COLOR = "#feffa9"
RENDER_RANGE_MORE_FRAME_LINE_COLOR = "rgba(0, 94, 255, 0.65)"

EVENT_JSON_TYPE = typing.Dict[
    str, typing.Union[
        int, float
    ]
]

JUDGELINE_JSON_TYPE = typing.Dict[
    str, typing.Union[
        str, int, float, typing.List[
            EVENT_JSON_TYPE
        ]
    ]
]

CHART_JSON_TYPE = typing.Dict[
    str, typing.Union[
        int, float, typing.List[
            JUDGELINE_JSON_TYPE
        ]
    ]
]

del typing