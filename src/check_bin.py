import fix_workpath as _
import init_logging as _

import logging
import pydub.utils
from os import popen
from os.path import exists, isfile

vaildfile = lambda x: exists(x) and isfile(x)

win_7z = vaildfile("./7z.exe") and vaildfile("./7z.dll")
unix_7z = vaildfile("./7z")
if not (win_7z or unix_7z):
    logging.fatal("7z Not Found")
    raise SystemExit

hasprogram = lambda name: pydub.utils.which(name) is not None
if not (hasprogram("avconv") or hasprogram("ffmpeg")):
    logging.warning("cannot find avconv or ffmpeg, unzip ...")
    
    if not vaildfile("./resources/pydub-ff.7z"):
        logging.fatal("resources/pydub-ff.7z Not Found")
        raise SystemExit
    
    popen("7z.exe x resources/pydub-ff.7z -y").read()
