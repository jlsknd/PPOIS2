"""
Модуль с моделью телевизора.
"""

from typing import Dict, Optional, Tuple, Any, List
from enum import Enum
from dataclasses import dataclass, field

from ..exceptions.tv_exceptions import (
    TVNotPoweredError,
    SmartTVNotSupportedError,
    DeviceNotFoundError,
    PortNotFoundError,
    InvalidValueError,
    InvalidModeError
)
from ..utils.validators import (
    validate_range,
    validate_channel,
    validate_brightness,
    validate_contrast,
    validate_volume,
    validate_equalizer_value,
    validate_port,
    validate_positive_number,
    validate_non_negative_number,
    validate_string_not_empty
)


class ScreenTechnology(Enum):
    """Технология экрана."""
    LED = "LED"
    OLED = "OLED"
    QLED = "QLED"
    PDP = "PDP"
    LCD = "LCD"


class ScreenCoverage(Enum):
    """Покрытие экрана."""
    GLOSSY = "глянцевое"
    SEMI_MATTE = "полуматовое"
    ANTI_GLARE = "антибликовое"
    ULTRA_ANTI_GLARE = "ультра-антибликовое"


class OperatingSystem(Enum):
    """Операционная система."""
    ANDROID_TV = "Android TV"
    VIDAA = "VIDAA"
    WEBOS = "WebOS"
    TIZEN = "Tizen"
    YANDEX_TV = "Яндекс ТВ"
    SALUT_TV = "Салют ТВ"


class TVMode(Enum):
    """Режимы работы телевизора."""
    TV = "Кабельное ТВ"
    SMART_TV = "Smart TV"
    HDMI = "HDMI"


@dataclass
class TechnicalSpecifications:
    """Технические характеристики телевизора."""
    model_name: str
    technology: ScreenTechnology
    screen_diagonal: float  # дюймы
    resolution: Tuple[int, int]  # ширина x высота
    response_time: int  # мс
    screen_coverage: ScreenCoverage
    refresh_rate: int  # Гц
    speakers_count: int
    speaker_power: int  # Вт
    hdmi_ports: int
    usb_ports: int
    lan_ports: int
    has_wifi: bool
    has_bluetooth: bool
    has_smart_tv: bool
    color: str
    weight: float  # кг
    lifespan: int  # лет
    brightness_nit: int  # нит
    operating_system: Optional[OperatingSystem] = None
    os_version: Optional[str] = None
    
 
    
    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        validate_positive_number(self.screen_diagonal, "диагональ")
        validate_positive_number(self.response_time, "время отклика")
        validate_positive_number(self.refresh_rate, "частота обновления")
        validate_positive_number(self.speakers_count, "количество динамиков")
        validate_positive_number(self.speaker_power, "мощность динамиков")
        validate_non_negative_number(self.hdmi_ports, "количество HDMI портов")  # может быть 0
        validate_non_negative_number(self.usb_ports, "количество USB портов")
        validate_non_negative_number(self.lan_ports, "количество LAN портов")
        validate_positive_number(self.weight, "вес")
        validate_positive_number(self.lifespan, "срок службы")
        validate_positive_number(self.brightness_nit, "яркость")
        validate_string_not_empty(self.model_name, "название модели")
        validate_string_not_empty(self.color, "цвет")


