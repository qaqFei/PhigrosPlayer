from threading import Thread
from ctypes import windll
from os import chdir, environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = str()
from os.path import exists, abspath, dirname
import webbrowser
import typing
import json
import sys
import time
import math

sys.excepthook = lambda *args: [print("^C"), windll.kernel32.ExitProcess(0)] if KeyboardInterrupt in args[0].mro() else sys.__excepthook__(*args)

from PIL import Image, ImageFilter
from pygame import mixer
import webcvapis

import Const
import Tool_Functions
import PhigrosGameObject

selfdir = dirname(sys.argv[0])
if selfdir == "": selfdir = abspath(".")
chdir(selfdir)

if not exists("./PhigrosAssets"):
    while True:
        print("PhigrosAssets not found, please download it from https://github.com/qaqFei/PhigrosPlayer_PhigrosAssets")
        time.sleep(0.1)

mixer.init()
chaptersDx = 0.0
inMainUI = False
lastMainUI_ChaptersClickX = 0.0
lastLastMainUI_ChaptersClickX = 0.0
mainUI_ChaptersMouseDown = False

def Load_Chapters():
    global Chapters, ChaptersMaxDx
    jsonData = json.loads(open("./PhigrosAssets/chapters.json", "r", encoding="utf-8").read())
    Chapters = PhigrosGameObject.Chapters(
        [
            PhigrosGameObject.Chapter(
                name = chapter["name"],
                cn_name = chapter["cn-name"],
                o_name = chapter["o-name"],
                image = chapter["image"],
                songs = [
                    PhigrosGameObject.Song(
                        name = song["name"],
                        composer = song["composer"],
                        image = song["image"],
                        preview = song["preview"],
                        difficlty = [
                            PhigrosGameObject.SongDifficlty(
                                name = diff["name"],
                                level = diff["level"],
                                chart = diff["chart"]
                            )
                            for diff in song["difficlty"]
                        ]
                    )
                    for song in chapter["songs"]
                ]
            )
            for chapter in jsonData["chapters"]
        ]
    )
    
    ChaptersMaxDx = w * (len(Chapters.items) - 1) * (295 / 1920) + w * 0.5 - w * 0.875

def Load_Resource():
    global ButtonWidth, ButtonHeight
    global CollectiblesIconWidth, CollectiblesIconHeight
    global MessageButtonSize
    global JoinQQGuildBannerWidth, JoinQQGuildBannerHeight
    global JoinQQGuildPromoWidth, JoinQQGuildPromoHeight
    
    Resource = {
        "logoipt": Image.open("./Resources/logoipt.png"),
        "warning": Image.open("./Resources/Start.png"),
        "phigros": Image.open("./Resources/phigros.png"),
        "AllSongBlur": Image.open("./Resources/AllSongBlur.png"),
        "facula": Image.open("./Resources/facula.png"),
        "collectibles": Image.open("./Resources/collectibles.png"),
        "setting": Image.open("./Resources/setting.png"),
        "ButtonLeftBlack": Image.open("./Resources/Button_Left_Black.png"),
        "ButtonRightBlack": None,
        "message": Image.open("./Resources/message.png"),
        "JoinQQGuildBanner": Image.open("./Resources/JoinQQGuildBanner.png"),
        "UISound_1": mixer.Sound("./Resources/UISound_1.wav"),
        "UISound_2": mixer.Sound("./Resources/UISound_2.wav"),
        "JoinQQGuildPromo": Image.open("./Resources/JoinQQGuildPromo.png"),
    }
    
    Resource["ButtonRightBlack"] = Resource["ButtonLeftBlack"].transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    
    root.reg_img(Resource["logoipt"], "logoipt")
    root.reg_img(Resource["warning"], "warning")
    root.reg_img(Resource["phigros"], "phigros")
    root.reg_img(Resource["AllSongBlur"], "AllSongBlur")
    root.reg_img(Resource["facula"], "facula")
    root.reg_img(Resource["collectibles"], "collectibles")
    root.reg_img(Resource["setting"], "setting")
    root.reg_img(Resource["ButtonLeftBlack"], "ButtonLeftBlack")
    root.reg_img(Resource["ButtonRightBlack"], "ButtonRightBlack")
    root.reg_img(Resource["message"], "message")
    root.reg_img(Resource["JoinQQGuildBanner"], "JoinQQGuildBanner")
    root.reg_img(Resource["JoinQQGuildPromo"], "JoinQQGuildPromo")
        
    ButtonWidth = w * 0.10875
    ButtonHeight = ButtonWidth / Resource["ButtonLeftBlack"].width * Resource["ButtonLeftBlack"].height # bleft and bright size is the same.
    CollectiblesIconWidth = w * 0.0265
    CollectiblesIconHeight = CollectiblesIconWidth / Resource["collectibles"].width * Resource["collectibles"].height
    MessageButtonSize = w * 0.025
    JoinQQGuildBannerWidth = w * 0.2
    JoinQQGuildBannerHeight = JoinQQGuildBannerWidth / Resource["JoinQQGuildBanner"].width * Resource["JoinQQGuildBanner"].height
    JoinQQGuildPromoWidth = w * 0.61
    JoinQQGuildPromoHeight = JoinQQGuildPromoWidth / Resource["JoinQQGuildPromo"].width * Resource["JoinQQGuildPromo"].height
    
    for chapter in Chapters.items:
        im = Image.open(f"./PhigrosAssets/{chapter.image}")
        chapter.im = im
        root.reg_img(im, f"chapter_{chapter.chapterId}_raw")
        root.reg_img(im.filter(ImageFilter.GaussianBlur(radius = (im.width + im.height) / 100)), f"chapter_{chapter.chapterId}_blur")
    
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
    
    # i donot want to update webcvapis module ...
    root._regims.clear()
    root.shutdown_fileserver()
    Thread(target=root._file_server.serve_forever, args=(0.1, ), daemon=True).start()
    
    return Resource

