from tkinter import Tk,Label,BooleanVar,StringVar
from tkinter.ttk import Entry,Button,Checkbutton,LabelFrame
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from os import chdir,popen
from os.path import exists,isfile,dirname
from sys import argv
import ctypes

import GUI_Const
import ConsoleWindow

ConsoleWindow.Hide()

selfdir = dirname(argv[0])
if selfdir == "": selfdir = "."
chdir(selfdir)

if exists("./Main.py"):
    target_path = "./Main.py"
elif exists("./Main.exe"):
    target_path = "./Main.exe"
else:
    print("Can't find Main.py or Main.exe.")
    raise SystemExit

TEXT = GUI_Const.CHINESE
if "-english" in argv or "-eng" in argv:
    TEXT = GUI_Const.ENGLISH

def hook_dropfiles_first(hwnd,callback):
    globals()[f"hook_dropfiles_dropfunc_prototype_{hwnd}"] = ctypes.WINFUNCTYPE(*(ctypes.c_uint64,)*5)(lambda hwnd,msg,wp,lp: [callback([ctypes.windll.shell32.DragQueryFileW(ctypes.c_uint64(wp),0,szFile := ctypes.create_unicode_buffer(260),ctypes.sizeof(szFile)),szFile.value][1]) if msg == 0x233 else None,ctypes.windll.user32.CallWindowProcW(*map(ctypes.c_uint64,(lptr,hwnd,msg,wp,lp)))][1]);ctypes.windll.shell32.DragAcceptFiles(hwnd,True);lptr = ctypes.windll.user32.GetWindowLongPtrA(hwnd,-4);ctypes.windll.user32.SetWindowLongPtrA(hwnd,-4,globals()[f"hook_dropfiles_dropfunc_prototype_{hwnd}"])

def OpenFile():
    fp = askopenfilename(
            filetypes = [
                (TEXT.FILE_INPUT_CHART_TYPE_TEXT,"*.zip"),
                (TEXT.FILE_INPUT_ALLFILE_TYPE,"*.*")
            ],
            parent = root,
            title = TEXT.FILE_INPUT_DIALOG_TITLE
        )
    if fp == "":
        return
    
    if not (exists(fp) and isfile(fp)):
        showerror(
            title = TEXT.ERROR_TITLE,
            message = TEXT.FILE_INPUT_ERROR_MESSAGE
        )
    
    file_input_entry.delete(0,"end")
    file_input_entry.insert(0,fp)

def lfdaot_callback():
    state = "normal" if lfdaot_checkbutton_var.get() else "disabled"
    lfdaot_render_video_checkbutton.configure(state = state)
    kwarg_lfdaot_file_entry.configure(state = state)
    kwarg_lfdaot_file_choose_button.configure(state = state)
    kwarg_lfdaot_frame_speed_entry.configure(state = state)

def setsize_callback():
    state = "normal" if setsize_checkbutton_var.get() else "disabled"
    kwarg_size_x_entry.configure(state = state)
    kwarg_size_connect_label.configure(state = state)
    kwarg_size_y_entry.configure(state = state)

def render_range_more_callback():
    state = "normal" if render_range_more_checkbutton_var.get() else "disabled"
    kwarg_render_range_more_scale_entry.configure(state = state)
    
def kwarg_lfdaot_file_choose_callback():
    fp = askopenfilename(
            filetypes = [
                (TEXT.FILE_INPUT_LFDAOT_TYPE_TEXT,"*.lfdaot"),
                (TEXT.FILE_INPUT_ALLFILE_TYPE,"*.*")
            ],
            parent = root,
            title = TEXT.FILE_INPUT_DIALOG_TITLE
        )
    if fp == "":
        return
    
    if not (exists(fp) and isfile(fp)):
        showerror(
            title = TEXT.ERROR_TITLE,
            message = TEXT.FILE_INPUT_ERROR_MESSAGE
        )
    
    kwarg_lfdaot_file_entry.delete(0,"end")
    kwarg_lfdaot_file_entry.insert(0,fp)

