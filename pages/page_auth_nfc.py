import threading
import time
import tkinter as tk
import managers.auth_manager as auth_manager
import setting
from PIL import Image, ImageTk
import hardware_manager
import managers.log_manager as log_manager

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
        self.content_frame = content_frame

        self.title = tk.Label(content_frame, text="NFC 인증", font=(setting.DEFAULT_FONT, 48, "bold"), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="NFC 태그를 인식시켜주세요", font=(setting.DEFAULT_FONT, 32), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)
        
        # Register callback for automatic re-registration after hardware init
        hardware_manager.register_callback('nfc', self._nfc_callback)

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
        log_manager.service.insert_log("NFC출입", "차단", f"PIN번호 입력시간이 초과되었습니다: NFC_UID={self.nfc_uid}")
        hardware_manager.safe_speaker_manager().play(setting.WRONG_SOUND_PATH)
        self._hide_password_frame()
        self._stop_password_timer()
        self.controller.after(3000, lambda: self.controller.show_page("MainPage"))

    def _on_key_press(self, key):
        hardware_manager.safe_speaker_manager().play(setting.CLICK_SOUND_PATH)
        self._start_password_timer()
        if len(self.password_entry) < 4:
            self.password_entry += key
            self.pw_display.config(text="*" * len(self.password_entry))
            if len(self.password_entry) == 4:
                self._verify_password()

    def _on_clear_press(self):
        hardware_manager.safe_speaker_manager().play(setting.CLICK_SOUND_PATH)
        self._start_password_timer()
        self.password_entry = ""
        self.pw_display.config(text="")

    def _on_cancel_press(self):
        log_manager.service.insert_log("NFC출입", "차단", f"PIN번호 입력을 취소했습니다: UNAME={self.user_name} UID={self.nfc_uid}")
        hardware_manager.safe_speaker_manager().play(setting.CLICK_SOUND_PATH)
        self._stop_password_timer()
        self.password_entry = ""
        self.pw_display.config(text="")
        self._hide_password_frame()
        self.controller.show_page("MainPage")

    def _verify_password(self):
        if self.password_entry == self.user_nfc_pin:
            self._open_door()
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
        else:
            self.password_fail_count += 1
            if self.password_fail_count >= 3:
                self.password_fail_count = 0
                self._set_title("NFC 인증 실패")
                self._set_sub_title("PIN번호를 확인하십시오")
                self._hide_password_frame()
                log_manager.service.insert_log("NFC출입", "차단", f"PIN번호 인증에 실패했습니다: UNAME={self.user_name} UID={self.nfc_uid}")
                hardware_manager.safe_speaker_manager().play(setting.WRONG_SOUND_PATH)
                self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            else:
                self._set_sub_title("PIN번호가 틀렸습니다")
                hardware_manager.safe_speaker_manager().play(setting.WRONG_SOUND_PATH)
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
            
            if hardware_manager.safe_nfc().initialized == False:
                self._set_title("NFC 센서 오류")
                self._set_sub_title("센서를 점검하십시오")
                hardware_manager.safe_speaker_manager().play(setting.WRONG_SOUND_PATH)
                self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
                return
            
            self._set_title("NFC 인증")
            for i in range(10, 0, -1):
                self._set_sub_title(f"카드를 인식시켜주세요 ({i}s)")
                self.nfc_uid = hardware_manager.safe_nfc().read_nfc(timeout=1.0)
                
                if not self.nfc_uid == None:
                    self.auth_nfc()
                    return
            self.controller.after(0, lambda: self.controller.show_page("MainPage"))

        threading.Thread(target=nfc_auth_process, daemon=True).start()

    def _nfc_callback(self, nfc_uid: str):
        if self.controller.now_page != "MainPage" or self.detect_nfc:
            print(f"NFC callback ignored - current page: {self.controller.now_page}, auth running: {self.detect_nfc}")
            return
        
        self.detect_nfc = True
        self.nfc_uid = nfc_uid
        self.controller.show_page("PageAuthNFC")
        self.auth_nfc()

    def auth_nfc(self):
        self.main_frame.config(bg=setting.AUTH_COLOR)
        self._set_title("NFC 인증")

        # auth logic
        self._set_sub_title("정보를 가져오고 있습니다")
        self.auth_result = auth_manager.service.request_nfc_auth(self.nfc_uid)
        
        if not self.auth_result.success or self.auth_result.code != 200:
            self._set_title("NFC 인증 실패")
            self._set_sub_title(self.auth_result.message)
            self._hide_password_frame()
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return
        
        self.user_name = self.auth_result.data.get("user_name", None)
        self.user_nfc_pin = self.auth_result.data.get("user_nfc_pin", None)

        if self.user_nfc_pin:
            self._set_title("PIN번호 인증")
            self._set_sub_title("PIN번호를 입력해주세요")
            self._create_password_frame()
            self._on_clear_press()
        else:
            self._open_door()
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
    
    def _open_door(self):
        self._hide_password_frame()
        self._stop_password_timer()
        self._set_title("NFC 인증 성공")
        self._set_sub_title(f"{self.auth_result.message}")
        log_manager.service.insert_log("NFC출입", "승인", f"문이 열렸습니다: NFC_UID={self.nfc_uid}")
        hardware_manager.safe_door().auto_open_door()
    
    def _set_title(self, text):
        self.title.config(text=text)

    def _set_sub_title(self, text):
        self.sub_title.config(text=text)
