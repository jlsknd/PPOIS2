"""
Модуль с валидаторами для проверки входных данных.
Соответствие требованию: использование аннотаций типов и исключений.
"""

from typing import Union, Any
from ..exceptions.tv_exceptions import InvalidValueError


def validate_range(
    value: Union[int, float],
    min_val: Union[int, float],
    max_val: Union[int, float],
    param_name: str
) -> Union[int, float]:
    """
    Проверка, что значение находится в заданном диапазоне.
    
    Args:
        value: Проверяемое значение
        min_val: Минимальное допустимое значение
        max_val: Максимальное допустимое значение
        param_name: Название параметра для сообщения об ошибке
        
    Returns:
        Проверенное значение
        
    Raises:
        InvalidValueError: Если значение вне диапазона
    """
    if not min_val <= value <= max_val:
        raise InvalidValueError(param_name, value, f"{min_val}-{max_val}")
    return value


def validate_channel(channel: int) -> int:
    """
    Проверка номера канала.
    
    Args:
        channel: Номер канала
        
    Returns:
        Проверенный номер канала
        
    Raises:
        InvalidValueError: Если канал вне диапазона 1-999
    """
    return validate_range(channel, 1, 999, "номер канала")


def validate_brightness(brightness: int) -> int:
    """Проверка яркости (0-100)."""
    return validate_range(brightness, 0, 100, "яркость")


def validate_contrast(contrast: int) -> int:
    """Проверка контраста (0-100)."""
    return validate_range(contrast, 0, 100, "контраст")


def validate_volume(volume: int) -> int:
    """Проверка громкости (0-100)."""
    return validate_range(volume, 0, 100, "громкость")


def validate_equalizer_value(value: int) -> int:
    """Проверка значения эквалайзера (-100 до 100)."""
    return validate_range(value, -100, 100, "значение эквалайзера")


def validate_port(port: int, max_ports: int, port_type: str) -> int:
    """
    Проверка номера порта.
    
    Args:
        port: Номер порта
        max_ports: Максимальное количество портов
        port_type: Тип порта для сообщения об ошибке
        
    Returns:
        Проверенный номер порта
        
    Raises:
        InvalidValueError: Если порт вне диапазона
    """
    return validate_range(port, 1, max_ports, f"{port_type} порт")


def validate_string_not_empty(value: str, param_name: str) -> str:
    """
    Проверка, что строка не пустая.
    
    Args:
        value: Проверяемая строка
        param_name: Название параметра
        
    Returns:
        Проверенная строка
        
    Raises:
        InvalidValueError: Если строка пустая
    """
    if not value or not value.strip():
        raise InvalidValueError(param_name, value, "непустая строка")
    return value.strip()


def validate_positive_number(value: Union[int, float], param_name: str) -> Union[int, float]:
    """
    Проверка, что число положительное.
    
    Args:
        value: Проверяемое число
        param_name: Название параметра
        
    Returns:
        Проверенное число
        
    Raises:
        InvalidValueError: Если число <= 0
    """
    if value <= 0:
        raise InvalidValueError(param_name, value, "положительное число")
    return value


def validate_non_negative_number(value: Union[int, float], param_name: str) -> Union[int, float]:
    """
    Проверка, что число неотрицательное (может быть 0).
    
    Args:
        value: Проверяемое число
        param_name: Название параметра
        
    Returns:
        Проверенное число
        
    Raises:
        InvalidValueError: Если число < 0
    """
    if value < 0:
        raise InvalidValueError(param_name, value, "неотрицательное число")
    return value