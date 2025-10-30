import setting
import tkinter as tk
from datetime import datetime
import os
import subprocess
import socket
import psutil

def get_program_pid() -> int:
    return os.getpid()

def get_now_datetime() -> datetime:
    return datetime.now()

def get_display_size() -> tuple[int, int]:
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    return screen_width, screen_height

def get_wifi_ssid():
    try:
        result = subprocess.check_output(
            ["iwgetid", "-r"], stderr=subprocess.DEVNULL
        )
        ssid = result.decode().strip()
        return ssid if ssid else None
    except subprocess.CalledProcessError:
        return None

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def get_status_korean(status) -> str:
    status_map = {
        setting.STATUS_ENABLE: "활성화",
        setting.STATUS_DISABLE: "비활성화",
        setting.STATUS_OPEN: "열림",
        setting.STATUS_RESTRIC: "내부인",
        setting.STATUS_CLOSE: "제한"
    }
    return status_map.get(status, "알 수 없음")

def get_hardware_info():
    cpu_usage = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    try: cpu_temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
    except: cpu_temp = 0
    info = {
        "cpu_usages": psutil.cpu_percent(interval=1, percpu=True),
        "cpu_count": psutil.cpu_count(),
        "cpu_temp": cpu_temp,
        "total_memory": memory_info.total,
        "used_memory": memory_info.used,
        "total_disk": psutil.disk_usage('/').total,
        "used_disk": psutil.disk_usage('/').used
    }
    return info

def format_bytes(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if size == 0:
        return "0B"
    
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.2f}{units[i]}"
