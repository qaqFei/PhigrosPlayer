from sys import argv
import typing
import time

argv.append("-no-mixer-reset-chart-time")

x = int(eval(argv[argv.index("-time++") + 1])) if "-time++" in argv else 3.0

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
    
    def chart_loaded(self,chart_obj):
        g = self._get_globals()
        g["no_mixer_reset_chart_time"] = True
        g["time"] = lambda: time.time() * x
        g["sleep"] = lambda t: time.sleep(t / x)
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None