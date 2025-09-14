import tkinter as tk
import threading
import setting
import time
import managers.log_manager as log_manager

class PageAdminLog(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        title_frame = tk.Frame(self)
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="로그열람", font=(setting.DEFAULT_FONT, 28, "bold"), fg="black").pack()
        tk.Label(title_frame, text="내부 장치 로그입니다. 최근 500개의 로그만 표시됩니다.", font=(setting.DEFAULT_FONT, 14), fg="black").pack()
        
        self.text_area = tk.Text(self, font=(setting.DEFAULT_FONT, 12), width=58, height=10)
        self.text_area.pack(expand=True, fill="both", padx=20)

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="뒤로가기", font=(setting.DEFAULT_FONT, 14), width=10, height=2,
                  command=lambda: self.controller.show_page("PageAdminMain")).pack(side="left", padx=5)
        self.refresh_button = tk.Button(buttons_frame, text="새로고침", font=(setting.DEFAULT_FONT, 14), width=10, height=2,
                  command=lambda: self.refresh_log())
        self.refresh_button.pack(side="left", padx=5)

    def refresh_log(self):
        def _refresh():
            self.refresh_button.config(state="disabled")
            self.text_area.delete("1.0", tk.END)
            logs = log_manager.service.get_logs(limit=500)
            for index, log in enumerate(reversed(logs)):
                log_time, method, action, details = log[1], log[2], log[3], log[4]
                self.text_area.insert(tk.END, f"{log_time} | {method} | {action} | {details}\n")
                if index % 100 == 0: self.text_area.see(tk.END)
                time.sleep(0.0001)
            self.text_area.see(tk.END)
            self.refresh_button.config(state="normal")
        threading.Thread(target=_refresh, daemon=True).start()
        
        print("[PageAdminLog] Log refreshed")

    def on_show(self):
        log_manager.service.insert_log("ADMIN", "ACCESS", "로그 열람 페이지에 접근했습니다.")
        self.refresh_log()
