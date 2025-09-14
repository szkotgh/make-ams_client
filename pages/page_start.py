import tkinter as tk
import setting
import managers.hardware_manager as hardware_manager

class PageStart(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title_lb = tk.Label(self, text="MAKE; AMS\nMAKE Authorize Management System", font=(setting.DEFAULT_FONT, 22, 'bold'), justify='center', anchor='center')
        self.title_lb.pack(pady=50, anchor='center')
        
        self.sub_lb = tk.Label(self, text="초기화 중입니다 . . .", font=(setting.DEFAULT_FONT, 16), justify='center', anchor='center')
        self.sub_lb.pack(pady=50, anchor='center')

    def on_show(self):
        if hardware_manager.is_initialized:
            hardware_manager.status_led.on('green')
            self.after(100, lambda: self.controller.show_page("MainPage"))
        else:
            self.after(100, lambda: self.controller.show_page("PageStart"))
