import io
import typing

from PIL import Image

_open = Image.open

def open_hook(*args, **kwargs):
    args = list(args)
    
    if isinstance(args[0], typing.IO):
        byteData = args[0].read()
        args[0] = io.BytesIO(byteData)
        
    elif isinstance(args[0], str):
        with open(args[0], "rb") as f:
            byteData = f.read()
            args[0] = io.BytesIO(byteData)
            
    elif isinstance(args[0], bytes):
        byteData = args[0]
        args[0] = io.BytesIO(byteData)
    
    else:
        raise TypeError("Unsupported type for image loading")

    im = _open(*args, **kwargs)
    im.byteData = byteData
    return im

Image.open = open_hook