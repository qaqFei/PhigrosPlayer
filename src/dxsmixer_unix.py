def toDowngradeAPI():
    from os import environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
    from pygame import mixer as _mixer
    
    _mixer.init()
    mixer = _mixer
    
    length = -1
    _load = mixer.music.load
    _get_pos = mixer.music.get_pos
    
    def _loadhook(fn: str):
        nonlocal length
        
        length = _mixer.Sound(fn).get_length()
        _load(fn)
        
    mixer.music.load = _loadhook
    mixer.music.get_length = lambda: length
    mixer.music.get_pos = lambda: _get_pos() / 1000
    
    return mixer

type musicCls = object
mixer = toDowngradeAPI()
