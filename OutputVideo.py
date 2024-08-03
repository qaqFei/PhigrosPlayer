from sys import argv
from os import system
from ctypes import windll
from os import chdir
from os.path import exists,abspath,dirname,isfile
from sys import argv
from tempfile import gettempdir
from time import time
from random import randint

if len(argv) < 4:
    print("Usage: OutputVideo <chart> <video-file-path> [--fps <fps>]")
    windll.kernel32.ExitProcess(1)

chart = argv[1]
videofilepath = argv[2]
lfdaottemppath = f"{gettempdir()}\\qfppr_outputvideo_{time() * randint(0, 2 << 31)}.lfdaot"
fps = 120 if "--fps" not in argv else argv[argv.index("--fps") + 1]

selfdir = dirname(argv[0])
if selfdir == "": selfdir = abspath(".")
chdir(selfdir)

def invfile(fp):
    return exists(fp) and isfile(fp)

main = ".\\Main.exe" if invfile(".\\Main.exe") else (".\\Main.py" if invfile(".\\Main.py") else [print("Can't find Main.exe or Main.py"), windll.kernel32.ExitProcess(1)])

while not exists(lfdaottemppath):
    system(f"{main} \"{chart}\" --lfdaot --lfdaot-file-savefp \"{lfdaottemppath}\" --lfdaot-frame-speed \"{fps}\" --lfdaot-file-output-autoexit --fullscreen") # create lfdaot file
system(f"{main} \"{chart}\" --lfdaot --lfdaot-file \"{lfdaottemppath}\" --lfdaot-render-video --lfdaot-render-video-savefp \"{videofilepath}\" --fullscreen") # create video file

system(f"del \"{lfdaottemppath}\"")