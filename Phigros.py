from threading import Thread
from ctypes import windll
from os import chdir, environ, listdir, popen; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = str()
from os.path import exists, abspath, dirname, isfile, isdir
from shutil import rmtree
from tempfile import gettempdir
from ntpath import basename
import typing
import json
import sys
import time
import math

sys.excepthook = lambda *args: [print("^C"), windll.kernel32.ExitProcess(0)] if KeyboardInterrupt in args[0].mro() else sys.__excepthook__(*args)

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from pygame import mixer
from pydub import AudioSegment
import cv2
import webcvapis

import PlaySound
import Chart_Objects_Phi
import Chart_Functions_Phi
import Chart_Objects_Rpe
import Chart_Functions_Rpe
import Const
import Find_Files
import ConsoleWindow
import Tool_Functions
import dialog
import Phigros_Tips
import info_loader
import version
import ppr_help
import rpe_easing
import ChartAnimation
import PhigrosGameObject

selfdir = dirname(sys.argv[0])
if selfdir == "": selfdir = abspath(".")
chdir(selfdir)

mixer.init()

def Load_Resource():
    Resource = {
        "logoipt": Image.open("./Resources/logoipt.png"),
        "warning": Image.open("./Resources/Start.png"),
        "phigros": Image.open("./Resources/phigros.png"),
        "AllSongBlur": Image.open("./Resources/AllSongBlur.png"),
        "facula": Image.open("./Resources/facula.png"),
    }
    
    root.reg_img(Resource["logoipt"], "logoipt")
    root.reg_img(Resource["warning"], "warning")
    root.reg_img(Resource["phigros"], "phigros")
    root.reg_img(Resource["AllSongBlur"], "AllSongBlur")
    root.reg_img(Resource["facula"], "facula")
    
    with open("./Resources/font.ttf", "rb") as f:
        root.reg_res(f.read(),"PhigrosFont")
    root.load_allimg()
    for im in root._is_loadimg.keys(): # ...  create image draw cache
        root.create_image(im, 0, 0, 50, 50, wait_execute=True)
    root.clear_canvas(wait_execute = True)
    root.run_js_wait_code()
    root.run_js_code(f"loadFont('PhigrosFont',\"{root.get_resource_path("PhigrosFont")}\");")
    while not root.run_js_code("font_loaded;"):
        time.sleep(0.1)
    
    root.shutdown_fileserver()
    return Resource

def bindEvents():
    root.jsapi.set_attr("click", eventManager.click)
    root.run_js_code("_click = (e) => pywebview.api.call_attr('click', e.x, e.y, e.button);")
    root.run_js_code("document.addEventListener('click', _click);")