def bindEvents():
    root.jsapi.set_attr("click", eventManager.click)
    root.run_js_code("_click = (e) => pywebview.api.call_attr('click', e.x, e.y);")
    root.run_js_code("document.addEventListener('mousedown', _click);")
    
    root.jsapi.set_attr("mousemove", eventManager.move)
    root.run_js_code("_mousemove = (e) => pywebview.api.call_attr('mousemove', e.x, e.y);")
    root.run_js_code("document.addEventListener('mousemove', _mousemove);")
    
    root.jsapi.set_attr("mouseup", eventManager.release)
    root.run_js_code("_mouseup = (e) => pywebview.api.call_attr('mouseup', e.x, e.y);")
    root.run_js_code("document.addEventListener('mouseup', _mouseup);")
    
    eventManager.regClickEventFs(mainUI_mouseClick, False)
    eventManager.regReleaseEvent(PhigrosGameObject.ReleaseEvent(mainUI_mouseRelease))
    eventManager.regMoveEvent(PhigrosGameObject.MoveEvent(mainUI_mouseMove))

def drawBackground():
    root.run_js_code(
        f"ctx.drawImage(\
            {root.get_img_jsvarname("AllSongBlur")},\
            0, 0, {w}, {h}\
        );",
        add_code_array = True
    )

def drawFaculas():
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

