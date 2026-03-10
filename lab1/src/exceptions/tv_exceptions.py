"""
Модуль с пользовательскими исключениями для телевизора.
Соответствие требованию: использование механизма исключений.
"""

from typing import Any, Optional


class TVError(Exception):
    """Базовое исключение для всех ошибок телевизора."""
    pass


class InvalidValueError(TVError):
    """Исключение при передаче недопустимого значения."""
    
    def __init__(self, param_name: str, value: Any, valid_range: str) -> None:
        """
        Инициализация исключения.
        
        Args:
            param_name: Название параметра
            value: Переданное значение
            valid_range: Допустимый диапазон
        """
        self.param_name = param_name
        self.value = value
        self.valid_range = valid_range
        message = f"Недопустимое значение для '{param_name}': {value}. Допустимо: {valid_range}"
        super().__init__(message)


class TVNotPoweredError(TVError):
    """Исключение при попытке действия с выключенным телевизором."""
    
    def __init__(self, action: str) -> None:
        """
        Инициализация исключения.
        
        Args:
            action: Действие, которое пытались выполнить
        """
        self.action = action
        message = f"Невозможно выполнить '{action}': телевизор выключен"
        super().__init__(message)


class InvalidModeError(TVError):
    """Исключение при попытке выполнить действие в неподходящем режиме."""
    
    def __init__(self, action: str, required_mode: str, current_mode: str) -> None:
        """
        Инициализация исключения.
        
        Args:
            action: Действие, которое пытались выполнить
            required_mode: Требуемый режим
            current_mode: Текущий режим
        """
        self.action = action
        self.required_mode = required_mode
        self.current_mode = current_mode
        message = f"Невозможно выполнить '{action}' в режиме '{current_mode}'. Требуется режим: {required_mode}"
        super().__init__(message)


class SmartTVNotSupportedError(TVError):
    """Исключение при отсутствии поддержки Smart TV."""
    
    def __init__(self, operation: str) -> None:
        """
        Инициализация исключения.
        
        Args:
            operation: Операция, которая требует Smart TV
        """
        self.operation = operation
        message = f"Операция '{operation}' требует Smart TV, который не поддерживается"
        super().__init__(message)


class DeviceNotFoundError(TVError):
    """Исключение при отсутствии подключенного устройства."""
    
    def __init__(self, device_type: str, identifier: Any) -> None:
        """
        Инициализация исключения.
        
        Args:
            device_type: Тип устройства
            identifier: Идентификатор устройства
        """
        self.device_type = device_type
        self.identifier = identifier
        message = f"{device_type} с идентификатором {identifier} не найден"
        super().__init__(message)


class PortNotFoundError(TVError):
    """Исключение при обращении к несуществующему порту."""
    
    def __init__(self, port_type: str, port_number: int, max_ports: int) -> None:
        """
        Инициализация исключения.
        
        Args:
            port_type: Тип порта
            port_number: Номер порта
            max_ports: Максимальное количество портов
        """
        self.port_type = port_type
        self.port_number = port_number
        self.max_ports = max_ports
        message = f"{port_type} порт {port_number} не существует. Доступны порты 1-{max_ports}"
        super().__init__(message)