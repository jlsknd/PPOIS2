"""
Сервис для управления телевизором и пультом.
"""
from typing import Optional, Dict, Any, List
from src.models.television import Television, TvSource, ChannelList
from src.models.remote import RemoteControl
from src.storage.tv_repository import TVRepository
from src.utils.exceptions import (
    TelevisionError, PowerStateError, SourceError,
    ChannelError, SettingsError
)


class TVService:
    """
    Сервис, предоставляющий высокоуровневые операции с телевизором.
    """
    
    def __init__(self, television: Television) -> None:
        self.tv = television
        self.remote = RemoteControl(television)
    
    def _save_state(self) -> None:
        """Сохраняет текущее состояние телевизора в JSON, не удаляя другие"""
        repo = TVRepository("data/televisions.json")
        
        # Загружаем все существующие телевизоры
        all_tvs = repo.load_all()
        
        # Обновляем текущий телевизор в списке
        found = False
        for i, tv in enumerate(all_tvs):
            if tv.name == self.tv.name:
                all_tvs[i] = self.tv
                found = True
                break
        
        # Если телевизор не найден (новый), добавляем его
        if not found:
            all_tvs.append(self.tv)
        
        # Сохраняем ВСЕ телевизоры обратно в файл
        repo.save_all(all_tvs)
    
    def execute_command(self, command: str, *args, **kwargs) -> str:
        """
        Выполняет команду, переданную из CLI.
        Возвращает строку результата для вывода пользователю.
        """
        try:
            # ===== Питание =====
            if command == "power_on":
                self.remote.power_on()
                self._save_state()
                return "[OK] Телевизор включен"
            
            elif command == "power_off":
                self.remote.power_off()
                self._save_state()
                return "[OK] Телевизор выключен"
            
            # ===== Источники =====
            elif command == "source_tv":
                self.remote.switch_to_tv()
                self._save_state()
                return "[OK] Переключено на кабельное ТВ"
            
            elif command == "source_smart":
                self.remote.switch_to_smart_tv()
                self._save_state()
                return "[OK] Переключено на Smart TV"
            
            # ===== Каналы =====
            elif command == "channel":
                channel = args[0]
                ch = self.remote.change_channel(channel)
                self._save_state()
                return f"[OK] Переключение на канал {ch.number}. {ch.name} ({ch.genre})"
            
            elif command == "channel_up":
                ch = self.remote.channel_up()
                self._save_state()
                if ch:
                    return f"[OK] Переключение на канал {ch.number}. {ch.name} ({ch.genre})"
                return "[WARN] Не удалось переключить канал"
            
            elif command == "channel_down":
                ch = self.remote.channel_down()
                self._save_state()
                if ch:
                    return f"[OK] Переключение на канал {ch.number}. {ch.name} ({ch.genre})"
                return "[WARN] Не удалось переключить канал"
            
            elif command == "channels":
                channels = self.remote.get_all_channels()
                result = ["\nСПИСОК КАНАЛОВ:"]
                for ch in channels:
                    result.append(f"  {ch['number']:3}. {ch['name']} ({ch['genre']})")
                return "\n".join(result)
            
            # ===== Громкость =====
            elif command == "volume":
                if not args:
                    return f"Текущая громкость: {self.tv.audio.volume}"
                level = args[0]
                self.remote.set_volume(level)
                self._save_state()
                return f"[OK] Громкость установлена на {level}"
            
            elif command == "volume_up":
                self.remote.volume_up()
                self._save_state()
                return f"[OK] Громкость: {self.tv.audio.volume}"
            
            elif command == "volume_down":
                self.remote.volume_down()
                self._save_state()
                return f"[OK] Громкость: {self.tv.audio.volume}"
            
            # ===== Изображение =====
            elif command == "brightness":
                if not args:
                    return f"Текущая яркость: {self.tv.screen.brightness}"
                level = args[0]
                self.remote.adjust_brightness(level)
                self._save_state()
                return f"[OK] Яркость установлена на {level}"
            
            elif command == "contrast":
                if not args:
                    return f"Текущий контраст: {self.tv.screen.contrast}"
                level = args[0]
                self.remote.adjust_contrast(level)
                self._save_state()
                return f"[OK] Контраст установлен на {level}"
            
            # ===== Эквалайзер =====
            elif command == "equalizer":
                if not args or len(args) < 3:
                    eq = self.tv.audio.equalizer
                    return f"Эквалайзер: НЧ={eq.low}, СЧ={eq.mid}, ВЧ={eq.high}"
                low, mid, high = map(int, args[:3])
                self.remote.set_equalizer(low, mid, high)
                self._save_state()
                return f"[OK] Эквалайзер: НЧ={low}, СЧ={mid}, ВЧ={high}"
            
            # ===== Сабвуфер =====
            elif command == "subwoofer":
                if not args:
                    status = "подключен" if self.tv.audio.subwoofer_connected else "не подключен"
                    return f"Сабвуфер: {status}"
                state = args[0].lower()
                if state in ["on", "off"]:
                    self.remote.connect_subwoofer(state == "on")
                    self._save_state()
                    return f"[OK] Сабвуфер {state == 'on' and 'подключен' or 'отключен'}"
                return "[ERROR] Используйте: subwoofer on|off"
            
            # ===== Bluetooth =====
            elif command == "bluetooth":
                return self._handle_bluetooth_commands(args)
            
            # ===== Wi-Fi =====
            elif command == "wifi":
                if not args:
                    status = "вкл" if self.tv._wifi_enabled else "выкл"
                    return f"Wi-Fi: {status}"
                state = args[0].lower()
                if state in ["on", "off"]:
                    if state == "on":
                        self.remote.enable_wifi()
                    else:
                        self.remote.disable_wifi()
                    self._save_state()
                    return f"[OK] Wi-Fi {state == 'on' and 'включен' or 'выключен'}"
                return "[ERROR] Используйте: wifi on|off"
            
            # ===== Обновление ПО =====
            elif command == "update":
                result = self.remote.update_software()
                self._save_state()
                return f"[OK] {result}"
            
            # ===== Статус =====
            elif command == "status":
                return self._format_status(self.tv.get_status())
            
            elif command == "specs":
                return self._format_specifications()
            
            elif command == "now":
                if self.tv.is_on and self.tv._current_source == TvSource.TV:
                    return f"Сейчас: {self.tv.current_channel_info}"
                elif self.tv.is_on:
                    return f"Текущий источник: {self.tv._current_source.value}"
                else:
                    return "Телевизор выключен"
            
            else:
                return f"[ERROR] Неизвестная команда: {command}"
                
        except TelevisionError as e:
            return f"[ERROR] {e}"
        except ValueError as e:
            return f"[ERROR] Неверные параметры: {e}"
        except Exception as e:
            return f"[ERROR] Непредвиденная ошибка: {e}"
    
    def _handle_bluetooth_commands(self, args) -> str:
        """Обрабатывает Bluetooth команды"""
        if not self.tv.specs.has_bluetooth:
            return "[ERROR] Данная модель не поддерживает Bluetooth"
        
        if not args:
            status = "включен" if self.tv._bluetooth_enabled else "выключен"
            return f"Bluetooth: {status}"
        
        subcommand = args[0].lower()
        
        if subcommand == "on":
            self.remote.enable_bluetooth()
            self._save_state()
            return "[OK] Bluetooth включен"
        
        elif subcommand == "off":
            self.remote.disable_bluetooth()
            self._save_state()
            return "[OK] Bluetooth выключен"
        
        elif subcommand == "scan":
            if not self.tv._bluetooth_enabled:
                return "[ERROR] Сначала включите Bluetooth (bluetooth on)"
            return "Найденные устройства:\n  1. Sony WH-1000XM4 (наушники)\n  2. JBL Charge 5 (колонка)\n  3. AirPods Pro (наушники)\nИспользуйте: bluetooth pair <название>"
        
        elif subcommand == "pair":
            if len(args) < 2:
                return "[ERROR] Укажите название устройства"
            device_name = args[1]
            self._save_state()
            return f"[OK] Устройство {device_name} сопряжено"
        
        elif subcommand == "connect":
            if len(args) < 2:
                return "[ERROR] Укажите название устройства"
            device_name = args[1]
            self._save_state()
            return f"[OK] Подключено к {device_name}"
        
        elif subcommand == "disconnect":
            if len(args) < 2:
                return "[ERROR] Укажите название устройства"
            device_name = args[1]
            self._save_state()
            return f"[OK] Отключено от {device_name}"
        
        elif subcommand == "devices":
            return "Сопряженные устройства:\n  - Нет устройств"
        
        else:
            return "[ERROR] Неизвестная Bluetooth команда"
    
    def _format_status(self, status: Dict[str, Any]) -> str:
        """Форматирует статус для вывода в CLI"""
        lines = [
            f"\n{'='*60}",
            f"  {status['name']}",
            f"{'='*60}",
            f"Состояние: {status['power']}",
            f"Источник: {status['source']}",
        ]
        
        if status.get('current_channel'):
            ch = status['current_channel']
            lines.append(f"Текущий канал: {ch['number']}. {ch['name']} ({ch['genre']})")
        
        lines.append(f"\nИзображение:")
        lines.append(f"  Яркость: {status['screen']['brightness']}")
        lines.append(f"  Контраст: {status['screen']['contrast']}")
        
        lines.append(f"\nЗвук:")
        lines.append(f"  Громкость: {status['audio']['volume']}")
        lines.append(f"  Сабвуфер: {'подключен' if status['audio']['subwoofer'] else 'отключен'}")
        eq = status['audio']['equalizer']
        lines.append(f"  Эквалайзер: НЧ={eq['low']}, СЧ={eq['mid']}, ВЧ={eq['high']}")
        
        lines.append(f"\nWi-Fi: {'включен' if status['wifi']['enabled'] else 'выключен'}")
        lines.append(f"Bluetooth: {'включен' if status['bluetooth']['enabled'] else 'выключен'}")
        
        if status['smart_tv']['supported']:
            lines.append(f"Smart TV: {status['smart_tv']['os']} (версия {status['smart_tv']['version']})")
        
        lines.append(f"{'='*60}")
        return "\n".join(lines)
    
    def _format_specifications(self) -> str:
        """Форматирует технические характеристики для вывода"""
        specs = self.tv.specs
        screen = specs.screen
        audio = specs.audio
        
        lines = [
            f"\n{'='*60}",
            f"ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ: {specs.model_name}",
            f"{'='*60}",
            f"\nЭКРАН:",
            f"  Технология: {screen.technology.value}",
            f"  Диагональ: {screen.diagonal}\"",
            f"  Разрешение: {screen.resolution_width}x{screen.resolution_height}",
            f"  Время отклика: {screen.response_time_ms} мс",
            f"  Покрытие: {screen.coverage.value}",
            f"  Частота обновления: {screen.refresh_rate_hz} Гц",
            f"  Яркость: {screen.brightness_nits} нит",
            f"\nАУДИО:",
            f"  Динамики: {audio.speakers_count} x {audio.speaker_power_w} Вт",
            f"  Сабвуфер: {'есть выход' if audio.has_subwoofer_output else 'нет выхода'}",
            f"\nФУНКЦИИ:",
            f"  Smart TV: {'да' if specs.has_smart_tv else 'нет'}",
            f"  Wi-Fi: {'да' if specs.has_wifi else 'нет'}",
            f"  Bluetooth: {'да' if specs.has_bluetooth else 'нет'}",
            f"\nРАЗЪЕМЫ:",
            f"  HDMI: {specs.hdmi_ports}",
            f"  USB: {specs.usb_ports}",
            f"  LAN: {specs.lan_ports}",
            f"\nФИЗИЧЕСКИЕ ХАРАКТЕРИСТИКИ:",
            f"  Цвет: {specs.color}",
            f"  Вес: {specs.weight_kg} кг",
            f"  Срок службы: {specs.service_life_years} лет",
        ]
        
        if specs.has_smart_tv:
            lines.append(f"\nОПЕРАЦИОННАЯ СИСТЕМА:")
            lines.append(f"  ОС: {specs.operating_system.value}")
            lines.append(f"  Версия: {specs.os_version}")
        
        lines.append(f"{'='*60}")
        return "\n".join(lines)