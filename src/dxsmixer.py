from __future__ import annotations

import typing
import time

import pywintypes

import dxsound
import tool_funcs
import tempdir

temp_dir = tempdir.createTempDir()

class musicCls:
    def __init__(self):
        self.dxs = None
        self.buffer = None
        self._position = 0
        self._lflag = 0
        self._volume = 1.0
    
    def _stopBuffer(self) -> None:
        if self.buffer is None: return
        
        try:
            self.buffer.Stop()
        except pywintypes.error as e:
            if e.winerror != -2147024890: # pywintypes.error: (-2147024890, 'Stop', '句柄无效。')
                raise e

    def _setBufferVolume(self, v: float) -> None:
        if self.buffer is None: return
        self.buffer.SetVolume(self.dxs.transform_volume(v))
    
    def load(self, fp: str) -> None:
        self.dxs = dxsound.directSound(dxsound.loadFile2Loadable(temp_dir, fp), enable_cache=False)
        self.buffer = None
        
    def unload(self) -> None:
        self.dxs = None
        self.buffer = None
        
    def play(self, isloop: typing.Literal[0, -1] = 0) -> None:
        self.lflag = 0 if isloop == 0 else 1
        
        if self.buffer is None:
            _, self.buffer = self.dxs.create(self.lflag)
            
        else:
            self._stopBuffer()
            self.buffer.Play(self.lflag)
            self.set_pos(0.0)
            
        self._setBufferVolume(self._volume)
        
    def stop(self) -> None:
        self._stopBuffer()
        self._position = 0
        
    def pause(self) -> None:
        self._position = self.buffer.GetCurrentPosition()
        self._stopBuffer()
        
    def unpause(self) -> None:
        self.buffer.Play(self.lflag)
        self.buffer.SetCurrentPosition(self._position)
    
    @tool_funcs.NoJoinThreadFunc
    def fadeout(self, t: int) -> None:
        t /= 1000
        st = time.time()
        
        while time.time() - st < t and self.buffer.GetStatus() != 0:
            p = (time.time() - st) / t
            p = max(0.0, min(1.0, p))
            self.set_volume(1.0 - p)
            time.sleep(1 / 30)
        
        self.stop()
        self.set_volume(1.0)
    
    def set_volume(self, volume: float) -> None:
        self._volume = volume
        self._setBufferVolume(volume)
        
    def get_volume(self) -> float:
        return self._volume
    
    def get_busy(self) -> bool:
        return self.buffer.GetStatus() != 0
    
    def set_pos(self, pos: float) -> None:
        self._position = int(pos * self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec)
        self.buffer.SetCurrentPosition(self._position)
        
    def get_pos(self) -> int:
        return self.buffer.GetCurrentPosition()[1] / self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec
    
    def get_length(self) -> float:
        return self.dxs._sdesc.dwBufferBytes / self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec
    
class mixerCls:
    def __init__(self):
        self.music = musicCls()
        
    def init(
        frequency: int = 44100,
        size: int = -16,
        channels: int = 2,
        buffer: int = 512,
        devicename: typing.Optional[str] = None,
        allowedchanges: int = 5,
    ) -> None: ...
    
    def Sound(self, fp: str):
        music = musicCls()
        music.load(fp)
        return music
    
mixer = mixerCls()
