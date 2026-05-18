"""
Модуль с вспомогательными функциями для ввода данных.
"""
from typing import TypeVar, Callable, Any, Optional, List, Tuple
from src.utils.exceptions import ValidationError

T = TypeVar('T')


def input_with_validation(
    prompt: str,
    validator: Callable[[str], T],
    error_message: str = "Ошибка ввода. Попробуйте снова.",
    retry: bool = True
) -> T:
    """
    Запрашивает ввод у пользователя и применяет валидатор.
    
    Args:
        prompt: Приглашение для ввода
        validator: Функция-валидатор, которая принимает строку и возвращает преобразованное значение
        error_message: Сообщение об ошибке
        retry: Повторять ли запрос при ошибке
        
    Returns:
        T: Преобразованное значение
        
    Raises:
        ValidationError: Если retry=False и произошла ошибка валидации
    """
    while True:
        try:
            user_input = input(prompt).strip()
            return validator(user_input)
        except ValidationError as e:
            print(f"❌ {str(e)}")
            if not retry:
                raise
        except KeyboardInterrupt:
            print("\n⚠️  Ввод прерван пользователем")
            if not retry:
                raise
        except Exception as e:
            print(f"❌ {error_message}: {str(e)}")
            if not retry:
                raise


def input_with_choices(
    prompt: str,
    choices: List[str],
    allow_custom: bool = False,
    custom_prompt: str = "Введите свой вариант: "
) -> str:
    """
    Запрашивает ввод с выбором из предложенных вариантов.
    
    Args:
        prompt: Приглашение для ввода
        choices: Список допустимых вариантов
        allow_custom: Разрешить ли ввод своего варианта
        custom_prompt: Приглашение для ввода своего варианта
        
    Returns:
        str: Выбранный вариант
    """
    print(prompt)
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    
    if allow_custom:
        print(f"  {len(choices) + 1}. Свой вариант")
    
    while True:
        try:
            user_input = input("Выберите номер (или введите значение): ").strip()
            
            # Проверяем, не является ли ввод числом-индексом
            if user_input.isdigit():
                idx = int(user_input)
                if 1 <= idx <= len(choices):
                    return choices[idx - 1]
                elif allow_custom and idx == len(choices) + 1:
                    return input(custom_prompt).strip()
            
            # Если это не индекс, проверяем, есть ли значение в списке
            if user_input in choices:
                return user_input
            
            # Если разрешен свой вариант, возвращаем введенное значение
            if allow_custom:
                return user_input
            
            print(f"❌ Пожалуйста, выберите вариант из списка")
        except KeyboardInterrupt:
            print("\n⚠️  Ввод прерван пользователем")
            raise


def input_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    """
    Запрашивает подтверждение (да/нет).
    
    Args:
        prompt: Приглашение для ввода
        default: Значение по умолчанию (True для да, False для нет, None - обязательный ввод)
        
    Returns:
        bool: True если да, False если нет
    """
    suffix = ""
    if default is True:
        suffix = " [Y/n]: "
    elif default is False:
        suffix = " [y/N]: "
    else:
        suffix = " [y/n]: "
    
    while True:
        try:
            user_input = input(prompt + suffix).strip().lower()
            
            if not user_input and default is not None:
                return default
            
            if user_input in ['y', 'yes', 'да', 'д', '+']:
                return True
            elif user_input in ['n', 'no', 'нет', 'н', '-']:
                return False
            else:
                print("Пожалуйста, ответьте 'да' или 'нет'")
        except KeyboardInterrupt:
            print("\n⚠️  Ввод прерван пользователем")
            raise