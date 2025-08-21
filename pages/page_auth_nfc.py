import threading
import time
import tkinter as tk
import auth_manager
import setting
from PIL import Image, ImageTk
import hardware_manager
import log_manager

class PageAuthNFC(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.detect_nfc = False
        self.nfc_uid = None
        self.password_entry = ""
        self.password_frame = None
        self.password_visible = False
        self.password_fail_count = 0
        self.password_timer = None
        self.password_timer_active = False

        self.main_frame = tk.Frame(self, width=setting.DISPLAY_WIDTH, height=setting.DISPLAY_HEIGHT, background=setting.AUTH_COLOR)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.left_frame = tk.Frame(self.main_frame, width=int(setting.DISPLAY_WIDTH * 0.4), bg=setting.AUTH_COLOR)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=50)
        self.left_frame.pack_propagate(False)
    
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        img_temp = Image.open(setting.NFC_ICON_IMG_PATH)
        img_temp = img_temp.resize((140, 140))
        img_temp = ImageTk.PhotoImage(img_temp)
        self.img_temp = img_temp
        self.image_label = tk.Label(self.left_frame, image=self.img_temp, bg=setting.AUTH_COLOR, borderwidth=0, highlightthickness=0)
        self.image_label.grid(row=1, column=0, pady=0)

        right_frame = tk.Frame(self.main_frame, width=int(setting.DISPLAY_WIDTH * 0.6), bg=setting.AUTH_COLOR)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)

        content_frame = tk.Frame(right_frame, bg=setting.AUTH_COLOR, pady=30)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.content_frame = content_frame  # 위치 조정 위해 저장

        self.title = tk.Label(content_frame, text="NFC 인증", font=(setting.DEFAULT_FONT, 48, "bold"), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="NFC 태그를 인식시켜주세요", font=(setting.DEFAULT_FONT, 32), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)
        
        threading.Thread(target=self._detect_nfc, daemon=True).start()

    def _create_password_frame(self):
        if self.password_frame:
            self.password_frame.destroy()
        
        # 타이틀을 위로 이동
        self.content_frame.place_configure(rely=0.3)

        right_frame = self.main_frame.winfo_children()[1]
        self.password_frame = tk.Frame(right_frame, bg=setting.AUTH_COLOR)
        self.password_frame.place(relx=0.5, rely=0.70, anchor=tk.CENTER)
        self.password_visible = True

        self.pw_display = tk.Label(
            self.password_frame,
            text="",
            font=(setting.DEFAULT_FONT, 32),
            width=12,
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.pw_display.pack(pady=(0, 20))

        keyboard_frame = tk.Frame(self.password_frame, bg=setting.AUTH_COLOR)
        keyboard_frame.pack()

        button_style = {
            'font': (setting.DEFAULT_FONT, 32),
            'width': 2,
            'height': 1,
            'bg': '#333333',
            'fg': 'white',
            'activebackground': '#333333',
            'activeforeground': 'white',
            'borderwidth': 0
        }

        row1 = tk.Frame(keyboard_frame, bg=setting.AUTH_COLOR)
        row1.pack()
        buttons = ['1', '2', '3', '4', '5', '6']
        for text in buttons:
            btn = tk.Button(row1, text=text, **button_style, command=lambda x=text: self._on_key_press(x))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            
        row2 = tk.Frame(keyboard_frame, bg=setting.AUTH_COLOR)
        row2.pack()
        buttons = ['7', '8', '9', '0', '정정', '취소']
        for text in buttons:
            if text == '정정':
                btn = tk.Button(row2, text=text, **button_style, command=self._on_clear_press)
            elif text == '취소':
                btn = tk.Button(row2, text=text, **button_style, command=self._on_cancel_press)
            else:
                btn = tk.Button(row2, text=text, **button_style, command=lambda x=text: self._on_key_press(x))
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.password_fail_count = 0
        self._start_password_timer()

    def _start_password_timer(self):
        self._stop_password_timer()
        time.sleep(0.02)
        self.password_timer_active = True
        self.password_timer = threading.Thread(target=self._password_timer_thread, daemon=True)
        self.password_timer.start()

    def _stop_password_timer(self):
        self.password_timer_active = False

    def _password_timer_thread(self):
        start_time = time.time()
        while self.password_timer_active:
            if self.password_visible == False:
                return
            elapsed = time.time() - start_time
            if elapsed >= 10:
                self.main_frame.after(0, self._password_timeout)
                return
            time.sleep(0.01)

    def _password_timeout(self):
        self._set_title("NFC 인증 실패")
        self._set_sub_title("입력 시간이 초과되었습니다")
        log_manager.service.insert_log("NFC출입", "차단", f"PIN번호 입력시간이 초과되었습니다: UNAME={self.user_name} UID={self.nfc_uid}")
        hardware_manager.speaker_manager.play(setting.WRONG_SOUND_PATH)
        self._hide_password_frame()
        self._stop_password_timer()
        self.controller.after(3000, lambda: self.controller.show_page("MainPage"))

    def _on_key_press(self, key):
        hardware_manager.speaker_manager.play(setting.CLICK_SOUND_PATH)
        self._start_password_timer()
        if len(self.password_entry) < 4:
            self.password_entry += key
            self.pw_display.config(text="*" * len(self.password_entry))
            if len(self.password_entry) == 4:
                self._verify_password()

    def _on_clear_press(self):
        hardware_manager.speaker_manager.play(setting.CLICK_SOUND_PATH)
        self._start_password_timer()
        self.password_entry = ""
        self.pw_display.config(text="")

    def _on_cancel_press(self):
        log_manager.service.insert_log("NFC출입", "차단", f"PIN번호 입력을 취소했습니다: UNAME={self.user_name} UID={self.nfc_uid}")
        hardware_manager.speaker_manager.play(setting.CLICK_SOUND_PATH)
        self._stop_password_timer()
        self.password_entry = ""
        self.pw_display.config(text="")
        self._hide_password_frame()
        self.controller.show_page("MainPage")

    def _verify_password(self):
        if self.password_entry == self.user_password:
            self._set_title(f"{self.user_name}님 환영합니다")
            self._set_sub_title("문이 열립니다")
            self._hide_password_frame()
            self._stop_password_timer()
            log_manager.service.insert_log("NFC출입", "승인", f"문이 열렸습니다: UNAME={self.user_name} UID={self.nfc_uid}")
            hardware_manager.door.auto_open_door()
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
        else:
            self.password_fail_count += 1
            if self.password_fail_count >= 3:
                self.password_fail_count = 0
                self._set_title("NFC 인증 실패")
                self._set_sub_title("PIN번호를 확인하십시오")
                self._hide_password_frame()
                log_manager.service.insert_log("NFC출입", "차단", f"PIN번호 인증에 실패했습니다: UNAME={self.user_name} UID={self.nfc_uid}")
                hardware_manager.speaker_manager.play(setting.WRONG_SOUND_PATH)
                self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            else:
                self._set_sub_title("PIN번호가 틀렸습니다")
                hardware_manager.speaker_manager.play(setting.WRONG_SOUND_PATH)
                self.password_entry = ""
                self.pw_display.config(text="")

    def _hide_password_frame(self):
        if self.password_frame:
            self.password_frame.place_forget()
            self.password_visible = False
            self.content_frame.place_configure(rely=0.5)

    def on_show(self):
        if self.detect_nfc:
            self.detect_nfc = False
            return
        
        def nfc_auth_process():
            self.main_frame.after(0, lambda: self.main_frame.config(bg=setting.AUTH_COLOR))
            
            if hardware_manager.nfc.initialized == False:
                self._set_title("NFC 센서 오류")
                self._set_sub_title("센서를 점검하십시오")
                hardware_manager.speaker_manager.play(setting.WRONG_SOUND_PATH)
                self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
                return
            
            self._set_title("NFC 인증")
            for i in range(10, 0, -1):
                self._set_sub_title(f"카드를 인식시켜주세요 ({i}s)")
                self.nfc_uid = hardware_manager.nfc.read_nfc(timeout=1.0)
                
                if not self.nfc_uid == None:
                    self.auth_nfc()
                    return
            self.controller.after(0, lambda: self.controller.show_page("MainPage"))

        threading.Thread(target=nfc_auth_process, daemon=True).start()

    def _detect_nfc(self):
        while True:
            time.sleep(0.3)
            if self.controller.now_page != "MainPage":
                continue
            
            try:
                self.nfc_uid = hardware_manager.nfc.read_nfc()
            except:
                continue
            
            if self.nfc_uid == None:
                continue
            self.detect_nfc = True
            self.controller.show_page("PageAuthNFC")
            self.auth_nfc()

    def auth_nfc(self):
        self.main_frame.config(bg=setting.AUTH_COLOR)
        self._set_title("NFC 인증")
        
        if not auth_manager.service.get_nfc_status() == setting.STATUS_ENABLE:
            self._set_title("NFC 인증 실패")
            self._set_sub_title("현재 이용할 수 없습니다.")
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return
        
        self._set_sub_title("정보를 가져오고 있습니다")
        
        # user info logic
        result = False
        enable = True
        if self.nfc_uid == "0497e436bc2a81" or self.nfc_uid == "c996123f":
            result = True
            self.user_name = "관리자"
            self.user_password = "1234"
        if self.nfc_uid == "0491b736bc2a81":
            result = True
            self.user_name = "이건희"
            self.user_password = "5678"
        if self.nfc_uid == "af6572d7" or self.nfc_uid == "60ea625c" or self.nfc_uid == "41bbacad":
            result = True
            self.user_name = "박여웅"
            self.user_password = "2162"
        if self.nfc_uid == "a503670b":
            result = True
            self.user_name = "송명근"
            self.user_password = "0000"
            enable = False
        
        # if not enable
        if enable == False:
            self._set_title("차단된 카드")
            self._set_sub_title("이 카드는 사용이 불가능합니다")
            log_manager.service.insert_log("NFC출입", "차단", f"차단된 카드로 접근을 시도했습니다: UID={self.nfc_uid}")
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return
        
        if result:
            self._set_title("PIN번호 인증")
            self._set_sub_title("PIN번호를 입력해주세요")
            self._create_password_frame()
            self._on_clear_press()
        else:
            self._set_title("NFC 인증 실패")
            # self._set_sub_title("알 수 없는 카드입니다")
            self._set_sub_title(f"알 수 없는 카드입니다\n{self.nfc_uid}")
            self._hide_password_frame()
            log_manager.service.insert_log("NFC출입", "차단", f"알 수 없는 카드로 접근 시도했습니다: UID={self.nfc_uid}")
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
    
    def _set_title(self, text):
        self.title.config(text=text)

    def _set_sub_title(self, text):
        self.sub_title.config(text=text)
