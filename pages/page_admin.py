import os
import threading
import tkinter as tk
import config

class PasswordDialog(tk.Frame):
    def __init__(self, parent, controller, on_success):
        super().__init__(parent)
        self.controller = controller
        self.on_success = on_success
        self.input_digits = []
        self._create_widgets()

    def _create_widgets(self):
        # Title
        title_frame = tk.Frame(self)
        title_frame.pack(pady=10)
        self.title_label = tk.Label(title_frame, text="AMS 관리자", font=(config.DEFAULT_FONT, 20, "bold"), fg="black")
        self.title_label.pack()
        self.sub_title_label = tk.Label(title_frame, text="비밀번호를 입력하십시오", font=(config.DEFAULT_FONT, 12), fg="black")
        self.sub_title_label.pack()

        # Circles
        self.circles_frame = tk.Frame(self)
        self.circles_frame.pack()
        self.circles = [
            tk.Label(self.circles_frame, text="○", font=(config.DEFAULT_FONT, 22))
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
        tk.Button(self, text="초기화면으로", font=(config.DEFAULT_FONT, 14), width=12, height=2, command=self._back_to_main).pack(pady=3)

    def _create_keypad_button(self, parent, char):
        if char == 'C':
            return tk.Button(parent, text="C", font=(config.DEFAULT_FONT, 14), width=5, height=2, command=self.input_clear)
        elif char == '<':
            return tk.Button(parent, text="←", font=(config.DEFAULT_FONT, 14), width=5, height=2, command=self.backspace)
        else:
            return tk.Button(parent, text=char, font=(config.DEFAULT_FONT, 14), width=5, height=2, command=lambda ch=char: self.add_digit(ch))

    def add_digit(self, digit):
        if len(self.input_digits) < 6:
            self.input_digits.append(digit)
            self.update_circles()
            if len(self.input_digits) == 6:
                self.check_password()

    def backspace(self):
        if self.input_digits:
            self.input_digits.pop()
            self.update_circles()

    def input_clear(self):
        self.input_digits = []
        self.update_circles()

    def update_circles(self):
        for i, lbl in enumerate(self.circles):
            lbl.config(text="●" if i < len(self.input_digits) else "○")

    def check_password(self):
        if ''.join(self.input_digits) == config.ADMIN_PW:
            self.input_clear()
            self.on_success()
        else:
            self.sub_title_label.config(text="비밀번호가 일치하지 않습니다.", fg=config.DISABLE_COLOR)
            threading.Timer(1.3, lambda: self.sub_title_label.config(text="비밀번호를 입력하십시오", fg="black")).start()
            self.input_clear()

    def _back_to_main(self):
        self.input_clear()
        self.controller.show_page("MainPage")

class PageAdmin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 비밀번호 입력 창과 관리자 프레임 생성
        self._create_admin_frame()
        self.password_dialog = PasswordDialog(self, controller, self.show_admin_page)
        self.password_dialog.pack(fill="both", expand=True)

    def _create_admin_frame(self):
        self.admin_frame = tk.Frame(self)

        tk.Label(self.admin_frame, text="관리자 메뉴", font=(config.DEFAULT_FONT, 28, "bold"), fg="black").pack(pady=50)

        button_frame = tk.Frame(self.admin_frame)
        button_frame.pack()

        tk.Button(button_frame, text="시스템 재시작", font=(config.DEFAULT_FONT, 16), width=12, height=3).pack(side="left", padx=5)
        tk.Button(button_frame, text="프로그램 종료", font=(config.DEFAULT_FONT, 16), width=12, height=3, command=lambda: os._exit(os.EX_OK)).pack(side="left", padx=5)
        tk.Button(button_frame, text="프로그램 재시작", font=(config.DEFAULT_FONT, 16), width=12, height=3, command=lambda: os._exit(1)).pack(side="left", padx=5)
        tk.Button(button_frame, text="자동문 작동", font=(config.DEFAULT_FONT, 16), width=12, height=3).pack(side="left", padx=5)

        tk.Button(self.admin_frame, text="관리자 종료", font=(config.DEFAULT_FONT, 14), width=10, height=2, command=self.back_to_main).pack(pady=20)

    def show_admin_page(self):
        self.password_dialog.pack_forget()
        self.admin_frame.pack(fill="both", expand=True)

    def back_to_main(self):
        self.admin_frame.pack_forget()
        self.password_dialog.input_clear()
        self.controller.show_page("MainPage")

    def on_show(self):
        self.admin_frame.pack_forget()
        self.password_dialog.input_clear()
        self.password_dialog.pack(fill="both", expand=True)
