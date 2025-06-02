import tkinter as tk
import config

class PageAdminLog(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="로그열람", font=(config.DEFAULT_FONT, 28, "bold"), fg="black").pack(pady=20)

        self.text_area = tk.Text(self, font=(config.DEFAULT_FONT, 14), width=60, height=10)
        self.text_area.pack(expand=True, fill="both", padx=20)

        tk.Button(self, text="뒤로가기", font=(config.DEFAULT_FONT, 14), width=10, height=2,
                  command=lambda: self.controller.show_page("MainPage")).pack(pady=10)

    def on_show(self):
        pass
