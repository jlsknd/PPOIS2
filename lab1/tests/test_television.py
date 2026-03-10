"""
Unit-тесты для класса Television.
"""

import unittest
from typing import Tuple

from src.models.television import (
    Television, TechnicalSpecifications, ScreenTechnology,
    ScreenCoverage, OperatingSystem, TVMode
)
from src.exceptions.tv_exceptions import (
    TVNotPoweredError, InvalidValueError,
    SmartTVNotSupportedError, DeviceNotFoundError,
    PortNotFoundError, InvalidModeError
)


class TestTelevision(unittest.TestCase):
    """Тесты для класса Television."""
    
    def setUp(self) -> None:
        """Подготовка перед каждым тестом."""
        self.specs = TechnicalSpecifications(
            model_name="Samsung QLED-55",
            technology=ScreenTechnology.QLED,
            screen_diagonal=55.0,
            resolution=(3840, 2160),
            response_time=5,
            screen_coverage=ScreenCoverage.ANTI_GLARE,
            refresh_rate=120,
            speakers_count=2,
            speaker_power=20,
            hdmi_ports=4,
            usb_ports=2,
            lan_ports=1,
            has_wifi=True,
            has_bluetooth=True,
            has_smart_tv=True,
            color="черный",
            weight=18.5,
            lifespan=10,
            brightness_nit=500,
            operating_system=OperatingSystem.TIZEN,
            os_version="5.0"
        )
        self.tv = Television(self.specs)
    
    def test_initial_state(self) -> None:
        """Тест начального состояния."""
        self.assertFalse(self.tv.is_on)
        self.assertEqual(self.tv.mode, TVMode.TV)
        self.assertEqual(self.tv.current_channel, 1)
        self.assertEqual(self.tv.get_brightness(), 50)
        self.assertEqual(self.tv.get_contrast(), 50)
        self.assertEqual(self.tv.get_volume(), 30)
        self.assertFalse(self.tv.is_subwoofer_connected())
    
    def test_turn_on_off(self) -> None:
        """Тест включения/выключения."""
        self.tv.turn_on()
        self.assertTrue(self.tv.is_on)
        self.assertEqual(self.tv.mode, TVMode.TV)
        
        self.tv.turn_off()
        self.assertFalse(self.tv.is_on)
    
    def test_switch_to_hdmi(self) -> None:
        """Тест переключения в режим HDMI."""
        self.tv.turn_on()
        self.tv.connect_hdmi(1, "PlayStation")
        
        self.tv.switch_to_hdmi(1)
        self.assertEqual(self.tv.mode, TVMode.HDMI)
        self.assertEqual(self.tv._current_hdmi_port, 1)
    
    def test_switch_to_hdmi_errors(self) -> None:
        """Тест ошибок при переключении в HDMI."""
        self.tv.turn_on()
        
        # Порт без устройства
        with self.assertRaises(DeviceNotFoundError):
            self.tv.switch_to_hdmi(2)
        
        # Несуществующий порт
        with self.assertRaises(PortNotFoundError):
            self.tv.switch_to_hdmi(5)
        
        # Телевизор выключен
        self.tv.turn_off()
        with self.assertRaises(TVNotPoweredError):
            self.tv.switch_to_hdmi(1)
    
    def test_set_contrast(self) -> None:
        """Тест установки контраста."""
        self.tv.turn_on()
        
        self.tv.set_contrast(75)
        self.assertEqual(self.tv.get_contrast(), 75)
        
        with self.assertRaises(InvalidValueError):
            self.tv.set_contrast(150)
    
    def test_set_volume(self) -> None:
        """Тест установки громкости."""
        self.tv.turn_on()
        
        self.tv.set_volume(42)
        self.assertEqual(self.tv.get_volume(), 42)
        
        with self.assertRaises(InvalidValueError):
            self.tv.set_volume(150)
    
    def test_connect_hdmi(self) -> None:
        """Тест подключения HDMI."""
        self.tv.turn_on()
        
        self.tv.connect_hdmi(1, "PlayStation")
        self.assertIn(1, self.tv.get_hdmi_devices())
        self.assertEqual(self.tv.get_hdmi_devices()[1], "PlayStation")
    
    def test_connect_hdmi_errors(self) -> None:
        """Тест ошибок при подключении HDMI."""
        self.tv.turn_on()
        
        # Несуществующий порт
        with self.assertRaises(PortNotFoundError):
            self.tv.connect_hdmi(5, "Xbox")
        
        # Пустое имя
        with self.assertRaises(InvalidValueError):
            self.tv.connect_hdmi(2, "")
        
        # Телевизор выключен
        self.tv.turn_off()
        with self.assertRaises(TVNotPoweredError):
            self.tv.connect_hdmi(1, "Test")
    
    def test_show_specs(self) -> None:
        """Тест отображения характеристик."""
        # Просто проверяем, что метод не падает с ошибкой
        try:
            self.tv.show_specs()
        except Exception as e:
            self.fail(f"show_specs raised {e}")
    
    def test_show_specs_without_smart_tv(self) -> None:
        """Тест отображения характеристик без Smart TV."""
        specs_no_smart = TechnicalSpecifications(
            model_name="Simple TV",
            technology=ScreenTechnology.LED,
            screen_diagonal=32.0,
            resolution=(1920, 1080),
            response_time=8,
            screen_coverage=ScreenCoverage.GLOSSY,
            refresh_rate=60,
            speakers_count=2,
            speaker_power=5,
            hdmi_ports=2,
            usb_ports=1,
            lan_ports=0,
            has_wifi=False,
            has_bluetooth=False,
            has_smart_tv=False,
            color="черный",
            weight=8.5,
            lifespan=7,
            brightness_nit=250
        )
        tv = Television(specs_no_smart)
        
        try:
            tv.show_specs()
        except Exception as e:
            self.fail(f"show_specs raised {e}")
    
    # ... остальные тесты из предыдущей версии ...


if __name__ == "__main__":
    unittest.main()