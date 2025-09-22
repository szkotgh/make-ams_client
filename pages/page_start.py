import time
import tkinter as tk
import setting
import threading
import managers.hardware_manager as hardware_manager

class PageStart(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="MAKE; AMS\nMAKE Authorize Management System", font=(setting.DEFAULT_FONT, 22, 'bold'), justify='center', anchor='center').pack(pady=50, anchor='center')
        
        self.initialized_text = tk.Label(self, text="하드웨어 초기화를 시작합니다 . . .", font=(setting.DEFAULT_FONT, 16), justify='center', anchor='center')
        self.initialized_text.pack(pady=50, anchor='center')

    def on_show(self):
        threading.Thread(target=self._on_show, daemon=True).start()

    def _on_show(self):
        while True:
            self.after(0, lambda: self.initialized_text.config(text=hardware_manager.initialized_text))
            
            if hardware_manager.is_initialized:
                if hardware_manager.status_led:
                    hardware_manager.status_led.on('green')
                self.controller.init_pages()
                self.after(0, lambda: self.controller.show_page("MainPage"))
                break

            time.sleep(0.05)