def kwarg_extend_file_choose_callback():
    fp = askopenfilename(
            filetypes = [
                (TEXT.FILE_INPUT_EXTEND_TYPE_TEXT,"*.py"),
                (TEXT.FILE_INPUT_ALLFILE_TYPE,"*.*")
            ],
            parent = root,
            title = TEXT.FILE_INPUT_DIALOG_TITLE
        )
    if fp == "":
        return
    
    if not (exists(fp) and isfile(fp)):
        showerror(
            title = TEXT.ERROR_TITLE,
            message = TEXT.FILE_INPUT_ERROR_MESSAGE
        )
    
    kwarg_extend_entry.delete(0,"end")
    kwarg_extend_entry.insert(0,fp)

def Launch():
    launch_command = f"start {target_path} "
    launch_args = []
    phi_fp = file_input_entry.get()
    
    if exists(phi_fp):
        launch_args.append(f"\"{phi_fp}\"")
    else:
        showerror(
            title = TEXT.ERROR_TITLE,
            message = TEXT.LAUNCH_FILE_ERROR_TEXT
        )
        return None

    if debug_checkbutton_var.get():
        launch_args.append("-debug")
    
    if fullscreen_checkbutton_var.get():
        launch_args.append("-fullscreen")
    
    if nojudgeline_checkbutton_var.get():
        launch_args.append("-nojudgeline")
    
    if judgeline_notransparent_checkbutton_var.get():
        launch_args.append("-judgeline-notransparent")
    
    if noclickeffect_randomblock_checkbutton_var.get():
        launch_args.append("-noclickeffect-randomblock")
    
    if loop_checkbutton_var.get():
        launch_args.append("-loop")
    
    if ease_event_interpolation_checkbutton_var.get():
        launch_args.append("-ease-event-interpolation")
    
    if frameless_checkbutton_var.get():
        launch_args.append("-frameless")
    
    if lfdaot_checkbutton_var.get():
        launch_args.append("-lfdaot")
        if kwarg_lfdaot_file_entry.get() != "":
            if exists(kwarg_lfdaot_file_entry.get()) and isfile(kwarg_lfdaot_file_entry.get()):
                launch_args.append(f"-lfdaot-file \"{kwarg_lfdaot_file_entry.get()}\"")
        launch_args.append(f"-lfdaot-frame-speed \"{kwarg_lfdaot_frame_speed_entry.get()}\"")
    
    if noclicksound_checkbutton_var.get():
        launch_args.append("-noclicksound")
    
    if render_range_more_checkbutton_var.get():
        launch_args.append("-render-range-more")
        launch_args.append(f"-render-range-more-scale \"{kwarg_render_range_more_scale_entry.get()}\"")
    
    if setsize_checkbutton_var.get():
        launch_args.append("-size")
        launch_args.append(f"\"{kwarg_size_x_entry.get()}\" \"{kwarg_size_y_entry.get()}\"")
    
    if lfdaot_render_video_checkbutton_var.get():
        launch_args.append("-lfdaot-render-video")
    
    if exists(kwarg_extend_entry.get()) and isfile(kwarg_extend_entry.get()):
        launch_args.append(f"-extend \"{kwarg_extend_entry.get()}\"")
    
    launch_args.append(f"-combotips \"{kwarg_combotips_entry.get()}\"")
    launch_args.append(f"-random-block-num \"{kwarg_random_block_num_entry.get()}\"")
    launch_args.append(f"-scale-note \"{kwarg_scale_note_entry.get()}\"")
    
    launch_command += " ".join(launch_args)
    popen(launch_command)

root = Tk()
root.withdraw()
root.title("Phigros Player Launcher")
root.iconbitmap("icon.ico")
root.resizable(False,False)
screen_width,screen_height = root.winfo_screenwidth(),root.winfo_screenheight()

file_input_label = Label(root,text=TEXT.FILE_INPUT_LABEL_TEXT)
file_input_label.grid(row=0,column=0,columnspan=100,padx=12,sticky="w")
file_input_entry = Entry(root,width=int(screen_width / 35))
file_input_entry.grid(row=0,column=101,columnspan=100,sticky="w")
file_input_filedialog_button = Button(root,text=TEXT.FILE_INPUT_FILEDIALOG_BUTTON_TEXT,command=OpenFile)
file_input_filedialog_button.grid(row=0,column=202,sticky="w")

