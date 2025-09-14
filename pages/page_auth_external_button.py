import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import setting
import managers.auth_manager as auth_manager
import managers.hardware_manager as hardware_manager
import managers.log_manager as log_manager
from datetime import datetime, timedelta

class PageAuthExternalButton(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.nfc_enable = False

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

        img_temp = Image.open(setting.DOOR_ICON_IMG_PATH)
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

        self.title = tk.Label(content_frame, text="외부인 출입", font=(setting.DEFAULT_FONT, 48, "bold"), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="잠시만 기다려주세요", font=(setting.DEFAULT_FONT, 32), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)
        
        # Register callback for automatic re-registration after hardware init
        hardware_manager.external_button.register_callback(self._detect_button)

    def on_show(self):
        log_manager.service.insert_log("EXTERNAL_AUTH", "ACCESS", "외부인 출입 인증 페이지에 접근했습니다.")
        threading.Thread(target=self.button_auth, daemon=True).start()
    
    def _detect_button(self):
        if self.controller.now_page != "MainPage":
            return

        self.controller.show_page("PageAuthExternalButton")
            
    def button_auth(self):
        self._set_title("외부인 출입")
        self.main_frame.config(bg=setting.AUTH_COLOR)

        # Check button enabled
        if not auth_manager.service.get_button_status() == setting.STATUS_ENABLE:
            self._set_title("외부인 출입 불가")
            self._set_sub_title("비활성화되어 있습니다")
            hardware_manager.speaker.play(setting.WRONG_SOUND_PATH)
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return

        # Auth Request
        self._set_sub_title("정보를 가져오고 있습니다")
        self.auth_result = auth_manager.service.request_button_auth()
        
        if not self.auth_result.success or self.auth_result.code != 200:
            self._set_title("외부인 출입 불가")
            self._set_sub_title(f"{self.auth_result.message}")
            log_manager.service.insert_log("EXTERNAL_AUTH", "FAIL", f"외부인 출입 거부 (상세: {self.auth_result.message})")
            hardware_manager.speaker.play(setting.WRONG_SOUND_PATH)
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return

        self._set_title("환영합니다")
        self._set_sub_title(f"{self.auth_result.message}")
        log_manager.service.insert_log("EXTERNAL_AUTH", "SUCCESS", "외부인 출입 승인 - 문이 열렸습니다.")
        hardware_manager.door.open_door()

        last_button_time = datetime.now()
        while True:
            if hardware_manager.external_button.read_button():
                last_button_time = datetime.now()
            if datetime.now() - last_button_time > timedelta(seconds=3):
                break
            time.sleep(0.1)
        
        hardware_manager.door.close_door()
        self.controller.after(0, lambda: self.controller.show_page("MainPage"))
    
    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))