import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
import auth_manager
import setting
import hardware_manager
import log_manager

class PageAuthInternalButton(tk.Frame):
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

        self.title = tk.Label(content_frame, text="문 열기", font=(setting.DEFAULT_FONT, 48, "bold"), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="문이 열립니다.", font=(setting.DEFAULT_FONT, 32), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)
        
        hardware_manager.internal_button.led_on()
        hardware_manager.internal_button.regi_callback(self._detect_button)

    def on_show(self):
        threading.Thread(target=self.open_button, daemon=True).start()
    
    def _detect_button(self):
        if self.controller.now_page != "MainPage":
            return
        
        self.controller.show_page("PageAuthInternalButton")
            
    def open_button(self):
        self.main_frame.config(bg=setting.AUTH_COLOR)

        self._set_title("내부인 퇴실")
        self._set_sub_title("문이 열립니다")
        log_manager.service.insert_log("시스템", "문열림", "내부에서 문을 열었습니다.")
        hardware_manager.door.auto_open_door()
        
        self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
    
    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))