args_LabelFrame = LabelFrame(root,text=TEXT.ARGS_TEXT)
args_LabelFrame.grid(row=1,column=0,columnspan=5000,padx=12,sticky="w")
kwargs_LabelFrame = LabelFrame(root,text=TEXT.KWARGS_TEXT)
kwargs_LabelFrame.grid(row=2,column=0,columnspan=5000,padx=12,sticky="w")

debug_checkbutton_var = BooleanVar(value=False) # -debug
debug_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.DEBUG,variable=debug_checkbutton_var)
debug_checkbutton.grid(sticky="w",row=0,column=0)
fullscreen_checkbutton_var = BooleanVar(value=False) # -fullscreen
fullscreen_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.FULLSCREEN,variable=fullscreen_checkbutton_var)
fullscreen_checkbutton.grid(sticky="w",row=0,column=1)
nojudgeline_checkbutton_var = BooleanVar(value=False) # -nojudgeline
nojudgeline_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.NOJUDGELINE,variable=nojudgeline_checkbutton_var)
nojudgeline_checkbutton.grid(sticky="w",row=0,column=2)
judgeline_notransparent_checkbutton_var = BooleanVar(value=False) # -judgeline-notransparent
judgeline_notransparent_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.JUDGELINE_NOTRANSPARENT,variable=judgeline_notransparent_checkbutton_var)
judgeline_notransparent_checkbutton.grid(sticky="w",row=1,column=0)
noclickeffect_randomblock_checkbutton_var = BooleanVar(value=False) # -noclickeffect-randomblock
noclickeffect_randomblock_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.NOCLICKEFFECT_RANDOMBLOCK,variable=noclickeffect_randomblock_checkbutton_var)
noclickeffect_randomblock_checkbutton.grid(sticky="w",row=1,column=1)
loop_checkbutton_var = BooleanVar(value=False) # -loop
loop_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.LOOP,variable=loop_checkbutton_var)
loop_checkbutton.grid(sticky="w",row=1,column=2)
lfdaot_checkbutton_var = BooleanVar(value=False) # -lfdaot
lfdaot_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.LFDAOT,variable=lfdaot_checkbutton_var,command=lfdaot_callback)
lfdaot_checkbutton.grid(sticky="w",row=2,column=0)
noclicksound_checkbutton_var = BooleanVar(value=False) # -noclicksound
noclicksound_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.NOCLICKSOUND,variable=noclicksound_checkbutton_var)
noclicksound_checkbutton.grid(sticky="w",row=2,column=1)
render_range_more_checkbutton_var = BooleanVar(value=False) # -render-range-more
render_range_more_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.RRM,variable=render_range_more_checkbutton_var,command=render_range_more_callback)
render_range_more_checkbutton.grid(sticky="w",row=2,column=2)
setsize_checkbutton_var = BooleanVar(value=False) # -size
setsize_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.SETSIZE,variable=setsize_checkbutton_var,command=setsize_callback)
setsize_checkbutton.grid(sticky="w",row=3,column=0)
lfdaot_render_video_checkbutton_var = BooleanVar(value=False) # -lfdaot-render-video
lfdaot_render_video_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.LFDAOT_RENDER_VIDEO,variable=lfdaot_render_video_checkbutton_var)
lfdaot_render_video_checkbutton.grid(sticky="w",row=4,column=0,columnspan=500)
lfdaot_render_video_checkbutton.configure(state = "disabled")
ease_event_interpolation_checkbutton_var = BooleanVar(value=False) # -ease-event-interpolation
ease_event_interpolation_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.EASE_EVENT_INTERPOLATION,variable=ease_event_interpolation_checkbutton_var)
ease_event_interpolation_checkbutton.grid(sticky="w",row=5,column=0)
frameless_checkbutton_var = BooleanVar(value=False) # -frameless
frameless_checkbutton = Checkbutton(args_LabelFrame,text=TEXT.ARGS.FRAMELESS,variable=frameless_checkbutton_var)
frameless_checkbutton.grid(sticky="w",row=5,column=1)

kwarg_combotips_var = StringVar(value="Autoplay") # -combotips
kwarg_combotips_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.COMBOTIPS)
kwarg_combotips_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_combotips_var)
kwarg_combotips_label.grid(row=0,column=0)
kwarg_combotips_entry.grid(row=0,column=1)

