import typing

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
    
    def globals(self):
        return self._get_globals()
    
    def loaded(self):
        root = self.globals()["root"]
        root.run_js_code("canvas_ele.style.filter = 'blur(5px)';")
    
    def update(self,locals_dict):
        pass
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None