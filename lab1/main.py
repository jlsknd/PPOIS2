#!/usr/bin/env python3
"""
Главный модуль программы с CLI интерфейсом.
"""

import sys
import json
import os
from typing import Optional, Dict, List, Any

from src.models.television import (
    Television, TechnicalSpecifications, ScreenTechnology,
    ScreenCoverage, OperatingSystem, TVMode
)
from src.models.remote import RemoteControl
from src.exceptions.tv_exceptions import TVError


# файл для сохранения данных
SAVE_FILE = "tvs.json"


def get_int_input(prompt: str, min_val: int = 1, max_val: int = 999, allow_zero: bool = False) -> int:
    """
    Получение целочисленного ввода от пользователя с проверкой диапазона.
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print(" Ввод не может быть пустым")
                continue
            
            num = int(value)
            
            if allow_zero and num == 0:
                return num
            
            if min_val <= num <= max_val:
                return num
            else:
                print(f" Введите число от {min_val} до {max_val}")
        except ValueError:
            print(" Ошибка: введите целое число")


def get_float_input(prompt: str, min_val: float = 0.1, allow_zero: bool = False) -> float:
    """
    Получение числа с плавающей точкой от пользователя.
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print(" Ввод не может быть пустым")
                continue
            
            num = float(value)
            
            if allow_zero and num == 0:
                return num
            
            if num >= min_val:
                return num
            else:
                print(f" Введите число не меньше {min_val}")
        except ValueError:
            print(" Ошибка: введите число")


def get_yes_no_input(prompt: str) -> bool:
    """
    Получение ответа да/нет от пользователя.
    """
    while True:
        value = input(prompt).strip().lower()
        if not value:
            print(" Ввод не может быть пустым")
            continue
        
        if value in ["да", "yes", "y", "1", "true"]:
            return True
        elif value in ["нет", "no", "n", "0", "false"]:
            return False
        else:
            print(" Введите 'да' или 'нет'")


def get_menu_choice(prompt: str, max_choice: int, show_zero: bool = True) -> str:
    """
    Получение выбора из меню с проверкой.
    """
    while True:
        choice = input(prompt).strip()
        if not choice:
            print("Ввод не может быть пустым")
            continue
        
        if show_zero and choice == "0":
            return choice
        
        try:
            num = int(choice)
            if 1 <= num <= max_choice:
                return choice
            else:
                range_text = f"от 1 до {max_choice}"
                if show_zero:
                    range_text += " или 0"
                print(f" Выберите пункт {range_text}")
        except ValueError:
            print(" Ошибка: введите число")


