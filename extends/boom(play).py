from sys import argv
from random import randint
import typing
import copy

x = int(eval(argv[argv.index("-boom") + 1])) if "-boom" in argv else 3

def get_effect_random_blocks() -> typing.Tuple[int,int,int,int]:
    return tuple((randint(1,90) for _ in range(4)))

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
    
    def chart_loaded(self,chart_obj):
        for judgeLine in chart_obj.judgeLineList:
            na = []
            nb = []
            for nai in judgeLine.notesAbove:
                nai.morebets = True
                for _ in range(x):
                    na.append(copy.copy(nai))
            for nbi in judgeLine.notesBelow:
                nbi.morebets = True
                for _ in range(x):
                    nb.append(copy.copy(nbi))
            judgeLine.notesAbove = na
            judgeLine.notesBelow = nb
            for note in judgeLine.notesAbove + judgeLine.notesBelow:
                note.effect_random_blocks = get_effect_random_blocks()
                note.effect_times = [get_effect_random_blocks() for _ in range(len(note.effect_times))]
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None