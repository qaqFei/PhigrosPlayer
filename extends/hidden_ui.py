import typing

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
    
    def update(self, locals_dict):
        task = locals_dict["Task"]
        task.RenderTasks = [i for i in task.RenderTasks if i.func.__name__ != "draw_ui"]
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None