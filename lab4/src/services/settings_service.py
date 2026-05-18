"""
Сервис для управления настройками телевизора.
"""
from typing import Dict, Any, Optional
from src.models.television import Television, Resolution
from src.utils.exceptions import SettingsError


class SettingsService:
    """
    Сервис для управления настройками изображения и звука.
    """
    
    def __init__(self, television: Television):
        """
        Инициализация сервиса настроек.
        
        Args:
            television: Телевизор для управления
        """
        self.tv = television
    
    def get_picture_settings(self) -> Dict[str, Any]:
        """
        Возвращает текущие настройки изображения.
        
        Returns:
            Dict: Словарь с настройками изображения
        """
        return {
            "brightness": self.tv.picture_settings.brightness,
            "contrast": self.tv.picture_settings.contrast,
            "resolution": self.tv.picture_settings.resolution.value
        }
    
    def set_brightness(self, value: int) -> None:
        """
        Устанавливает яркость.
        
        Args:
            value: Значение яркости (0-100)
            
        Raises:
            SettingsError: При неверном значении
        """
        if not 0 <= value <= 100:
            raise SettingsError("Яркость должна быть от 0 до 100")
        
        self.tv.picture_settings.brightness = value
    
    def set_contrast(self, value: int) -> None:
        """
        Устанавливает контраст.
        
        Args:
            value: Значение контраста (0-100)
            
        Raises:
            SettingsError: При неверном значении
        """
        if not 0 <= value <= 100:
            raise SettingsError("Контраст должна быть от 0 до 100")
        
        self.tv.picture_settings.contrast = value
    
    def set_resolution(self, resolution: Resolution) -> None:
        """
        Устанавливает разрешение.
        
        Args:
            resolution: Разрешение из перечисления Resolution
        """
        self.tv.picture_settings.resolution = resolution
    
    def get_sound_settings(self) -> Dict[str, Any]:
        """
        Возвращает текущие настройки звука.
        
        Returns:
            Dict: Словарь с настройками звука
        """
        return {
            "volume": self.tv.sound_settings.volume,
            "subwoofer_connected": self.tv.sound_settings.subwoofer_connected,
            "equalizer": {
                "low": self.tv.sound_settings.equalizer.low,
                "mid": self.tv.sound_settings.equalizer.mid,
                "high": self.tv.sound_settings.equalizer.high
            }
        }
    
    def set_volume(self, value: int) -> None:
        """
        Устанавливает громкость.
        
        Args:
            value: Значение громкости (0-100)
            
        Raises:
            SettingsError: При неверном значении
        """
        if not 0 <= value <= 100:
            raise SettingsError("Громкость должна быть от 0 до 100")
        
        self.tv.sound_settings.volume = value
    
    def set_equalizer(self, low: int, mid: int, high: int) -> None:
        """
        Устанавливает настройки эквалайзера.
        
        Args:
            low: Низкие частоты (-100 до 100)
            mid: Средние частоты (-100 до 100)
            high: Высокие частоты (-100 до 100)
            
        Raises:
            SettingsError: При неверных значениях
        """
        if not all(-100 <= x <= 100 for x in [low, mid, high]):
            raise SettingsError("Все значения эквалайзера должны быть от -100 до 100")
        
        self.tv.sound_settings.equalizer.low = low
        self.tv.sound_settings.equalizer.mid = mid
        self.tv.sound_settings.equalizer.high = high
    
    def connect_subwoofer(self, connected: bool) -> None:
        """
        Подключает или отключает сабвуфер.
        
        Args:
            connected: True для подключения, False для отключения
        """
        self.tv.sound_settings.subwoofer_connected = connected