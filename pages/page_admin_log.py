import tkinter as tk
import setting
import utils
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
        tk.Button(buttons_frame, text="새로고침", font=(setting.DEFAULT_FONT, 14), width=10, height=2,
                  command=lambda: self.refresh_log()).pack(side="left", padx=5)

    def refresh_log(self):
        self.text_area.delete("1.0", tk.END)
        logs = log_manager.service.get_logs(limit=500)
        for log in reversed(logs):
            time, method, action, details = log[1], log[2], log[3], log[4]
            self.text_area.insert(tk.END, f"{time} | {method} | {action} | {details}\n")
        self.text_area.see(tk.END)
        print("[PageAdminLog] Log refreshed")

    def on_show(self):
        log_manager.service.insert_log("관리자", "승인", "로그를 열람했습니다.")
        self.refresh_log()