def drawChapterItem(item: PhigrosGameObject.Chapter, dx: float):
    chapterIndex = Chapters.items.index(item)
    
    if chapterIndex == Chapters.aFrom:
        p = 1.0 - (time.time() - Chapters.aSTime) / 1.5
    elif chapterIndex == Chapters.aTo:
        p = (time.time() - Chapters.aSTime) / 1.5
    else:
        p = 0.0
    
    p = p if 0.0 <= p <= 1.0 else (0.0 if p < 0.0 else 1.0)
    p = 1.0 - (1.0 - p) ** 2
    
    chapterWidth = w * (0.221875 + (0.5640625 - 0.221875) * p)
    chapterImWidth = h * (1.0 - 140 / 1080 * 2) / item.im.height * item.im.width
    dPower = 215 / 425 + (215 / 1085 - 215 / 425) * p
    
    chapterRect = (
        dx, h * (140 / 1080),
        dx + chapterWidth, h * (1.0 - 140 / 1080)
    )
    
    root.run_js_code(
        f"ctx.drawDiagonalRectangleClipImage(\
            {", ".join(map(str, chapterRect))},\
            {root.get_img_jsvarname(f"chapter_{item.chapterId}_raw")},\
            {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
            {dPower}, {p}\
        );",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.drawDiagonalRectangleClipImage(\
            {", ".join(map(str, chapterRect))},\
            {root.get_img_jsvarname(f"chapter_{item.chapterId}_blur")},\
            {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
            {dPower}, {1.0 - p}\
        );",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.drawRotateText2(\
            '{processStringToLiteral(item.name)}',\
            {chapterRect[2] - dPower * chapterWidth - (w + h) / 150}, {chapterRect[3] - (w + h) / 150},\
            -75, 'rgba(255, 255, 255, {0.95 * (1.0 - p)})', '{(w + h) / 50}px PhigrosFont',\
            'left', 'bottom'\
        );",
        add_code_array = True
    )
    
    return w * (295 / 1920) + (w * 0.5 - w * (295 / 1920)) * p

def drawChapters():
    chapterX = w * 0.034375 + chaptersDx
    for chapter in Chapters.items:
        chapterX += drawChapterItem(chapter, chapterX)

def drawButton(buttonName: typing.Literal["ButtonLeftBlack", "ButtonRightBlack"], iconName: str, buttonPos: tuple[float, float]):
    root.run_js_code(
        f"ctx.drawImage(\
           {root.get_img_jsvarname(buttonName)},\
           {buttonPos[0]}, {buttonPos[1]}, {ButtonWidth}, {ButtonHeight}\
        );",
        add_code_array = True
    )
    
    centerPoint = (0.35, 0.395) if buttonName == "ButtonLeftBlack" else (0.65, 0.605)
    
    root.run_js_code(
        f"ctx.drawImage(\
           {root.get_img_jsvarname(iconName)},\
           {buttonPos[0] + ButtonWidth * centerPoint[0] - CollectiblesIconWidth / 2},\
           {buttonPos[1] + ButtonHeight * centerPoint[1] - CollectiblesIconHeight / 2},\
           {CollectiblesIconWidth}, {CollectiblesIconHeight}\
        );",
        add_code_array = True
    )

def drawDialog(
    p: float,
    dialogImageName: str, diagonalPower: float,
    dialogImageSize: tuple[float, float],
    noText: str, yesText: str
):
            
    root.run_js_code(
        f"dialog_canvas_ctx.clear();",
        add_code_array = True
    )
            
    p = 1.0 - (1.0 - p) ** 3
    tempWidth = dialogImageSize[0] * (0.65 + p * 0.35)
    tempHeight = dialogImageSize[1] * (0.65 + p * 0.35)
    diagonalRectanglePowerPx = diagonalPower * tempWidth
    
    root.run_js_code(
        f"dialog_canvas_ctx.drawAlphaImage(\
            {root.get_img_jsvarname(dialogImageName)},\
            {w / 2 - tempWidth / 2}, {h * 0.39 - tempHeight / 2},\
            {tempWidth}, {tempHeight}, {p}\
        );",
        add_code_array = True
    )
    
    diagonalRectangle = (
        w / 2 - tempWidth / 2 - diagonalRectanglePowerPx * 0.2,
        h * 0.39 + tempHeight / 2,
        w / 2 + tempWidth / 2 - diagonalRectanglePowerPx,
        h * 0.39 + tempHeight / 2 + tempHeight * 0.2
    )
    
    root.run_js_code(
        f"dialog_canvas_ctx.drawDiagonalRectangle(\
            {", ".join(map(str, diagonalRectangle))},\
            {diagonalPower * 0.2}, 'rgba(0, 0, 0, {0.85 * p})'\
        );",
        add_code_array = True
    )
    
    root.run_js_code(
        f"dialog_canvas_ctx.drawDiagonalRectangleText(\
            {", ".join(map(str, diagonalRectangle))},\
            {diagonalPower * 0.2},\
            '{processStringToLiteral(noText)}',\
            '{processStringToLiteral(yesText)}',\
            'rgba(255, 255, 255, {p})',\
            '{(w + h) / 100 * (0.65 + p * 0.35)}px PhigrosFont'\
        );",
        add_code_array = True
    )
    
    return (
        diagonalRectangle[0] + diagonalRectanglePowerPx * 0.2, diagonalRectangle[1],
        diagonalRectangle[0] + (diagonalRectangle[2] - diagonalRectangle[0]) / 2, diagonalRectangle[3]
    ), (
        diagonalRectangle[0] + (diagonalRectangle[2] - diagonalRectangle[0]) / 2, diagonalRectangle[1],
        diagonalRectangle[2] - diagonalRectanglePowerPx * 0.2, diagonalRectangle[3]
    )

