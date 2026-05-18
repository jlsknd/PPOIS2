from flask import Flask, render_template, request, redirect, url_for
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.storage.tv_repository import TVRepository
from src.services.tv_service import TVService
from src.models.television import TvSource, ChannelList
from src.models.screen import Screen, ScreenTechnology, ScreenCoverage
from src.models.audio import AudioSystem, Equalizer
from src.models.specs import TechnicalSpecifications, OperatingSystem
from src.models.television import Television

app = Flask(__name__)

repo = TVRepository("data/televisions.json")
tvs = repo.load_all()
current_tv_index = 0 if tvs else None
current_service = TVService(tvs[current_tv_index]) if tvs else None

show_bt_list = False

ALLOWED_COLORS = [
    ("черный", "#1a1a1a"), ("белый", "#ffffff"), ("серебристый", "#c0c0c0"),
    ("серый", "#808080"), ("красный", "#ff0000"), ("синий", "#0000ff"),
    ("зеленый", "#00ff00"), ("желтый", "#ffff00"), ("золотой", "#ffd700"),
    ("розовый", "#ff69b4"), ("фиолетовый", "#800080"), ("оранжевый", "#ffa500"),
    ("коричневый", "#8b4513"), ("бежевый", "#f5f5dc")
]

TECHNOLOGIES = [
    ("LED", ScreenTechnology.LED), ("OLED", ScreenTechnology.OLED),
    ("QLED", ScreenTechnology.QLED), ("PDP", ScreenTechnology.PDP),
    ("LCD", ScreenTechnology.LCD)
]

OS_TYPES = [
    ("ANDROID_TV", "Android TV"), ("VIDAA", "VIDAA"), ("WEBOS", "WebOS"),
    ("TIZEN", "Tizen"), ("YANDEX_TV", "Яндекс ТВ"), ("SALUT_TV", "Салют ТВ")
]

def get_tv():
    if current_tv_index is not None and current_tv_index < len(tvs):
        return tvs[current_tv_index]
    return None

@app.route("/")
def index():
    color_map = dict(ALLOWED_COLORS)
    tv_list = []
    for i, tv in enumerate(tvs):
        color_hex = color_map.get(tv.specs.color, "#1a1a1a")
        tv_list.append({
            "index": i, "name": tv.name, "model": tv.specs.model_name,
            "is_on": tv.is_on, "selected": i == current_tv_index,
            "color": tv.specs.color, "color_hex": color_hex
        })
    return render_template("index.html", tvs=tv_list)

@app.route("/select/<int:index>")
def select_tv(index):
    global current_tv_index, current_service
    if 0 <= index < len(tvs):
        current_tv_index = index
        current_service = TVService(tvs[index])
    return redirect(url_for("index"))

@app.route("/control")
def control():
    tv = get_tv()
    if not tv:
        return redirect(url_for("index"))
    channels = ChannelList.get_all()
    
    bt_paired_devices = []
    bt_paired_names = []
    if hasattr(tv, '_bt_paired_devices'):
        bt_paired_devices = tv._bt_paired_devices
        bt_paired_names = [d["name"] for d in bt_paired_devices]
    
    bt_scan_results = []
    if hasattr(tv, '_bt_scan_results'):
        bt_scan_results = tv._bt_scan_results
    
    bt_connected_devices = [d for d in bt_paired_devices if d.get("connected", False)]
    
    hdmi_devices = getattr(tv, '_hdmi_devices', {})
    
    return render_template("control.html", 
                          tv=tv, 
                          status=tv.get_status(), 
                          channels=channels,
                          bt_paired_devices=bt_paired_devices,
                          bt_paired_names=bt_paired_names,
                          bt_scan_results=bt_scan_results,
                          bt_connected_devices=bt_connected_devices,
                          hdmi_devices=hdmi_devices,
                          show_bt_list=show_bt_list)

