import typing
from time import time

render_times = []

def get_average_render_time():
    return sum(render_times) / len(render_times) # this list not possible is empty.

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
    
    def globals(self):
        return self._get_globals()
    
    def loaded(self):
        pass
    
    def update(self,locals_dict):
        use_time = time() - locals_dict["GetFrameRenderTask_Phi_CallTime"]
        fps = 1 / use_time
        render_times.append(use_time)
        average = get_average_render_time()
        print(f"GetFrameRenderTask:\n\tthis: {use_time:.5f}s/item = {fps:.2f}fps,\n\taverage: {average:.5f}s/item = {(1 / average):.2f}fps")
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None