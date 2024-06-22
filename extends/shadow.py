import typing

shadowColor = "#111111EE"
shadowBlur = 7.5

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
        root.run_js_code('''
        CanvasRenderingContext2D.prototype._extend_shadow_drawimg_func = CanvasRenderingContext2D.prototype.drawImage;
        CanvasRenderingContext2D.prototype.drawImage = function (im,x,y,w,h) {
            this.shadowColor = "SHADOWCOLOR";
            this.shadowBlur = SHADOWBLUR;
            this.shadowOffsetX = 17.5;
            this.shadowOffsetY = 17.5;
            return this._extend_shadow_drawimg_func(im,x,y,w,h);
        }
        '''.replace("SHADOWCOLOR",shadowColor).replace("SHADOWBLUR",str(shadowBlur)))
    
    def update(self,locals_dict):
        pass
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None