import os
import tkinter as tk
import config
import utils

class PageAdminMain(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.admin_frame = tk.Frame(self)
        self.admin_frame.pack(expand=True)

        title_frame = tk.Frame(self.admin_frame)
        title_frame.pack(pady=30)

        tk.Label(title_frame, text="관리자 메뉴", font=(config.DEFAULT_FONT, 28, "bold"), fg="black").pack(pady=10)
        tk.Label(title_frame, text=f"디스플레이 크기: {utils.get_display_size()}", font=(config.DEFAULT_FONT, 16), fg="black").pack()
        self.uptime = utils.get_now_datetime() - config.START_TIME
        self.uptime_label = tk.Label(title_frame, text=f"작동시간: {self.uptime}", font=(config.DEFAULT_FONT, 16), fg="black")
        def update_uptime():
            self.uptime = utils.get_now_datetime() - config.START_TIME
            self.uptime_label.config(text=f"작동시간: {self.uptime}")
            self.uptime_label.after(1000, update_uptime)
        update_uptime()
        self.uptime_label.pack()

        button_frame = tk.Frame(self.admin_frame)
        button_frame.pack()

        tk.Button(button_frame, text="시스템 재시작", font=(config.DEFAULT_FONT, 16, 'bold'), width=10, height=3, command=lambda: os.system("sudo reboot now")).pack(side="left", padx=2)
        tk.Button(button_frame, text="프로그램 종료", font=(config.DEFAULT_FONT, 16, 'bold'), width=10, height=3, command=lambda: os._exit(0)).pack(side="left", padx=2)
        tk.Button(button_frame, text="프로그램 재시작", font=(config.DEFAULT_FONT, 16, 'bold'), width=10, height=3, command=lambda: os._exit(1)).pack(side="left", padx=2)
        tk.Button(button_frame, text="자동문 작동", font=(config.DEFAULT_FONT, 16, 'bold'), width=10, height=3).pack(side="left", padx=2)
        tk.Button(button_frame, text="로그 열람", font=(config.DEFAULT_FONT, 16, 'bold'), width=10, height=3, command=lambda: self.controller.show_page("PageAdminLog")).pack(side="left", padx=2)

        tk.Button(self.admin_frame, text="관리자 종료", font=(config.DEFAULT_FONT, 14), width=10, height=2, command=lambda: self.controller.show_page("MainPage")).pack(pady=20)

    def on_show(self):
        pass