def showStartAnimation():
    global faManager
    
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
            eventManager.regClickEventFs(start_animation_click_cb, True)
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
    a3_sound_fadeout = False
    def a3_click_cb(*args):
        nonlocal a3_clicked_time, a3_clicked
        a3_clicked_time = time.time()
        a3_clicked = True
    eventManager.regClickEventFs(a3_click_cb, True)
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
            root.create_rectangle( # no wait
                0, 0, w, h, fillStyle = "#000000"
            )
            break
        
        root.clear_canvas(wait_execute = True)
        
        drawBackground()
        
        root.create_rectangle(
            0, 0, w, h,
            fillStyle = f"rgba(0, 0, 0, {(math.sin(atime / 1.5) + 1.0) / 5 + 0.15})",
            wait_execute = True
        )
        
        for i in range(50):
            root.create_line(
                0, h * (i / 50), w, h * (i / 50),
                strokeStyle = "rgba(162, 206, 223, 0.03)",
                lineWidth = 0.25, wait_execute = True
            )
    
        drawFaculas()
        
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
            if not a3_sound_fadeout:
                a3_sound_fadeout = True
                mixer.music.fadeout(500)
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {1.0 - (1.0 - (time.time() - a3_clicked_time)) ** 2})",
                wait_execute = True
            )
        
        root.run_js_wait_code()
    
    root.run_js_code(f"mask.style.backdropFilter = '';", add_code_array = True)
    mixer.music.load("./Resources/ChapterSelect.mp3")
    mixer.music.play(-1)
    mainRender()

def soundEffect_From0To1():
    v = 0.0
    for _ in range(100):
        v += 0.01
        if mixer.music.get_pos() / 1000 <= 3.0:
            mixer.music.set_volume(v)
            time.sleep(0.02)
        else:
            mixer.music.set_volume(1.0)
            return None

def processStringToLiteral(string: str):
    return string.replace("\\","\\\\").replace("'","\\'").replace("\"","\\\"").replace("`","\\`").replace("\n", "\\n")

def mainUI_mouseMove(x, y):
    global lastMainUI_ChaptersClickX, lastLastMainUI_ChaptersClickX, chaptersDx
    if inMainUI and mainUI_ChaptersMouseDown:
        chaptersDx += x - lastMainUI_ChaptersClickX
        lastLastMainUI_ChaptersClickX = lastMainUI_ChaptersClickX
        lastMainUI_ChaptersClickX = x

def mainUI_mouseClick(x, y):
    global lastMainUI_ChaptersClickX, lastLastMainUI_ChaptersClickX, mainUI_ChaptersMouseDown
    
    if not inMainUI:
        return None
    
    for e in eventManager.clickEvents:
        if e.tag == "mainUI" and Tool_Functions.InRect(x, y, e.rect):
            return None
    
    lastMainUI_ChaptersClickX = x
    lastLastMainUI_ChaptersClickX = x
    mainUI_ChaptersMouseDown = True

def mainUI_mouseRelease(x, y):
    global mainUI_ChaptersMouseDown
    downed = mainUI_ChaptersMouseDown # 按下过
    mainUI_ChaptersMouseDown = False
    
    if downed and inMainUI:
        Thread(target=chapterUI_easeSroll, daemon=True).start()    

