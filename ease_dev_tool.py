from threading import Thread
from ctypes import windll
import importlib.util

import web_canvas

def Main():
    while True:
        module_fp = input("Enter module fp: ")
        try:
            module_spec = importlib.util.spec_from_file_location("ease_dev_module", module_fp)
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            ease_func = module.ease
            
            cv.clear_canvas(wait_execute = True)
            cv.create_line(
                100, 600, 600, 600,
                lineWidth = 2,
                fillStyle = "#222",
                wait_execute = True
            )
            cv.create_line(
                100, 100, 100, 600,
                lineWidth = 2,
                fillStyle = "#222",
                wait_execute = True
            )
            dx = 1 / 5e4
            p = 0.0
            while p <= 1.0:
                v = ease_func(p)
                p += dx
                cv.create_circle(
                    100 + p * 500, (1 - v) * 500 + 100,
                    r = 5,
                    strokeStyle = "#000",
                    wait_execute = True
                )
            cv.run_js_wait_code()
            
        except Exception as e:
            print(f"Error: {e}")

cv = web_canvas.WebCanvas(
    700, 700,
    100, 100,
    title = "Ease Dev Tool",
    resizable = False
)
Thread(target=Main,daemon=True).start()
cv.loop_to_close()
windll.kernel32.ExitProcess(0)