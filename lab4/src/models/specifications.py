"""
Модуль содержит класс TechnicalSpecifications для хранения технических характеристик телевизора.
"""
from enum import Enum
from typing import Optional, Tuple, List, Dict
import re


class ScreenTechnology(Enum):
    """Технология экрана"""
    LED = "LED"
    OLED = "OLED"
    QLED = "QLED"
    PDP = "PDP"
    LCD = "LCD"


class ScreenCoating(Enum):
    """Тип покрытия экрана"""
    GLOSSY = "глянцевое"
    SEMI_MATTE = "полуматовое"
    ANTI_GLARE = "антибликовое"
    ULTRA_ANTI_GLARE = "ультра-антибликовое"


class Resolution(Enum):
    """Стандартное разрешение экрана"""
    HD = "HD"
    FULL_HD = "Full HD"
    ULTRA_HD_4K = "4K Ultra HD"


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
    """
    Класс, представляющий технические характеристики телевизора.
    """
    
    def __init__(
        self,
        # Основные характеристики
        screen_technology: ScreenTechnology,
        model_name: str,
        screen_diagonal: float,  # в дюймах
        resolution_width: int,
        resolution_height: int,
        response_time_ms: int,  # время отклика в мс
        screen_coating: ScreenCoating,
        refresh_rate_hz: int,  # частота обновления
        # Тюнеры
        has_dvb_s: bool,
        has_dvb_s2: bool,
        has_dvb_t: bool,
        has_dvb_t2: bool,
        has_dvb_c: bool,
        has_dvb_c2: bool,
        # Аудио
        speakers_count: int,
        speaker_power_w: float,
        # Функции
        has_smart_tv: bool,
        has_wifi: bool,
        has_bluetooth: bool,
        # Разъемы
        antenna_input_count: int,
        hdmi_ports_count: int,
        usb_ports_count: int,
        lan_ports_count: int,
        composite_video_inputs: int,
        # Физические характеристики
        color: str,
        dimensions_without_stand: Tuple[float, float, float],  # x*y*z мм
        weight_kg: float,
        vesa_mount: Tuple[int, int],  # x*y мм
        aspect_ratio: Tuple[int, int],  # x:y
        service_life_years: int,
        brightness_nits: int,
        operating_system: OperatingSystem,
        has_audio_out_for_subwoofer: bool,
        current_os_version: str = "0.0"  # версия в формате X.Y, по умолчанию 0.0 если нет ОС
    ) -> None:
        self.screen_technology = screen_technology
        self.model_name = model_name
        self.screen_diagonal = screen_diagonal
        self.resolution_width = resolution_width
        self.resolution_height = resolution_height
        self.response_time_ms = response_time_ms
        self.screen_coating = screen_coating
        self.refresh_rate_hz = refresh_rate_hz
        
        # Тюнеры
        self.has_dvb_s = has_dvb_s
        self.has_dvb_s2 = has_dvb_s2
        self.has_dvb_t = has_dvb_t
        self.has_dvb_t2 = has_dvb_t2
        self.has_dvb_c = has_dvb_c
        self.has_dvb_c2 = has_dvb_c2
        
        # Аудио
        self.speakers_count = speakers_count
        self.speaker_power_w = speaker_power_w
        
        # Функции
        self.has_smart_tv = has_smart_tv
        self.has_wifi = has_wifi
        self.has_bluetooth = has_bluetooth
        
        # Разъемы
        self.antenna_input_count = antenna_input_count
        self.hdmi_ports_count = hdmi_ports_count
        self.usb_ports_count = usb_ports_count
        self.lan_ports_count = lan_ports_count
        self.composite_video_inputs = composite_video_inputs
        
        # Физические характеристики
        self.color = color
        self.dimensions_without_stand = dimensions_without_stand
        self.weight_kg = weight_kg
        self.vesa_mount = vesa_mount
        self.aspect_ratio = aspect_ratio
        self.service_life_years = service_life_years
        self.brightness_nits = brightness_nits
        self.operating_system = operating_system
        self.has_audio_out_for_subwoofer = has_audio_out_for_subwoofer
        
        # Версия ПО - только если есть Smart TV
        if not has_smart_tv:
            self._current_os_version = "0.0"
            self._original_major_version = 0
        else:
            self._current_os_version = current_os_version
            self._original_major_version = self._get_major_version()
    
    def _get_major_version(self) -> int:
        """Извлекает мажорную версию (число до точки)"""
        if not self.has_smart_tv:
            return 0
        try:
            return int(self._current_os_version.split('.')[0])
        except (ValueError, IndexError):
            return 12  # значение по умолчанию
    
    def _get_minor_version(self) -> int:
        """Извлекает минорную версию (число после точки)"""
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
    def current_os_version(self) -> str:
        """Текущая версия ОС"""
        return self._current_os_version
    
    @current_os_version.setter
    def current_os_version(self, value: str) -> None:
        """Сеттер для версии ОС с валидацией"""
        if not self.has_smart_tv:
            raise ValueError("Телевизор не имеет Smart TV, версия ОС отсутствует")
        
        if not value or not isinstance(value, str):
            raise ValueError("Версия ОС должна быть непустой строкой")
        
        # Проверяем формат X.Y
        pattern = r'^\d+\.\d+$'
        if not re.match(pattern, value):
            raise ValueError("Версия ОС должна быть в формате X.Y (например 12.2)")
        
        self._current_os_version = value
    
    def increment_version(self) -> str:
        """
        Увеличивает минорную версию на 0.1.
        Если минорная версия достигает 9, увеличивается мажорная.
        
        Returns:
            str: Новая версия или сообщение об актуальности
        """
        if not self.has_smart_tv:
            return "Телевизор не имеет Smart TV, обновление ПО недоступно"
        
        major = self._get_major_version()
        minor = self._get_minor_version()
        original_major = self._original_major_version
        
        # Проверяем, не превысила ли мажорная версия исходную + 1
        if major > original_major + 1:
            return f"Версия {self._current_os_version} актуальна"
        
        # Увеличиваем минорную версию
        minor += 1
        if minor >= 10:
            major += 1
            minor = 0
        
        new_version = f"{major}.{minor}"
        self._current_os_version = new_version
        return new_version
    
    def get_resolution(self) -> Tuple[int, int]:
        """Возвращает разрешение экрана как кортеж (ширина, высота)"""
        return (self.resolution_width, self.resolution_height)
    
    def get_resolution_standard(self) -> Resolution:
        """
        Определяет стандарт разрешения на основе размеров.
        Упрощенная логика для демонстрации.
        """
        if self.resolution_width >= 3840:
            return Resolution.ULTRA_HD_4K
        elif self.resolution_width >= 1920:
            return Resolution.FULL_HD
        else:
            return Resolution.HD
    
    def __str__(self) -> str:
        """Строковое представление для вывода информации"""
        smart_status = "Smart TV" if self.has_smart_tv else "обычный"
        return (
            f"{self.model_name} ({self.screen_technology.value}, "
            f"{self.screen_diagonal}\", {smart_status})"
        )