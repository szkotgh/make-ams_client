import os
import tkinter as tk
import config

class PageAdminMain(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.admin_frame = tk.Frame(self)
        self.admin_frame.pack(expand=True)

        tk.Label(self.admin_frame, text="관리자 메뉴", font=(config.DEFAULT_FONT, 28, "bold"), fg="black").pack(pady=50)

        button_frame = tk.Frame(self.admin_frame)
        button_frame.pack()

        tk.Button(button_frame, text="시스템 재시작", font=(config.DEFAULT_FONT, 16), width=12, height=3).pack(side="left", padx=5)
        tk.Button(button_frame, text="프로그램 종료", font=(config.DEFAULT_FONT, 16), width=12, height=3, command=lambda: os._exit(os.EX_OK)).pack(side="left", padx=5)
        tk.Button(button_frame, text="프로그램 재시작", font=(config.DEFAULT_FONT, 16), width=12, height=3, command=lambda: os._exit(1)).pack(side="left", padx=5)
        tk.Button(button_frame, text="자동문 작동", font=(config.DEFAULT_FONT, 16), width=12, height=3).pack(side="left", padx=5)

        tk.Button(self.admin_frame, text="관리자 종료", font=(config.DEFAULT_FONT, 14), width=10, height=2, command=lambda: self.controller.show_page("MainPage")).pack(pady=20)

    def on_show(self):
        pass