@app.route("/action/<action>")
def action(action):
    global tvs, repo
    tv = get_tv()
    if not tv:
        return redirect(url_for("index"))

    if action == "power":
        if tv.is_on: tv.turn_off()
        else: tv.turn_on()
    elif action == "source_tv":
        tv.switch_to_tv()
    elif action == "source_smart":
        tv.switch_to_smart_tv()
    elif action == "channel_up":
        tv.next_channel()
    elif action == "channel_down":
        tv.prev_channel()
    elif action.startswith("channel_"):
        ch_num = int(action.split("_")[1])
        tv.set_channel(ch_num)
    elif action == "volume_up":
        tv.volume_up()
    elif action == "volume_down":
        tv.volume_down()
    elif action == "mute":
        tv.mute()
    elif action == "brightness_up":
        tv.screen.brightness = min(100, tv.screen.brightness + 5)
    elif action == "brightness_down":
        tv.screen.brightness = max(0, tv.screen.brightness - 5)
    elif action == "contrast_up":
        tv.screen.contrast = min(100, tv.screen.contrast + 5)
    elif action == "contrast_down":
        tv.screen.contrast = max(0, tv.screen.contrast - 5)
    elif action == "wifi_toggle":
        if tv._wifi_enabled: tv.disable_wifi()
        else: tv.enable_wifi()
    elif action == "bluetooth_toggle":
        if tv._bluetooth_enabled: tv.disable_bluetooth()
        else: tv.enable_bluetooth()
    elif action == "subwoofer_toggle":
        tv.audio.connect_subwoofer(not tv.audio.subwoofer_connected)
    elif action == "update_os":
        if tv.is_on and tv.specs.has_smart_tv and tv._wifi_enabled:
            tv.update_software()
    elif action == "update_all":
        if tv.is_on and tv.specs.has_smart_tv and tv._wifi_enabled:
            current = float(tv.specs.os_version)
            max_version = tv.specs._original_version + 1.0
            while current < max_version:
                tv.update_software()
                current = float(tv.specs.os_version)

    repo.save_all(tvs)
    return redirect(url_for("control"))

@app.route("/set_volume", methods=["POST"])
def set_volume():
    tv = get_tv()
    if tv:
        vol = int(request.form.get("volume", 30))
        tv.audio.volume = max(0, min(100, vol))
        repo.save_all(tvs)
    return redirect(url_for("control"))

@app.route("/set_brightness", methods=["POST"])
def set_brightness():
    tv = get_tv()
    if tv:
        val = int(request.form.get("brightness", 50))
        tv.screen.brightness = max(0, min(100, val))
        repo.save_all(tvs)
    return redirect(url_for("control"))

@app.route("/set_contrast", methods=["POST"])
def set_contrast():
    tv = get_tv()
    if tv:
        val = int(request.form.get("contrast", 50))
        tv.screen.contrast = max(0, min(100, val))
        repo.save_all(tvs)
    return redirect(url_for("control"))

@app.route("/set_equalizer", methods=["POST"])
def set_equalizer():
    tv = get_tv()
    if tv:
        low = int(request.form.get("eq_low", 0))
        mid = int(request.form.get("eq_mid", 0))
        high = int(request.form.get("eq_high", 0))
        tv.audio.equalizer.set_all(low, mid, high)
        repo.save_all(tvs)
    return redirect(url_for("control"))

