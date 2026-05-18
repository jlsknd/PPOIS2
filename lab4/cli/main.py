#!/usr/bin/env python3
"""
Главный модуль CLI приложения "Модель телевизора".
"""
import sys
import os
import cmd
from typing import Optional, List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.models.television import Television, TvSource
from src.models.screen import Screen, ScreenTechnology, ScreenCoverage, Resolution
from src.models.audio import AudioSystem, Equalizer
from src.models.specs import TechnicalSpecifications, OperatingSystem
from src.services.tv_service import TVService
from src.services.tv_manager import TelevisionManager
from src.utils.exceptions import TelevisionError
from src.utils.input_helpers import input_yes_no


class TelevisionCLI(cmd.Cmd):
    """
    Интерактивный командный интерфейс для управления телевизорами.
    """
    
    intro = """
    ====================================================================
              УПРАВЛЕНИЕ ТЕЛЕВИЗОРАМИ (версия 3.0)
    ====================================================================
    Команды управления телевизорами:
      tv list        - показать список телевизоров
      tv select      - выбрать телевизор из списка
      tv add         - добавить новый телевизор
      tv remove      - удалить текущий телевизор
      tv info        - информация о текущем телевизоре
      tv specs       - технические характеристики

    Команды управления (после выбора телевизора):
      on / off       - включить/выключить
      tv / smart     - переключение источников
      channel N      - переключить канал (например: channel 8)
      ch+ / ch-      - следующий/предыдущий канал
      channels       - показать список всех каналов
      now            - что сейчас идет
      volume N       - установить громкость (0-100)
      vol+ / vol-    - увеличить/уменьшить громкость
      brightness N   - установить яркость (0-100)
      contrast N     - установить контраст (0-100)
      equalizer L M H - эквалайзер (НЧ СЧ ВЧ от -100 до 100)
      subwoofer on|off - подключение сабвуфера
      bluetooth      - управление Bluetooth
      wifi on|off    - управление Wi-Fi
      update         - обновить ПО
      status         - показать состояние

    Служебные команды:
      help / ?       - справка
      exit / quit    - выход
    ====================================================================
    """
    prompt = "TV> "
    
    def __init__(self, tv_manager: TelevisionManager) -> None:
        super().__init__()
        self.manager = tv_manager
        self.current_service: Optional[TVService] = None
        self._update_prompt()
    
    def _update_prompt(self) -> None:
        tv_name = self.manager.current_tv_name
        self.prompt = f"[{tv_name}]> "
    
    def _ensure_tv_selected(self) -> bool:
        tv = self.manager.get_tv_for_current_session()
        if tv:
            self.current_service = TVService(tv)
            self._update_prompt()
            return True
        return False
    
    def _reload_data(self) -> None:
        """Перезагружает данные из файла (синхронизация с Web)"""
        self.manager._load_televisions()
        if self.manager.current_tv is None and self.manager._televisions:
            self.manager._current_tv_index = 0
            self._update_prompt()
    
    # ========== КОМАНДЫ УПРАВЛЕНИЯ ТЕЛЕВИЗОРАМИ ==========
    
    def do_tv(self, arg: str) -> None:
        args = arg.split()
        if not args:
            print("Использование: tv list|select|add|remove|info|specs")
            return
        
        command = args[0].lower()
        
        if command == "list":
            self.do_tv_list("")
        elif command == "select":
            self.do_tv_select("")
        elif command == "add":
            self.do_tv_add("")
        elif command == "remove":
            self.do_tv_remove("")
        elif command == "info":
            self.do_tv_info("")
        elif command == "specs":
            self.do_tv_specs("")
        else:
            print(f"Неизвестная команда: tv {command}")
    
    def do_tv_list(self, arg: str) -> None:
        self._reload_data()
        self.manager.print_televisions_list()
    
    def do_tv_select(self, arg: str) -> None:
        self._reload_data()
        if self.manager.select_television():
            self._update_prompt()
            self.do_status("")
    
    def do_tv_add(self, arg: str) -> None:
        self._reload_data()
        tv = self.manager.add_television_interactive()
        if tv:
            self._update_prompt()
            print(f"\n[OK] Телевизор '{tv.name}' добавлен!")
            self.do_status("")
    
    def do_tv_remove(self, arg: str) -> None:
        if self.manager.remove_current_tv():
            self._update_prompt()
    
    def do_tv_info(self, arg: str) -> None:
        self._reload_data()
        tv = self.manager.current_tv
        if not tv:
            print("[ERROR] Телевизор не выбран")
            return
        
        print(f"\n=== Информация о телевизоре: {tv.name} ===")
        print(f"Модель: {tv.specs.model_name}")
        print(f"Технология: {tv.specs.screen.technology.value}")
        print(f"Диагональ: {tv.specs.screen.diagonal}\"")
        print(f"Разрешение: {tv.specs.screen.resolution_width}x{tv.specs.screen.resolution_height}")
        print(f"Smart TV: {'да' if tv.specs.has_smart_tv else 'нет'}")
        print(f"Wi-Fi: {'да' if tv.specs.has_wifi else 'нет'}")
        print(f"Bluetooth: {'да' if tv.specs.has_bluetooth else 'нет'}")
        print(f"ОС: {tv.specs.operating_system.value}")
        print(f"Версия ОС: {tv.specs.os_version}")
        
        if tv.is_on:
            print(f"\nСостояние: ВКЛЮЧЕН")
            print(f"Источник: {tv._current_source.value}")
        else:
            print(f"\nСостояние: ВЫКЛЮЧЕН")
    
    def do_tv_specs(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("specs")
        print(result)
    
    # ========== КОМАНДЫ УПРАВЛЕНИЯ ТЕЛЕВИЗОРОМ ==========
    
    def do_on(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("power_on")
        print(result)
        self.do_status("")
    
    def do_off(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("power_off")
        print(result)
    
    def do_tv_source(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("source_tv")
        print(result)
        self.do_status("")
    
    def do_smart(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("source_smart")
        print(result)
        self.do_status("")
    
    def do_channel(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        if not arg:
            print("[ERROR] Укажите номер канала")
            return
        try:
            channel = int(arg)
            result = self.current_service.execute_command("channel", channel)
            print(result)
        except ValueError:
            print("[ERROR] Номер канала должен быть числом")
    
    def do_ch_plus(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("channel_up")
        print(result)
    
    def do_ch_minus(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("channel_down")
        print(result)
    
    def do_channels(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("channels")
        print(result)
    
    def do_now(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("now")
        print(result)
    
    def do_volume(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        if not arg:
            result = self.current_service.execute_command("volume")
            print(result)
            return
        try:
            level = int(arg)
            if 0 <= level <= 100:
                result = self.current_service.execute_command("volume", level)
                print(result)
            else:
                print("[ERROR] Громкость должна быть от 0 до 100")
        except ValueError:
            print("[ERROR] Громкость должна быть числом")
    
    def do_vol_plus(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("volume_up")
        print(result)
    
    def do_vol_minus(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("volume_down")
        print(result)
    
    def do_brightness(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        if not arg:
            result = self.current_service.execute_command("brightness")
            print(result)
            return
        try:
            level = int(arg)
            if 0 <= level <= 100:
                result = self.current_service.execute_command("brightness", level)
                print(result)
            else:
                print("[ERROR] Яркость должна быть от 0 до 100")
        except ValueError:
            print("[ERROR] Яркость должна быть числом")
    
    def do_contrast(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        if not arg:
            result = self.current_service.execute_command("contrast")
            print(result)
            return
        try:
            level = int(arg)
            if 0 <= level <= 100:
                result = self.current_service.execute_command("contrast", level)
                print(result)
            else:
                print("[ERROR] Контраст должен быть от 0 до 100")
        except ValueError:
            print("[ERROR] Контраст должен быть числом")
    
    def do_equalizer(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        if not arg:
            result = self.current_service.execute_command("equalizer")
            print(result)
            return
        parts = arg.split()
        if len(parts) != 3:
            print("[ERROR] Укажите три значения для НЧ, СЧ и ВЧ")
            return
        try:
            low, mid, high = map(int, parts)
            result = self.current_service.execute_command("equalizer", low, mid, high)
            print(result)
        except ValueError:
            print("[ERROR] Значения должны быть числами от -100 до 100")
    
    def do_subwoofer(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        if not arg:
            result = self.current_service.execute_command("subwoofer")
            print(result)
            return
        state = arg.strip().lower()
        if state in ["on", "off"]:
            result = self.current_service.execute_command("subwoofer", state)
            print(result)
        else:
            print("[ERROR] Используйте: subwoofer on|off")
    
    def do_bluetooth(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        args = arg.split() if arg else []
        result = self.current_service.execute_command("bluetooth", *args)
        print(result)
    
    def do_wifi(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        if not arg:
            result = self.current_service.execute_command("wifi")
            print(result)
            return
        state = arg.strip().lower()
        if state in ["on", "off"]:
            result = self.current_service.execute_command("wifi", state)
            print(result)
        else:
            print("[ERROR] Используйте: wifi on|off")
    
    def do_update(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("update")
        print(result)
    
    def do_status(self, arg: str) -> None:
        if not self._ensure_tv_selected():
            return
        result = self.current_service.execute_command("status")
        print(result)
    
    def do_exit(self, arg: str) -> bool:
        print("\nДо свидания!")
        return True
    
    def do_quit(self, arg: str) -> bool:
        return self.do_exit(arg)
    
    def do_clear(self, arg: str) -> None:
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_ch(self, arg: str) -> None:
        self.do_channel(arg)
    
    def do_vol(self, arg: str) -> None:
        self.do_volume(arg)
    
    def do_eq(self, arg: str) -> None:
        self.do_equalizer(arg)
    
    def do_list(self, arg: str) -> None:
        self.do_tv_list(arg)
    
    def do_add(self, arg: str) -> None:
        self.do_tv_add(arg)
    
    def do_select(self, arg: str) -> None:
        self.do_tv_select(arg)
    
    def do_remove(self, arg: str) -> None:
        self.do_tv_remove(arg)
    
    def emptyline(self) -> None:
        pass
    
    def default(self, line: str) -> None:
        print(f"[ERROR] Неизвестная команда: {line}")
        print("   Введите 'help' для списка команд")


def main() -> None:
    try:
        manager = TelevisionManager()
        cli = TelevisionCLI(manager)
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            args = sys.argv[2:]
            
            if command == "list":
                manager.print_televisions_list()
            elif command == "add" and "--interactive" not in args:
                print("Для интерактивного добавления запустите программу без аргументов")
            else:
                print(f"Неизвестная команда: {command}")
                print("Запустите программу без аргументов для интерактивного режима")
        else:
            try:
                if manager.list_televisions():
                    print("\nНайденные телевизоры:")
                    manager.print_televisions_list()
                    
                    if input_yes_no("\nВыбрать телевизор сейчас?", default=True):
                        manager.select_television()
                else:
                    print("\nСписок телевизоров пуст.")
                    if input_yes_no("Хотите добавить новый телевизор?", default=True):
                        manager.add_television_interactive()
                
                cli.cmdloop()
            except KeyboardInterrupt:
                print("\n\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"[ERROR] Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()