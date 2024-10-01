import os.path
import sys
import traceback
import time
from ctypes import windll
from tkinter.messagebox import showerror

def excepthook(etype, value, tb):
    if KeyboardInterrupt in etype.mro():
        print("^C")
        windll.kernel32.ExitProcess(0)
    
    errortext = "".join(traceback.format_exception(etype, value, tb))
    errorfile = f"error_{time.time()}.txt"
    with open(errorfile, "w", encoding="utf-8") as f:
        f.write(errortext)
    
    showerror(title="程序发生错误", message=f"很抱歉, PhigrosPlayer 发生了错误\n已生成错误文件到: {os.path.abspath(errorfile)}\n请将错误文件发送给开发者以获得帮助\nhttps://github.com/qaqFei/PhigrosPlayer\n\n\n{errortext}")
    windll.kernel32.ExitProcess(0)

sys.excepthook = excepthook