import tkinter as tk
import config
import utils
import log_manager

class PageAdminLog(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        title_frame = tk.Frame(self)
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="로그열람", font=(config.DEFAULT_FONT, 28, "bold"), fg="black").pack()
        tk.Label(title_frame, text="내부 장치 로그입니다. 최근 100개의 로그만 표시됩니다.", font=(config.DEFAULT_FONT, 14), fg="black").pack()
        
        self.text_area = tk.Text(self, font=(config.DEFAULT_FONT, 12), width=58, height=10)
        self.text_area.pack(expand=True, fill="both", padx=20)

        tk.Button(self, text="뒤로가기", font=(config.DEFAULT_FONT, 14), width=10, height=2,
                  command=lambda: self.controller.show_page("PageAdminMain")).pack(pady=10)

    def refresh_log(self):
        self.text_area.delete("1.0", tk.END)
        logs = log_manager.service.get_logs(limit=100)
        for log in logs:
            time, method, action, details = log[1], log[2], log[3], log[4]
            self.text_area.insert(tk.END, f"{time} | {method} | {action} | {details}\n")
        self.text_area.see(tk.END)

    def on_show(self):
        self.refresh_log()
