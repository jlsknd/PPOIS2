"""
Модуль содержит класс RemoteControl - пульт дистанционного управления.
"""
from typing import Optional, List, Dict, Any
from src.models.television import Television, TvSource, Channel
from src.utils.exceptions import PowerStateError, SourceError, ChannelError, SettingsError


class RemoteControl:
    def __init__(self, television: Television):
        self.tv = television #принимает объект тв, которым будет управлять пульт
    
    def power_on(self) -> None:
        try:
            self.tv.turn_on()
        except RuntimeError as e:
            raise PowerStateError(str(e))
    
    def power_off(self) -> None:
        try:
            self.tv.turn_off()
        except RuntimeError as e:
            raise PowerStateError(str(e))
    
    def power_toggle(self) -> None:
        if self.tv.is_on:
            self.power_off()
        else:
            self.power_on()
    
    def switch_to_tv(self) -> None:
        try:
            self.tv.switch_to_tv()
        except RuntimeError as e:
            raise SourceError(str(e))
    
    def switch_to_smart_tv(self) -> None:
        if not self.tv.specs.has_smart_tv:
            raise SourceError("Данная модель не поддерживает Smart TV")
        try:
            self.tv.switch_to_smart_tv()
        except RuntimeError as e:
            raise SourceError(str(e))
    
    def change_channel(self, channel_number: int) -> Channel:
        try:
            return self.tv.set_channel(channel_number)
        except (RuntimeError, ValueError) as e:
            raise ChannelError(str(e))
    
    def channel_up(self) -> Optional[Channel]:
        try:
            return self.tv.next_channel()
        except Exception as e:
            raise ChannelError(str(e))
    
    def channel_down(self) -> Optional[Channel]:
        try:
            return self.tv.prev_channel()
        except Exception as e:
            raise ChannelError(str(e))
    
    def set_volume(self, level: int) -> None:
        if not self.tv.is_on:
            raise SettingsError("Сначала включите телевизор")
        try:
            self.tv.set_volume(level)
        except ValueError as e:
            raise SettingsError(str(e))
    
    def volume_up(self, step: int = 5) -> None:
        if not self.tv.is_on:
            raise SettingsError("Сначала включите телевизор")
        self.tv.volume_up(step)
    
    def volume_down(self, step: int = 5) -> None:
        if not self.tv.is_on:
            raise SettingsError("Сначала включите телевизор")
        self.tv.volume_down(step)
    
    def mute(self) -> None:
        if not self.tv.is_on:
            raise SettingsError("Сначала включите телевизор")
        self.set_volume(0)
    
    def adjust_brightness(self, level: int) -> None:
        if not self.tv.is_on:
            raise SettingsError("Сначала включите телевизор")
        try:
            self.tv.set_brightness(level)
        except ValueError as e:
            raise SettingsError(str(e))
    
    def adjust_contrast(self, level: int) -> None:
        if not self.tv.is_on:
            raise SettingsError("Сначала включите телевизор")
        try:
            self.tv.set_contrast(level)
        except ValueError as e:
            raise SettingsError(str(e))
    
    def set_equalizer(self, low: int, mid: int, high: int) -> None:
        if not self.tv.is_on:
            raise SettingsError("Сначала включите телевизор")
        try:
            self.tv.set_equalizer(low, mid, high)
        except ValueError as e:
            raise SettingsError(str(e))
    
    def connect_subwoofer(self, connected: bool = True) -> None:
        self.tv.connect_subwoofer(connected)
    
    def enable_wifi(self) -> None:
        try:
            self.tv.enable_wifi()
        except RuntimeError as e:
            raise SettingsError(str(e))
    
    def disable_wifi(self) -> None:
        self.tv.disable_wifi()
    
    def enable_bluetooth(self) -> None:
        try:
            self.tv.enable_bluetooth()
        except RuntimeError as e:
            raise SettingsError(str(e))
    
    def disable_bluetooth(self) -> None:
        self.tv.disable_bluetooth()
    
    def update_software(self) -> str:
        if not self.tv.is_on:
            raise PowerStateError("Для обновления ПО включите телевизор")
        return self.tv.update_software()
    
    def get_status(self) -> dict:
        return self.tv.get_status()