"""
Модуль с классом AudioSystem - звуковая система телевизора.
"""
from typing import Dict, Optional


class Equalizer:
    """Класс эквалайзера"""
    
    def __init__(self, low: int = 0, mid: int = 0, high: int = 0) -> None:
        self._low = 0
        self._mid = 0
        self._high = 0
        self.set_all(low, mid, high)
    
    @property
    def low(self) -> int:
        return self._low
    
    @low.setter
    def low(self, value: int) -> None:
        if not -100 <= value <= 100:
            raise ValueError("Низкие частоты должны быть от -100 до 100")
        self._low = value
    
    @property
    def mid(self) -> int:
        return self._mid
    
    @mid.setter
    def mid(self, value: int) -> None:
        if not -100 <= value <= 100:
            raise ValueError("Средние частоты должны быть от -100 до 100")
        self._mid = value
    
    @property
    def high(self) -> int:
        return self._high
    
    @high.setter
    def high(self, value: int) -> None:
        if not -100 <= value <= 100:
            raise ValueError("Высокие частоты должны быть от -100 до 100")
        self._high = value
    
    def set_all(self, low: int, mid: int, high: int) -> None:
        self.low = low
        self.mid = mid
        self.high = high
    
    def get_all(self) -> Dict[str, int]:
        return {"low": self._low, "mid": self._mid, "high": self._high}
    
    def __str__(self) -> str:
        return f"НЧ: {self._low}, СЧ: {self._mid}, ВЧ: {self._high}"


class AudioSystem:
    """Класс звуковой системы телевизора"""
    
    def __init__(
        self,
        speakers_count: int = 2,
        speaker_power_w: float = 10.0,
        has_subwoofer_output: bool = False,
        volume: int = 30,
        equalizer: Optional[Equalizer] = None
    ) -> None:
        self.speakers_count = speakers_count
        self.speaker_power_w = speaker_power_w
        self.has_subwoofer_output = has_subwoofer_output
        self._subwoofer_connected = False
        
        self._volume = max(0, min(100, volume))
        self.equalizer = equalizer or Equalizer()  #если объект не передан, создается новый 
    
    @property
    def volume(self) -> int:
        return self._volume
    
    @volume.setter
    def volume(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError("Громкость должна быть от 0 до 100")
        self._volume = value
    
    def volume_up(self, step: int = 5) -> None:
        self._volume = min(100, self._volume + step)
    
    def volume_down(self, step: int = 5) -> None:
        self._volume = max(0, self._volume - step)
    
    def mute(self) -> None:
        self._volume = 0
    
    @property
    def subwoofer_connected(self) -> bool:
        return self._subwoofer_connected
    
    def connect_subwoofer(self, connected: bool = True) -> None:
        if not self.has_subwoofer_output:
            raise ValueError("Данная модель не поддерживает подключение сабвуфера")
        self._subwoofer_connected = connected
    
    def get_total_power(self) -> float:
        return self.speakers_count * self.speaker_power_w
    
    def __str__(self) -> str:
        sub_status = "OK. подключен" if self._subwoofer_connected else "Hе подключен!!!"
        return (f"Громкость: {self._volume}, Динамики: {self.speakers_count}x{self.speaker_power_w}Вт, "
                f"Сабвуфер: {sub_status}\nЭквалайзер: {self.equalizer}")
    
    def get_info(self) -> dict:
        return {
            "speakers_count": self.speakers_count,
            "speaker_power_w": self.speaker_power_w,
            "total_power_w": self.get_total_power(),
            "has_subwoofer_output": self.has_subwoofer_output,
            "subwoofer_connected": self._subwoofer_connected,
            "volume": self._volume,
            "equalizer": self.equalizer.get_all()
        }