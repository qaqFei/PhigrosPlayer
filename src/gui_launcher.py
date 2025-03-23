import fix_workpath as _

import os
import sys
import ctypes
import glfw
import imgui
import threading
import subprocess
from imgui.integrations.glfw import GlfwRenderer
from os import popen
from os.path import exists, isfile, isdir
from sys import executable

if exists("./main.py") and isfile("./main.py"):
    target_path = f"\"PhigrosPlayer\" \"{executable}\" ./main.py"
elif exists("./main.exe") and isfile("./main.exe"):
    target_path = "./main.exe"
else:
    print("Can't find main.py or main.exe.")
    raise SystemExit

# Setup argument settings
arg_setting = [
    ("调试", "debug"),
    ("全屏", "fullscreen"),
    ("自动循环", "loop"),
    ("禁用点击音效", "noclicksound"),
    ("扩展渲染范围", "render-range-more"),
    ("窗口无边框", "frameless"),
    ("禁用自动游玩", "noautoplay"),
    ("启用实时准度", "rtacc"),
    ("低画质模式", "lowquality"),
    ("显示帧率", "showfps"),
    ("不播放谱面, 立即结算", "noplaychart"),
    ("启用rpe谱面control类字段", "rpe-control", "有极大的性能开销"),
    ("替换文本为中文 (wl)", "wl-more-chinese"),
    ("使用 raf 限制帧率", "renderdemand"),
    ("异步渲染", "renderasync"),
    ("保留渲染的 JavaScript 代码", "enable-jslog"),
    ("启用 BitmapImage", "enable-jscanvas-bitmap"),
    ("降级音频API", "soundapi-downgrade"),
    ("不清理临时文件", "nocleartemp"),
    ("脱离 WebView", "disengage-webview"),
    ("禁用 localhost 作为内置服务器地址", "nolocalhost"),
    ("使用 16:9 的比例", "usu169"),
    ("渲染视频", "render-video"),
    ("渲染视频后自动退出", "render-video-autoexit"),
]

kwarg_setting = [
    ("连击提示文本", "combotips", "AUTOPLAY", "string"),
    ("打击特效随机块数量", "random-block-num", 4, "int"),
    ("设置音符缩放", "scale-note", 1.0, "float"),
    ("设置窗口大小 (如: \"1920 1080\")", "size", None, "string-nowarp"),
    ("设置渲染范围更多的缩放", "render-range-more-scale", 2.0, "float"),
    ("设置窗口宿主 (hwnd)", "window-host", None, "int"),
    ("设置低画质渲染缩放", "lowquality-scale", 2.0, "float"),
    ("设置资源路径", "res", None, "path-dir"),
    ("设置谱面速度", "speed", 1.0, "float"),
    ("设置打击特效方块的圆角系数", "clickeffect-randomblock-roundn", 0.0, "float"),
    ("设置打击音效音量", "clicksound-volume", 1.0, "float"),
    ("设置音乐音量", "musicsound-volume", 1.0, "float"),
    ("设置低画质渲染缩放 (js调用层)", "lowquality-imjscvscale-x", 1.0, "float"),
    ("使用 phira 谱面 (id)", "phira-chart", None, "int"),
    ("保存 phira 谱面路径", "phira-chart-save", None, "path"),
    ("播放时跳过的时间", "skip-time", 0.0, "float"),
    ("设置 渲染JavaScript 代码输出路径", "jslog-path", None, "path"),
    ("设置低画质渲染最大尺寸 (js调用层)", "lowquality-imjs-maxsize", 256, "int"),
    ("设置 rpe 谱面纹理缩放方法", "rpe-texture-scalemethod", "by-width", "choice", ["by-width", "by-height"]),
    ("扩展", "extended", None, "path"),
    ("设置渲染视频的帧率", "render-video-fps", 60.0, "float"),
    ("设置生成视频编码", "render-video-fourcc", "mp4v", "string"),
    ("设置渲染视频的保存路径", "render-video-savefp", None, "path"),
    ("手动指定 rpe 谱面版本", "rpeversion", None, "int"),
]

