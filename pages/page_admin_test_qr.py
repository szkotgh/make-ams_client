import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
import managers.hardware_manager as hardware_manager
import setting

class PageAdminTestQR(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 상태 변수
        self.detect_qr_value = None
        self.test_running = False
        self._test_lock = threading.Lock()

        # main frame
        self.main_frame = tk.Frame(self, width=setting.DISPLAY_WIDTH, height=setting.DISPLAY_HEIGHT, background=setting.AUTH_COLOR)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # left frame
        self.left_frame = tk.Frame(self.main_frame, width=int(setting.DISPLAY_WIDTH * 0.4), bg=setting.AUTH_COLOR)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=50)
        self.left_frame.pack_propagate(False)
    
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        img_temp = Image.open(setting.QR_ICON_IMG_PATH)
        img_temp = img_temp.resize((140, 140))
        img_temp = ImageTk.PhotoImage(img_temp)
        self.img_temp = img_temp
        self.image_label = tk.Label(self.left_frame, image=self.img_temp, bg=setting.AUTH_COLOR, borderwidth=0, highlightthickness=0)
        self.image_label.grid(row=1, column=0, pady=0)

        # right frame
        right_frame = tk.Frame(self.main_frame, width=int(setting.DISPLAY_WIDTH * 0.6), bg=setting.AUTH_COLOR)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)

        content_frame = tk.Frame(right_frame, bg=setting.AUTH_COLOR)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.title = tk.Label(content_frame, text="QR 테스트", font=(setting.DEFAULT_FONT, 48, "bold"), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="QR을 인식시켜주세요", font=(setting.DEFAULT_FONT, 32), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)

        tk.Button(content_frame, text="나가기", font=(setting.DEFAULT_FONT, 16, 'bold'), fg="black", height=1, width=8, command=self._exit_test).pack()

        self.test_running = False
        hardware_manager.qr.register_callback(self._detect_qr)
        threading.Thread(target=self._check_qr_status, daemon=True).start()
    def _detect_qr(self, _qr_result: str):
        print(f"[PageAdminTestQR] QR detected: {_qr_result}")
        
        if self.controller.now_page != "PageAdminTestQR" or self.test_running:
            print(f"[PageAdminTestQR] QR ignored - current page: {self.controller.now_page}, test running: {self.test_running}")
            return

        with self._test_lock:
            if self.test_running:
                return
            self.detect_qr_value = _qr_result
            self.test_running = True
            print(f"[PageAdminTestQR] QR test started, transitioning to PageAdminTestQR")
            self.controller.show_page("PageAdminTestQR")
            threading.Thread(target=self._run_test_flow, daemon=True).start()

    def _exit_test(self):
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        self.controller.show_page("PageAdminMain")
        with self._test_lock:
            self.test_running = False
    
    def _check_qr_status(self):
        while True:
            if self.test_running:
                time.sleep(1)
                continue

            if hardware_manager.qr.is_initialized == False:
                self._set_sub_title("오류: 센서를 점검하십시오.")
            else:
                self._set_sub_title("QR을 인식시켜주세요")
            time.sleep(1)
            continue

    def _run_test_flow(self):
        self.main_frame.config(bg=setting.AUTH_COLOR)

        hardware_manager.speaker.play(setting.SUCCESS_SOUND_PATH)
        self._set_sub_title(f"{self.detect_qr_value}")
        time.sleep(3)
        self._set_sub_title("QR을 인식시켜주세요")
        with self._test_lock:
            self.test_running = False
        
    def on_show(self):
        self.main_frame.config(bg=setting.AUTH_COLOR)

        if self.test_running:
            return

    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))
        