kwarg_random_block_num_var = StringVar(value="4") # -random-block-num
kwarg_random_block_num_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.RANDOM_BLOCK_NUM)
kwarg_random_block_num_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_random_block_num_var)
kwarg_random_block_num_label.grid(row=1,column=0)
kwarg_random_block_num_entry.grid(row=1,column=1)

kwarg_scale_note_var = StringVar(value="1.0") # -scale-note
kwarg_scale_note_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.SCALE_NOTE)
kwarg_scale_note_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_scale_note_var)
kwarg_scale_note_label.grid(row=2,column=0)
kwarg_scale_note_entry.grid(row=2,column=1)

kwarg_lfdaot_file_var = StringVar(value="") # -lfdaot-file
kwarg_lfdaot_file_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.LFDAOT_FILE)
kwarg_lfdaot_file_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_lfdaot_file_var)
kwarg_lfdaot_file_choose_button = Button(kwargs_LabelFrame,text=TEXT.FILE_INPUT_FILEDIALOG_BUTTON_TEXT,command=kwarg_lfdaot_file_choose_callback)
kwarg_lfdaot_file_label.grid(row=3,column=0)
kwarg_lfdaot_file_entry.grid(row=3,column=1)
kwarg_lfdaot_file_choose_button.grid(row=3,column=2,columnspan=100,sticky="w")
kwarg_lfdaot_file_entry.configure(state = "disabled")
kwarg_lfdaot_file_choose_button.configure(state = "disabled")

kwarg_size_x_var = StringVar(value="NULL") # -size-file
kwarg_size_y_var = StringVar(value="NULL")
kwarg_size_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.SIZE)
kwarg_size_x_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_size_x_var)
kwarg_size_y_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_size_y_var)
kwarg_size_connect_label = Label(kwargs_LabelFrame,text="x")
kwarg_size_label.grid(row=4,column=0)
kwarg_size_x_entry.grid(row=4,column=1)
kwarg_size_connect_label.grid(row=4,column=2)
kwarg_size_y_entry.grid(row=4,column=3)
kwarg_size_x_entry.configure(state = "disabled")
kwarg_size_connect_label.configure(state = "disabled")
kwarg_size_y_entry.configure(state = "disabled")

kwarg_lfdaot_frame_speed_var = StringVar(value="60.0") # -lfdaot-frame-speed
kwarg_lfdaot_frame_speed_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.LFDAOT_FRAME_SPEED)
kwarg_lfdaot_frame_speed_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_lfdaot_frame_speed_var)
kwarg_lfdaot_frame_speed_label.grid(row=5,column=0)
kwarg_lfdaot_frame_speed_entry.grid(row=5,column=1)
kwarg_lfdaot_frame_speed_entry.configure(state = "disabled")

kwarg_render_range_more_scale_var = StringVar(value="2.0") # -render-range-more-scale
kwarg_render_range_more_scale_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.RENDER_RANGE_MORE_SCALE)
kwarg_render_range_more_scale_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_render_range_more_scale_var)
kwarg_render_range_more_scale_label.grid(row=6,column=0)
kwarg_render_range_more_scale_entry.grid(row=6,column=1)
kwarg_render_range_more_scale_entry.configure(state = "disabled")

kwarg_extend_var = StringVar(value="") # -extend
kwarg_extend_label = Label(kwargs_LabelFrame,text=TEXT.KWARGS.EXTEND)
kwarg_extend_entry = Entry(kwargs_LabelFrame,textvariable=kwarg_extend_var)
kwarg_extend_button = Button(kwargs_LabelFrame,text=TEXT.FILE_INPUT_FILEDIALOG_BUTTON_TEXT,command=kwarg_extend_file_choose_callback)
kwarg_extend_label.grid(row=7,column=0)
kwarg_extend_entry.grid(row=7,column=1)
kwarg_extend_button.grid(row=7,column=2,columnspan=100,sticky="w")

Launch_Button = Button(root,text=TEXT.LAUNCH_BUTTON_TEXT,command=Launch)
Launch_Button.grid(row=3,column=0,columnspan=5000,padx=12,pady=5,sticky="w")

root.update()
hook_dropfiles_first(root.winfo_id(),lambda file:([file_input_entry.delete(0,"end"),file_input_entry.insert(0,file)] if isfile(file) else None))
root.deiconify()
root.mainloop()