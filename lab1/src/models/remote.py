"""
Модуль с классом пульта дистанционного управления.
"""

from typing import Optional, Dict, Any
from .television import Television, TVMode
from ..exceptions.tv_exceptions import TVError


class RemoteControl:
    """Класс пульта дистанционного управления."""
    
    def __init__(self, tv: Television) -> None:
        """
        Инициализация пульта.
        
        Args:
            tv: Телевизор, которым управляет пульт
        """
        self._tv = tv
        self._last_channel: int = 1
    
    def power(self) -> None:
        """Кнопка включения/выключения."""
        if self._tv.is_on:
            self._tv.turn_off()
            print(" Телевизор выключен")
        else:
            self._tv.turn_on()
            print(" Телевизор включен")
    
    def tv_mode(self) -> None:
        """Переключение в режим кабельного ТВ."""
        try:
            self._tv.switch_to_tv_mode()
            print(" Режим: Кабельное ТВ")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def smart_tv_mode(self) -> None:
        """Переключение в режим Smart TV."""
        try:
            self._tv.switch_to_smart_tv()
            print(" Режим: Smart TV")
            print("   В этом режиме недоступно переключение каналов")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def hdmi_mode(self, port: int) -> None:
        """Переключение в режим HDMI."""
        try:
            self._tv.switch_to_hdmi(port)
            device = self._tv.get_hdmi_devices().get(port, "Неизвестное устройство")
            print(f" Режим: HDMI {port} ({device})")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def channel_up(self) -> None:
        """Кнопка следующий канал (только в режиме ТВ)."""
        try:
            self._tv.channel_up()
            print(f" Канал {self._tv.current_channel}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def channel_down(self) -> None:
        """Кнопка предыдущий канал (только в режиме ТВ)."""
        try:
            self._tv.channel_down()
            print(f" Канал {self._tv.current_channel}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def set_channel(self, channel: int) -> None:
        """
        Выбор канала по номеру (только в режиме ТВ).
        
        Args:
            channel: Номер канала
        """
        try:
            self._tv.set_channel(channel)
            print(f" Канал {channel}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def volume_up(self) -> None:
        """Увеличение громкости на 5."""
        try:
            self._tv.volume_up()
            print(f" Громкость: {self._tv.get_volume()}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def volume_down(self) -> None:
        """Уменьшение громкости на 5."""
        try:
            self._tv.volume_down()
            print(f" Громкость: {self._tv.get_volume()}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def set_volume(self, value: int) -> None:
        """
        Установка конкретного значения громкости.
        
        Args:
            value: Значение громкости (0-100)
        """
        try:
            self._tv.set_volume(value)
            print(f" Громкость: {self._tv.get_volume()}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def mute(self) -> None:
        """Отключение звука."""
        try:
            self._tv.set_volume(0)
            print(" Звук отключен")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def set_brightness(self, value: int) -> None:
        """
        Установка яркости.
        
        Args:
            value: Значение яркости
        """
        try:
            self._tv.set_brightness(value)
            print(f" Яркость: {self._tv.get_brightness()}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def set_contrast(self, value: int) -> None:
        """
        Установка контраста.
        
        Args:
            value: Значение контраста
        """
        try:
            self._tv.set_contrast(value)
            print(f" Контраст: {self._tv.get_contrast()}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def set_equalizer(self, high: int, mid: int, low: int) -> None:
        """
        Настройка эквалайзера.
        
        Args:
            high: Высокие частоты
            mid: Средние частоты
            low: Низкие частоты
        """
        try:
            self._tv.set_equalizer(high, mid, low)
            eq = self._tv.get_equalizer()
            print(f" Эквалайзер: ВЧ={eq['high']}, СЧ={eq['mid']}, НЧ={eq['low']}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def toggle_subwoofer(self) -> None:
        """Переключение сабвуфера."""
        try:
            self._tv.toggle_subwoofer()
            status = "подключен" if self._tv.is_subwoofer_connected() else "отключен"
            print(f" Сабвуфер {status}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def toggle_wifi(self) -> None:
        """Включение/выключение Wi-Fi."""
        if not self._tv.can_use_wifi():
            print(" У этого телевизора нет Wi-Fi модуля")
            return
        try:
            new_status = self._tv.toggle_wifi()
            status_text = "включен" if new_status else "выключен"
            print(f" Wi-Fi {status_text}")
        except Exception as e:
            print(f" Ошибка: {e}")
    
    def toggle_bluetooth(self) -> None:
        """Включение/выключение Bluetooth."""
        if not self._tv.can_use_bluetooth():
            print(" У этого телевизора нет Bluetooth модуля")
            return
        try:
            new_status = self._tv.toggle_bluetooth()
            status_text = "включен" if new_status else "выключен"
            print(f" Bluetooth {status_text}")
        except Exception as e:
            print(f" Ошибка: {e}")
    
    def connect_hdmi(self, port: int, device: str) -> None:
        """
        Подключение HDMI устройства.
        
        Args:
            port: Номер порта
            device: Название устройства
        """
        if not self._tv.can_connect_hdmi():
            print(" У этого телевизора нет HDMI портов")
            return
        try:
            self._tv.connect_hdmi(port, device)
            print(f" Устройство {device} подключено к HDMI {port}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def disconnect_hdmi(self, port: int) -> None:
        """
        Отключение HDMI устройства.
        
        Args:
            port: Номер порта
        """
        if not self._tv.can_connect_hdmi():
            print("!!! У этого телевизора нет HDMI портов!!!")
            return
        try:
            device = self._tv.disconnect_hdmi(port)
            print(f" Устройство {device} отключено от HDMI {port}")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def update_software(self) -> None:
        """Обновление ПО (только в режиме Smart TV)."""
        if not self._tv.can_update_software():
            print("!!! Этот телевизор не поддерживает Smart TV !!!")
            return
        try:
            result = self._tv.update_software()
            if result:
                print(f" ПО обновлено до версии {result:.1f}")
            else:
                print(" Текущая версия ПО актуальна")
        except TVError as e:
            print(f" Ошибка: {e}")
    
    def show_status(self) -> None:
        """Показать текущее состояние телевизора."""
        status = self._tv.get_status()
        
        print("\n" + "="*60)
        print(f"СОСТОЯНИЕ ТЕЛЕВИЗОРА")
        print("="*60)
        print(f"Питание: {'1 ВКЛ' if status['is_on'] else '0 ВЫКЛ'}")
        print(f"Режим: {status['mode']}")
        
        if status['is_on']:
            if status['mode'] == "Кабельное ТВ":
                print(f"Канал: {status['current_channel']}")
            elif status['mode'] == "HDMI" and status['current_hdmi_port']:
                port = status['current_hdmi_port']
                device = status['hdmi_devices'].get(port, "Неизвестно")
                print(f"HDMI {port}: {device}")
            
            print(f"\nИзображение:")
            print(f"  Яркость: {status['brightness']}")
            print(f"  Контраст: {status['contrast']}")
            print(f"\nЗвук:")
            print(f"  Громкость: {status['volume']}")
            print(f"  Сабвуфер: {'ВКЛ' if status['subwoofer'] else 'ВЫКЛ'}")
            print(f"  Эквалайзер: ВЧ={status['equalizer']['high']}, "
                  f"СЧ={status['equalizer']['mid']}, НЧ={status['equalizer']['low']}")
            print(f"\nСеть:")
            if status['has_wifi']:
                print(f"  Wi-Fi: {' ВКЛ' if status['wifi'] else ' ВЫКЛ'}")
            else:
                print("  Wi-Fi:  НЕТ МОДУЛЯ")
            
            if status['has_bluetooth']:
                print(f"  Bluetooth: {' ВКЛ' if status['bluetooth'] else ' ВЫКЛ'}")
            else:
                print("  Bluetooth:  НЕТ МОДУЛЯ")
            
            print(f"\nHDMI устройства:")
            if status['has_hdmi']:
                if status['hdmi_devices']:
                    for port, device in status['hdmi_devices'].items():
                        print(f"  HDMI {port}: {device}")
                else:
                    print("  Нет подключенных устройств")
            else:
                print("  НЕТ ПОРТОВ")
            print(f"\nВерсия ПО: {status['software_version']:.1f}")
        print("="*60)
    
    def show_mode_info(self) -> None:
        """Показать информацию о текущем режиме."""
        status = self._tv.get_status()
        
        print(f"\n Текущий режим: {status['mode']}")
        if status['mode'] == "Кабельное ТВ":
            print(f"   Канал: {status['current_channel']}")
            print("   Доступно: переключение каналов, настройки")
        elif status['mode'] == "HDMI" and status['current_hdmi_port']:
            port = status['current_hdmi_port']
            device = status['hdmi_devices'].get(port, "Неизвестно")
            print(f"   Порт HDMI {port}: {device}")
            print("   Доступно: настройки изображения и звука")
        elif status['mode'] == "Smart TV":
            print("   Доступно: приложения, настройки, обновление ПО")
            print("   !!! Недоступно: переключение каналов !!!")