class PhigrosLauncher:
    def __init__(self):
        # Initialize window
        if not glfw.init():
            sys.exit(1)
        
        # Create window
        self.window = glfw.create_window(900, 700, "Phigros Player Launcher", None, None)
        if not self.window:
            glfw.terminate()
            sys.exit(1)
        
        # Set window icon
        if os.path.exists("icon.ico"):
            try:
                from PIL import Image
                import numpy as np
                # Load icon
                img = Image.open("icon.ico")
                img_data = np.array(img.convert("RGBA"))
                glfw.set_window_icon(self.window, 1, [(img.width, img.height, img_data)])
            except ImportError:
                print("PIL not installed, skipping window icon")
        else:
            print("icon.ico not found, skipping window icon")
        
        # Make context current
        glfw.make_context_current(self.window)
        
        # Initialize imgui
        imgui.create_context()

        
        print("Loading font...")
        # Load custom font
        io = imgui.get_io()
        try:
            font_path = os.path.join("resources", "font.ttf")
            if os.path.exists(font_path):
                print(f"Loading font {font_path}")
                # Load font with default size 16.0 and Chinese character ranges
                font_size = 16.0
                # Add Chinese character ranges (0x4E00 to 0x9FFF)
                glyph_ranges = io.fonts.get_glyph_ranges_chinese_full()
                io.fonts.add_font_from_file_ttf(font_path, font_size, glyph_ranges=glyph_ranges)
                print("Font loaded")
            else:
                print(f"Font file not found: {font_path}")
        except Exception as e:
            print(f"Failed to load font: {e}")

        


        self.impl = GlfwRenderer(self.window)

        
        # Configure style
        style = imgui.get_style()
        style.colors[imgui.COLOR_FRAME_BACKGROUND] = (0.2, 0.2, 0.2, 0.7)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.3, 0.3, 0.3, 1.0)
        style.colors[imgui.COLOR_HEADER_ACTIVE] = (0.3, 0.4, 0.7, 1.0)
        style.frame_rounding = 4.0



        # Application state
        self.chart_file = ""
        self.arg_values = [False] * len(arg_setting)
        self.kwarg_values = [""] * len(kwarg_setting)
        
        # Initialize default values
        for i, setting in enumerate(kwarg_setting):
            if setting[2] is not None:
                self.kwarg_values[i] = str(setting[2])
        
        # Add drop capability
        self.setup_drop_handling()

    def setup_drop_handling(self):
        if sys.platform == "win32":
            def glfw_drop_callback(window, paths):
                if len(paths) > 0 and isfile(paths[0]):
                    self.chart_file = paths[0]
            
            glfw.set_drop_callback(self.window, glfw_drop_callback)

    def file_dialog(self, directory=False):
        if sys.platform == "win32":
            try:
                import tkinter as tk
                from tkinter.filedialog import askopenfilename, askdirectory
                
                root = tk.Tk()
                root.withdraw()
                if directory:
                    file_path = askdirectory(title="选择文件夹")
                else:
                    file_path = askopenfilename(title="选择文件")
                root.destroy()
                return file_path
            except Exception as e:
                print(f"Dialog error: {e}")
                return ""
        else:
            # Fallback for other platforms
            return ""
    
    def launch(self):
        launch_args = []
        nowarp_args = []
        
        if not exists(self.chart_file):
            imgui.open_popup("Error")
            self.error_message = "谱面文件不存在或不为文件"
            return
        
        launch_args.append(self.chart_file)
        
        # Add boolean args
        for i, arg in enumerate(arg_setting):
            if self.arg_values[i]:
                launch_args.append(f"--{arg[1]}")
        
        # Add keyword args
        for i, (setting, value) in enumerate(zip(kwarg_setting, self.kwarg_values)):
            if not value:
                continue
            
            kwarg = setting
            userinput = value
            isnoawrp = False
            
            # Validate input
            if kwarg[3] == "int":
                try:
                    userinput = int(float(userinput))
                except ValueError:
                    imgui.open_popup("Error")
                    self.error_message = f"参数 {kwarg[1]} 的值应为整数"
                    return
                    
            elif kwarg[3] == "float":
                try:
                    userinput = float(userinput)
                except ValueError:
                    imgui.open_popup("Error")
                    self.error_message = f"参数 {kwarg[1]} 的值应为浮点数"
                    return
                    
            elif kwarg[3] == "string-nowarp":
                isnoawrp = True
                
            elif kwarg[3] == "path":
                if not (exists(userinput) and isfile(userinput)):
                    imgui.open_popup("Error")
                    self.error_message = f"参数 {kwarg[1]} 的值应为存在的文件"
                    return
                    
            elif kwarg[3] == "path-dir":
                if not (exists(userinput) and isdir(userinput)):
                    imgui.open_popup("Error")
                    self.error_message = f"参数 {kwarg[1]} 的值应为存在的文件夹"
                    return
                    
            elif kwarg[3] == "choice":
                if userinput not in kwarg[4]:
                    imgui.open_popup("Error")
                    self.error_message = f"参数 {kwarg[1]} 的值应为以下之一: {kwarg[4]}"
                    return
            
            # Add argument if it's different from default
            if str(userinput) != str(kwarg[2]):
                if isnoawrp:
                    nowarp_args.append(f"--{kwarg[1]}")
                    nowarp_args.append(f"{userinput}")
                else:
                    launch_args.append(f"--{kwarg[1]}")
                    launch_args.append(f"{userinput}")
        
        command = "start " + target_path + " " + " ".join(map(lambda x: f"\"{x}\"", launch_args)) + " " + " ".join(nowarp_args)
        print(command)
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=lambda: popen(command)).start()

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.impl.process_inputs()
            
            imgui.new_frame()
            
            # Set window size
            imgui.set_next_window_size(imgui.get_io().display_size.x, imgui.get_io().display_size.y)
            imgui.set_next_window_position(0, 0)
            
            imgui.begin(
                "Phigros Player Launcher",
                flags=imgui.WINDOW_NO_RESIZE | 
                      imgui.WINDOW_NO_MOVE |
                      imgui.WINDOW_NO_COLLAPSE | 
                      imgui.WINDOW_NO_TITLE_BAR
            )
            
            # Chart file input
            imgui.text("谱面文件:")
            imgui.same_line()
            imgui.push_item_width(imgui.get_window_width() * 0.7)
            changed, self.chart_file = imgui.input_text("##chart", self.chart_file, 1024)
            imgui.pop_item_width()
            imgui.same_line()
            
            if imgui.button("选择##file"):
                file_path = self.file_dialog()
                if file_path:
                    self.chart_file = file_path
            
            # Tabs for arguments and keyword arguments
            if imgui.begin_tab_bar("settings_tabs"):
                # Boolean arguments tab
                if imgui.begin_tab_item("Arguments")[0]:
                    imgui.begin_child("args_scrolling", 0, imgui.get_window_height() * 0.8, True)
                    
                    # Show checkboxes for boolean arguments
                    cols = 2
                    imgui.columns(cols)
                    
                    for i, arg in enumerate(arg_setting):
                        changed, self.arg_values[i] = imgui.checkbox(f"{arg[0]}##arg{i}", self.arg_values[i])
                        
                        # Go to next column after half the items
                        if (i + 1) % (len(arg_setting) // cols + 1) == 0:
                            imgui.next_column()
                    
                    imgui.columns(1)
                    imgui.end_child()
                    imgui.end_tab_item()
                # Keyword arguments tab
                if imgui.begin_tab_item("Keyword Arguments")[0]:
                    imgui.begin_child("kwargs_scrolling", 0, imgui.get_window_height() * 0.8, True)
                    
                    # Calculate a consistent width for all input fields
                    input_width = imgui.get_window_width() * 0.2
                    browse_button_width = 60
                    right_margin = browse_button_width + input_width + 40  # 200px margin from the right edge
                    
                    for i, kwarg in enumerate(kwarg_setting):
                        imgui.push_id(str(i))
                        
                        # Display the label with left alignment
                        label_text = f"{kwarg[0]} ({kwarg[3]}): "
                        imgui.text(label_text)
                        
                        # Calculate available width for positioning
                        avail_width = imgui.get_content_region_available_width()
                        
                        # Calculate position for right-aligned input with margin
                        input_pos_x = imgui.get_window_width() - right_margin
                        if input_pos_x > imgui.get_cursor_pos_x():
                            imgui.same_line(position=input_pos_x)
                        else:
                            # If there's not enough space, move to next line
                            imgui.same_line()
                        
                        imgui.push_item_width(input_width)
                        
                        if kwarg[3] == "choice":
                            current_idx = kwarg[4].index(self.kwarg_values[i]) if self.kwarg_values[i] in kwarg[4] else 0
                            changed, current_idx = imgui.combo("##value", current_idx, kwarg[4])
                            if changed:
                                self.kwarg_values[i] = kwarg[4][current_idx]
                        else:
                            changed, self.kwarg_values[i] = imgui.input_text("##value", self.kwarg_values[i], 1024)
                        
                        imgui.pop_item_width()
                        
                        if kwarg[3] in ["path", "path-dir"]:
                            imgui.same_line()
                            if imgui.button("浏览##" + ("file" if kwarg[3] == "path" else "dir") + str(i), width=browse_button_width):
                                path = self.file_dialog(directory=(kwarg[3] == "path-dir"))
                                if path:
                                    self.kwarg_values[i] = path
                        
                        imgui.pop_id()
                    
                    imgui.end_child()
                    imgui.end_tab_item()
                imgui.end_tab_bar()
            
            # Launch button
            if imgui.button("启动", width=120, height=40):
                self.launch()
            
            # Error popup
            if imgui.begin_popup_modal("Error", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)[0]:
                imgui.text(self.error_message)
                if imgui.button("确定", width=120):
                    imgui.close_current_popup()
                imgui.end_popup()
            
            imgui.end()
            
            # Render
            imgui.render()
            glfw.make_context_current(self.window)
            glfw.swap_buffers(self.window)
            self.impl.render(imgui.get_draw_data())
        
        # Cleanup
        self.impl.shutdown()
        glfw.terminate()

if __name__ == "__main__":
    app = PhigrosLauncher()
    app.run()
