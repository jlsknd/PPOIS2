"""
Модуль с пользовательскими исключениями для приложения.
"""

class TelevisionError(Exception):
    """Базовое исключение для приложения телевизор"""
    pass


class PowerStateError(TelevisionError):
    """Исключение при неверном состоянии питания"""
    pass


class SourceError(TelevisionError):
    """Исключение при ошибках с источником сигнала"""
    pass


class ChannelError(TelevisionError):
    """Исключение при ошибках с каналами"""
    pass


class SettingsError(TelevisionError):
    """Исключение при неверных настройках"""
    pass


class BluetoothError(TelevisionError):
    """Исключение при работе с Bluetooth"""
    pass


class StorageError(TelevisionError):
    """Исключение при работе с хранилищем данных"""
    pass


class ValidationError(TelevisionError):
    """Исключение при ошибках валидации данных"""
    pass