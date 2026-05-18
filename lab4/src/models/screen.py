"""
Модуль с классом Screen - экран телевизора.
"""
from enum import Enum
from typing import Tuple, Optional


class ScreenTechnology(Enum):
    """Технология экрана"""
    LED = "LED"
    OLED = "OLED"
    QLED = "QLED"
    PDP = "PDP"
    LCD = "LCD"


class ScreenCoverage(Enum):
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


class Screen:
    """
    Класс, представляющий экран телевизора.
    Содержит все настройки изображения.
    """
    
    def __init__(
        self,
        technology: ScreenTechnology = ScreenTechnology.LED,
        diagonal: float = 42.0,
        resolution_width: int = 1080,
        resolution_height: int = 1920,
        response_time_ms: int = 5,
        coverage: ScreenCoverage = ScreenCoverage.ANTI_GLARE,
        refresh_rate_hz: int = 60,
        brightness_nits: int = 300,
        brightness_level: int = 50,
        contrast_level: int = 50
    ) -> None:
        self.technology = technology
        self.diagonal = diagonal
        self.resolution_width = resolution_width
        self.resolution_height = resolution_height
        self.response_time_ms = response_time_ms
        self.coverage = coverage
        self.refresh_rate_hz = refresh_rate_hz
        self.brightness_nits = brightness_nits
        
        self._brightness = max(0, min(100, brightness_level))
        self._contrast = max(0, min(100, contrast_level))
    
    @property
    def brightness(self) -> int:
        return self._brightness
    
    @brightness.setter
    def brightness(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError("Яркость должна быть от 0 до 100")
        self._brightness = value
    
    @property
    def contrast(self) -> int:
        return self._contrast
    
    @contrast.setter
    def contrast(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError("Контраст должен быть от 0 до 100")
        self._contrast = value
    
    def get_resolution(self) -> Tuple[int, int]:
        return (self.resolution_width, self.resolution_height)
    
    def get_resolution_standard(self) -> Resolution:
        if self.resolution_width >= 3840:
            return Resolution.ULTRA_HD_4K
        elif self.resolution_width >= 1920:
            return Resolution.FULL_HD
        else:
            return Resolution.HD
    
    def __str__(self) -> str:
        return (f"Экран: {self.technology.value}, {self.diagonal}\", "
                f"{self.resolution_width}x{self.resolution_height}, "
                f"яркость: {self._brightness}, контраст: {self._contrast}")
    
    def get_info(self) -> dict:
        return {
            "technology": self.technology.value,
            "diagonal": self.diagonal,
            "resolution": f"{self.resolution_width}x{self.resolution_height}",
            "response_time_ms": self.response_time_ms,
            "coverage": self.coverage.value,
            "refresh_rate_hz": self.refresh_rate_hz,
            "brightness_nits": self.brightness_nits,
            "current_brightness": self._brightness,
            "current_contrast": self._contrast
        }