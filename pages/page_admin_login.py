import os
import threading
import time
import tkinter as tk
import setting
import log_manager
import hardware_manager

class PageAdminLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.input_digits = []
        self.error_count = 0
        self.inactivity_timer_active = False
        self.inactivity_thread = None

        # Title
        title_frame = tk.Frame(self)
        title_frame.pack(pady=10)
        self.title_label = tk.Label(title_frame, text="AMS 관리자", font=(setting.DEFAULT_FONT, 20, "bold"), fg="black")
        self.title_label.pack()
        self.sub_title_label = tk.Label(title_frame, text="", font=(setting.DEFAULT_FONT, 12), fg="black")
        self.sub_title_label.pack()

        # Circles
        self.circles_frame = tk.Frame(self)
        self.circles_frame.pack()
        self.circles = [
            tk.Label(self.circles_frame, text="○", font=(setting.DEFAULT_FONT, 22))
            for _ in range(6)
        ]
        for lbl in self.circles:
            lbl.pack(side="left", padx=5)

        # Keypad
        keypad_frame = tk.Frame(self)
        keypad_frame.pack(pady=3)
        btn_texts = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['C', '0', '<']
        ]
        for row in btn_texts:
            row_frame = tk.Frame(keypad_frame)
            row_frame.pack()
            for char in row:
                btn = self._create_keypad_button(row_frame, char)
                btn.pack(side="left", padx=3, pady=3)

        # Back button
        def cancel_login():
            self.stop_inactivity_timer()
            self.controller.show_page("MainPage")
        tk.Button(self, text="로그인 취소", font=(setting.DEFAULT_FONT, 14), width=12, height=2,
                  command=cancel_login).pack(pady=3)

    def start_inactivity_timer(self):
        self.inactivity_timer_active = True
        self.last_input_time = time.time()
        self.inactivity_thread = threading.Thread(target=self._inactivity_watchdog, daemon=True)
        self.inactivity_thread.start()

    def stop_inactivity_timer(self):
        self.inactivity_timer_active = False

    def _reset_inactivity_timer(self):
        self.last_input_time = time.time()

    def _inactivity_watchdog(self):
        while self.inactivity_timer_active:
            if time.time() - self.last_input_time > 10:
                self.stop_inactivity_timer()
                hardware_manager.safe_speaker_manager().play(setting.WRONG_SOUND_PATH)
                self.controller.after(0, lambda: self.controller.show_page("MainPage"))
                return
            time.sleep(0.2)

    def _create_keypad_button(self, parent, char):
        def on_click(action=None):
            hardware_manager.safe_speaker_manager().play(setting.CLICK_SOUND_PATH)
            if action:
                action()
        if char == 'C':
            return tk.Button(parent, text="C", font=(setting.DEFAULT_FONT, 14, 'bold'), width=5, height=2,
                             command=lambda: on_click(self.input_clear))
        elif char == '<':
            return tk.Button(parent, text="←", font=(setting.DEFAULT_FONT, 14, 'bold'), width=5, height=2,
                             command=lambda: on_click(self.backspace))
        else:
            return tk.Button(parent, text=char, font=(setting.DEFAULT_FONT, 14, 'bold'), width=5, height=2,
                             command=lambda ch=char: on_click(lambda: self.add_digit(ch)))

    def add_digit(self, digit):
        self._reset_inactivity_timer()

        if len(self.input_digits) < 6:
            self.input_digits.append(digit)
            self.update_circles()
            if len(self.input_digits) == 6:
                self.check_password()

    def backspace(self):
        self._reset_inactivity_timer()

        if self.input_digits:
            self.input_digits.pop()
            self.update_circles()

    def input_clear(self):
        self._reset_inactivity_timer()

        self.input_digits = []
        self.update_circles()

    def update_circles(self):
        for i, lbl in enumerate(self.circles):
            lbl.config(text="●" if i < len(self.input_digits) else "○")

    def check_password(self):
        if ''.join(self.input_digits) == setting.ADMIN_PW:
            hardware_manager.safe_speaker_manager().play(setting.SUCCESS_SOUND_PATH)
            self.input_clear()
            self.stop_inactivity_timer()
            log_manager.service.insert_log("관리자", "로그인", "관리자페이지에 로그인했습니다.")
            self.controller.show_page("PageAdminMain")
        else:
            self.error_count += 1
            if self.error_count == 3:
                hardware_manager.safe_speaker_manager().play(setting.DTMG)
            elif self.error_count == 6:
                hardware_manager.safe_speaker_manager().play(setting.JTMG)
            else:
                hardware_manager.safe_speaker_manager().play(setting.WRONG_SOUND_PATH)
            self.sub_title_label.config(text="비밀번호가 일치하지 않습니다", fg=setting.DISABLE_COLOR)
            threading.Timer(1.5, self._reset_subtitle).start()
            self.input_clear()

    def _reset_subtitle(self):
        self.sub_title_label.config(text="비밀번호를 입력하십시오", fg="black")

    def on_show(self):
        self.error_count = 0
        self.input_clear()
        self._reset_subtitle()
        self.start_inactivity_timer()
        
