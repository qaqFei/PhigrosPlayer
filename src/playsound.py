from __future__ import annotations

import math
from struct import unpack

import win32comext.directsound.directsound as ds
import win32event as w32e
from pywintypes import WAVEFORMATEX

CACHE_BUFFER_MAXSIZE = 512
_VOLUME_MIN = -10000
_VOLUME_MAX = 0

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
    def __init__(self, data: bytes):
        self._hdr = data[0:44]
        self._bufdata = data[44:]
        self._sdesc = ds.DSBUFFERDESC()
        self._sdesc.dwBufferBytes, self._sdesc.lpwfxFormat = _wav_header_unpack(self._hdr)
        self._sdesc.dwFlags = ds.DSBCAPS_CTRLVOLUME | ds.DSBCAPS_CTRLPOSITIONNOTIFY | ds.DSBCAPS_GLOBALFOCUS
        self.dxs = ds.DirectSoundCreate(None, None)
        self.dxs.SetCooperativeLevel(None, ds.DSSCL_PRIORITY)
        
        self._volume = 0 # -10000 ~ 0
        self._buffers = []
        
        self._volume = _VOLUME_MIN
        self._create()
        self._volume = _VOLUME_MAX
        
    def _create(self):
        if len(self._buffers) > CACHE_BUFFER_MAXSIZE:
            self._buffers = self._buffers[:CACHE_BUFFER_MAXSIZE]
        
        if self._buffers:
            for e, buf in self._buffers:
                if buf.GetStatus() == 0:
                    buf.Play(0)
                    return e, buf
        
        event = w32e.CreateEvent(None, 0, 0, None)
        
        buffer = self.dxs.CreateSoundBuffer(self._sdesc, None)
        buffer.QueryInterface(ds.IID_IDirectSoundNotify).SetNotificationPositions((-1, event))
        buffer.Update(0, self._bufdata)
        buffer.SetVolume(self._volume)
        buffer.Play(0)
        self._buffers.append((event, buffer))
        return event, buffer
    
    def set_volume(self, v: float):
        self._volume = int(-10000 if v <= 1e-5 else (0 if v >= 1.0 else 2000 * math.log10(v)))
    
    def play(self, wait: bool = False):
        event, buffer = self._create()
        buffer.Play(0)
        
        if wait:
            w32e.WaitForSingleObject(event, -1)