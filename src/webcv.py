from __future__ import annotations

import fix_workpath as _

import threading
import typing
import http.server
import io
import time
from ctypes import windll
from os.path import abspath
from random import randint

import webview
from PIL import Image

current_thread = threading.current_thread
screen_width = windll.user32.GetSystemMetrics(0)
screen_height = windll.user32.GetSystemMetrics(1)

framerate_counter = '''\
(() => {

_frame_count = 0;
_frame_lastreftime = performance.now();
_framerate_ckeck_limit = 25;
framerate = -1;

_frame_counter = () => {
    _frame_count++;
    
    if (_frame_count >= _framerate_ckeck_limit) {
        const uset = performance.now() - _frame_lastreftime;
        framerate = uset != 0.0 ? _frame_count / (uset / 1000) : Infinity;
        _frame_count = 0;
        _frame_lastreftime = performance.now();
        
        if (framerate != Infinity) {
            _framerate_ckeck_limit = framerate * 0.25;
        }
    }
    
    requestAnimationFrame(_frame_counter);
}

requestAnimationFrame(_frame_counter);

})();
'''
    
class WebCanvas_FileServerHandler(http.server.BaseHTTPRequestHandler):
    _canvas: WebCanvas
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        
        if self.path[1:] in self._canvas._regims:
            im:Image.Image = self._canvas._regims[self.path[1:]]
            temp_btyeio = io.BytesIO()
            im.save(temp_btyeio, "png")
            self.wfile.write(temp_btyeio.getvalue())
        elif self.path[1:] in self._canvas._regres:
            data:bytes = self._canvas._regres[self.path[1:]]
            self.wfile.write(data)
    
    def log_request(self, *args, **kwargs) -> None: ...

class JsApi:
    def __init__(self) -> None:
        self.things: dict[str, typing.Any] = {}
    
    def get_thing(self, name: str):
        return self.things[name]
    
    def set_thing(self, name: str, value: typing.Any):
        self.things[name] = value
    
    def get_attr(self,name: str):
        return getattr(self, name)
    
    def set_attr(self, name: str, value: typing.Any):
        setattr(self, name, value)
    
    def call_attr(self,name: str, *args, **kwargs):
        return getattr(self, name)(*args, **kwargs)

class PILResourcePacker:
    def __init__(self, cv: WebCanvas):
        self.cv = cv
        self.imgs: list[tuple[str, Image.Image|bytes]] = []
    
    def reg_img(self, img: Image.Image|bytes, name: str):
        self.imgs.append((name, img))
    
    def pack(self):
        datas = []
        dataindexs = []
        datacount = 0
        for name, img in self.imgs:
            if isinstance(img, Image.Image):
                btio = io.BytesIO()
                img.save(btio, "png") # toooooooooooooo slow
                data = btio.getvalue()
            else:
                data = img
                
            datas.append(data)
            dataindexs.append([name, [datacount, len(data)]])
            datacount += len(data)
        return b"".join(datas), dataindexs

    def load(self, data: bytes, indexs: list[list[str, list[int, int]]]):
        rid = f"pilrespacker_{randint(0, 2 << 31)}"
        self.cv.reg_res(data, rid)
        imnames = self.cv.wait_jspromise(f"loadrespackage('{self.cv.get_resource_path(rid)}', {indexs});")
        self.cv.wait_loadimgs(self.cv.get_imgcomplete_jseval(imnames))
        self.cv.unreg_res(rid)
        self.cv.run_js_code(f"[{",".join(map(self.cv.get_img_jsvarname, imnames))}].forEach(im => URL.revokeObjectURL(im.src));")
        
        def createcache():
            codes = []
            codes.append(f"cachecv = document.createElement('canvas');")
            codes.append(f"cachecv.width = cachecv.height = 1;")
            codes.append(f"cachectx = cachecv.getContext('2d');")
            for im in imnames:
                codes.append(f"cachectx.drawImage({self.cv.get_img_jsvarname(im)}, 0, 0);")
            codes.append(f"delete cachecv; delete cachectx;")
            self.cv.run_js_code("".join(codes))
            
        threading.Thread(target=createcache, daemon=True).start()
    
    def getnames(self):
        return [name for name, _ in self.imgs]

    def unload(self, names: list[str]):
        self.cv.run_js_code(f"{";".join(map(lambda x: f"delete {self.cv.get_img_jsvarname(x)}", names))};")

def ban_threadtest_current_thread():
    obj = current_thread()
    obj.name = "MainThread"
    return obj

webview.threading.current_thread = ban_threadtest_current_thread

