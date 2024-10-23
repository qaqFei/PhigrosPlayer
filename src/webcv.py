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
        else:
            self.wfile.write(bytes())
    
    def log_request(self, *args, **kwargs) -> None: ...

class JsApi:
    def __init__(self) -> None:
        self.things:dict[str, typing.Any] = {}
    
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
        html_path: str = ".\\web_canvas.html"
    ):
        self.jsapi = JsApi()
        self._web = webview.create_window(
            title = title,
            url = abspath(html_path),
            resizable = resizable,
            js_api = self.jsapi,
            frameless = frameless
        )
        self._web_init_var = {
            "width": width,
            "height": height,
            "x": x,
            "y": y
        }
        self._destroyed = threading.Event()
        self.debug = debug
        self._regims: dict[str, Image.Image] = {}
        self._regres: dict[str, bytes] = {}
        self._is_loadimg: dict[str, bool] = {}
        self._JavaScript_WaitToExecute_CodeArray: list[str] = []
        threading.Thread(target=webview.start, kwargs={"debug": self.debug}, daemon=True).start()
        self._init()
    
    def title(self, title: str) -> str: self._web.set_title(title)
    def winfo_screenwidth(self) -> int: return screen_width
    def winfo_screenheight(self) -> int: return screen_height
    def winfo_hwnd(self) -> int: return self._web_hwnd
    def winfo_legacywindowwidth(self) -> int: return self._web.evaluate_js("window.innerWidth;")
    def winfo_legacywindowheight(self) -> int: return self._web.evaluate_js("window.innerHeight;")

    def destroy(self): self._web.destroy()
    def resize(self, width: int, height: int): self._web.resize(width, height)
    def move(self, x: int, y:int): self._web.move(x, y)
    
    def run_js_code(self, code: str, add_code_array: bool = False):
        return self._JavaScript_WaitToExecute_CodeArray.append(code) if add_code_array else self._web.evaluate_js(code)
    
    def run_js_wait_code(self):
        self._web.evaluate_js(f"JavaScript_WaitToExecute_CodeArray = {self._JavaScript_WaitToExecute_CodeArray}; process_jswteca();")
        self._JavaScript_WaitToExecute_CodeArray.clear()
    
    def process_code_string_syntax_tostring(self, code: str):
        return code.replace("\\", "\\\\").replace("'", "\\'").replace("\"", "\\\"").replace("`", "\\`").replace("\n", "\\n")
    
    def process_code_string_syntax_tocode(self, code: str):
        return f"'{self.process_code_string_syntax_tostring(code)}'"

    def create_rectangle(
        self,
        x0: int|float, y0: int|float,
        x1: int|float, y1: int|float,
        fillStyle: str|None = None,
        strokeStyle: str|None = None,
        wait_execute: bool = False
    ) -> None:
        code = f"\
            ctx.save();\
            ctx.fillStyle = \"{fillStyle}\";\
            ctx.strokeStyle = \"{strokeStyle}\";\
            ctx.fillRect({x0}, {y0}, {x1 - x0}, {y1 - y0});\
            ctx.restore();\
        "
        self.run_js_code(code, wait_execute)
    
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
        wait_execute: bool = False
    ) -> None:
        text = self.process_code_string_syntax_tocode(text)
        self.run_js_code(f"ctx.save(); ctx.font = \"{font}\"; ctx.textAlign = \"{textAlign}\"; ctx.textBaseline = \"{textBaseline}\"; ctx.fillStyle = \"{fillStyle}\"; ctx.strokeStyle = \"{strokeStyle}\"; ctx.{method}Text({text},{x},{y}); ctx.restore();", wait_execute)
    
    def create_polygon(
        self, points: typing.Iterator[typing.Tuple[int|float, int|float]],
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
        if imgname not in self._is_loadimg:
            raise ValueError("Image not found.")
        
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
    
    def get_img_jsvarname(self, imname:str):
        return f"{imname}_img"
    
    def reg_img(self, im:Image.Image, name:str) -> None:
        self._regims[name] = im
        self._is_loadimg[name] = False
    
    def reg_res(self, res_data:bytes, name:str) -> None:
        self._regres[name] = res_data
    
    def load_allimg(self) -> None:
        for imgname in self._regims:
            self._load_img(imgname)
        while True:
            complete_list = self.run_js_code(f"[{",".join([f"{self.get_img_jsvarname(item)}.complete" for item in self._regims])}]")
            if all(complete_list): break
            time.sleep(0.2)
    
    def reg_event(self, name: str, callback: typing.Callable) -> None:
        setattr(self._web.events, name, getattr(self._web.events, name) + callback)
    
    def wait_for_close(self) -> None:
        self._destroyed.wait()
    
    def shutdown_fileserver(self) -> None:
        self._file_server.shutdown()
    
    def get_resource_path(self, name:str) -> str:
        return f"http://127.0.0.1:{self._web_port + 1}/{name}"
    
    def _closed_callback(self) -> None:
        self._destroyed.set()
    
    def _load_img(self, imgname:str) -> None:
        jsvarname = self.get_img_jsvarname(imgname)
        code = f"\
        if (!window.{jsvarname}){chr(123)}\
            {jsvarname} = document.createElement('img');\
            {jsvarname}.crossOrigin = \"Anonymous\";\
            {jsvarname}.src = 'http://127.0.0.1:{self._web_port + 1}/{imgname}';\
            {jsvarname}.loading = \"eager\";\
        {chr(125)}\
        "
        self.run_js_code(code)
        self._is_loadimg[imgname] = True

    def _init(
        self
    ) -> None:
        self._web.resize(self._web_init_var["width"], self._web_init_var["height"])
        self._web.move(self._web_init_var["x"], self._web_init_var["y"])
        self._web_init_var.clear()
        self._web.events.closed += self._closed_callback
        
        title = self._web.title
        temp_title = self._web.title + " " * randint(0, 4096)
        self._web.set_title(temp_title)
        while True:
            self._web_hwnd = windll.user32.FindWindowW(None, temp_title)
            if self._web_hwnd:
                break
        self._web.set_title(title)
        
        self._web_port = int(self._web._server.address.split(":")[2].split("/")[0])
        WebCanvas_FileServerHandler._canvas = self
        self._file_server = http.server.HTTPServer(("localhost", self._web_port + 1), WebCanvas_FileServerHandler)
        threading.Thread(target=self._file_server.serve_forever, daemon=True).start()