class Television:
    """Класс, представляющий телевизор."""
    
    def __init__(self, specs: TechnicalSpecifications) -> None:
        """
        Инициализация телевизора.
        
        Args:
            specs: Технические характеристики
        """
        self.specs = specs
        self._is_on: bool = False
        self._mode: TVMode = TVMode.TV  # Текущий режим
        self._current_channel: int = 1
        self._brightness: int = 50
        self._contrast: int = 50
        self._volume: int = 30
        self._subwoofer_connected: bool = False
        self._equalizer: Dict[str, int] = {"high": 0, "mid": 0, "low": 0}
        self._wifi_enabled: bool = specs.has_wifi  # по умолчанию включен, если есть модуль
        self._bluetooth_enabled: bool = specs.has_bluetooth  # по умолчанию включен, если есть модуль
        self._network_connection: bool = False
        self._hdmi_devices: Dict[int, str] = {}
        self._current_hdmi_port: Optional[int] = None
        self._software_version: float = float(specs.os_version) if specs.os_version else 1.0
    
    @property
    def mode(self) -> TVMode:
        """Текущий режим работы."""
        return self._mode
    
    @property
    def is_on(self) -> bool:
        """Проверка, включен ли телевизор."""
        return self._is_on
    
    @property
    def current_channel(self) -> int:
        """Текущий канал."""
        return self._current_channel
    
    @property
    def software_version(self) -> float:
        """Текущая версия ПО."""
        return self._software_version
    
    # Методы проверки возможностей
    def can_connect_hdmi(self) -> bool:
        """Проверка, есть ли HDMI порты."""
        return self.specs.hdmi_ports > 0
    
    def can_use_wifi(self) -> bool:
        """Проверка, есть ли Wi-Fi."""
        return self.specs.has_wifi
    
    def can_use_bluetooth(self) -> bool:
        """Проверка, есть ли Bluetooth."""
        return self.specs.has_bluetooth
    
    def can_update_software(self) -> bool:
        """Проверка, можно ли обновить ПО (есть Smart TV)."""
        return self.specs.has_smart_tv
    
    # Методы для управления Wi-Fi и Bluetooth
    def toggle_wifi(self) -> bool:
        """
        Переключение состояния Wi-Fi.
        
        Returns:
            Новое состояние Wi-Fi
        """
        if not self.can_use_wifi():
            return False
        self._wifi_enabled = not self._wifi_enabled
        return self._wifi_enabled
    
    def get_wifi_status(self) -> bool:
        """Получение состояния Wi-Fi."""
        return self._wifi_enabled
    
    def toggle_bluetooth(self) -> bool:
        """
        Переключение состояния Bluetooth.
        
        Returns:
            Новое состояние Bluetooth
        """
        if not self.can_use_bluetooth():
            return False
        self._bluetooth_enabled = not self._bluetooth_enabled
        return self._bluetooth_enabled
    
    def get_bluetooth_status(self) -> bool:
        """Получение состояния Bluetooth."""
        return self._bluetooth_enabled
    
    def _check_powered(self, action: str) -> None:
        """
        Проверка, что телевизор включен.
        
        Args:
            action: Действие для сообщения об ошибке
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
        """
        if not self._is_on:
            raise TVNotPoweredError(action)
    
    def _check_tv_mode(self, action: str) -> None:
        """
        Проверка, что телевизор в режиме ТВ.
        
        Args:
            action: Действие для сообщения об ошибке
            
        Raises:
            InvalidModeError: Если не в режиме ТВ
        """
        if self._mode != TVMode.TV:
            raise InvalidModeError(action, "кабельное ТВ", self._mode.value)
    
    def turn_on(self) -> None:
        """Включение телевизора."""
        self._is_on = True
        self._mode = TVMode.TV  # При включении всегда в режиме ТВ
    
    def turn_off(self) -> None:
        """Выключение телевизора."""
        self._is_on = False
    
    def switch_to_smart_tv(self) -> None:
        """
        Переключение в режим Smart TV.
        
        Raises:
            TVNotPoweredError: Если телевизор выключен
            SmartTVNotSupportedError: Если Smart TV не поддерживается
        """
        self._check_powered("переключение на Smart TV")
        
        if not self.specs.has_smart_tv:
            raise SmartTVNotSupportedError("переключение на Smart TV")
        
        self._mode = TVMode.SMART_TV
    
    def switch_to_tv_mode(self) -> None:
        """
        Переключение в режим кабельного ТВ.
        
        Raises:
            TVNotPoweredError: Если телевизор выключен
        """
        self._check_powered("переключение на кабельное ТВ")
        self._mode = TVMode.TV
    
    def switch_to_hdmi(self, port: int) -> None:
        """
        Переключение в режим HDMI.
        
        Args:
            port: Номер HDMI порта
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            PortNotFoundError: Если порт не существует
            DeviceNotFoundError: Если на порту нет устройства
        """
        self._check_powered("переключение на HDMI")
        
        if self.specs.hdmi_ports == 0:
            raise PortNotFoundError("HDMI", port, 0)
        
        if port < 1 or port > self.specs.hdmi_ports:
            raise PortNotFoundError("HDMI", port, self.specs.hdmi_ports)
        
        if port not in self._hdmi_devices:
            raise DeviceNotFoundError("HDMI устройство", port)
        
        self._mode = TVMode.HDMI
        self._current_hdmi_port = port
    
    def set_channel(self, channel: int) -> None:
        """
        Установка канала (только в режиме ТВ).
        
        Args:
            channel: Номер канала
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            InvalidModeError: Если не в режиме ТВ
            InvalidValueError: Если неверный номер канала
        """
        self._check_powered("переключение канала")
        self._check_tv_mode("переключение канала")
        self._current_channel = validate_channel(channel)
    
    def channel_up(self) -> None:
        """Переключение на следующий канал (только в режиме ТВ)."""
        self._check_powered("переключение канала")
        self._check_tv_mode("переключение канала")
        
        if self._current_channel < 999:
            self._current_channel += 1
        else:
            self._current_channel = 1
    
    def channel_down(self) -> None:
        """Переключение на предыдущий канал (только в режиме ТВ)."""
        self._check_powered("переключение канала")
        self._check_tv_mode("переключение канала")
        
        if self._current_channel > 1:
            self._current_channel -= 1
        else:
            self._current_channel = 999
    
    def set_brightness(self, value: int) -> None:
        """
        Установка яркости.
        
        Args:
            value: Значение яркости (0-100)
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            InvalidValueError: Если неверное значение
        """
        self._check_powered("изменение яркости")
        self._brightness = validate_brightness(value)
    
    def get_brightness(self) -> int:
        """Получение текущей яркости."""
        return self._brightness
    
    def set_contrast(self, value: int) -> None:
        """
        Установка контраста.
        
        Args:
            value: Значение контраста (0-100)
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            InvalidValueError: Если неверное значение
        """
        self._check_powered("изменение контраста")
        self._contrast = validate_contrast(value)
    
    def get_contrast(self) -> int:
        """Получение текущего контраста."""
        return self._contrast
    
    def set_volume(self, value: int) -> None:
        """
        Установка громкости (работает в любом режиме).
        
        Args:
            value: Значение громкости (0-100)
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            InvalidValueError: Если неверное значение
        """
        self._check_powered("изменение громкости")
        self._volume = validate_volume(value)
    
    def get_volume(self) -> int:
        """Получение текущей громкости."""
        return self._volume
    
    def volume_up(self) -> None:
        """Увеличение громкости на 5 (работает в любом режиме)."""
        self._check_powered("изменение громкости")
        self._volume = min(self._volume + 5, 100)
    
    def volume_down(self) -> None:
        """Уменьшение громкости на 5 (работает в любом режиме)."""
        self._check_powered("изменение громкости")
        self._volume = max(self._volume - 5, 0)
    
    def set_equalizer(self, high: int, mid: int, low: int) -> None:
        """
        Настройка эквалайзера.
        
        Args:
            high: Высокие частоты (-100 до 100)
            mid: Средние частоты (-100 до 100)
            low: Низкие частоты (-100 до 100)
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            InvalidValueError: Если неверное значение
        """
        self._check_powered("настройка эквалайзера")
        self._equalizer["high"] = validate_equalizer_value(high)
        self._equalizer["mid"] = validate_equalizer_value(mid)
        self._equalizer["low"] = validate_equalizer_value(low)
    
    def get_equalizer(self) -> Dict[str, int]:
        """Получение текущих настроек эквалайзера."""
        return self._equalizer.copy()
    
    def toggle_subwoofer(self) -> None:
        """Переключение состояния сабвуфера."""
        self._check_powered("переключение сабвуфера")
        self._subwoofer_connected = not self._subwoofer_connected
    
    def is_subwoofer_connected(self) -> bool:
        """Проверка подключения сабвуфера."""
        return self._subwoofer_connected
    
    def connect_hdmi(self, port: int, device_name: str) -> None:
        """
        Подключение устройства по HDMI.
        
        Args:
            port: Номер HDMI порта
            device_name: Название устройства
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            PortNotFoundError: Если неверный порт или нет портов
            InvalidValueError: Если пустое название
        """
        self._check_powered("подключение HDMI")
        
        if self.specs.hdmi_ports == 0:
            raise PortNotFoundError("HDMI", port, 0)
        
        if port < 1 or port > self.specs.hdmi_ports:
            raise PortNotFoundError("HDMI", port, self.specs.hdmi_ports)
        
        if not device_name or not device_name.strip():
            raise InvalidValueError("название устройства", device_name, "непустая строка")
        
        self._hdmi_devices[port] = device_name.strip()
    
    def disconnect_hdmi(self, port: int) -> str:
        """
        Отключение устройства от HDMI.
        
        Args:
            port: Номер HDMI порта
            
        Returns:
            Название отключенного устройства
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            PortNotFoundError: Если порт не существует или нет портов
            DeviceNotFoundError: Если на порту нет устройства
        """
        self._check_powered("отключение HDMI")
        
        if self.specs.hdmi_ports == 0:
            raise PortNotFoundError("HDMI", port, 0)
        
        if port < 1 or port > self.specs.hdmi_ports:
            raise PortNotFoundError("HDMI", port, self.specs.hdmi_ports)
        
        if port not in self._hdmi_devices:
            raise DeviceNotFoundError("HDMI устройство", port)
        
        return self._hdmi_devices.pop(port)
    
    def get_hdmi_devices(self) -> Dict[int, str]:
        """Получение списка подключенных HDMI устройств."""
        return self._hdmi_devices.copy()
    
    def update_software(self) -> Optional[float]:
        """
        Обновление программного обеспечения.
        
        Returns:
            Новая версия ПО или None, если обновление не требуется
            
        Raises:
            TVNotPoweredError: Если телевизор выключен
            SmartTVNotSupportedError: Если Smart TV не поддерживается
            InvalidModeError: Если не в режиме Smart TV
        """
        self._check_powered("обновление ПО")
        
        if not self.specs.has_smart_tv:
            raise SmartTVNotSupportedError("обновление ПО")
        
        if self._mode != TVMode.SMART_TV:
            raise InvalidModeError("обновление ПО", "Smart TV", self._mode.value)
        
        # Базовая версия из характеристик
        base_version = float(self.specs.os_version) if self.specs.os_version else 1.0
        
        # Проверяем, не достигли ли предела (x+1)
        if self._software_version >= base_version + 1.0:
            return None
        
        # Увеличиваем версию на 0.1
        self._software_version = round(self._software_version + 0.1, 1)
        return self._software_version
    
    def get_status(self) -> Dict[str, Any]:
        """
        Получение полного состояния телевизора.
        
        Returns:
            Словарь с текущим состоянием
        """
        return {
            "is_on": self._is_on,
            "mode": self._mode.value,
            "current_channel": self._current_channel if self._mode == TVMode.TV else None,
            "current_hdmi_port": self._current_hdmi_port if self._mode == TVMode.HDMI else None,
            "brightness": self._brightness,
            "contrast": self._contrast,
            "volume": self._volume,
            "subwoofer": self._subwoofer_connected,
            "equalizer": self._equalizer.copy(),
            "wifi": self._wifi_enabled,
            "bluetooth": self._bluetooth_enabled,
            "network": self._network_connection,
            "hdmi_devices": self._hdmi_devices.copy(),
            "software_version": self._software_version,
            "has_hdmi": self.specs.hdmi_ports > 0,
            "has_wifi": self.specs.has_wifi,
            "has_bluetooth": self.specs.has_bluetooth,
            "has_smart_tv": self.specs.has_smart_tv
        }
    
    def show_specs(self) -> None:
        """Показать технические характеристики."""
        print("\n" + "="*60)
        print(f"ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ: {self.specs.model_name}")
        print("="*60)
        print(f"Технология экрана: {self.specs.technology.value}")
        print(f"Диагональ: {self.specs.screen_diagonal} дюймов")
        print(f"Разрешение: {self.specs.resolution[0]}x{self.specs.resolution[1]}")
        print(f"Время отклика: {self.specs.response_time} мс")
        print(f"Покрытие экрана: {self.specs.screen_coverage.value}")
        print(f"Частота обновления: {self.specs.refresh_rate} Гц")
        print(f"Яркость: {self.specs.brightness_nit} нит")
        print(f"\nАудио:")
        print(f"  Динамиков: {self.specs.speakers_count}")
        print(f"  Мощность: {self.specs.speaker_power} Вт")
        print(f"\nРазъемы:")
        print(f"  HDMI: {self.specs.hdmi_ports} {'(нет)' if self.specs.hdmi_ports == 0 else ''}")
        print(f"  USB: {self.specs.usb_ports}")
        print(f"  LAN: {self.specs.lan_ports}")
        print(f"\nSmart TV:")
        print(f"  Поддержка: {'да' if self.specs.has_smart_tv else 'нет'}")
        if self.specs.has_smart_tv and self.specs.operating_system:
            print(f"  ОС: {self.specs.operating_system.value}")
            print(f"  Версия: {self.specs.os_version}")
        print(f"  Wi-Fi: {'да' if self.specs.has_wifi else 'нет'}")
        print(f"  Bluetooth: {'да' if self.specs.has_bluetooth else 'нет'}")
        print(f"\nРазмеры и вес:")
        print(f"  Цвет: {self.specs.color}")
        print(f"  Вес: {self.specs.weight} кг")
        print(f"  Срок службы: {self.specs.lifespan} лет")
        print("="*60)