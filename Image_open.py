from PIL import Image
from sys import argv

_open = Image.open
Resource_Path = "./Resources" if "--res" not in argv else argv[argv.index("-res") + 1]

def open(fp, *args, **kwargs): # try load res from user
    if isinstance(fp, str):
        fp_user = fp.replace("./Resources", Resource_Path)
        try:
            return _open(fp_user, *args, **kwargs) # change the function at Main.py
        except Exception:
            return _open(fp, *args, **kwargs)
    else:
        return _open(fp, *args, **kwargs)