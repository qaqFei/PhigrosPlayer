#phi score manager
import typing

psm_event_type = typing.Literal["bad","miss","good","perfect"]

class Manager:
    def __init__(self,note_num) -> None:
        if not isinstance(note_num,int):
            raise TypeError("note_num must be int.")
        self._num = note_num
        self._events = []
    
    def add_event(self,state:psm_event_type):
        if not isinstance(state,str):
            raise TypeError("state must be str.")
        if state not in ["bad","miss","good","perfect"]:
            raise ValueError("state must be 'bad','miss','good','perfect'.")
        self._events.append(state)
    
    def _get_max_combo(self) -> int:
        max_combo = 0
        now_combo = 0
        for event in self._events:
            if event == "good" or event == "perfect":
                now_combo += 1
                if now_combo > max_combo:
                    max_combo = now_combo
            else:
                now_combo = 0
        return max_combo
    
    def get_combo(self) -> int:
        combo = 0
        for event in self._events[::-1]:
            if event == "good" or event == "perfect":
                combo += 1
            else:
                return combo
        return combo
    
    def get_score(self) -> float:
        acc_score = self._events.count("perfect") + self._events.count("good") * 0.685
        acc_score /= self._num
        acc_score *= 100_0000
        combo_score = self._get_max_combo() / self._num
        combo_score *= 100_0000
        return acc_score * 0.9 + combo_score * 0.1
    
    def get_stringscore(self,score:float) -> str:
        score_integer = int(score + 0.5)
        return f"{score_integer:>7}".replace(" ","0")
    
    def get_judgeLine_color(self) -> str:
        if "bad" not in self._events and "miss" not in self._events:
            if "good" in self._events:
                return "#a2eeff"
            else:
                return "#feffa9"
        else:
            return "#FFFFFF"