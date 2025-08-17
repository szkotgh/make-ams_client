import tkinter as tk

import setting

class PageStart(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title_lb = tk.Label(self, text="MAKE; AMS\nMAKE Authorize Management System", font=(setting.DEFAULT_FONT, 22, 'bold')).pack(pady=50)
        self.sub_lb = tk.Label(self, text="시작 중입니다 . . .", font=(setting.DEFAULT_FONT, 16)).pack(pady=50)

    def on_show(self):
        self.after(500, lambda: self.controller.show_page("MainPage"))
