import tempfile
import os
import typing

from jnius import autoclass, cast # type: ignore

PythonActivity = autoclass("org.kivy.android.PythonActivity")
MediaPlayer = autoclass("android.media.MediaPlayer")
File = autoclass("java.io.File")
FileInputStream = autoclass("java.io.FileInputStream")
FileDescriptor = autoclass("java.io.FileDescriptor")

class directSound:
    def __init__(self, data: bytes | str, enable_cache: bool = True):
        self._is_temp_file = False
        
        if isinstance(data, str):
            self._file_path = data
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(data)
                self._file_path = f.name
                self._is_temp_file = True
                
        self._channels = 2
        self._sample_rate = 44100
        self._audio_format = 16
        self._enable_cache = enable_cache
        self._volume = 1.0  # 0.0 ~ 1.0
        self._media_player = MediaPlayer()
        self._sdesc = None
        fis = FileInputStream(self._file_path)
        fd = cast(FileDescriptor, fis.getFD())
        self._media_player.setDataSource(fd)
        self._media_player.prepare()
        fis.close()
    
    def getSampleRate(self):
        return self._sample_rate

    def getAudioChannels(self):
        return self._channels

    def getAudioFormat(self):
        return self._audio_format
    
    def set_volume(self, v: float):
        self._volume = max(0.0, min(1.0, v))
        if self._media_player is None:
            fis = FileInputStream(self._file_path)
            fd = cast(FileDescriptor, fis.getFD())
            self._media_player = MediaPlayer()
            self._media_player.setDataSource(fd)
            self._media_player.prepare()
            fis.close()
        self._media_player.setVolume(self._volume, self._volume)
    
    def play(self, wait: bool = False):
        if self._media_player is None:
            fis = FileInputStream(self._file_path)
            fd = cast(FileDescriptor, fis.getFD())
            self._media_player = MediaPlayer()
            self._media_player.setDataSource(fd)
            self._media_player.prepare()
            fis.close()
        self._media_player.start()
        if wait:
            while self._media_player.isPlaying():
                pass
        return self._media_player
    
    def create(self, playMethod: typing.Literal[0, 1] = 0):
        if self._media_player is None:
            self._media_player = MediaPlayer()
            fis = FileInputStream(self._file_path)
            fd = cast(FileDescriptor, fis.getFD())
            self._media_player.setDataSource(fd)
            self._media_player.prepare()
            fis.close()
        return (None, self._media_player)

    def stop(self):
        if self._media_player:
            self._media_player.stop()
            self._media_player.prepare()
    
    def release(self):
        if self._media_player is not None:
            self._media_player.release()
            self._media_player = None
        if self._is_temp_file:
            try:
                os.remove(self._file_path)
            except:
                pass