@app.route("/add_tv", methods=["GET", "POST"])
def add_tv():
    global tvs, repo, current_tv_index, current_service

    if request.method == "POST":
        errors = []
        form_data = request.form.to_dict()
        
        name = request.form.get("name", "").strip()
        if not name: errors.append("Название телевизора не может быть пустым")
        
        model_name = request.form.get("model_name", "").strip()
        if not model_name: errors.append("Модель телевизора не может быть пустой")
        
        try:
            diagonal = float(request.form.get("screen_diagonal", 0))
            if diagonal < 10 or diagonal > 100:
                errors.append("Диагональ должна быть от 10 до 100 дюймов")
        except ValueError: errors.append("Диагональ должна быть числом")
        
        try:
            res_w = int(request.form.get("resolution_width", 0))
            res_h = int(request.form.get("resolution_height", 0))
            if res_w < 640 or res_w > 7680: errors.append("Ширина разрешения должна быть от 640 до 7680")
            if res_h < 480 or res_h > 4320: errors.append("Высота разрешения должна быть от 480 до 4320")
        except ValueError: errors.append("Разрешение должно быть целыми числами")
        
        try:
            response_time = int(request.form.get("response_time_ms", 0))
            if response_time < 1 or response_time > 50: errors.append("Время отклика должно быть от 1 до 50 мс")
        except ValueError: errors.append("Время отклика должно быть целым числом")
        
        try:
            refresh = int(request.form.get("refresh_rate_hz", 0))
            if refresh < 24 or refresh > 360: errors.append("Частота обновления должна быть от 24 до 360 Гц")
        except ValueError: errors.append("Частота обновления должна быть целым числом")
        
        try:
            brightness_nits = int(request.form.get("brightness_nits", 0))
            if brightness_nits < 100 or brightness_nits > 2000:
                errors.append("Яркость должна быть от 100 до 2000 нит")
            if brightness_nits < 0:
                errors.append("Яркость не может быть отрицательной")
        except ValueError:
            errors.append("Яркость должна быть целым числом")
        
        try:
            speakers = int(request.form.get("speakers_count", 0))
            if speakers < 0 or speakers > 6: errors.append("Количество динамиков должно быть от 0 до 6")
        except ValueError: errors.append("Количество динамиков должно быть целым числом")
        
        try:
            speaker_power = float(request.form.get("speaker_power_w", 0))
            if speaker_power < 0 or speaker_power > 15:
                errors.append("Мощность динамиков должна быть от 0 до 15 Вт")
        except ValueError: errors.append("Мощность динамиков должна быть числом")
        
        try:
            hdmi = int(request.form.get("hdmi_ports", 0))
            usb = int(request.form.get("usb_ports", 0))
            lan = int(request.form.get("lan_ports", 0))
            if hdmi < 0 or hdmi > 8: errors.append("HDMI порты должны быть от 0 до 8")
            if usb < 0 or usb > 8: errors.append("USB порты должны быть от 0 до 8")
            if lan < 0 or lan > 2: errors.append("LAN порты должны быть от 0 до 2")
        except ValueError: errors.append("Количество портов должно быть целыми числами")
        
        try:
            weight = float(request.form.get("weight_kg", 0))
            if weight < 0.1 or weight > 500: errors.append("Вес должен быть от 0.1 до 500 кг")
        except ValueError: errors.append("Вес должен быть числом")
        
        try:
            life = int(request.form.get("service_life_years", 0))
            if life < 1 or life > 30: errors.append("Срок службы должен быть от 1 до 30 лет")
        except ValueError: errors.append("Срок службы должен быть целым числом")
        
        color = request.form.get("color", "").strip()
        allowed_color_values = [c[0] for c in ALLOWED_COLORS]
        if color not in allowed_color_values: errors.append("Цвет должен быть выбран из списка")
        
        has_smart_tv = "has_smart_tv" in request.form
        operating_system = request.form.get("operating_system", "NONE")
        os_version = request.form.get("os_version", "").strip()
        
        import re
        if has_smart_tv:
            if not re.match(r'^\d+\.\d+$', os_version):
                errors.append("Версия ОС должна быть в формате 'число.число'")
        else:
            if operating_system != "NONE":
                errors.append("Противоречие: если нет Smart TV, операционная система не может быть выбрана")
            if os_version and os_version != "0.0":
                errors.append("Противоречие: если нет Smart TV, версия ОС не может быть указана")
        
        if errors:
            return render_template("add_tv.html", errors=errors, form_data=form_data,
                                 technologies=TECHNOLOGIES, os_types=OS_TYPES,
                                 allowed_colors=ALLOWED_COLORS)
        
        try:
            tech_map = dict(TECHNOLOGIES)
            technology = tech_map.get(request.form.get("technology", "LED"), ScreenTechnology.LED)

            screen = Screen(
                technology=technology, diagonal=diagonal,
                resolution_width=res_w, resolution_height=res_h,
                response_time_ms=response_time, refresh_rate_hz=refresh,
                brightness_nits=brightness_nits, brightness_level=50, contrast_level=50
            )

            audio = AudioSystem(
                speakers_count=speakers, speaker_power_w=speaker_power,
                has_subwoofer_output="has_subwoofer" in request.form, volume=30
            )

            if not has_smart_tv:
                operating_system_enum = OperatingSystem.NONE
                final_os_version = "0.0"
            else:
                os_map = dict(OS_TYPES)
                operating_system_enum = os_map.get(operating_system, OperatingSystem.ANDROID_TV)
                final_os_version = os_version

            specs = TechnicalSpecifications(
                model_name=model_name, screen=screen, audio=audio,
                hdmi_ports=hdmi, usb_ports=usb, lan_ports=lan,
                has_wifi="has_wifi" in request.form, has_bluetooth="has_bluetooth" in request.form,
                has_smart_tv=has_smart_tv, operating_system=operating_system_enum,
                current_os_version=final_os_version, color=color, weight_kg=weight,
                service_life_years=life
            )

            tv = Television(specs, name=name)
            tvs.append(tv)
            repo.save_all(tvs)

            if len(tvs) == 1:
                current_tv_index = 0
                current_service = TVService(tvs[0])

            return redirect(url_for("index"))

        except Exception as e:
            errors.append(f"Ошибка создания телевизора: {str(e)}")
            return render_template("add_tv.html", errors=errors, form_data=form_data,
                                 technologies=TECHNOLOGIES, os_types=OS_TYPES,
                                 allowed_colors=ALLOWED_COLORS)

    return render_template("add_tv.html", errors=[], form_data={},
                          technologies=TECHNOLOGIES, os_types=OS_TYPES,
                          allowed_colors=ALLOWED_COLORS)


