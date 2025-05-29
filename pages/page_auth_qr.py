import threading
import time
import tkinter as tk
from PIL import Image, ImageTk

import auth_manager
import config

class PageAuthQR(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.nfc_enable = False

        # main frame
        self.main_frame = tk.Frame(self, width=config.DISPLAY_WIDTH, height=config.DISPLAY_HEIGHT, background=config.AUTH_COLOR)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # left frame
        self.left_frame = tk.Frame(self.main_frame, width=int(config.DISPLAY_WIDTH * 0.4), bg=config.AUTH_COLOR)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=50)
        self.left_frame.pack_propagate(False)
    
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        img_temp = Image.open(config.QR_ICON_IMG_PATH)
        img_temp = img_temp.resize((140, 140))
        img_temp = ImageTk.PhotoImage(img_temp)
        self.img_temp = img_temp
        self.image_label = tk.Label(self.left_frame, image=self.img_temp, bg=config.AUTH_COLOR, borderwidth=0, highlightthickness=0)
        self.image_label.grid(row=1, column=0, pady=0)

        # right frame
        right_frame = tk.Frame(self.main_frame, width=int(config.DISPLAY_WIDTH * 0.6), bg=config.AUTH_COLOR)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)

        content_frame = tk.Frame(right_frame, bg=config.AUTH_COLOR)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.title = tk.Label(content_frame, text="QR 인증", font=(config.DEFAULT_FONT, 48, "bold"), fg="white", bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="QR을 인식시켜주세요", font=(config.DEFAULT_FONT, 32), fg="white", bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)

        # bottom frame
        bottom_frame = tk.Frame(self.main_frame, bg=config.AUTH_COLOR)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)
        bottom_frame.config(height=100)
        self.bottom_label = tk.Label(bottom_frame, text="QR 인증을 위해 인식시켜주세요.", font=(config.DEFAULT_FONT, 16), bg=config.AUTH_COLOR, fg="black")
        self.bottom_label.pack(pady=20)

    def on_show(self):
        threading.Thread(target=self._run_auth_flow, daemon=True).start()

    def _run_auth_flow(self):
        self.main_frame.config(bg=config.AUTH_COLOR)
        self._set_title("QR 인증")

        # QR init
        self._set_sub_title("QR 모듈 초기화 중입니다")
        time.sleep(1)

        # QR Wait
        self._set_sub_title("QR 태그를 인식시켜주세요")
        time.sleep(3)

        # Auth Request
        ## QR Enable
        if not auth_manager.service.get_qr_status() == config.STATUS_ENABLE:
            self._set_title("QR 인증 불가")
            self._set_sub_title("QR 모듈이 비활성화되어 있습니다.")
        ## QR Disable
        else:
            if auth_manager.service.request_qr_auth():
                self._set_title("QR 인증 성공")
                self._set_sub_title("이건희님, 출입이 승인되었습니다.")
            else:
                self._set_title("QR 인증 실패")
                self._set_sub_title(f"인증 실패. 처음부터 다시 시도하세요.")

        time.sleep(5)
        self.controller.after(0, lambda: self.controller.show_page("MainPage"))

    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))