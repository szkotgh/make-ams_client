import threading
import time
import tkinter as tk
from PIL import Image, ImageTk

import auth_manager
import config
import hardware_manager

class PageAuthButton(tk.Frame):
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

        img_temp = Image.open(config.DOOR_ICON_IMG_PATH)
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

        self.title = tk.Label(content_frame, text="외부인 출입", font=(config.DEFAULT_FONT, 48, "bold"), fg="white", bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="잠시만 기다려주세요", font=(config.DEFAULT_FONT, 32), fg="white", bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)
        
        threading.Thread(target=self._detect_button, daemon=True).start()

    def on_show(self):
        threading.Thread(target=self.button_auth, daemon=True).start()
    
    def _detect_button(self):
        while True:
            time.sleep(0.05)
            
            if self.controller.now_page != "MainPage":
                continue
            
            if hardware_manager.service.read_button():
                self.controller.show_page("PageAuthButton")
                time.sleep(1)
            
    def button_auth(self):
        self.main_frame.config(bg=config.AUTH_COLOR)

        # Check button enabled
        if not auth_manager.service.get_button_status() == config.STATUS_ENABLE:
            self._set_title("외부인 출입 불가")
            self._set_sub_title("비활성화되어 있습니다")
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return

        # Button init
        self._set_title("외부인 출입")
        self._set_sub_title("잠시만 기다려주십시오")
        time.sleep(1)

        # Auth Request
        # ## Button 
        # else:
        #     if auth_manager.service.request_button_auth():
        #         self._set_title("환영합니다")
        #         self._set_sub_title("메이크에 오신 것을 환영합니다")
        #         hardware_manager.service.auto_open_door()
        #     else:
        #         self._set_title("외부인 출입 불가")
        #         self._set_sub_title(f"출입이 거부되었습니다")
        self._set_title("환영합니다")
        self._set_sub_title("메이크에 오신 것을 환영합니다")
        hardware_manager.service.auto_open_door()
        
        self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
    
    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))