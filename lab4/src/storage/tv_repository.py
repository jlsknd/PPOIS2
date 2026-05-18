"""
Модуль для сохранения и загрузки телевизоров в/из JSON файла.
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from src.models.television import Television
from src.models.screen import Screen, ScreenTechnology, ScreenCoverage
from src.models.audio import AudioSystem, Equalizer
from src.models.specs import TechnicalSpecifications, OperatingSystem
from src.utils.exceptions import StorageError


class TVRepository:
    def __init__(self, file_path: str = "data/televisions.json"):
        self.file_path = file_path
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def _tv_to_dict(self, tv: Television) -> Dict[str, Any]:
        specs = tv.specs
        screen = specs.screen
        audio = specs.audio

        return {
            "name": tv.name,
            "specs": {
                "model_name": specs.model_name,
                "screen": {
                    "technology": screen.technology.value,
                    "diagonal": screen.diagonal,
                    "resolution_width": screen.resolution_width,
                    "resolution_height": screen.resolution_height,
                    "response_time_ms": screen.response_time_ms,
                    "coverage": screen.coverage.value,
                    "refresh_rate_hz": screen.refresh_rate_hz,
                    "brightness_nits": screen.brightness_nits,
                    "brightness": screen.brightness,
                    "contrast": screen.contrast,
                },
                "audio": {
                    "speakers_count": audio.speakers_count,
                    "speaker_power_w": audio.speaker_power_w,
                    "has_subwoofer_output": audio.has_subwoofer_output,
                    "subwoofer_connected": audio.subwoofer_connected,
                    "volume": audio.volume,
                    "equalizer": {
                        "low": audio.equalizer.low,
                        "mid": audio.equalizer.mid,
                        "high": audio.equalizer.high,
                    },
                },
                "has_dvb_s": specs.has_dvb_s,
                "has_dvb_s2": specs.has_dvb_s2,
                "has_dvb_t": specs.has_dvb_t,
                "has_dvb_t2": specs.has_dvb_t2,
                "has_dvb_c": specs.has_dvb_c,
                "has_dvb_c2": specs.has_dvb_c2,
                "hdmi_ports": specs.hdmi_ports,
                "usb_ports": specs.usb_ports,
                "lan_ports": specs.lan_ports,
                "antenna_inputs": specs.antenna_inputs,
                "composite_inputs": specs.composite_inputs,
                "color": specs.color,
                "weight_kg": specs.weight_kg,
                "dimensions": list(specs.dimensions),
                "vesa_mount": list(specs.vesa_mount),
                "aspect_ratio": list(specs.aspect_ratio),
                "service_life_years": specs.service_life_years,
                "has_wifi": specs.has_wifi,
                "has_bluetooth": specs.has_bluetooth,
                "has_smart_tv": specs.has_smart_tv,
                "operating_system": (
                    specs.operating_system.value
                    if hasattr(specs.operating_system, "value")
                    else str(specs.operating_system)
                ),
                "os_version": specs.os_version,
            },
            "state": {
                "is_on": tv._is_on,
                "current_source": (
                    tv._current_source.value
                    if hasattr(tv._current_source, "value")
                    else str(tv._current_source)
                ),
                "current_channel": tv._current_channel,
                "wifi_enabled": tv._wifi_enabled,
                "bluetooth_enabled": tv._bluetooth_enabled,
            },
        }

    def _dict_to_tv(self, data: Dict[str, Any]) -> Television:
        spec_data = data["specs"]
        screen_data = spec_data["screen"]
        audio_data = spec_data["audio"]

        technology = ScreenTechnology(screen_data["technology"])
        coverage = ScreenCoverage(screen_data["coverage"])

        screen = Screen(
            technology=technology,
            diagonal=screen_data["diagonal"],
            resolution_width=screen_data["resolution_width"],
            resolution_height=screen_data["resolution_height"],
            response_time_ms=screen_data["response_time_ms"],
            coverage=coverage,
            refresh_rate_hz=screen_data["refresh_rate_hz"],
            brightness_nits=screen_data["brightness_nits"],
            brightness_level=screen_data.get("brightness", 50),
            contrast_level=screen_data.get("contrast", 50),
        )

        eq = Equalizer(
            low=audio_data["equalizer"]["low"],
            mid=audio_data["equalizer"]["mid"],
            high=audio_data["equalizer"]["high"],
        )

        audio = AudioSystem(
            speakers_count=audio_data["speakers_count"],
            speaker_power_w=audio_data["speaker_power_w"],
            has_subwoofer_output=audio_data["has_subwoofer_output"],
            volume=audio_data.get("volume", 30),
            equalizer=eq,
        )

        if audio_data.get("subwoofer_connected", False):
            try:
                audio.connect_subwoofer(True)
            except ValueError:
                pass

        os_map = {
            "отсутствует": OperatingSystem.NONE,
            "Android TV": OperatingSystem.ANDROID_TV,
            "VIDAA": OperatingSystem.VIDAA,
            "WebOS": OperatingSystem.WEBOS,
            "Tizen": OperatingSystem.TIZEN,
            "Яндекс ТВ": OperatingSystem.YANDEX_TV,
            "Салют ТВ": OperatingSystem.SALUT_TV,
        }
        os_value = spec_data["operating_system"]
        operating_system = os_map.get(os_value, OperatingSystem.NONE)

        specs = TechnicalSpecifications(
            model_name=spec_data["model_name"],
            screen=screen,
            audio=audio,
            has_dvb_s=spec_data["has_dvb_s"],
            has_dvb_s2=spec_data["has_dvb_s2"],
            has_dvb_t=spec_data["has_dvb_t"],
            has_dvb_t2=spec_data["has_dvb_t2"],
            has_dvb_c=spec_data["has_dvb_c"],
            has_dvb_c2=spec_data["has_dvb_c2"],
            hdmi_ports=spec_data["hdmi_ports"],
            usb_ports=spec_data["usb_ports"],
            lan_ports=spec_data["lan_ports"],
            antenna_inputs=spec_data["antenna_inputs"],
            composite_inputs=spec_data["composite_inputs"],
            color=spec_data["color"],
            weight_kg=spec_data["weight_kg"],
            dimensions=tuple(spec_data["dimensions"]),
            vesa_mount=tuple(spec_data["vesa_mount"]),
            aspect_ratio=tuple(spec_data["aspect_ratio"]),
            service_life_years=spec_data["service_life_years"],
            has_wifi=spec_data["has_wifi"],
            has_bluetooth=spec_data["has_bluetooth"],
            has_smart_tv=spec_data["has_smart_tv"],
            operating_system=operating_system,
            current_os_version=spec_data.get("os_version", "1.0"),
        )

        tv = Television(specs, name=data["name"])

        if "state" in data:
            state = data["state"]
            if state.get("is_on", False):
                try:
                    tv.turn_on()
                except RuntimeError:
                    pass

            from src.models.television import TvSource

            source_value = state.get("current_source", "выключен")
            for src in TvSource:
                if src.value == source_value:
                    tv._current_source = src
                    break

            tv._current_channel = state.get("current_channel", 1)
            tv._wifi_enabled = state.get("wifi_enabled", False)
            tv._bluetooth_enabled = state.get("bluetooth_enabled", False)

        return tv

    def save_all(self, televisions: List[Television]) -> None:
        try:
            data = [self._tv_to_dict(tv) for tv in televisions]
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise StorageError(f"Ошибка сохранения: {str(e)}")

    def load_all(self) -> List[Television]:
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            televisions = []
            for item in data:
                try:
                    tv = self._dict_to_tv(item)
                    televisions.append(tv)
                except Exception as e:
                    print(f"Ошибка загрузки телевизора: {str(e)}")
                    continue
            return televisions
        except json.JSONDecodeError as e:
            raise StorageError(f"Ошибка формата JSON: {str(e)}")
        except Exception as e:
            raise StorageError(f"Ошибка загрузки: {str(e)}")

    def add(self, television: Television) -> None:
        tvs = self.load_all()
        tvs.append(television)
        self.save_all(tvs)

    def remove(self, index: int) -> bool:
        tvs = self.load_all()
        if 0 <= index < len(tvs):
            tvs.pop(index)
            self.save_all(tvs)
            return True
        return False

    def get_all(self) -> List[Television]:
        return self.load_all()