class WebCanvas:
    def __init__(
        self,
        width: int, height: int,
        x: int, y: int,
        debug: bool = False,
        title: str = "WebCanvas",
        resizable: bool = True,
        frameless: bool = False,
        html_path: str = ".\\web_canvas.html",
        renderdemand: bool = False,
        renderasync: bool = False,
        jslog: bool = False,
        jslog_path: str = ".\\web_canvas.jslog.txt"
    ):
        self.jsapi = JsApi()
        self._destroyed = threading.Event()
        self._regims: dict[str, Image.Image] = {}
        self._regres: dict[str, bytes] = {}
        self._is_loadimg: dict[str, bool] = {}
        self._jscodes: list[str] = []
        self._framerate: int|float = -1
        
        self._rdevent = threading.Event()
        self._raevent = threading.Event()
        self.renderdemand = renderdemand
        self.renderasync = renderasync
        
        self.jslog = jslog
        self.jslog_path = jslog_path
        self.jslog_f = open(jslog_path, "w", encoding="utf-8") if self.jslog else None
        
        self.web = webview.create_window(
            title = title,
            url = abspath(html_path),
            resizable = resizable,
            js_api = self.jsapi,
            frameless = frameless
        )
        threading.Thread(target=webview.start, kwargs={"debug": debug}, daemon=True).start()
        
        self.web.resize(width, height)
        self.web.move(x, y)
        self.web.events.closed += self._destroyed.set
        
        title = self.web.title
        temp_title = self.web.title + " " * randint(0, 4096)
        self.web.set_title(temp_title)
        
        self.web_hwnd = 0
        while not self.web_hwnd:
            self.web_hwnd = windll.user32.FindWindowW(None, temp_title)
            time.sleep(0.01)
        self.web.set_title(title)
        
        self.web_port = int(self.web._server.address.split(":")[2].split("/")[0])
        WebCanvas_FileServerHandler._canvas = self
        self.file_server = http.server.HTTPServer(("localhost", self.web_port + 1), WebCanvas_FileServerHandler)
        threading.Thread(target=self.file_server.serve_forever, daemon=True).start()
        
        self.jsapi.set_attr("_rdcallback", self._rdevent.set)
        self._raevent.set()
    
    def title(self, title: str) -> str: self.web.set_title(title)
    def winfo_screenwidth(self) -> int: return screen_width
    def winfo_screenheight(self) -> int: return screen_height
    def winfo_hwnd(self) -> int: return self.web_hwnd
    def winfo_legacywindowwidth(self) -> int: return self.web.evaluate_js("window.innerWidth;")
    def winfo_legacywindowheight(self) -> int: return self.web.evaluate_js("window.innerHeight;")

    def destroy(self): self.web.destroy()
    def resize(self, width: int, height: int): self.web.resize(width, height)
    def move(self, x: int, y:int): self.web.move(x, y)
    
    def run_js_code(self, code: str, add_code_array: bool = False):
        if self.jslog and not code.endswith(";"): code += ";"
        return self._jscodes.append(code) if add_code_array else self.web.evaluate_js(code)
    
    def _rjwc(self, codes: list[str]):
        framerate: int|float = self.web.evaluate_js(f"{codes}.forEach(r2eval);\nframerate;")
        
        if self.renderdemand:
            self._rdevent.wait()
            self._rdevent.clear()
        
        self._framerate = framerate
        
        if self.renderasync:
            self._raevent.set()
    
    def run_js_wait_code(self):
        self.run_js_code("requestAnimationFrame(() => pywebview.api.call_attr('_rdcallback'));", add_code_array=True)
        self.run_js_code("if (!('_frame_counter' in window)) {&FRAMERATE_CODE&};".replace("&FRAMERATE_CODE&", framerate_counter), add_code_array=True)
        
        codes = self._jscodes.copy()
        self._jscodes.clear()
        
        if self.jslog:
            self.jslog_f.write("\n// JSCODE - FRAME - START //\n")
            self.jslog_f.writelines(codes)
            self.jslog_f.write("\n// JSCODE - FRAME - END //\n")
        
        if not self.renderasync:
            return self._rjwc(codes)
        else:
            self._raevent.wait()
            self._raevent.clear()
            threading.Thread(target=self._rjwc, args=(codes, ), daemon=True).start()
    
    def string2cstring(self, code: str): return code.replace("\\", "\\\\").replace("'", "\\'").replace("\"", "\\\"").replace("`", "\\`").replace("\n", "\\n")
    def string2sctring_hqm(self, code: str): return f"'{self.string2cstring(code)}'"
    def get_framerate(self) -> int|float: return self._framerate
    
    def create_line(
        self,
        x0: int|float, y0: int|float,
        x1: int|float, y1: int|float,
        lineWidth: int = 1,
        fillStyle: str|None = None,
        strokeStyle:str|None = None,
        wait_execute: bool = False
    ) -> None:
        code = f"\
            ctx.save();\
            ctx.fillStyle = \"{fillStyle}\";\
            ctx.strokeStyle = \"{strokeStyle}\";\
            ctx.lineWidth = {lineWidth};\
            ctx.beginPath();\
            ctx.moveTo({x0},{y0});\
            ctx.lineTo({x1},{y1});\
            ctx.closePath();\
            ctx.stroke();\
            ctx.restore();\
        "
        self.run_js_code(code, wait_execute)
    
    def create_text(
        self,
        x: int|float, y: int|float,
        text: str, font: str,
        textAlign: typing.Literal["start", "end", "left", "right", "center"] = "start",
        textBaseline: typing.Literal["top", "hanging", "middle", "alphabetic", "ideographic", "bottom"] = "alphabetic",
        fillStyle: str|None = None,
        strokeStyle: str|None = None,
        method: typing.Literal["fill", "stroke"] = "fill",
        maxwidth: float|None = None,
        wait_execute: bool = False
    ) -> None:
        text = self.string2sctring_hqm(text)
        self.run_js_code(f"ctx.save(); ctx.font = \"{font}\"; ctx.textAlign = \"{textAlign}\"; ctx.textBaseline = \"{textBaseline}\"; ctx.fillStyle = \"{fillStyle}\"; ctx.strokeStyle = \"{strokeStyle}\"; ctx.{method}Text({text}, {x}, {y}, {maxwidth if maxwidth is not None else "undefined"}); ctx.restore();", wait_execute)
    
    def create_polygon(
        self, points: typing.Iterator[tuple[int|float, int|float]],
        fillStyle: str|None = None,
        strokeStyle: str|None = None,
        wait_execute: bool = False
    ) -> None:
        code = f"\
            ctx.save();\
            ctx.fillStyle = \"{fillStyle}\";\
            ctx.strokeStyle = \"{strokeStyle}\";\
            ctx.beginPath();\
            ctx.moveTo({points[0][0]}, {points[0][1]});\
        " + "".join([f"ctx.lineTo({point[0]}, {point[1]});" for point in points[1:]])
        self.run_js_code(code + "ctx.closePath(); ctx.stroke(); ctx.fill(); ctx.restore();", wait_execute)
    
    def create_image(
        self, imgname: str,
        x: int|float, y: int|float,
        width: int|float, height: int|float,
        wait_execute: bool = False
    ) -> None:
        jsvarname = self.get_img_jsvarname(imgname)
        self.run_js_code(f"ctx.drawImage({jsvarname}, {x}, {y}, {width}, {height});", wait_execute)

    def clear_rectangle(
        self,
        x0: int|float, y0: int|float,
        x1: int|float, y1: int|float,
        wait_execute: bool = False
    ) -> None:
        self.run_js_code(f"ctx.clearRect({x0}, {y0}, {x1 - x0}, {y1 - y0});", wait_execute)
    
    def clear_canvas(self, wait_execute: bool = False) -> None:
        self.run_js_code("ctx.clear();", wait_execute)
    
    def get_img_jsvarname(self, imname: str):
        return f"{imname}_img"
    
    def reg_img(self, im: Image.Image, name: str) -> None:
        self._regims[name] = im
        self._is_loadimg[name] = False
    
    def reg_res(self, res_data: bytes, name: str) -> None:
        self._regres[name] = res_data
    
    def unreg_res(self, name: str) -> None:
        self._regres.pop(name)
    
    def get_imgcomplete_jseval(self, ns: list[str]) -> str:
        return f"[{",".join([f"{self.get_img_jsvarname(item)}.complete" for item in ns])}]"
    
    def wait_loadimgs(self, complete_code: str) -> None:
        while not all(self.run_js_code(complete_code)):
            time.sleep(0.01)
        
    def load_allimg(self) -> None:
        for imgname in self._regims: self._load_img(imgname)
        self.wait_loadimgs(self.get_imgcomplete_jseval(self._regims))
    
    def reg_event(self, name: str, callback: typing.Callable) -> None:
        setattr(self.web.events, name, getattr(self.web.events, name) + callback)
    
    def wait_for_close(self) -> None:
        self._destroyed.wait()
        
        if self.jslog:
            self.jslog_f.write(f"\n\n// Webview closed.\n")
            self.jslog_f.flush()
            self.jslog_f.close()
    
    def get_resource_path(self, name: str) -> str:
        return f"http://127.0.0.1:{self.web_port + 1}/{name}"

    def wait_jspromise(self, code: str) -> None:
        eid = f"wait_jspromise_{randint(0, 2 << 31)}"
        ete = threading.Event()
        ecbname = f"{eid}_callback"
        result = None
        
        def _callback(jsresult):
            nonlocal result
            result = jsresult
            ete.set()
            
        self.jsapi.set_attr(ecbname, _callback)
        self.run_js_code(f"eval({self.string2sctring_hqm(code)}).then((result) => pywebview.api.call_attr('{ecbname}', result));")
        ete.wait()
        delattr(self.jsapi, ecbname)
        return result
    
    def _load_img(self, imgname: str) -> None:
        jsvarname = self.get_img_jsvarname(imgname)
        code = f"\
        if (!window.{jsvarname}){chr(123)}\
            {jsvarname} = document.createElement('img');\
            {jsvarname}.crossOrigin = \"Anonymous\";\
            {jsvarname}.src = 'http://127.0.0.1:{self.web_port + 1}/{imgname}';\
            {jsvarname}.loading = \"eager\";\
        {chr(125)}\
        "
        self.run_js_code(code)
        self._is_loadimg[imgname] = True

class FakeCanvas(WebCanvas):
    def __init__(self, *args, **kwargs): ...