@app.route("/action/bt_scan")
def bt_scan():
    """Сканирование Bluetooth устройств (сопряжение)"""
    global show_bt_list
    tv = get_tv()
    if not tv or not tv.is_on or not tv.specs.has_bluetooth or not tv._bluetooth_enabled:
        return redirect(url_for("control"))
    
    new_devices = [
        {"name": "Sony WH-1000XM4", "type": "наушники"},
        {"name": "JBL Charge 5", "type": "колонка"},
        {"name": "AirPods Pro", "type": "наушники"},
        {"name": "Xiaomi Mi Band", "type": "фитнес-браслет"},
    ]
    
    tv._bt_scan_results = new_devices
    show_bt_list = True
    return redirect(url_for("control"))


@app.route("/action/bt_pair/<device_name>")
def bt_pair(device_name):
    """Сопряжение с Bluetooth устройством"""
    tv = get_tv()
    if not tv or not tv.is_on or not tv.specs.has_bluetooth or not tv._bluetooth_enabled:
        return redirect(url_for("control"))
    
    if not hasattr(tv, '_bt_paired_devices'):
        tv._bt_paired_devices = []
    
    for device in tv._bt_paired_devices:
        if device["name"] == device_name:
            return redirect(url_for("control"))
    
    if hasattr(tv, '_bt_scan_results'):
        for device in tv._bt_scan_results:
            if device["name"] == device_name:
                tv._bt_paired_devices.append({
                    "name": device["name"],
                    "type": device["type"],
                    "connected": False
                })
                break
    
    return redirect(url_for("control"))


@app.route("/action/bt_connect/<device_name>")
def bt_connect(device_name):
    """Подключение к Bluetooth устройству"""
    tv = get_tv()
    if not tv or not tv.is_on or not tv.specs.has_bluetooth or not tv._bluetooth_enabled:
        return redirect(url_for("control"))
    
    if not hasattr(tv, '_bt_paired_devices'):
        tv._bt_paired_devices = []
    
    for device in tv._bt_paired_devices:
        device["connected"] = (device["name"] == device_name)
    
    return redirect(url_for("control"))


@app.route("/action/bt_disconnect/<device_name>")
def bt_disconnect(device_name):
    """Отключение Bluetooth устройства"""
    tv = get_tv()
    if not tv or not tv.is_on or not tv.specs.has_bluetooth:
        return redirect(url_for("control"))
    
    if hasattr(tv, '_bt_paired_devices'):
        for device in tv._bt_paired_devices:
            if device["name"] == device_name:
                device["connected"] = False
                break
    
    return redirect(url_for("control"))


@app.route("/action/bt_toggle_list")
def bt_toggle_list():
    """Показать/скрыть список Bluetooth устройств"""
    global show_bt_list
    show_bt_list = not show_bt_list
    return redirect(url_for("control"))


@app.route("/action/bt_clear_scan")
def bt_clear_scan():
    """Очистить список найденных устройств"""
    tv = get_tv()
    if not tv:
        return redirect(url_for("control"))
    
    if hasattr(tv, '_bt_scan_results'):
        delattr(tv, '_bt_scan_results')
    
    return redirect(url_for("control"))


