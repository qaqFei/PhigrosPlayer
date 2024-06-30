from PIL import Image
from sys import argv

Resource_Path = "./Resources" if "-res" not in argv else argv[argv.index("-res") + 1]

def open(fp:str, *args, **kwargs): # try load res from user
    fp_user = fp.replace("./Resources", Resource_Path)
    try:
        return Image._open(fp_user, *args, **kwargs) # change the function at Main.py
    except Exception:
        return Image._open(fp, *args, **kwargs)