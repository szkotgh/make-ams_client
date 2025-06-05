import threading
import time
import tkinter as tk
import auth_manager
import config
from PIL import Image, ImageTk

import hardware_manager

class PageAuthNFC(tk.Frame):
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

        img_temp = Image.open(config.NFC_ICON_IMG_PATH)
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

        self.title = tk.Label(content_frame, text="NFC 인증", font=(config.DEFAULT_FONT, 48, "bold"), fg="white", bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="NFC 태그를 인식시켜주세요", font=(config.DEFAULT_FONT, 32), fg="white", bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)

        # bottom frame
        bottom_frame = tk.Frame(self.main_frame, bg=config.AUTH_COLOR)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)
        bottom_frame.config(height=100)
        self.bottom_label = tk.Label(bottom_frame, text="NFC 인증을 위해 태그를 인식시켜주세요.", font=(config.DEFAULT_FONT, 16), bg=config.AUTH_COLOR, fg="black")
        self.bottom_label.pack(pady=20)
        
        # Start NFC detection thread
        threading.Thread(target=self._detect_nfc, daemon=True).start()

    def on_show(self):
        def nfc_auth_process():
            if not auth_manager.service.get_nfc_status() == config.STATUS_ENABLE:
                self.main_frame.after(0, lambda: self.main_frame.config(bg=config.DISABLE_COLOR))
                self._set_title("NFC 인증 불가")
                self._set_sub_title("NFC 모듈이 비활성화되어 있습니다.")
                self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
                return

            self.main_frame.after(0, lambda: self.main_frame.config(bg=config.AUTH_COLOR))
            self._set_title("NFC 인증")
            for i in range(10, 0, -1):
                self._set_sub_title(f"카드를 인식시켜주세요 ({i}s)")
                nfc_uid = hardware_manager.service.read_nfc(timeout=1.0)
                if nfc_uid is not None:
                    self._set_sub_title(nfc_uid + "\n태그를 인식했습니다.")
                    self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
                    return
            self._set_sub_title("카드를 인식하지 못했습니다.\n다시 시도해주세요.")
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))

        threading.Thread(target=nfc_auth_process, daemon=True).start()

    def _detect_nfc(self):
        while True:
            time.sleep(0.3)
            
            # 메인화면이 아닐 경우 대기
            if self.controller.now_page != "MainPage":
                continue
            
            # NFC를 인식할 때까지 대기
            nfc_uid = hardware_manager.service.read_nfc()
            if nfc_uid == None:
                continue
            
            # NFC 인증 화면으로 전환
            self.controller.show_page("PageAuthNFC")
            
            if not auth_manager.service.get_nfc_status() == config.STATUS_ENABLE:
                self.main_frame.config(bg=config.DISABLE_COLOR)
                self._set_title("NFC 인증 불가")
                self._set_sub_title("NFC 모듈이 비활성화되어 있습니다.")
                time.sleep(1)
                continue
            
            self.main_frame.config(bg=config.AUTH_COLOR)
            self._set_title("NFC 인증")
            self._set_sub_title(nfc_uid + "\n태그를 인식했습니다.")
            
            time.sleep(3)
            self.controller.after(0, lambda: self.controller.show_page("MainPage"))

    def _set_title(self, text):
        self.title.config(text=text)

    def _set_sub_title(self, text):
        self.sub_title.config(text=text)