#  Лабораторная работа №1: Модель телевизора


Важные сущности: телевизор, пульт дистанционного управления, экран, звуковая система, технические характеристики. 

Операции: операция включения и выключения, операция выбора телеканала, операция настройки изображения и звука, операция подключения внешних устройств, операция обновления программного обеспечения.




##  Классы и атрибуты

### класс `Television`
| Атрибут | Тип | Описание |
|---------|-----|----------|
| `_is_on` | `bool` | Состояние питания |
| `_mode` | `TVMode` | Текущий режим |
| `_current_channel` | `int` | Текущий канал |
| `_brightness` | `int` | Яркость (0-100) |
| `_contrast` | `int` | Контраст (0-100) |
| `_volume` | `int` | Громкость (0-100) |
| `_wifi_enabled` | `bool` | Состояние Wi-Fi |
| `_bluetooth_enabled` | `bool` | Состояние Bluetooth |
| `_hdmi_devices` | `Dict[int, str]` | HDMI устройства |

### класс `RemoteControl`
| Атрибут | Тип | Описание |
|---------|-----|----------|
| `_tv` | `Television` | Управляемый телевизор |

### класс `TechnicalSpecifications`
| Атрибут | Тип | Описание |
|---------|-----|----------|
| `model_name` | `str` | Название модели |
| `technology` | `ScreenTechnology` | Технология экрана |
| `screen_diagonal` | `float` | Диагональ (дюймы) |
| `resolution` | `Tuple` | Разрешение |
| `hdmi_ports` | `int` | Количество HDMI |
| `has_wifi` | `bool` | Наличие Wi-Fi |
| `has_smart_tv` | `bool` | Поддержка Smart TV |

### класс `TVManager`
| Атрибут | Тип | Описание |
|---------|-----|----------|
| `_tvs` | `Dict[str, Television]` | Все телевизоры |
| `_current_tv_name` | `str` | Текущий ТВ |
| `_remote` | `RemoteControl` | Пульт для текущего ТВ |



##  Методы классов

### `Television` (основные)
| Метод | Описание |
|-------|----------|
| `turn_on()` / `turn_off()` | Вкл/выкл |
| `switch_to_smart_tv()` / `switch_to_tv_mode()` | Переключение режимов |
| `switch_to_hdmi(port)` | Переключение на HDMI |
| `set_channel(channel)` / `channel_up/down()` | Управление каналами |
| `set_volume(value)` / `volume_up/down()` / `mute()` | Управление громкостью |
| `set_brightness(value)` / `set_contrast(value)` | Настройка изображения |
| `set_equalizer(h,m,l)` / `toggle_subwoofer()` | Настройка звука |
| `toggle_wifi()` / `toggle_bluetooth()` | Переключение сети |
| `connect_hdmi(port, device)` / `disconnect_hdmi(port)` | Управление HDMI |
| `update_software()` | Обновление ПО |
| `get_status()` | Получение состояния |

### `RemoteControl`
| Метод | Описание |
|-------|----------|
| `power()` | Кнопка питания |
| `tv_mode()` / `smart_tv_mode()` / `hdmi_mode(port)` | Выбор режима |
| `channel_up/down()` / `set_channel(channel)` | Кнопки каналов |
| `volume_up/down()` / `set_volume()` / `mute()` | Кнопки громкости |
| `set_brightness()` / `set_contrast()` | Настройки изображения |
| `set_equalizer()` / `toggle_subwoofer()` | Настройки звука |
| `toggle_wifi()` / `toggle_bluetooth()` | Настройки сети |
| `connect_hdmi()` / `disconnect_hdmi()` | Управление HDMI |
| `update_software()` | Обновление ПО |
| `show_status()` | Показать состояние |

### `TVManager`
| Метод | Описание |
|-------|----------|
| `add_tv()` | Добавление ТВ |
| `list_tvs()` | Список всех ТВ |
| `select_tv()` | Выбор текущего ТВ |
| `remove_tv()` | Удаление ТВ |
| `run_control_menu()` | Меню управления |


##  Состояния

### Состояния телевизора

Выключен → Включен (Режим ТВ/Smart TV/HDMI) → Выключен



## Исключения

| Исключение | Причина | Действие |
|------------|---------|----------|
| `TVNotPoweredError` | Действие с выключенным ТВ | Сообщение об ошибке, возврат в меню |
| `InvalidValueError` | Недопустимое значение параметра | Сообщение, повтор ввода |
| `InvalidModeError` | Действие в неправильном режиме | Сообщение, возврат в меню |
| `SmartTVNotSupportedError` | Действие без поддержки Smart TV | Сообщение, возврат |
| `PortNotFoundError` | Несуществующий порт | Сообщение, повтор ввода |
| `DeviceNotFoundError` | Отсутствие устройства на порту | Сообщение, возврат |






