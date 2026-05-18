"""
Модуль для управления коллекцией телевизоров.
"""
from typing import List, Optional, Dict, Any
from src.models.television import Television
from src.models.screen import Screen, ScreenTechnology, ScreenCoverage
from src.models.audio import AudioSystem
from src.models.specs import TechnicalSpecifications, OperatingSystem
from src.storage.tv_repository import TVRepository
from src.utils.exceptions import TelevisionError
from src.utils.input_helpers import input_with_validation, input_with_choices, input_yes_no
from src.utils.validators import validate_int, validate_float


class TelevisionManager:
    """Менеджер для управления несколькими телевизорами."""
    
    def __init__(self, repository: Optional[TVRepository] = None):
        self.repository = repository or TVRepository()
        self._current_tv_index: Optional[int] = None
        self._televisions: List[Television] = []
        self._load_televisions()
    
    def _load_televisions(self) -> None:
        try:
            self._televisions = self.repository.load_all()
        except Exception as e:
            print(f"Ошибка загрузки телевизоров: {e}")
            self._televisions = []
    
    def _save_televisions(self) -> None:
        try:
            self.repository.save_all(self._televisions)
        except Exception as e:
            print(f" Ошибка сохранения телевизоров: {e}")
    
    @property
    def current_tv(self) -> Optional[Television]:
        if self._current_tv_index is not None and 0 <= self._current_tv_index < len(self._televisions):
            return self._televisions[self._current_tv_index]
        return None
    
    @property
    def current_tv_name(self) -> str:
        tv = self.current_tv
        return tv.name if tv else "телевизор не выбран"
    
    def list_televisions(self) -> List[Dict[str, Any]]:
        result = []
        for i, tv in enumerate(self._televisions):
            result.append({
                "index": i,
                "name": tv.name,
                "model": tv.specs.model_name,
                "diagonal": tv.specs.screen.diagonal,
                "technology": tv.specs.screen.technology.value,
                "selected": (i == self._current_tv_index)
            })
        return result
    
    def print_televisions_list(self) -> None:
        if not self._televisions:
            print("\n Список телевизоров пуст")
            return
        
        print("\n" + "="*60)
        print(f"{'№':<4} {'Название':<25} {'Модель':<20} {'Диагональ':<10}")
        print("-"*60)
        
        for i, tv in enumerate(self._televisions):
            selected_mark = "▶ " if i == self._current_tv_index else "  "
            print(f"{selected_mark}{i+1:<2} {tv.name:<25} {tv.specs.model_name:<20} {tv.specs.screen.diagonal:<10}\"")
        
        print("="*60)
    
    def select_television(self, index: Optional[int] = None) -> bool:
        if not self._televisions:
            print("\n Список телевизоров пуст. Сначала добавьте телевизор.")
            return False
        
        if index is None:
            self.print_televisions_list()
            try:
                choice = input_with_validation(
                    f"\nВыберите телевизор (1-{len(self._televisions)}): ",
                    lambda x: validate_int(x, 1, len(self._televisions), "Номер")
                )
                index = choice - 1
            except KeyboardInterrupt:
                print("\n Выбор отменен")
                return False
        
        if 0 <= index < len(self._televisions):
            self._current_tv_index = index
            tv = self._televisions[index]
            print(f"\n Выбран телевизор: {tv.name}")
            return True
        
        print(f"\nТелевизор с индексом {index} не найден")
        return False
    
    def add_television_interactive(self) -> Optional[Television]:
        print("\n" + "="*60)
        print("ДОБАВЛЕНИЕ НОВОГО ТЕЛЕВИЗОРА")
        print("="*60)
        print("(Для отмены нажмите Ctrl+C)\n")
        
        try:
            # Основная информация
            tv_name = input("Название для удобства: ").strip()
            if not tv_name:
                tv_name = "Мой телевизор"
            
            model_name = input("Модель: ").strip() or "Телевизор"
            
            # Экран
            technology = ScreenTechnology(
                input_with_choices(
                    "Технология экрана:",
                    [t.value for t in ScreenTechnology]
                )
            )
            diagonal = input_with_validation(
                "Диагональ (дюймы): ",
                lambda x: validate_float(x, 10, 200, "Диагональ")
            )
            res_w = input_with_validation(
                "Ширина разрешения: ",
                lambda x: validate_int(x, 640, 7680, "Ширина")
            )
            res_h = input_with_validation(
                "Высота разрешения: ",
                lambda x: validate_int(x, 480, 4320, "Высота")
            )
            response_time = input_with_validation(
                "Время отклика (мс): ",
                lambda x: validate_int(x, 1, 50, "Время отклика")
            )
            refresh = input_with_validation(
                "Частота обновления (Гц): ",
                lambda x: validate_int(x, 24, 360, "Частота")
            )
            brightness_nits = input_with_validation(
                "Яркость (нит): ",
                lambda x: validate_int(x, 100, 4000, "Яркость")
            )
            
            screen = Screen(
                technology=technology,
                diagonal=diagonal,
                resolution_width=res_w,
                resolution_height=res_h,
                response_time_ms=response_time,
                refresh_rate_hz=refresh,
                brightness_nits=brightness_nits
            )
            
            # Звук
            speakers = input_with_validation(
                "Количество динамиков: ",
                lambda x: validate_int(x, 0, 20, "Динамики")
            )
            speaker_power = input_with_validation(
                "Мощность динамика (Вт): ",
                lambda x: validate_float(x, 0, 500, "Мощность")
            )
            has_sub_out = input_yes_no("Поддержка сабвуфера: ", default=False)
            
            audio = AudioSystem(
                speakers_count=speakers,
                speaker_power_w=speaker_power,
                has_subwoofer_output=has_sub_out
            )
            
            # Характеристики
            hdmi = input_with_validation(
                "Количество HDMI портов: ",
                lambda x: validate_int(x, 0, 8, "HDMI")
            )
            usb = input_with_validation(
                "Количество USB портов: ",
                lambda x: validate_int(x, 0, 8, "USB")
            )
            has_wifi = input_yes_no("Wi-Fi: ", default=True)
            has_bt = input_yes_no("Bluetooth: ", default=True)
            has_smart = input_yes_no("Smart TV: ", default=True)
            
            specs = TechnicalSpecifications(
                model_name=model_name,
                screen=screen,
                audio=audio,
                hdmi_ports=hdmi,
                usb_ports=usb,
                has_wifi=has_wifi,
                has_bluetooth=has_bt,
                has_smart_tv=has_smart
            )
            
            tv = Television(specs, name=tv_name)
            self._televisions.append(tv)
            self._save_televisions()
            
            print(f"\nТелевизор '{tv_name}' успешно добавлен!")
            
            if input_yes_no("Сделать текущим?", default=True):
                self._current_tv_index = len(self._televisions) - 1
            
            return tv
            
        except KeyboardInterrupt:
            print("\n\nДобавление отменено")
            return None
        except Exception as e:
            print(f"\nОшибка: {e}")
            return None
    
    def remove_current_tv(self) -> bool:
        if self._current_tv_index is None:
            print("\n Телевизор не выбран")
            return False
        
        tv = self.current_tv
        if not tv:
            self._current_tv_index = None
            return False
        
        print(f"\n Удаление: {tv.name}")
        if input_yes_no("Вы уверены?", default=False):
            self._televisions.pop(self._current_tv_index)
            self._current_tv_index = None if not self._televisions else 0
            self._save_televisions()
            print(" Телевизор удален")
            return True
        
        return False
    
    def remove_by_index(self, index: int) -> bool:
        if 0 <= index < len(self._televisions):
            tv = self._televisions[index]
            print(f"\nУдаление: {tv.name}")
            if input_yes_no("Вы уверены?", default=False):
                self._televisions.pop(index)
                if self._current_tv_index is not None:
                    if self._current_tv_index == index:
                        self._current_tv_index = None if not self._televisions else 0
                    elif self._current_tv_index > index:
                        self._current_tv_index -= 1
                self._save_televisions()
                print(" Телевизор удален")
                return True
        return False
    
    def get_tv_for_current_session(self) -> Optional[Television]:
        if not self._televisions:
            print("\n Нет телевизоров. Добавьте новый.")
            return None
        
        if self._current_tv_index is None:
            print("\n Телевизор не выбран.")
            if input_yes_no("Выбрать сейчас?", default=True):
                if not self.select_television():
                    return None
            else:
                return None
        
        return self.current_tv