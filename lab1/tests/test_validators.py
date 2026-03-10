"""
Unit-тесты для валидаторов.
"""

import unittest

from src.utils.validators import (
    validate_range, validate_channel, validate_brightness,
    validate_contrast, validate_volume, validate_equalizer_value,
    validate_port, validate_string_not_empty, validate_positive_number,
    validate_non_negative_number
)
from src.exceptions.tv_exceptions import InvalidValueError


class TestValidators(unittest.TestCase):
    """Тесты для валидаторов."""
    
    def test_validate_range(self) -> None:
        """Тест проверки диапазона."""
        # Валидные значения
        self.assertEqual(validate_range(5, 0, 10, "test"), 5)
        self.assertEqual(validate_range(0, 0, 10, "test"), 0)
        self.assertEqual(validate_range(10, 0, 10, "test"), 10)
        
        # Невалидные значения
        with self.assertRaises(InvalidValueError):
            validate_range(-1, 0, 10, "test")
        
        with self.assertRaises(InvalidValueError):
            validate_range(11, 0, 10, "test")
    
    def test_validate_channel(self) -> None:
        """Тест проверки канала."""
        self.assertEqual(validate_channel(1), 1)
        self.assertEqual(validate_channel(500), 500)
        self.assertEqual(validate_channel(999), 999)
        
        with self.assertRaises(InvalidValueError):
            validate_channel(0)
        
        with self.assertRaises(InvalidValueError):
            validate_channel(1000)
    
    def test_validate_brightness(self) -> None:
        """Тест проверки яркости."""
        self.assertEqual(validate_brightness(0), 0)
        self.assertEqual(validate_brightness(50), 50)
        self.assertEqual(validate_brightness(100), 100)
        
        with self.assertRaises(InvalidValueError):
            validate_brightness(-1)
        
        with self.assertRaises(InvalidValueError):
            validate_brightness(101)
    
    def test_validate_contrast(self) -> None:
        """Тест проверки контраста."""
        self.assertEqual(validate_contrast(0), 0)
        self.assertEqual(validate_contrast(75), 75)
        
        with self.assertRaises(InvalidValueError):
            validate_contrast(-10)
    
    def test_validate_volume(self) -> None:
        """Тест проверки громкости."""
        self.assertEqual(validate_volume(0), 0)
        self.assertEqual(validate_volume(30), 30)
        self.assertEqual(validate_volume(100), 100)
        
        with self.assertRaises(InvalidValueError):
            validate_volume(-5)
        
        with self.assertRaises(InvalidValueError):
            validate_volume(150)
    
    def test_validate_equalizer_value(self) -> None:
        """Тест проверки значения эквалайзера."""
        self.assertEqual(validate_equalizer_value(-100), -100)
        self.assertEqual(validate_equalizer_value(0), 0)
        self.assertEqual(validate_equalizer_value(100), 100)
        
        with self.assertRaises(InvalidValueError):
            validate_equalizer_value(-101)
        
        with self.assertRaises(InvalidValueError):
            validate_equalizer_value(101)
    
    def test_validate_port(self) -> None:
        """Тест проверки порта."""
        self.assertEqual(validate_port(1, 4, "HDMI"), 1)
        self.assertEqual(validate_port(4, 4, "HDMI"), 4)
        
        with self.assertRaises(InvalidValueError):
            validate_port(0, 4, "HDMI")
        
        with self.assertRaises(InvalidValueError):
            validate_port(5, 4, "HDMI")
    
    def test_validate_string_not_empty(self) -> None:
        """Тест проверки непустой строки."""
        self.assertEqual(validate_string_not_empty("test", "name"), "test")
        self.assertEqual(validate_string_not_empty("  test  ", "name"), "test")
        
        with self.assertRaises(InvalidValueError):
            validate_string_not_empty("", "name")
        
        with self.assertRaises(InvalidValueError):
            validate_string_not_empty("   ", "name")
    
    def test_validate_positive_number(self) -> None:
        """Тест проверки положительного числа."""
        self.assertEqual(validate_positive_number(1, "test"), 1)
        self.assertEqual(validate_positive_number(0.5, "test"), 0.5)
        
        with self.assertRaises(InvalidValueError):
            validate_positive_number(0, "test")
        
        with self.assertRaises(InvalidValueError):
            validate_positive_number(-5, "test")
    
    def test_validate_non_negative_number(self) -> None:
        """Тест проверки неотрицательного числа."""
        self.assertEqual(validate_non_negative_number(0, "test"), 0)
        self.assertEqual(validate_non_negative_number(5, "test"), 5)
        self.assertEqual(validate_non_negative_number(10.5, "test"), 10.5)
        
        with self.assertRaises(InvalidValueError):
            validate_non_negative_number(-1, "test")
        
        with self.assertRaises(InvalidValueError):
            validate_non_negative_number(-0.1, "test")


if __name__ == "__main__":
    unittest.main()