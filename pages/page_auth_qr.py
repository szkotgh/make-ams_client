import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
import hardware_manager
import auth_manager
import config
import log_manager

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
        
        self.qr_listner = hardware_manager.QRListener()
        self.qr_listner.start()
        
        self.qr_value = None
        threading.Thread(target=self._detect_qr, daemon=True).start()

    def _detect_qr(self):
        while True:
            time.sleep(0.05)
            if not self.controller.now_page == "MainPage":
                continue
            
            self.qr_value = self.qr_listner.get_qr_detect_result()
            if self.qr_value == None:
                continue
            
            self.controller.after(0, lambda: self.controller.show_page("PageAuthQR"))
            threading.Thread(target=self._run_auth_flow, daemon=True).start()

    def on_show(self):
        self.main_frame.config(bg=config.AUTH_COLOR)
        self._set_title("QR 인증")
        
        
        threading.Thread(target=self._run_auth_flow, daemon=True).start()
        
        self.controller.after(3000, lambda: self.controller.show_page("MainPage"))

    def _run_auth_flow(self):
        self.main_frame.config(bg=config.AUTH_COLOR)
        self._set_title("QR 인증")

        # Auth Request
        ## QR Enable
        if not auth_manager.service.get_qr_status() == config.STATUS_ENABLE:
            self._set_title("QR 인증 불가")
            self._set_sub_title("QR 모듈이 비활성화되어 있습니다.")
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return

        # get info
        self._set_sub_title("정보를 가져오고 있습니다")
        time.sleep(0.5)
        
        # user auth logic
        result = False
        user_name = None
        
        if self.qr_value == "G23KA4AGA":
            result = True
            user_name = "관리자"
            
        # open door
        if result:
            self._set_title("QR 인증 성공")
            self._set_sub_title(f"{user_name}님 환영합니다")
            log_manager.service.insert_log("QR출입", "승인", f"QR출입이 승인되었습니다: UNAME={user_name} VALUE={self.qr_value}")
            hardware_manager.service.auto_open_door()
        else:
            self._set_title("QR 인증 실패")
            self._set_sub_title(f"인증에 실패하였습니다\n{self.qr_value}")
            log_manager.service.insert_log("QR출입", "차단", f"올바르지 않은 QR로 접근을 시도했습니다: VALUE={self.qr_value}")
        

        self.controller.after(3000, lambda: self.controller.show_page("MainPage"))

    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))