def chapterUI_easeSroll():
    global chaptersDx
    dx = (lastMainUI_ChaptersClickX - lastLastMainUI_ChaptersClickX)
    
    while abs(dx) > w * 0.001:
        dx *= 0.9
        chaptersDx += dx
        if - chaptersDx <= - w / 10 or - chaptersDx >= ChaptersMaxDx - w / 10: # 往右 = 负, 左 = 正, 反的, 所以`-cheaptersDx`
            Thread(target=cheapterUI_easeBack, daemon=True).start()
            return None
        time.sleep(1 / 120)
    Thread(target=cheapterUI_easeBack, daemon=True).start()

def cheapterUI_easeBack():
    global chaptersDx
    
    cdx = - chaptersDx
    
    if 0 <= cdx <= ChaptersMaxDx:
        return None

    if cdx < 0:
        dx = -cdx
    else:
        dx = ChaptersMaxDx - cdx
    dx *= -1 # 前面cdx = 负的, 所以变回来
    
    lastv = 0.0
    av = 0.0
    ast = time.time()
    while True:
        p = (time.time() - ast) / 0.75
        if p > 1.0:
            chaptersDx += dx - av
            break
        
        v = 1.0 - (1.0 - p) ** 4
        dxv = (v - lastv) * dx
        av += dxv
        chaptersDx += dxv
        lastv = v
        
        time.sleep(1 / 120)