class TVManager:
    """Класс для управления несколькими телевизорами."""
    
    def __init__(self) -> None:
        """Инициализация менеджера."""
        self._tvs: Dict[str, Television] = {}
        self._current_tv_name: Optional[str] = None
        self._remote: Optional[RemoteControl] = None
        self._load_from_file()  # загружаем сохраненные телевизоры
    
    def _save_to_file(self) -> None:
        """Сохраняет все телевизоры в файл."""
        try:
            data = []
            for name, tv in self._tvs.items():
                specs = tv.specs
                # преобразуем enum в строки для сохранения
                tv_data = {
                    "name": name,
                    "specs": {
                        "model_name": specs.model_name,
                        "technology": specs.technology.value,
                        "screen_diagonal": specs.screen_diagonal,
                        "resolution": list(specs.resolution),
                        "response_time": specs.response_time,
                        "screen_coverage": specs.screen_coverage.value,
                        "refresh_rate": specs.refresh_rate,
                        "speakers_count": specs.speakers_count,
                        "speaker_power": specs.speaker_power,
                        "hdmi_ports": specs.hdmi_ports,
                        "usb_ports": specs.usb_ports,
                        "lan_ports": specs.lan_ports,
                        "has_wifi": specs.has_wifi,
                        "has_bluetooth": specs.has_bluetooth,
                        "has_smart_tv": specs.has_smart_tv,
                        "color": specs.color,
                        "weight": specs.weight,
                        "lifespan": specs.lifespan,
                        "brightness_nit": specs.brightness_nit,
                        "os": specs.operating_system.value if specs.operating_system else None,
                        "os_version": specs.os_version,

                    },
                    "current_tv": (name == self._current_tv_name)  # запоминаем, какой был текущим
                }
                data.append(tv_data)
            
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"!!! Не удалось сохранить данные: {e}")
    
    def _load_from_file(self) -> None:
        """Загружает телевизоры из файла."""
        if not os.path.exists(SAVE_FILE):
            return
        
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_tv_name = None
            
            for tv_data in data:
                try:
                    specs_data = tv_data["specs"]
                    
                    # преобразуем строки обратно в enum
                    tech_map = {
                        "LED": ScreenTechnology.LED,
                        "OLED": ScreenTechnology.OLED,
                        "QLED": ScreenTechnology.QLED,
                        "PDP": ScreenTechnology.PDP,
                        "LCD": ScreenTechnology.LCD
                    }
                    technology = tech_map.get(specs_data["technology"], ScreenTechnology.LED)
                    
                    coverage_map = {
                        "глянцевое": ScreenCoverage.GLOSSY,
                        "полуматовое": ScreenCoverage.SEMI_MATTE,
                        "антибликовое": ScreenCoverage.ANTI_GLARE,
                        "ультра-антибликовое": ScreenCoverage.ULTRA_ANTI_GLARE
                    }
                    coverage = coverage_map.get(specs_data["screen_coverage"], ScreenCoverage.ANTI_GLARE)
                    
                    os_map = {
                        "Android TV": OperatingSystem.ANDROID_TV,
                        "VIDAA": OperatingSystem.VIDAA,
                        "WebOS": OperatingSystem.WEBOS,
                        "Tizen": OperatingSystem.TIZEN,
                        "Яндекс ТВ": OperatingSystem.YANDEX_TV,
                        "Салют ТВ": OperatingSystem.SALUT_TV
                    }
                    operating_system = os_map.get(specs_data["os"]) if specs_data["os"] else None
                    
                    specs = TechnicalSpecifications(
                        model_name=specs_data["model_name"],
                        technology=technology,
                        screen_diagonal=specs_data["screen_diagonal"],
                        resolution=tuple(specs_data["resolution"]),
                        response_time=specs_data["response_time"],
                        screen_coverage=coverage,
                        refresh_rate=specs_data["refresh_rate"],
                        speakers_count=specs_data["speakers_count"],
                        speaker_power=specs_data["speaker_power"],
                        hdmi_ports=specs_data["hdmi_ports"],
                        usb_ports=specs_data["usb_ports"],
                        lan_ports=specs_data["lan_ports"],
                        has_wifi=specs_data["has_wifi"],
                        has_bluetooth=specs_data["has_bluetooth"],
                        has_smart_tv=specs_data["has_smart_tv"],
                        color=specs_data["color"],
                        weight=specs_data["weight"],
                        lifespan=specs_data["lifespan"],
                        brightness_nit=specs_data["brightness_nit"],
                        operating_system=operating_system,
                        os_version=specs_data["os_version"],
                     
                    )
                    
                    tv = Television(specs)
                    self._tvs[tv_data["name"]] = tv
                    
                    # запоминаем, какой телевизор был текущим
                    if tv_data.get("current_tv", False):
                        current_tv_name = tv_data["name"]
                    
                except Exception as e:
                    print(f" Ошибка при загрузке телевизора: {e}")
                    continue
            
            # восстанавливаем текущий телевизор
            if current_tv_name and current_tv_name in self._tvs:
                self._current_tv_name = current_tv_name
                self._remote = RemoteControl(self._tvs[current_tv_name])
            elif self._tvs:
                # если текущий не найден, выбираем первый
                self._current_tv_name = list(self._tvs.keys())[0]
                self._remote = RemoteControl(self._tvs[self._current_tv_name])
            
            if self._tvs:
                print(f" Загружено {len(self._tvs)} телевизоров из файла")
            
        except Exception as e:
            print(f"!!! Не удалось загрузить данные: {e}")
    
    def add_tv(self) -> None:
        """Добавление нового телевизора."""
        print("\n" + "="*60)
        print("ДОБАВЛЕНИЕ НОВОГО ТЕЛЕВИЗОРА")
        print("="*60)
        
        try:
            # Основная информация
            while True:
                name = input("Название модели: ").strip()
                if not name:
                    print(" Название не может быть пустым")
                    continue
                if name in self._tvs:
                    print(f" Телевизор '{name}' уже существует")
                    continue
                break
            
            print("\nТехнология экрана:")
            print("1. LED")
            print("2. OLED")
            print("3. QLED")
            print("4. PDP")
            print("5. LCD")
            tech_choice = get_menu_choice("Выберите (1-5): ", 5, show_zero=False)
            
            tech_map = {
                "1": ScreenTechnology.LED,
                "2": ScreenTechnology.OLED,
                "3": ScreenTechnology.QLED,
                "4": ScreenTechnology.PDP,
                "5": ScreenTechnology.LCD
            }
            technology = tech_map[tech_choice]
            
            # Диагональ
            diagonal = get_float_input("Диагональ экрана (дюймы): ", min_val=1.0)
            
            # Разрешение
            print("\nРазрешение экрана:")
            print("1. HD (1280x720)")
            print("2. Full HD (1920x1080)")
            print("3. 4K Ultra HD (3840x2160)")
            res_choice = get_menu_choice("Выберите (1-3): ", 3, show_zero=False)
            
            resolution_map = {
                "1": (1280, 720),
                "2": (1920, 1080),
                "3": (3840, 2160)
            }
            resolution = resolution_map[res_choice]
            
            # Время отклика
            response_time = get_int_input("Время отклика (мс): ", min_val=1)
            
            # Покрытие экрана
            print("\nПокрытие экрана:")
            print("1. Глянцевое")
            print("2. Полуматовое")
            print("3. Антибликовое")
            print("4. Ультра-антибликовое")
            cov_choice = get_menu_choice("Выберите (1-4): ", 4, show_zero=False)
            
            coverage_map = {
                "1": ScreenCoverage.GLOSSY,
                "2": ScreenCoverage.SEMI_MATTE,
                "3": ScreenCoverage.ANTI_GLARE,
                "4": ScreenCoverage.ULTRA_ANTI_GLARE
            }
            coverage = coverage_map[cov_choice]
            
            # Частота обновления
            refresh_rate = get_int_input("Частота обновления (Гц): ", min_val=1)
            
            # Количество динамиков
            speakers = get_int_input("Количество динамиков: ", min_val=1)
            
            # Мощность динамика
            speaker_power = get_int_input("Мощность динамика (Вт): ", min_val=1)
            
            # Количество портов (может быть 0)
            print("\n(Можно ввести 0, если портов нет)")
            hdmi_ports = get_int_input("Количество HDMI портов: ", min_val=0, max_val=10, allow_zero=True)
            usb_ports = get_int_input("Количество USB портов: ", min_val=0, max_val=10, allow_zero=True)
            lan_ports = get_int_input("Количество LAN портов: ", min_val=0, max_val=5, allow_zero=True)
            
            wifi = get_yes_no_input("Встроенный Wi-Fi (да/нет): ")
            bluetooth = get_yes_no_input("Встроенный Bluetooth (да/нет): ")
            smart_tv = get_yes_no_input("Поддержка Smart TV (да/нет): ")
            
            while True:
                color = input("Цвет телевизора: ").strip()
                if not color:
                    print(" Цвет не может быть пустым")
                    continue
                break
            
            # Вес
            weight = get_float_input("Вес (кг): ", min_val=0.1)
            
            # Срок службы
            lifespan = get_int_input("Срок службы (лет): ", min_val=1)
            
            # Яркость
            brightness = get_int_input("Яркость (нит): ", min_val=1)
            
            # Операционная система (если есть Smart TV)
            operating_system = None
            os_version = None
            if smart_tv:
                print("\nОперационная система:")
                print("1. Android TV")
                print("2. VIDAA")
                print("3. WebOS")
                print("4. Tizen")
                print("5. Яндекс ТВ")
                print("6. Салют ТВ")
                os_choice = get_menu_choice("Выберите (1-6): ", 6, show_zero=False)
                
                os_map = {
                    "1": OperatingSystem.ANDROID_TV,
                    "2": OperatingSystem.VIDAA,
                    "3": OperatingSystem.WEBOS,
                    "4": OperatingSystem.TIZEN,
                    "5": OperatingSystem.YANDEX_TV,
                    "6": OperatingSystem.SALUT_TV
                }
                operating_system = os_map[os_choice]
                
                while True:
                    os_version = input("Версия ОС: ").strip()
                    if not os_version:
                        print(" Введите версию ОС")
                        continue
                    break
            
            # Создание характеристик
            specs = TechnicalSpecifications(
                model_name=name,
                technology=technology,
                screen_diagonal=diagonal,
                resolution=resolution,
                response_time=response_time,
                screen_coverage=coverage,
                refresh_rate=refresh_rate,
                speakers_count=speakers,
                speaker_power=speaker_power,
                hdmi_ports=hdmi_ports,
                usb_ports=usb_ports,
                lan_ports=lan_ports,
                has_wifi=wifi,
                has_bluetooth=bluetooth,
                has_smart_tv=smart_tv,
                color=color,
                weight=weight,
                lifespan=lifespan,
                brightness_nit=brightness,
                operating_system=operating_system,
                os_version=os_version
            )
            
            # Создание телевизора
            tv = Television(specs)
            self._tvs[name] = tv
            
            # Сохраняем в файл
            self._save_to_file()
            
            print(f"\n Телевизор '{name}' успешно добавлен и сохранен!")
            
            # Если это первый телевизор, делаем его текущим
            if len(self._tvs) == 1:
                self._current_tv_name = name
                self._remote = RemoteControl(tv)
                print(f" Телевизор '{name}' выбран для управления")
            
        except Exception as e:
            print(f" Непредвиденная ошибка: {e}")
    
    def list_tvs(self) -> bool:
        """Вывод списка всех телевизоров."""
        if not self._tvs:
            print("\n Нет добавленных телевизоров")
            return False
        
        print("\n" + "="*60)
        print("СПИСОК ТЕЛЕВИЗОРОВ")
        print("="*60)
        
        for i, (name, tv) in enumerate(self._tvs.items(), 1):
            marker = "*" if name == self._current_tv_name else "  "
            power = " ВКЛ" if tv.is_on else " ВЫКЛ"
            mode = tv.mode.value
            print(f"{marker} {i}. {name} - {power} - {mode}")
        
        return True
    
    def select_tv(self) -> None:
        """Выбор текущего телевизора."""
        if not self.list_tvs():
            return
        
        while True:
            try:
                choice = input("\nВведите номер телевизора (0 для отмены): ").strip()
                if not choice:
                    print(" Введите номер")
                    continue
                
                if choice == "0":
                    return
                
                idx = int(choice) - 1
                if 0 <= idx < len(self._tvs):
                    name = list(self._tvs.keys())[idx]
                    self._current_tv_name = name
                    self._remote = RemoteControl(self._tvs[name])
                    self._save_to_file()  # сохраняем выбор
                    print(f" Выбран телевизор: {name}")
                    return
                else:
                    print(f" Введите число от 1 до {len(self._tvs)}")
            except ValueError:
                print(" Ошибка: введите число")
    
    def remove_tv(self) -> None:
        """Удаление телевизора."""
        if not self.list_tvs():
            return
        
        while True:
            try:
                choice = input("\nВведите номер телевизора для удаления (0 для отмены): ").strip()
                if not choice:
                    print(" Введите номер")
                    continue
                
                if choice == "0":
                    return
                
                idx = int(choice) - 1
                if 0 <= idx < len(self._tvs):
                    name = list(self._tvs.keys())[idx]
                    
                    confirm = get_yes_no_input(f"Удалить телевизор '{name}'? (да/нет): ")
                    if confirm:
                        del self._tvs[name]
                        
                        if self._current_tv_name == name:
                            self._current_tv_name = None
                            self._remote = None
                        
                        self._save_to_file()  # сохраняем после удаления
                        print(f" Телевизор '{name}' удален")
                    return
                else:
                    print(f" Введите число от 1 до {len(self._tvs)}")
            except ValueError:
                print(" Ошибка: введите число")
    
    def get_current_tv(self) -> Optional[Television]:
        """Получение текущего телевизора."""
        if not self._tvs:
            print("\n Нет добавленных телевизоров")
            return None
        
        if not self._current_tv_name:
            print("\n Сначала выберите телевизор")
            return None
        
        if self._current_tv_name not in self._tvs:
            print("\n Текущий телевизор не найден")
            self._current_tv_name = None
            self._remote = None
            return None
        
        return self._tvs[self._current_tv_name]
    
    def run_control_menu(self) -> None:
        """Меню управления текущим телевизором."""
        tv = self.get_current_tv()
        if not tv or not self._remote:
            return
        
        while True:
            status = tv.get_status()
            
            print("\n" + "="*60)
            print(f"УПРАВЛЕНИЕ ТЕЛЕВИЗОРОМ: {self._current_tv_name}")
            print("="*60)
            print(f"Состояние: {' ВКЛ' if tv.is_on else ' ВЫКЛ'}")
            print(f"Режим: {status['mode']}")
            
            if tv.is_on:
                print(f"Громкость: {tv.get_volume()}")
                if status['mode'] == "Кабельное ТВ":
                    print(f"Канал: {tv.current_channel}")
                elif status['mode'] == "HDMI" and status['current_hdmi_port']:
                    port = status['current_hdmi_port']
                    device = status['hdmi_devices'].get(port, "Неизвестно")
                    print(f"HDMI {port}: {device}")
            
            print("-"*60)
            print("РЕЖИМЫ:")
            print("1.  Кабельное ТВ")
            print("2.  Smart TV")
            if tv.can_connect_hdmi() and tv.get_hdmi_devices():
                print("3.  HDMI (выбрать порт)")
            print("-"*60)
            print("УПРАВЛЕНИЕ:")
            print("4.  Вкл/Выкл")
            
            if tv.is_on and status['mode'] == "Кабельное ТВ":
                print("\nКАНАЛЫ:")
                print("5.  Канал вверх")
                print("6.  Канал вниз")
                print("7.  Выбрать канал")
            
            print("\nГРОМКОСТЬ:")
            print("8.  Громкость +5")
            print("9.  Громкость -5")
            print("10.  Установить громкость")
            print("11.  Без звука")
            
            print("\nНАСТРОЙКИ:")
            print("12.  Изображение")
            print("13.  Звук")
            print("14.  Сеть")
            print("15.  Состояние")
            print("16.  Технические характеристики")
            
            if tv.is_on and status['mode'] == "Smart TV" and tv.can_update_software():
                print("\nSMART TV:")
                print("17.  Обновить ПО")
            
            if tv.is_on and status['mode'] != "Smart TV" and tv.can_connect_hdmi():
                print("\nHDMI:")
                if tv.can_connect_hdmi():
                    print("18. 🔌 Подключить HDMI устройство")
                    if tv.get_hdmi_devices():
                        print("19. 🔌 Отключить HDMI устройство")
            
            print("\n0. ↩ Назад")
            print("="*60)
            
            # Определяем максимальный пункт меню
            max_choice = 16
            if tv.is_on and status['mode'] == "Smart TV" and tv.can_update_software():
                max_choice = 17
            if tv.is_on and status['mode'] != "Smart TV" and tv.can_connect_hdmi():
                max_choice = 18
                if tv.get_hdmi_devices():
                    max_choice = 19
            
            choice = get_menu_choice("Выберите действие: ", max_choice, show_zero=True)
            
            if choice == "0":
                self._save_to_file()  # сохраняем перед выходом
                break
            elif choice == "1":
                self._remote.tv_mode()
            elif choice == "2":
                self._remote.smart_tv_mode()
            elif choice == "3" and tv.can_connect_hdmi() and tv.get_hdmi_devices():
                try:
                    print("Доступные HDMI порты:")
                    for port, device in tv.get_hdmi_devices().items():
                        print(f"  {port}. {device}")
                    port = get_int_input("Номер HDMI порта: ", 1, tv.specs.hdmi_ports)
                    self._remote.hdmi_mode(port)
                except ValueError:
                    print(" Ошибка ввода")
            elif choice == "4":
                self._remote.power()
            elif choice == "5" and tv.is_on and status['mode'] == "Кабельное ТВ":
                self._remote.channel_up()
            elif choice == "6" and tv.is_on and status['mode'] == "Кабельное ТВ":
                self._remote.channel_down()
            elif choice == "7" and tv.is_on and status['mode'] == "Кабельное ТВ":
                ch = get_int_input("Номер канала (1-999): ", 1, 999)
                self._remote.set_channel(ch)
            elif choice == "8":
                self._remote.volume_up()
            elif choice == "9":
                self._remote.volume_down()
            elif choice == "10":
                vol = get_int_input("Громкость (0-100): ", 0, 100)
                self._remote.set_volume(vol)
            elif choice == "11":
                self._remote.mute()
            elif choice == "12":
                self._picture_settings_menu()
            elif choice == "13":
                self._audio_settings_menu()
            elif choice == "14":
                self._network_settings_menu()
            elif choice == "15":
                self._remote.show_status()
            elif choice == "16":
                tv.show_specs()
            elif choice == "17" and tv.is_on and status['mode'] == "Smart TV" and tv.can_update_software():
                self._remote.update_software()
            elif choice == "18" and tv.is_on and status['mode'] != "Smart TV" and tv.can_connect_hdmi():
                self._hdmi_connect_menu()
            elif choice == "19" and tv.is_on and status['mode'] != "Smart TV" and tv.can_connect_hdmi() and tv.get_hdmi_devices():
                self._hdmi_disconnect_menu()
    
    def _picture_settings_menu(self) -> None:
        """Меню настроек изображения."""
        if not self._remote:
            return
        
        tv = self.get_current_tv()
        if not tv or not tv.is_on:
            print(" Телевизор выключен")
            return
        
        while True:
            print("\n--- НАСТРОЙКИ ИЗОБРАЖЕНИЯ ---")
            print(f"Текущая яркость: {tv.get_brightness()}")
            print(f"Текущий контраст: {tv.get_contrast()}")
            print()
            print("1. Изменить яркость")
            print("2. Изменить контраст")
            print("0. Назад")
            
            choice = get_menu_choice("Выберите: ", 2, show_zero=True)
            
            if choice == "0":
                break
            elif choice == "1":
                val = get_int_input("Яркость (0-100): ", 0, 100)
                self._remote.set_brightness(val)
            elif choice == "2":
                val = get_int_input("Контраст (0-100): ", 0, 100)
                self._remote.set_contrast(val)
    
    def _audio_settings_menu(self) -> None:
        """Меню настроек звука."""
        if not self._remote:
            return
        
        tv = self.get_current_tv()
        if not tv or not tv.is_on:
            print(" Телевизор выключен")
            return
        
        while True:
            print("\n--- НАСТРОЙКИ ЗВУКА ---")
            print(f"Громкость: {tv.get_volume()}")
            print(f"Сабвуфер: {'да' if tv.is_subwoofer_connected() else 'нет'}")
            eq = tv.get_equalizer()
            print(f"Эквалайзер: ВЧ={eq['high']}, СЧ={eq['mid']}, НЧ={eq['low']}")
            print()
            print("1. Переключить сабвуфер")
            print("2. Настроить эквалайзер")
            print("0. Назад")
            
            choice = get_menu_choice("Выберите: ", 2, show_zero=True)
            
            if choice == "0":
                break
            elif choice == "1":
                self._remote.toggle_subwoofer()
            elif choice == "2":
                high = get_int_input("Высокие частоты (-100..100): ", -100, 100)
                mid = get_int_input("Средние частоты (-100..100): ", -100, 100)
                low = get_int_input("Низкие частоты (-100..100): ", -100, 100)
                self._remote.set_equalizer(high, mid, low)
    
    def _network_settings_menu(self) -> None:
        """Меню настроек сети."""
        if not self._remote:
            return
        
        tv = self.get_current_tv()
        if not tv or not tv.is_on:
            print(" Телевизор выключен")
            return
        
        while True:
            status = tv.get_status()
            
            print("\n--- НАСТРОЙКИ СЕТИ ---")
            if tv.can_use_wifi():
                wifi_status = "1 ВКЛ" if status['wifi'] else "0 ВЫКЛ"
                print(f"Wi-Fi: {wifi_status}")
            else:
                print("Wi-Fi:  НЕТ МОДУЛЯ")
            
            if tv.can_use_bluetooth():
                bt_status = "1 ВКЛ" if status['bluetooth'] else "0 ВЫКЛ"
                print(f"Bluetooth: {bt_status}")
            else:
                print("Bluetooth:  НЕТ МОДУЛЯ")
            
            print()
            print("1.  Переключить Wi-Fi")
            print("2.  Переключить Bluetooth")
            print("0. Назад")
            
            choice = input("Выберите: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                if tv.can_use_wifi():
                    self._remote.toggle_wifi()
                else:
                    print(" У этого телевизора нет Wi-Fi модуля")
            elif choice == "2":
                if tv.can_use_bluetooth():
                    self._remote.toggle_bluetooth()
                else:
                    print(" У этого телевизора нет Bluetooth модуля")
            else:
                print(" Неверный выбор")
    
    def _hdmi_connect_menu(self) -> None:
        """Меню подключения HDMI устройства."""
        tv = self.get_current_tv()
        if not tv:
            return
        
        if not tv.can_connect_hdmi():
            print(" У этого телевизора нет HDMI портов")
            return
        
        port = get_int_input(f"Номер HDMI порта (1-{tv.specs.hdmi_ports}): ", 1, tv.specs.hdmi_ports)
        
        while True:
            device = input("Название устройства: ").strip()
            if not device:
                print(" Название не может быть пустым")
                continue
            break
        
        self._remote.connect_hdmi(port, device)
        self._save_to_file()  # сохраняем после подключения
    
    def _hdmi_disconnect_menu(self) -> None:
        """Меню отключения HDMI устройства."""
        tv = self.get_current_tv()
        if not tv:
            return
        
        if not tv.can_connect_hdmi():
            print(" У этого телевизора нет HDMI портов")
            return
        
        devices = tv.get_hdmi_devices()
        if not devices:
            print(" Нет подключенных HDMI устройств")
            return
        
        print("Подключенные устройства:")
        for port, device in devices.items():
            print(f"  {port}. {device}")
        
        port = get_int_input("Номер HDMI порта для отключения: ", 1, tv.specs.hdmi_ports)
        self._remote.disconnect_hdmi(port)
        self._save_to_file()  # сохраняем после отключения


def main() -> None:
    """Главная функция программы."""
    manager = TVManager()
    
    print("\n" + "="*60)
    print("ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ ТЕЛЕВИЗОРАМИ")
    print("="*60)
    
    if manager._tvs:
        print(f"\n Загружено {len(manager._tvs)} телевизоров")
    else:
        print("\n Начните с добавления первого телевизора!")
    
    while True:
        print("\n" + "="*60)
        print("ГЛАВНОЕ МЕНЮ")
        print("="*60)
        
        if manager._current_tv_name:
            tv = manager.get_current_tv()
            if tv:
                power = "1 ВКЛ" if tv.is_on else "0 ВЫКЛ"
                mode = tv.mode.value
                print(f"Текущий ТВ: {manager._current_tv_name} - {power} - {mode}")
        else:
            print("Текущий ТВ: не выбран")
        
        print("\n1.  Добавить новый телевизор")
        print("2.  Показать все телевизоры")
        print("3.  Выбрать телевизор")
        print("4.  Удалить телевизор")
        print("5.  Управление текущим телевизором")
        print("0.  Выход")
        print("="*60)
        
        choice = get_menu_choice("Выберите действие: ", 5, show_zero=True)
        
        if choice == "0":
            manager._save_to_file()  # сохраняем перед выходом
            print("\n До свидания!")
            sys.exit(0)
        elif choice == "1":
            manager.add_tv()
        elif choice == "2":
            manager.list_tvs()
        elif choice == "3":
            manager.select_tv()
        elif choice == "4":
            manager.remove_tv()
        elif choice == "5":
            manager.run_control_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n До свидания!")
        sys.exit(0)
    except Exception as e:
        print(f"\n Ошибка: {e}")
        sys.exit(1)