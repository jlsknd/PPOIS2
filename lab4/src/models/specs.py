"""
Модуль с классом TechnicalSpecifications - технические характеристики телевизора.
"""
from enum import Enum
from typing import Tuple, Optional
from .screen import Screen
from .audio import AudioSystem


class OperatingSystem(Enum):
    """Операционная система"""
    NONE = "отсутствует"
    ANDROID_TV = "Android TV"
    VIDAA = "VIDAA"
    WEBOS = "WebOS"
    TIZEN = "Tizen"
    YANDEX_TV = "Яндекс ТВ"
    SALUT_TV = "Салют ТВ"


class TechnicalSpecifications:
    """Технические характеристики телевизора"""
    
    def __init__(
        self,
        model_name: str,
        screen: Screen,
        audio: AudioSystem,
        has_dvb_s: bool = False,
        has_dvb_s2: bool = False,
        has_dvb_t: bool = True,
        has_dvb_t2: bool = True,
        has_dvb_c: bool = False,
        has_dvb_c2: bool = False,
        hdmi_ports: int = 3,
        usb_ports: int = 2,
        lan_ports: int = 1,
        antenna_inputs: int = 1,
        composite_inputs: int = 0,
        color: str = "черный",
        weight_kg: float = 15.0,
        dimensions: Tuple[float, float, float] = (1000, 600, 250),
        vesa_mount: Tuple[int, int] = (200, 200),
        aspect_ratio: Tuple[int, int] = (16, 9),
        service_life_years: int = 10,
        has_wifi: bool = True,
        has_bluetooth: bool = True,
        has_smart_tv: bool = True,
        operating_system: OperatingSystem = OperatingSystem.ANDROID_TV,
        current_os_version: str = "1.0"
    ) -> None:
        self.model_name = model_name
        self.screen = screen
        self.audio = audio
        
        self.has_dvb_s = has_dvb_s
        self.has_dvb_s2 = has_dvb_s2
        self.has_dvb_t = has_dvb_t
        self.has_dvb_t2 = has_dvb_t2
        self.has_dvb_c = has_dvb_c
        self.has_dvb_c2 = has_dvb_c2
        
        self.hdmi_ports = hdmi_ports
        self.usb_ports = usb_ports
        self.lan_ports = lan_ports
        self.antenna_inputs = antenna_inputs
        self.composite_inputs = composite_inputs
        
        self.color = color
        self.weight_kg = weight_kg
        self.dimensions = dimensions
        self.vesa_mount = vesa_mount
        self.aspect_ratio = aspect_ratio
        self.service_life_years = service_life_years
        
        self.has_wifi = has_wifi
        self.has_bluetooth = has_bluetooth
        self.has_smart_tv = has_smart_tv
        self.operating_system = operating_system
        
        if has_smart_tv:
            self._current_os_version = current_os_version
            self._original_major_version = self._get_major_version()
            self._original_version = float(current_os_version)
        else:
            self._current_os_version = "0.0"
            self._original_major_version = 0
            self._original_version = 0.0
    
    def _get_major_version(self) -> int:
        try:
            return int(self._current_os_version.split('.')[0])
        except (ValueError, IndexError):
            return 1
    
    def _get_minor_version(self) -> int:
        if not self.has_smart_tv:
            return 0
        try:
            parts = self._current_os_version.split('.')
            if len(parts) >= 2:
                return int(parts[1])
            return 0
        except (ValueError, IndexError):
            return 0
    
    @property
    def os_version(self) -> str:
        return self._current_os_version
    
    def update_software(self) -> str:
        """
        Обновляет ПО. Увеличивает версию на 0.1.
        Если версия достигла исходной + 1.0, сообщает об актуальности.
        
        Returns:
            str: Новая версия или сообщение об актуальности
        """
        if not self.has_smart_tv:
            return "Телевизор не имеет Smart TV, обновление ПО недоступно"
        
        current = float(self._current_os_version)
        max_version = self._original_version + 1.0
        
        if current >= max_version:
            return f"Версия {self._current_os_version} актуальна"
        
        new_version = round(current + 0.1, 1)
        self._current_os_version = f"{new_version:.1f}"
        return self._current_os_version
    
    def __str__(self) -> str:
        return (f"{self.model_name} | Экран: {self.screen.technology.value}, "
                f"{self.screen.diagonal}\" | Аудио: {self.audio.speakers_count}x{self.audio.speaker_power_w}Вт")