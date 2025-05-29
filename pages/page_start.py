import tkinter as tk

class PageStart(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.title_lb = tk.Label(self, text="MAKE; AMS - Make Authorize Management System").pack(pady=50)
        self.sub_lb = tk.Label(self, text="장치 클라이언트를 로드 중입니다 . . .").pack(pady=50)
    
        self.after(3, lambda: controller.show_page("MainPage"))