def mainRender():
    global inMainUI
    inMainUI = True
    
    faManager.faculas.clear()
    mainRenderSt = time.time()
    
    messageRect = (w * 0.015, h * 0.985 - MessageButtonSize, MessageButtonSize, MessageButtonSize)
    JoinQQGuildBannerRect = (0.0, h - JoinQQGuildBannerHeight, JoinQQGuildBannerWidth, JoinQQGuildBannerHeight)
    events = []
    
    clickedMessage = False
    clickMessageTime = float("nan")
    canClickMessage = True
    messageBackTime = 7.0
    messageBacking = False
    messageBackSt = float("nan")
    def clickMessage(*args):
        nonlocal clickedMessage, clickMessageTime, canClickJoinQQGuildBanner
        if canClickMessage:
            clickMessageTime = time.time()
            clickedMessage = True
            canClickJoinQQGuildBanner = True
            Resource["UISound_1"].play()
    events.append(PhigrosGameObject.ClickEvent(
        rect = (messageRect[0], messageRect[1], messageRect[0] + messageRect[2], messageRect[1] + messageRect[3]),
        callback = clickMessage,
        once = False,
        tag = "mainUI"
    ))
    eventManager.regClickEvent(events[-1])
    
    clickedJoinQQGuildBanner = False
    clickedJoinQQGuildBannerTime = float("nan")
    canClickJoinQQGuildBanner = False
    def clickJoinQQGuildBanner(*args):
        global inMainUI
        nonlocal clickedJoinQQGuildBanner, clickedJoinQQGuildBannerTime, messageBackTime
        
        if canClickJoinQQGuildBanner and (time.time() - clickMessageTime) > 0.1:
            clickedJoinQQGuildBannerTime = time.time()
            clickedJoinQQGuildBanner = True
            messageBackTime = float("inf")
            inMainUI = False
            Resource["UISound_2"].play()
    events.append(PhigrosGameObject.ClickEvent(
        rect = (JoinQQGuildBannerRect[0], JoinQQGuildBannerRect[1], JoinQQGuildBannerRect[0] + JoinQQGuildBannerRect[2], JoinQQGuildBannerRect[1] + JoinQQGuildBannerRect[3]),
        callback = clickJoinQQGuildBanner,
        once = False
    ))
    eventManager.regClickEvent(events[-1])
    
    JoinQQGuildPromoNoEvent = None
    JoinQQGuildPromoYesEvent = None
    JoinQQGuildBacking = False
    JoinQQGuildBackingSt = float("nan")
    
    def JoinQQGuildPromoNoCallback(*args):
        global inMainUI
        nonlocal JoinQQGuildBacking, JoinQQGuildBackingSt, clickedJoinQQGuildBanner
        nonlocal JoinQQGuildPromoNoEvent, JoinQQGuildPromoYesEvent
        
        JoinQQGuildBacking = True
        JoinQQGuildBackingSt = time.time()
        clickedJoinQQGuildBanner = False
        
        eventManager.unregClickEvent(JoinQQGuildPromoNoEvent)
        eventManager.unregClickEvent(JoinQQGuildPromoYesEvent)
        
        JoinQQGuildPromoNoEvent = None
        JoinQQGuildPromoYesEvent = None
        inMainUI = True
    
    def JoinQQGuildPromoYesCallback(*args):
        webbrowser.open_new("https://qun.qq.com/qqweb/qunpro/share?inviteCode=21JzOLUd6J0")
        JoinQQGuildPromoNoCallback(*args)
    
    while True:
        root.clear_canvas(wait_execute = True)
        
        drawBackground()
        
        root.create_rectangle(
            0, 0, w, h,
            fillStyle = "rgba(0, 0, 0, 0.7)",
            wait_execute = True
        )
        
        drawFaculas()
        
        drawButton("ButtonLeftBlack", "collectibles", (0, 0))
        drawButton("ButtonRightBlack", "setting", (w - ButtonWidth, h - ButtonHeight))
        drawChapters()
        
        root.run_js_code(
            f"ctx.drawAlphaImage(\
                {root.get_img_jsvarname("message")},\
                {", ".join(map(str, messageRect))}, 0.7\
            );",
            add_code_array = True
        )
        
        if clickedMessage and time.time() - clickMessageTime >= messageBackTime:
            clickedMessage = False
            messageBacking = True
            messageBackSt = time.time()
            canClickJoinQQGuildBanner = False
            
            if messageBackTime == 0.0:
                messageBackTime = 2.0 # back JoinQQGuild
            elif messageBackTime == 2.0:
                messageBackTime = 7.0
        
        if clickedMessage and time.time() - clickMessageTime <= 1.5:
            root.run_js_code(
                f"ctx.drawImage(\
                    {root.get_img_jsvarname("JoinQQGuildBanner")},\
                    {JoinQQGuildBannerRect[0] - JoinQQGuildBannerWidth + (1.0 - (1.0 - ((time.time() - clickMessageTime) / 1.5)) ** 6) * JoinQQGuildBannerWidth}, {JoinQQGuildBannerRect[1]},\
                    {JoinQQGuildBannerRect[2]}, {JoinQQGuildBannerRect[3]}\
                );",
                add_code_array = True
            )
        elif not clickedMessage and messageBacking:
            if time.time() - messageBackSt > 1.5:
                messageBacking = False
                messageBackSt = time.time() - 1.5 # 防止回弹
                canClickMessage = True
            root.run_js_code(
                f"ctx.drawImage(\
                    {root.get_img_jsvarname("JoinQQGuildBanner")},\
                    {JoinQQGuildBannerRect[0] - (1.0 - (1.0 - ((time.time() - messageBackSt) / 1.5)) ** 6) * JoinQQGuildBannerWidth}, {JoinQQGuildBannerRect[1]},\
                    {JoinQQGuildBannerRect[2]}, {JoinQQGuildBannerRect[3]}\
                );",
                add_code_array = True
            )
        elif clickedMessage:
            root.run_js_code(
                f"ctx.drawImage(\
                    {root.get_img_jsvarname("JoinQQGuildBanner")},\
                    {JoinQQGuildBannerRect[0]}, {JoinQQGuildBannerRect[1]},\
                    {JoinQQGuildBannerRect[2]}, {JoinQQGuildBannerRect[3]}\
                );",
                add_code_array = True
            )
        
        if clickedMessage and canClickMessage:
            canClickMessage = False
        
        if clickedJoinQQGuildBanner:
            canClickJoinQQGuildBanner = False
            p = (time.time() - clickedJoinQQGuildBannerTime) / 0.35
            p = p if p <= 1.0 else 1.0
            ep = 1.0 - (1.0 - p) ** 2
            
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {ep * 0.5})",
                wait_execute = True                
            )
            
            root.run_js_code(
                f"mask.style.backdropFilter = 'blur({(w + h) / 120 * ep}px)';",
                add_code_array = True
            )
            
            noRect, yesRect = drawDialog(
                p, "JoinQQGuildPromo",
                Const.JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER,
                (JoinQQGuildPromoWidth, JoinQQGuildPromoHeight),
                "关闭", "跳转到外部应用"
            )
            
            if JoinQQGuildPromoNoEvent is None and JoinQQGuildPromoYesEvent is None:
                JoinQQGuildPromoNoEvent = PhigrosGameObject.ClickEvent( # once is false, remove event in callback
                    noRect, JoinQQGuildPromoNoCallback, False
                )
                JoinQQGuildPromoYesEvent = PhigrosGameObject.ClickEvent(
                    yesRect, JoinQQGuildPromoYesCallback, False
                )
                eventManager.regClickEvent(JoinQQGuildPromoNoEvent)
                eventManager.regClickEvent(JoinQQGuildPromoYesEvent)
            else:
                JoinQQGuildPromoNoEvent.rect = noRect
                JoinQQGuildPromoYesEvent.rect = yesRect
        elif JoinQQGuildBacking and time.time() - JoinQQGuildBackingSt < 0.35:
            p = 1.0 - (time.time() - JoinQQGuildBackingSt) / 0.35
            ep = 1.0 - (1.0 - p) ** 2
            
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {ep * 0.5})",
                wait_execute = True                
            )
            
            root.run_js_code(
                f"mask.style.backdropFilter = 'blur({(w + h) / 120 * ep}px)';",
                add_code_array = True
            )
            
            drawDialog(
                p, "JoinQQGuildPromo",
                Const.JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER,
                (JoinQQGuildPromoWidth, JoinQQGuildPromoHeight),
                "关闭", "跳转到外部应用"
            )
        elif JoinQQGuildBacking:
            root.run_js_code(
                "mask.style.backdropFilter = 'blur(0px)';",
                add_code_array = True
            )
            
            root.run_js_code(
                "dialog_canvas_ctx.clear();",
                add_code_array = True
            )
            
            JoinQQGuildBacking = False
            JoinQQGuildBackingSt = float("nan")
            messageBackTime = 0.0
        
        if time.time() - mainRenderSt < 2.0:
            root.create_rectangle(
                0, 0, w, h,
                fillStyle = f"rgba(0, 0, 0, {(1.0 - (time.time() - mainRenderSt) / 2.0) ** 2})",
                wait_execute = True
            )
        
        root.run_js_wait_code()
    
    eventManager.clickEvents.clear()
    inMainUI = False

