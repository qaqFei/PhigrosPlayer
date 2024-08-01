import typing
import Chart_Objects_Phi
import Chart_Objects_Rpe

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
    
    def chart_loaded(self, chart_obj: Chart_Objects_Phi.Phigros_Chart | Chart_Objects_Rpe.Rpe_Chart):
        pass
    
    def globals(self):
        return self._get_globals()
    
    def loaded(self):
        pass
    
    def update(self,locals_dict):
        pass
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None