import tkinter.messagebox
from os import system

import webview.platforms.winforms

if webview.platforms.winforms.renderer != "edgechromium":
    tkinter.messagebox.showerror("错误", "请使用EdgeChromium渲染器\n关闭此对话框后将启动安装程序")
    system(".\\ecwv_installer.exe")
    if webview.platforms.winforms._is_chromium():
        webview.platforms.winforms.renderer = "edgechromium"
    else:
        tkinter.messagebox.showwarning("警告", "EdgeChromium渲染器安装失败或取消\n请手动安装\n接下来将继续运行程序, 能不能跑起来全看天意吧...")