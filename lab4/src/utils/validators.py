"""
Модуль с валидаторами для проверки вводимых данных.
"""
from typing import Any, Tuple, Optional
from src.utils.exceptions import ValidationError


def validate_int(value: str, min_val: Optional[int] = None, max_val: Optional[int] = None, 
                field_name: str = "Значение") -> int:
    """
    Проверяет, что значение является целым числом в заданном диапазоне.
    
    Args:
        value: Строка для проверки
        min_val: Минимальное допустимое значение
        max_val: Максимальное допустимое значение
        field_name: Название поля для сообщения об ошибке
        
    Returns:
        int: Проверенное целое число
        
    Raises:
        ValidationError: Если значение не прошло проверку
    """
    try:
        int_val = int(value)
    except ValueError:
        raise ValidationError(f"{field_name} должно быть целым числом")
    
    if min_val is not None and int_val < min_val:
        raise ValidationError(f"{field_name} должно быть не меньше {min_val}")
    
    if max_val is not None and int_val > max_val:
        raise ValidationError(f"{field_name} должно быть не больше {max_val}")
    
    return int_val


def validate_float(value: str, min_val: Optional[float] = None, max_val: Optional[float] = None,
                   field_name: str = "Значение") -> float:
    """
    Проверяет, что значение является числом с плавающей точкой в заданном диапазоне.
    """
    try:
        float_val = float(value)
    except ValueError:
        raise ValidationError(f"{field_name} должно быть числом")
    
    if min_val is not None and float_val < min_val:
        raise ValidationError(f"{field_name} должно быть не меньше {min_val}")
    
    if max_val is not None and float_val > max_val:
        raise ValidationError(f"{field_name} должно быть не больше {max_val}")
    
    return float_val


def validate_bool(value: str, field_name: str = "Значение") -> bool:
    """
    Проверяет, что значение является булевым (да/нет, true/false, 1/0).
    """
    val_lower = value.strip().lower()
    if val_lower in ['да', 'yes', 'y', 'true', '1', '+']:
        return True
    elif val_lower in ['нет', 'no', 'n', 'false', '0', '-']:
        return False
    else:
        raise ValidationError(f"{field_name} должно быть 'да' или 'нет'")


def validate_choice(value: str, choices: list, field_name: str = "Значение") -> str:
    """
    Проверяет, что значение находится в списке допустимых вариантов.
    """
    if value not in choices:
        choices_str = ", ".join(choices)
        raise ValidationError(f"{field_name} должно быть одним из: {choices_str}")
    return value


def validate_tuple(value: str, expected_parts: int, separator: str = 'x',
                   field_name: str = "Значение") -> Tuple[int, ...]:
    """
    Проверяет, что значение является кортежем чисел (например, "1920x1080").
    """
    parts = value.split(separator)
    if len(parts) != expected_parts:
        raise ValidationError(f"{field_name} должно содержать {expected_parts} числа, разделенных '{separator}'")
    
    try:
        return tuple(int(part.strip()) for part in parts)
    except ValueError:
        raise ValidationError(f"Все части {field_name} должны быть целыми числами")