def showStartAnimation():
    start_animation_clicked = False
    def start_animation_click_cb(*args): nonlocal start_animation_clicked; start_animation_clicked = True
    
    a1_t = 5.0
    a1_st = time.time()
    mixer.music.load("./Resources/NewSplashSceneBGM.mp3")
    played_NewSplashSceneBGM = False
    while True:
        p = (time.time() - a1_st) / a1_t
        if p > 1.0: break
                
        if p > 0.4 and not played_NewSplashSceneBGM:
            played_NewSplashSceneBGM = True
            mixer.music.play(-1)
            Thread(target=soundEffect_From0To1, daemon=True).start()
        
        if p > 0.4:
            eventManager.regClickEventFs(start_animation_click_cb, None, True)
            if start_animation_clicked:
                break
            
        root.clear_canvas(wait_execute = True)
        
        root.run_js_code(
            f"ctx.drawAlphaImage(\
                {root.get_img_jsvarname("logoipt")},\
                0, 0, {w}, {h}, {Tool_Functions.easeAlpha(p)}\
            );",
            add_code_array = True
        )
        
        root.run_js_wait_code()
    
    a2_t = 5.0
    a2_st = time.time()
    while True:
        p = (time.time() - a2_st) / a2_t
        if p > 1.0: break
        if start_animation_clicked: break
        
        root.clear_canvas(wait_execute = True)
        
        root.run_js_code(
            f"ctx.drawAlphaImage(\
                {root.get_img_jsvarname("warning")},\
                0, 0, {w}, {h}, {Tool_Functions.easeAlpha(p)}\
            );",
            add_code_array = True
        )
        
        root.run_js_wait_code()
    
    for e in eventManager.clickEvents:
        if e.callback is start_animation_click_cb:
            eventManager.clickEvents.remove(e)
            break
    
    faManager = PhigrosGameObject.FaculaAnimationManager()
    Thread(target=faManager.main, daemon=True).start()
    a3_st = time.time()
    a3_clicked = False
    a3_clicked_time = float("nan")
    def a3_click_cb(*args):
        nonlocal a3_clicked_time, a3_clicked
        a3_clicked_time = time.time()
        a3_clicked = True
    eventManager.regClickEventFs(a3_click_cb, None, True)
    phigros_logo_width = 0.25
    phigros_logo_rect = (
        w / 2 - w * phigros_logo_width / 2,
        h * (100 / 230) - h * phigros_logo_width / Resource["phigros"].width * Resource["phigros"].height / 2,
        w * phigros_logo_width, w * phigros_logo_width / Resource["phigros"].width * Resource["phigros"].height
    )
    if not abs(mixer.music.get_pos() / 1000 - 8.0) <= 0.05:
        mixer.music.set_pos(8.0)
    while True:
        atime = time.time() - a3_st
        
        if a3_clicked and time.time() - a3_clicked_time > 1.0:
            mixer.music.fadeout(500)
            root.create_rectangle( # no wait
                0, 0, w, h, fillStyle = "#000000"
            )
            break
        
        root.clear_canvas(wait_execute = True)
        
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("AllSongBlur")},\
                0, 0, {w}, {h}\
            );",
            add_code_array = True
        )
        
        root.create_rectangle(
            0, 0, w, h,
            fillStyle = f"rgba(0, 0, 0, {(math.sin(atime / 1.5) + 1.0) / 5 + 0.15})",
            wait_execute = True
        )
        
        for i in range(50):
            root.create_line(
                0, h * (i / 50), w, h * (i / 50),
                strokeStyle = "rgba(162, 206, 223, 0.03)",
                lineWidth = 0.5, wait_execute = True
            )
        
        for facula in faManager.faculas:
            if facula["startTime"] <= time.time() <= facula["endTime"]:
                state = faManager.getFaculaState(facula)
                sizePx = facula["size"] * (w + h) / 40
                root.run_js_code(
                    f"ctx.drawAlphaImage(\
                        {root.get_img_jsvarname("facula")},\
                        {facula["x"] * w - sizePx / 2}, {state["y"] * h - sizePx / 2},\
                        {sizePx}, {sizePx},\
                        {state["alpha"] * 0.4}\
                    );",
                    add_code_array = True
                )
        
        root.run_js_code(
            f"ctx.drawImage(\
                {root.get_img_jsvarname("phigros")},\
                {", ".join(map(str, phigros_logo_rect))}\
            );",
            add_code_array = True
        )
        
        textBlurTime = atime % 5.5
        if textBlurTime > 3.0:
            textBlur = math.sin(math.pi * (textBlurTime - 3.0) / 2.5) * 10
        else:
            textBlur = 0.0
        
        root.run_js_code(
            f"ctx.shadowColor = '#FFFFFF'; ctx.shadowBlur = {textBlur};",
            add_code_array = True
        )
        
        root.create_text(
            w / 2,
            h * (155 / 230),
            text = "点  击  屏  幕  开  始",
            font = f"{(w + h) / 125}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = "#FFFFFF",
            wait_execute = True
        )
        
        root.run_js_code(
            "ctx.shaderColor = 'rgba(0, 0, 0, 0)'; ctx.shadowBlur = 0;",
            add_code_array = True
        )
        
        root.create_text(
            w / 2,
            h * 0.98,
            text = "Version: NULL",
            font = f"{(w + h) / 250}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = "#888888",
            wait_execute = True
        )
        
        if atime <= 2.0:
            blurP = 1.0 - (1.0 - atime / 2.0) ** 3
            root.run_js_code(f"mask.style.backdropFilter = 'blur({(w + h) / 60 * (1 - blurP)}px)';", add_code_array = True)
        else:
            root.run_js_code(f"mask.style.backdropFilter = '';", add_code_array = True)
        
        if a3_clicked and time.time() - a3_clicked_time <= 1.0:
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {1.0 - (1.0 - (time.time() - a3_clicked_time)) ** 2})",
                wait_execute = True
            )
        
        root.run_js_wait_code()
    
    root.run_js_code(f"mask.style.backdropFilter = '';", add_code_array = True)
    faManager.stop = True
    mixer.music.load("./Resources/ChapterSelect.mp3")
    mixer.music.play(-1)
    mainRender()

def soundEffect_From0To1():
    v = 0.0
    for i in range(100):
        v += 0.01
        if mixer.music.get_pos() / 1000 <= 3.0:
            mixer.music.set_volume(v)
            time.sleep(0.02)
        else:
            mixer.music.set_volume(1.0)
            return None

def mainRender():
    while True:
        root.clear_canvas(wait_execute = True)
        root.run_js_wait_code()

root = webcvapis.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "Phigros",
    debug = "--debug" in sys.argv
)
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root._web.toggle_fullscreen()
webdpr = root.run_js_code("window.devicePixelRatio;")
root.run_js_code(f"lowquality_scale = {1.0 / webdpr};")
if "--window-host" in sys.argv:
    windll.user32.SetParent(root.winfo_hwnd(), eval(sys.argv[sys.argv.index("--window-host") + 1]))

Resource = Load_Resource()
eventManager = PhigrosGameObject.EventManager()
bindEvents()
Thread(target=showStartAnimation, daemon=True).start()
    
root.loop_to_close()
windll.kernel32.ExitProcess(0)