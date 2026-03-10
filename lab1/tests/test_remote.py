"""
Unit-тесты для класса RemoteControl.
"""

import unittest
from unittest.mock import patch
from io import StringIO

from src.models.television import (
    Television,
    TechnicalSpecifications,
    ScreenTechnology,
    ScreenCoverage,
    OperatingSystem,
)
from src.models.remote import RemoteControl


class TestRemoteControl(unittest.TestCase):
    """Тесты для класса RemoteControl."""

    def setUp(self) -> None:
        """Подготовка перед каждым тестом."""
        self.specs = TechnicalSpecifications(
            model_name="Test TV",
            technology=ScreenTechnology.LED,
            screen_diagonal=42.0,
            resolution=(1920, 1080),
            response_time=5,
            screen_coverage=ScreenCoverage.ANTI_GLARE,
            refresh_rate=60,
            speakers_count=2,
            speaker_power=10,
            hdmi_ports=3,
            usb_ports=2,
            lan_ports=1,
            has_wifi=True,
            has_bluetooth=True,
            has_smart_tv=True,
            color="черный",
            weight=12.5,
            lifespan=8,
            brightness_nit=300,
            operating_system=OperatingSystem.TIZEN,
            os_version="1.0",
        )
        self.tv = Television(self.specs)
        self.remote = RemoteControl(self.tv)

    def test_power_button(self) -> None:
        """Тест кнопки питания."""
        self.assertFalse(self.tv.is_on)

        self.remote.power()
        self.assertTrue(self.tv.is_on)

        self.remote.power()
        self.assertFalse(self.tv.is_on)

    def test_smart_tv_mode_success(self) -> None:
        """Тест успешного переключения в Smart TV."""
        self.tv.turn_on()
        self.remote.smart_tv_mode()
        self.assertEqual(self.tv.mode.value, "Smart TV")

    def test_smart_tv_mode_errors(self) -> None:
        """Тест ошибок при переключении в Smart TV."""
        # Телевизор выключен
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.smart_tv_mode()
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Телевизор без Smart TV
        specs_no_smart = TechnicalSpecifications(
            model_name="No Smart TV",
            technology=ScreenTechnology.LED,
            screen_diagonal=32.0,
            resolution=(1920, 1080),
            response_time=8,
            screen_coverage=ScreenCoverage.GLOSSY,
            refresh_rate=60,
            speakers_count=2,
            speaker_power=5,
            hdmi_ports=2,
            usb_ports=1,
            lan_ports=0,
            has_wifi=False,
            has_bluetooth=False,
            has_smart_tv=False,
            color="черный",
            weight=8.5,
            lifespan=7,
            brightness_nit=250,
        )
        tv_no_smart = Television(specs_no_smart)
        remote_no_smart = RemoteControl(tv_no_smart)
        tv_no_smart.turn_on()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            remote_no_smart.smart_tv_mode()
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_tv_mode(self) -> None:
        """Тест переключения в режим ТВ."""
        self.tv.turn_on()
        self.tv.switch_to_smart_tv()
        self.remote.tv_mode()
        self.assertEqual(self.tv.mode.value, "Кабельное ТВ")

    def test_hdmi_mode_success(self) -> None:
        """Тест успешного переключения в HDMI."""
        self.tv.turn_on()
        self.tv.connect_hdmi(1, "PlayStation")
        self.remote.hdmi_mode(1)
        self.assertEqual(self.tv.mode.value, "HDMI")

    def test_hdmi_mode_errors(self) -> None:
        """Тест ошибок при переключении в HDMI."""
        self.tv.turn_on()

        # Порт без устройства
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.hdmi_mode(2)
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Несуществующий порт
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.hdmi_mode(5)
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Телевизор выключен
        self.tv.turn_off()
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.hdmi_mode(1)
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_channel_control_success(self) -> None:
        """Тест успешного управления каналами."""
        self.tv.turn_on()

        # Устанавливаем начальный канал
        self.remote.set_channel(5)
        self.assertEqual(self.tv.current_channel, 5)

        # Канал вверх
        self.remote.channel_up()
        self.assertEqual(self.tv.current_channel, 6)

        # Канал вниз
        self.remote.channel_down()
        self.assertEqual(self.tv.current_channel, 5)

        # Установка нового канала
        self.remote.set_channel(42)
        self.assertEqual(self.tv.current_channel, 42)

    def test_channel_control_errors(self) -> None:
        """Тест ошибок при управлении каналами."""
        # Телевизор выключен
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.channel_up()
            self.assertIn("Ошибка", mock_stdout.getvalue())

        self.tv.turn_on()
        self.tv.switch_to_smart_tv()

        # В режиме Smart TV
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.channel_up()
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Невалидный канал
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.set_channel(1000)
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_volume_control_success(self) -> None:
        """Тест успешного управления громкостью."""
        self.tv.turn_on()

        # Пошаговое изменение
        self.remote.volume_up()
        self.assertEqual(self.tv.get_volume(), 35)
        self.remote.volume_down()
        self.assertEqual(self.tv.get_volume(), 30)

        # Прямая установка
        self.remote.set_volume(75)
        self.assertEqual(self.tv.get_volume(), 75)

        # Mute
        self.remote.mute()
        self.assertEqual(self.tv.get_volume(), 0)

    def test_volume_control_errors(self) -> None:
        """Тест ошибок при управлении громкостью."""
        # Телевизор выключен
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.volume_up()
            self.assertIn("Ошибка", mock_stdout.getvalue())

        self.tv.turn_on()

        # Невалидное значение
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.set_volume(150)
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_picture_settings_success(self) -> None:
        """Тест успешных настроек изображения."""
        self.tv.turn_on()

        self.remote.set_brightness(70)
        self.assertEqual(self.tv.get_brightness(), 70)

        self.remote.set_contrast(80)
        self.assertEqual(self.tv.get_contrast(), 80)

    def test_picture_settings_errors(self) -> None:
        """Тест ошибок при настройке изображения."""
        # Телевизор выключен
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.set_brightness(70)
            self.assertIn("Ошибка", mock_stdout.getvalue())

        self.tv.turn_on()

        # Невалидные значения
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.set_brightness(150)
            self.assertIn("Ошибка", mock_stdout.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.set_contrast(200)
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_audio_settings_success(self) -> None:
        """Тест успешных настроек звука."""
        self.tv.turn_on()

        # Эквалайзер
        self.remote.set_equalizer(50, -20, 30)
        eq = self.tv.get_equalizer()
        self.assertEqual(eq["high"], 50)
        self.assertEqual(eq["mid"], -20)
        self.assertEqual(eq["low"], 30)

        # Сабвуфер
        self.remote.toggle_subwoofer()
        self.assertTrue(self.tv.is_subwoofer_connected())
        self.remote.toggle_subwoofer()
        self.assertFalse(self.tv.is_subwoofer_connected())

    def test_audio_settings_errors(self) -> None:
        """Тест ошибок при настройке звука."""
        # Телевизор выключен
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.set_equalizer(50, 0, 0)
            self.assertIn("Ошибка", mock_stdout.getvalue())

        self.tv.turn_on()

        # Невалидные значения эквалайзера
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.set_equalizer(200, 0, 0)
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_hdmi_management_success(self) -> None:
        """Тест успешного управления HDMI."""
        self.tv.turn_on()

        # Подключение
        self.remote.connect_hdmi(1, "PlayStation")
        devices = self.tv.get_hdmi_devices()
        self.assertIn(1, devices)
        self.assertEqual(devices[1], "PlayStation")

        # Отключение
        self.remote.disconnect_hdmi(1)
        self.assertNotIn(1, self.tv.get_hdmi_devices())

    def test_hdmi_management_errors(self) -> None:
        """Тест ошибок при управлении HDMI."""
        self.tv.turn_on()

        # Подключение на несуществующий порт
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.connect_hdmi(5, "Xbox")
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Подключение с пустым именем
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.connect_hdmi(1, "")
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Отключение с пустого порта
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.disconnect_hdmi(2)
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Телевизор выключен
        self.tv.turn_off()
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.connect_hdmi(1, "Test")
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_smart_tv_functions(self) -> None:
        """Тест функций Smart TV."""
        self.tv.turn_on()
        self.tv.switch_to_smart_tv()

        # Обновление ПО
        old_version = self.tv.software_version
        self.remote.update_software()
        self.assertGreater(self.tv.software_version, old_version)

        # Повторное обновление (до лимита)
        self.tv._software_version = 1.9
        self.remote.update_software()
        self.assertEqual(self.tv.software_version, 2.0)

    def test_smart_tv_functions_errors(self) -> None:
        """Тест ошибок функций Smart TV."""
        # Телевизор выключен
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.update_software()
            self.assertIn("Ошибка", mock_stdout.getvalue())

        # Включен, но не в режиме Smart TV
        self.tv.turn_on()
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.update_software()
            self.assertIn("Ошибка", mock_stdout.getvalue())

    def test_wifi_toggle(self) -> None:
        """Тест переключения Wi-Fi."""
        self.tv.turn_on()

        # Получаем начальное состояние
        initial_status = self.tv.get_wifi_status()

        # Переключаем
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.toggle_wifi()
            output = mock_stdout.getvalue()
            new_status = self.tv.get_wifi_status()
            self.assertNotEqual(initial_status, new_status)
            self.assertIn("Wi-Fi", output)

    def test_bluetooth_toggle(self) -> None:
        """Тест переключения Bluetooth."""
        self.tv.turn_on()

        # Получаем начальное состояние
        initial_status = self.tv.get_bluetooth_status()

        # Переключаем
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.toggle_bluetooth()
            output = mock_stdout.getvalue()
            new_status = self.tv.get_bluetooth_status()
            self.assertNotEqual(initial_status, new_status)
            self.assertIn("Bluetooth", output)

    def test_wifi_toggle_no_module(self) -> None:
        """Тест переключения Wi-Fi при отсутствии модуля."""
        specs_no_wifi = TechnicalSpecifications(
            model_name="No WiFi TV",
            technology=ScreenTechnology.LED,
            screen_diagonal=32.0,
            resolution=(1920, 1080),
            response_time=8,
            screen_coverage=ScreenCoverage.GLOSSY,
            refresh_rate=60,
            speakers_count=2,
            speaker_power=5,
            hdmi_ports=2,
            usb_ports=1,
            lan_ports=0,
            has_wifi=False,
            has_bluetooth=False,
            has_smart_tv=False,
            color="черный",
            weight=8.5,
            lifespan=7,
            brightness_nit=250,
        )
        tv_no_wifi = Television(specs_no_wifi)
        remote_no_wifi = RemoteControl(tv_no_wifi)
        tv_no_wifi.turn_on()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            remote_no_wifi.toggle_wifi()
            self.assertIn("нет Wi-Fi модуля", mock_stdout.getvalue())

    def test_bluetooth_toggle_no_module(self) -> None:
        """Тест переключения Bluetooth при отсутствии модуля."""
        specs_no_bt = TechnicalSpecifications(
            model_name="No Bluetooth TV",
            technology=ScreenTechnology.LED,
            screen_diagonal=32.0,
            resolution=(1920, 1080),
            response_time=8,
            screen_coverage=ScreenCoverage.GLOSSY,
            refresh_rate=60,
            speakers_count=2,
            speaker_power=5,
            hdmi_ports=2,
            usb_ports=1,
            lan_ports=0,
            has_wifi=True,
            has_bluetooth=False,
            has_smart_tv=False,
            color="черный",
            weight=8.5,
            lifespan=7,
            brightness_nit=250,
        )
        tv_no_bt = Television(specs_no_bt)
        remote_no_bt = RemoteControl(tv_no_bt)
        tv_no_bt.turn_on()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            remote_no_bt.toggle_bluetooth()
            self.assertIn("нет Bluetooth модуля", mock_stdout.getvalue())

    def test_show_status_on(self) -> None:
        """Тест отображения статуса при включенном ТВ."""
        self.tv.turn_on()
        self.tv.set_channel(7)
        self.tv.set_volume(50)
        self.tv.set_brightness(60)
        self.tv.connect_hdmi(1, "PlayStation")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.show_status()
            output = mock_stdout.getvalue()
            self.assertIn("СОСТОЯНИЕ ТЕЛЕВИЗОРА", output)
            self.assertIn("Канал: 7", output)
            self.assertIn("Громкость: 50", output)
            self.assertIn("Яркость: 60", output)
            self.assertIn("PlayStation", output)

    def test_show_status_off(self) -> None:
        """Тест отображения статуса при выключенном ТВ."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.remote.show_status()
            output = mock_stdout.getvalue()
            self.assertIn("СОСТОЯНИЕ ТЕЛЕВИЗОРА", output)
            self.assertIn("Питание:", output)
            self.assertIn("ВЫКЛ", output)

    def test_edge_cases(self) -> None:
        """Тест граничных случаев."""
        self.tv.turn_on()

        # Каналы
        self.tv._current_channel = 999
        self.remote.channel_up()
        self.assertEqual(self.tv.current_channel, 1)

        self.remote.channel_down()
        self.assertEqual(self.tv.current_channel, 999)

        # Громкость
        self.tv._volume = 100
        self.remote.volume_up()
        self.assertEqual(self.tv.get_volume(), 100)

        self.tv._volume = 0
        self.remote.volume_down()
        self.assertEqual(self.tv.get_volume(), 0)


if __name__ == "__main__":
    unittest.main()
