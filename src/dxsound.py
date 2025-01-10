from __future__ import annotations

import math
import typing
from struct import unpack

import win32comext.directsound.directsound as ds
import win32event as w32e
from pywintypes import WAVEFORMATEX
from pydub import AudioSegment

CACHE_BUFFER_MAXSIZE = 128
PRE_CACHE_SIZE = 16

def _wav_header_unpack(data):
    (
        format,
        nchannels,
        samplespersecond,
        datarate,
        blockalign,
        bitspersample,
        data,
        datalength
    ) = unpack("<4sl4s4slhhllhh4sl", data)[5:]
    wfx = WAVEFORMATEX()
    wfx.wFormatTag = format
    wfx.nChannels = nchannels
    wfx.nSamplesPerSec = samplespersecond
    wfx.nAvgBytesPerSec = datarate
    wfx.nBlockAlign = blockalign
    wfx.wBitsPerSample = bitspersample
    return datalength, wfx

class directSound:
    def __init__(self, data: bytes, enable_cache: bool = True):
        self._hdr = data[0:44]
        self._bufdata = data[44:]
        self._sdesc = ds.DSBUFFERDESC()
        self._sdesc.dwBufferBytes, self._sdesc.lpwfxFormat = _wav_header_unpack(self._hdr)
        self._sdesc.dwFlags = ds.DSBCAPS_CTRLVOLUME | ds.DSBCAPS_CTRLPOSITIONNOTIFY | ds.DSBCAPS_GLOBALFOCUS
        self.dxs = ds.DirectSoundCreate(None, None)
        self.dxs.SetCooperativeLevel(None, ds.DSSCL_PRIORITY)
        
        self._enable_cache = enable_cache
        self._volume = 0 # -10000 ~ 0
        self._buffers = []
        
        if self._enable_cache:
            self.set_volume(0.0)
            for _ in range(PRE_CACHE_SIZE): self.play()
            self.set_volume(1.0)
    
    def create(self, playMethod: typing.Literal[0, 1]):
        if self._enable_cache:
            if len(self._buffers) > CACHE_BUFFER_MAXSIZE:
                for i in reversed(self._buffers):
                    e, buf = i
                    if buf.GetStatus() == 0:
                        self._buffers.remove(i)
                        break
            
            if self._buffers:
                for e, buf in self._buffers:
                    if buf.GetStatus() == 0:
                        buf.SetVolume(self._volume)
                        buf.SetCurrentPosition(0)
                        buf.Play(playMethod)
                        return e, buf
        
        event = w32e.CreateEvent(None, 0, 0, None)
        buffer = self.dxs.CreateSoundBuffer(self._sdesc, None)
        buffer.QueryInterface(ds.IID_IDirectSoundNotify).SetNotificationPositions((-1, event))
        buffer.Update(0, self._bufdata)
        buffer.SetVolume(self._volume)
        buffer.Play(playMethod)
        if self._enable_cache:
            self._buffers.append((event, buffer))
        return event, buffer
    
    def transform_volume(self, v: float):
        return int(-10000 if v <= 1e-5 else (0 if v >= 1.0 else 2000 * math.log10(v)))
    
    def set_volume(self, v: float):
        self._volume = self.transform_volume(v)
    
    def play(self, wait: bool = False, playMethod: typing.Literal[0, 1] = 0):
        event, buffer = self.create(playMethod)
        
        if wait:
            w32e.WaitForSingleObject(event, -1)
        
        return event, buffer

def loadFile2Loadable(temp_dir: str, path: str):
    try:
        seg: AudioSegment = AudioSegment.from_file(path)
        fp = f"{temp_dir}/{hash(path)}.wav"
        seg.export(fp, format="wav")
        return open(fp, "rb").read()
    except FileNotFoundError as e:
        print(temp_dir, path, repr(e))