root = webcvapis.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "Phigros",
    debug = "--debug" in sys.argv,
    resizable = False
)
webdpr = root.run_js_code("window.devicePixelRatio;")
root.run_js_code(f"lowquality_scale = {1.0 / webdpr};")
w, h = int(root.winfo_screenwidth() * 0.61803398874989484820458683436564), int(root.winfo_screenheight() * 0.61803398874989484820458683436564)
root.resize(w, h)
w_legacy, h_legacy = root.winfo_legacywindowwidth(), root.winfo_legacywindowheight()
dw_legacy, dh_legacy = w - w_legacy, h - h_legacy
dw_legacy *= webdpr; dh_legacy *= webdpr
dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
del w_legacy, h_legacy
root.resize(w + dw_legacy, h + dh_legacy)
root.move(int(root.winfo_screenwidth() / 2 - (w + dw_legacy) / webdpr / 2), int(root.winfo_screenheight() / 2 - (h + dh_legacy) / webdpr / 2))

if "--window-host" in sys.argv:
    windll.user32.SetParent(root.winfo_hwnd(), eval(sys.argv[sys.argv.index("--window-host") + 1]))

Load_Chapters()
Resource = Load_Resource()
eventManager = PhigrosGameObject.EventManager()
bindEvents()
Thread(target=showStartAnimation, daemon=True).start()
    
root.loop_to_close()
windll.kernel32.ExitProcess(0)