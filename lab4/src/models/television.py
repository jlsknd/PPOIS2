"""
Модуль с классом Television - основной класс телевизора.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from .screen import Screen
from .audio import AudioSystem
from .specs import TechnicalSpecifications


class TvSource(Enum):
    OFF = "выключен"
    TV = "кабельное ТВ"
    SMART_TV = "Smart TV"


class Channel:
    def __init__(self, number: int, name: str, genre: str = "общий"):
        self.number = number
        self.name = name
        self.genre = genre
    
    def __str__(self) -> str:
        return f"{self.number}. {self.name} ({self.genre})"


class ChannelList:
    _channels: List[Channel] = [
        Channel(1, "Первый канал", "общий"), Channel(2, "Беларусь 1", "общий"), Channel(3, "НТВ", "новости"),
        Channel(4, "СТС", "развлекательный"), Channel(5, "ТНТ", "развлекательный"), Channel(6, "Карусель", "детский"),
        Channel(7, "2х2","развлекательный"), Channel(8, "Детский", "детский"), Channel(9, "СТК", "новости"),
        Channel(10, "Пятница", "развлекательный"), Channel(11, "Беларусь 2", "общий"), Channel(12, "Мир", "новости"),
        Channel(13, "Disney", "детский"), Channel(14, "Animal Planet", "познавательный"), Channel(15, "Discovery", "познавательный"),
        Channel(16, "МузТВ", "музыка"), Channel(17, "Рен ТВ", "общий"), Channel(18, "Домашний", "женский" )
    ]
    
    @classmethod
    def get_all(cls) -> List[Channel]:
        return cls._channels.copy()
    
    @classmethod
    def get_by_number(cls, number: int) -> Optional[Channel]:
        for ch in cls._channels:
            if ch.number == number:
                return ch
        return None
    
    @classmethod
    def get_numbers(cls) -> List[int]:
        return [ch.number for ch in cls._channels]


class Television:
    def __init__(self, specs: TechnicalSpecifications, name: str = "Мой телевизор") -> None:
        self.name = name
        self.specs = specs
        
        self._is_on: bool = False
        self._current_source: TvSource = TvSource.OFF
        self._current_channel: int = 1
        self._wifi_enabled: bool = False
        self._bluetooth_enabled: bool = False
        self._hdmi_devices: Dict[int, str] = {}
    
    @property
    def is_on(self) -> bool:
        return self._is_on
    
    @property
    def screen(self) -> Screen:
        return self.specs.screen
    
    @property
    def audio(self) -> AudioSystem:
        return self.specs.audio
    
    def _check_powered(self, action: str) -> None:
        if not self._is_on:
            raise RuntimeError(f"Сначала включите телевизор")
    
    def _check_tv_mode(self, action: str = "переключение канала") -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        if self._current_source != TvSource.TV:
            raise RuntimeError(f"Действие '{action}' доступно только в режиме ТВ")
    
    def turn_on(self) -> None:
        if self._is_on:
            raise RuntimeError("Телевизор уже включен")
        self._is_on = True
        self._current_source = TvSource.TV
    
    def turn_off(self) -> None:
        if not self._is_on:
            raise RuntimeError("Телевизор уже выключен")
        self._is_on = False
        self._current_source = TvSource.OFF
    
    def switch_to_tv(self) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self._current_source = TvSource.TV
    
    def switch_to_smart_tv(self) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        if not self.specs.has_smart_tv:
            raise RuntimeError("Данная модель не поддерживает Smart TV")
        self._current_source = TvSource.SMART_TV
    
    def set_channel(self, channel: int) -> Channel:
        self._check_tv_mode("установка канала")
        ch = ChannelList.get_by_number(channel)
        if not ch:
            nums = ChannelList.get_numbers()
            raise ValueError(f"Канал {channel} не существует. Доступны: {min(nums)}-{max(nums)}")
        self._current_channel = channel
        return ch
    
    def next_channel(self) -> Optional[Channel]:
        self._check_tv_mode("переключение канала")
        channels = ChannelList.get_numbers()
        
        if not channels:
            return None
        
        try:
            current_index = channels.index(self._current_channel)
        except ValueError:
            self._current_channel = channels[0]
            return ChannelList.get_by_number(channels[0])
        
        next_index = (current_index + 1) % len(channels)
        next_channel_num = channels[next_index]
        self._current_channel = next_channel_num
        return ChannelList.get_by_number(next_channel_num)
    
    def prev_channel(self) -> Optional[Channel]:
        self._check_tv_mode("переключение канала")
        channels = ChannelList.get_numbers()
        
        if not channels:
            return None
        
        try:
            current_index = channels.index(self._current_channel)
        except ValueError:
            self._current_channel = channels[-1]
            return ChannelList.get_by_number(channels[-1])
        
        prev_index = (current_index - 1 + len(channels)) % len(channels)
        prev_channel_num = channels[prev_index]
        self._current_channel = prev_channel_num
        return ChannelList.get_by_number(prev_channel_num)
    
    def set_brightness(self, value: int) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.screen.brightness = value
    
    def set_contrast(self, value: int) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.screen.contrast = value
    
    def set_volume(self, value: int) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.audio.volume = value
    
    def volume_up(self, step: int = 5) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.audio.volume_up(step)
    
    def volume_down(self, step: int = 5) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.audio.volume_down(step)
    
    def mute(self) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.audio.mute()
    
    def set_equalizer(self, low: int, mid: int, high: int) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.audio.equalizer.set_all(low, mid, high)
    
    def connect_subwoofer(self, connected: bool = True) -> None:
        if not self._is_on:
            raise RuntimeError("Сначала включите телевизор")
        self.audio.connect_subwoofer(connected)
    
    def enable_wifi(self) -> None:
        if not self.specs.has_wifi:
            raise RuntimeError("Данная модель не поддерживает Wi-Fi")
        self._wifi_enabled = True
    
    def disable_wifi(self) -> None:
        self._wifi_enabled = False
    
    def enable_bluetooth(self) -> None:
        if not self.specs.has_bluetooth:
            raise RuntimeError("Данная модель не поддерживает Bluetooth")
        self._bluetooth_enabled = True
    
    def disable_bluetooth(self) -> None:
        self._bluetooth_enabled = False
    
    def update_software(self) -> str:
        if not self._is_on:
            raise RuntimeError("Для обновления ПО включите телевизор")
        if not self.specs.has_smart_tv:
            return "Телевизор не имеет Smart TV, обновление ПО недоступно"
        return self.specs.update_software()
    
    def get_status(self) -> Dict[str, Any]:
        channel_info = None
        if self._is_on and self._current_source == TvSource.TV:
            ch = ChannelList.get_by_number(self._current_channel)
            if ch:
                channel_info = {"number": ch.number, "name": ch.name, "genre": ch.genre}
        
        #  получение значения source
        source_value = self._current_source.value if hasattr(self._current_source, 'value') else str(self._current_source)
        
        #  получение значения ОС
        os_value = self.specs.operating_system.value if hasattr(self.specs.operating_system, 'value') else str(self.specs.operating_system)
        
        return {
            "name": self.name,
            "power": "включен" if self._is_on else "выключен",
            "source": source_value,
            "current_channel": channel_info,
            "screen": {"brightness": self.screen.brightness, "contrast": self.screen.contrast},
            "audio": {
                "volume": self.audio.volume,
                "subwoofer": self.audio.subwoofer_connected,
                "equalizer": self.audio.equalizer.get_all()
            },
            "wifi": {"supported": self.specs.has_wifi, "enabled": self._wifi_enabled},
            "bluetooth": {"supported": self.specs.has_bluetooth, "enabled": self._bluetooth_enabled},
            "smart_tv": {
                "supported": self.specs.has_smart_tv,
                "os": os_value,
                "version": self.specs.os_version if self.specs.has_smart_tv else None
            }
        }