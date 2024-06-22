import typing

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
    
    def globals(self):
        return self._get_globals()
    
    def update(self,locals_dict):
        task = locals_dict["Task"]
        task.RenderTasks = [i for i in task.RenderTasks if i.func.__name__ != "draw_ui"]