@app.route("/delete_tv")
def delete_tv():
    """Удаление текущего телевизора"""
    global tvs, repo, current_tv_index, current_service, show_bt_list
    
    if current_tv_index is not None and current_tv_index < len(tvs):
        deleted_name = tvs[current_tv_index].name
        tvs.pop(current_tv_index)
        
        if len(tvs) == 0:
            current_tv_index = None
            current_service = None
        else:
            current_tv_index = 0
            current_service = TVService(tvs[0])
        
        repo.save_all(tvs)
        show_bt_list = False
    
    return redirect(url_for("index"))


@app.route("/status")
def status():
    tv = get_tv()
    if not tv:
        return redirect(url_for("index"))
    
    bt_connected_devices = []
    if hasattr(tv, '_bt_paired_devices'):
        bt_connected_devices = [d for d in tv._bt_paired_devices if d.get("connected", False)]
    
    hdmi_devices = getattr(tv, '_hdmi_devices', {})
    
    return render_template("status.html", 
                          status=tv.get_status(),
                          bt_connected_devices=bt_connected_devices,
                          hdmi_devices=hdmi_devices)


@app.route("/specs")
def specs():
    tv = get_tv()
    if not tv: return redirect(url_for("index"))
    return render_template("specs.html", specs=tv.specs)

@app.route("/channels")
def channels():
    tv = get_tv()
    if not tv: return redirect(url_for("index"))
    channels_list = ChannelList.get_all()
    return render_template("channels.html", tv=tv, channels=channels_list)

@app.route("/hdmi")
def hdmi():
    tv = get_tv()
    if not tv: return redirect(url_for("index"))
    hdmi_ports = [{"port": port, "device": getattr(tv, '_hdmi_devices', {}).get(port, None)} 
                  for port in range(1, tv.specs.hdmi_ports + 1)]
    return render_template("hdmi.html", tv=tv, hdmi_ports=hdmi_ports, max_ports=tv.specs.hdmi_ports)

@app.route("/hdmi/connect", methods=["POST"])
def hdmi_connect():
    tv = get_tv()
    if not tv: return redirect(url_for("index"))
    try:
        port = int(request.form.get("port", 0))
        device_name = request.form.get("device_name", "").strip()
        if port < 1 or port > tv.specs.hdmi_ports:
            return render_template("hdmi.html", tv=tv, error=f"Порт должен быть от 1 до {tv.specs.hdmi_ports}",
                                  hdmi_ports=[], max_ports=tv.specs.hdmi_ports)
        if not device_name:
            return render_template("hdmi.html", tv=tv, error="Название устройства не может быть пустым",
                                  hdmi_ports=[], max_ports=tv.specs.hdmi_ports)
        if not hasattr(tv, '_hdmi_devices'): tv._hdmi_devices = {}
        if port in tv._hdmi_devices:
            return render_template("hdmi.html", tv=tv, error=f"HDMI порт {port} уже занят",
                                  hdmi_ports=[], max_ports=tv.specs.hdmi_ports)
        tv._hdmi_devices[port] = device_name
        repo.save_all(tvs)
        return redirect(url_for("hdmi"))
    except ValueError:
        return render_template("hdmi.html", tv=tv, error="Порт должен быть числом",
                              hdmi_ports=[], max_ports=tv.specs.hdmi_ports)

@app.route("/hdmi/disconnect", methods=["POST"])
def hdmi_disconnect():
    tv = get_tv()
    if not tv: return redirect(url_for("index"))
    try:
        port = int(request.form.get("port", 0))
        if port < 1 or port > tv.specs.hdmi_ports:
            return render_template("hdmi.html", tv=tv, error=f"Порт должен быть от 1 до {tv.specs.hdmi_ports}",
                                  hdmi_ports=[], max_ports=tv.specs.hdmi_ports)
        if not hasattr(tv, '_hdmi_devices') or port not in tv._hdmi_devices:
            return render_template("hdmi.html", tv=tv, error=f"На порту HDMI {port} нет устройства",
                                  hdmi_ports=[], max_ports=tv.specs.hdmi_ports)
        del tv._hdmi_devices[port]
        repo.save_all(tvs)
        return redirect(url_for("hdmi"))
    except ValueError:
        return render_template("hdmi.html", tv=tv, error="Порт должен быть числом",
                              hdmi_ports=[], max_ports=tv.specs.hdmi_ports)

if __name__ == "__main__":
    app.run(debug=True)