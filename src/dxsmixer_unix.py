import typing
import time

from jnius import autoclass  # type: ignore

import tool_funcs

MediaPlayer = autoclass("android.media.MediaPlayer")

class musicCls:
    def __init__(self):
        self.dxs = None
        self.buffer = None
        
        self._lflag = 0
        self._volume = 1.0
        
        self._paused = False
        self._pause_pos = 0
        self._pause_volume = 0.0
        self.dxs = MediaPlayer()
    
    def load(self, fp: str):
        self.unload()
        if not self.dxs:
            self.dxs = MediaPlayer()
        self.dxs.setDataSource(fp)
        self.dxs.prepare()
        
    def unload(self):
        if self.dxs:
            self.dxs.release()
        self.dxs = None
        self.buffer = None
        self._paused = False
        
    def play(self, isloop: typing.Literal[0, -1] = 0):
        self.lflag = False if isloop == 0 else True
        self.dxs.setLooping(self.lflag)
        self.dxs.start()
        
    def stop(self):
        if self.dxs:
            self.dxs.stop()
        
    def pause(self):
        if self._paused: return
        self._paused = True
        
        if self.dxs:
            self.dxs.pause()
        
    def unpause(self):
        if not self._paused: return
        self._paused = False
        
        if self.dxs:
            self.dxs.start()
    
    @tool_funcs.NoJoinThreadFunc
    def fadeout(self, t: int):
        if self._paused: return
        t /= 1000.0
        st = time.time()
        rvol = self.get_volume()
        while time.time() - st < t and self.get_busy():
            p = (time.time() - st) / t
            p = max(0.0, min(1.0, p))
            self.set_volume(1.0 - p)
            time.sleep(1 / 15)
        self.set_volume(rvol)
        self.stop()
    
    def set_volume(self, volume: float):
        self._volume = volume
        if self.dxs:
            self.dxs.setVolume(float(volume), float(volume))
        
    def get_volume(self):
        return self._volume
    
    def get_busy(self) -> bool:
        if self.dxs:
            return self.dxs.isPlaying()
        return False
    
    def set_pos(self, pos: float):
        if self.dxs:
            self.dxs.seekTo(int(pos * 1000))
        
    def get_pos(self) -> float:
        if self.dxs:
            return self.dxs.getCurrentPosition() / 1000.0
    
    def get_length(self) -> float:
        if self.dxs:
            return self.dxs.getDuration() / 1000.0
    
class mixerCls:
    def __init__(self):
        self.music = musicCls()
        
    def init(*args, **kwargs) -> None: ...
    
    def Sound(self, fp: str):
        music = musicCls()
        music.load(fp)
        return music

mixer = mixerCls()
