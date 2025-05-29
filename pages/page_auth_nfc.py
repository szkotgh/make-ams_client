import threading
import time
import tkinter as tk
import auth_manager
import config
from PIL import Image, ImageTk

class PageAuthNFC(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.nfc_enable = False

        # Create main frame with two columns: left (image), right (content)
        main_frame = tk.Frame(self, width=config.DISPLAY_WIDTH, height=config.DISPLAY_HEIGHT, background=config.AUTH_COLOR)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Left frame for image
        left_frame = tk.Frame(main_frame, width=int(config.DISPLAY_WIDTH * 0.4), bg=config.AUTH_COLOR)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_frame.pack_propagate(False)
    
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        img_temp = Image.open(config.NFC_ICON_IMG_PATH)
        img_temp = img_temp.resize((140, 140))
        img_temp = ImageTk.PhotoImage(img_temp)
        self.img_temp = img_temp
        self.image_label = tk.Label(left_frame, image=self.img_temp, bg=config.AUTH_COLOR, borderwidth=0, highlightthickness=0)
        self.image_label.grid(row=1, column=0, pady=20)

        # Right frame for text content
        right_frame = tk.Frame(main_frame, width=int(config.DISPLAY_WIDTH * 0.6), bg=config.AUTH_COLOR)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)

        # Center content vertically and horizontally
        content_frame = tk.Frame(right_frame, bg=config.AUTH_COLOR)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.title = tk.Label(content_frame, text="NFC 인증", font=(config.DEFAULT_FONT, 48, "bold"), bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack(pady=50)
        self.sub_title = tk.Label(content_frame, text="NFC 태그를 인식시켜주세요", font=(config.DEFAULT_FONT, 32), bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=10)

    def on_show(self):
        threading.Thread(target=self._run_auth_flow, daemon=True).start()

    def _run_auth_flow(self):
        self._set_title("NFC 인증")
        self._set_sub_title("NFC 모듈 초기화 중입니다")

        # NFC init
        time.sleep(1)

        # NFC Wait
        self._set_sub_title("NFC 태그를 인식시켜주세요")
        time.sleep(3)

        # Auth Request
        if auth_manager.service.get_nfc_status() and auth_manager.service.request_nfc_auth():
            self._set_sub_title("인증 성공. 환영합니다.")
            self.controller.after(0, lambda: self.controller.show_page("MainPage"))
        else:
            self._set_sub_title("인증 실패. 다시 시도해주세요.")

        # Reset NFC status
        self._set_title("이건희님, 환영합니다")
        for i in range(3, 0, -1):
            self._set_sub_title(f"{i}초 초기화면으로 돌아갑니다.")
            time.sleep(1)

        self.controller.after(0, lambda: self.controller.show_page("MainPage"))

    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))