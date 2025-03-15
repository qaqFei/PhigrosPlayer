import threading

class RangeLock:
    def __init__(self):
        self.locks: dict[tuple[int, int], threading.Lock] = {}
        self._aquired: dict[tuple[int, int], list[threading.Lock]] = {}
    
    def aquire(self, start: int, end: int):
        k = (start, end)
        aqed: list[threading.Lock] = []
        
        for r, l in self.locks.copy().items():
            if (
                start <= r[0] <= end <= r[1]
                or r[0] <= start <= r[1] <= end
                or start <= r[0] <= r[1] <= end
                or r[0] <= start <= end <= r[1]
            ):
                l.acquire()
                aqed.append(l)
        
        if k not in self.locks:
            self.locks[k] = threading.Lock()
            self.locks[k].acquire()
            aqed.append(self.locks[k])
        
        if k not in self._aquired:
            self._aquired[k] = aqed
        else:
            self._aquired[k].extend(aqed)
    
    def release(self, start: int, end: int):
        for l in self._aquired.pop((start, end)):
            l.release()
