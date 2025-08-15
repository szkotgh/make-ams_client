import config
import tkinter as tk
from datetime import datetime
import psutil
import os

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

def get_status_korean(status) -> str:
    status_map = {
        config.STATUS_ENABLE: "활성화",
        config.STATUS_DISABLE: "비활성화",
        config.STATUS_OPEN: "열림",
        config.STATUS_RESTRIC: "내부인",
        config.STATUS_CLOSE: "제한"
    }
    return status_map.get(status, "알 수 없음")