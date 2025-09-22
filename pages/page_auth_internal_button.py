from PIL import Image, ImageTk
import managers.auth_manager as auth_manager
import threading
import time
import tkinter as tk
import setting
from datetime import datetime, timedelta
import managers.hardware_manager as hardware_manager
import managers.log_manager as log_manager

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
        
    def page_init(self):
        hardware_manager.internal_button.led_on()
        hardware_manager.internal_button.register_callback(self._detect_button)

    def on_show(self):
        log_manager.service.insert_log("SYSTEM", "ACCESS", "내부인 출입 페이지에 접근했습니다.")
        threading.Thread(target=self.open_button, daemon=True).start()
    
    def _detect_button(self):
        if self.controller.now_page != "MainPage":
            return
        
        self.controller.show_page("PageAuthInternalButton")
            
    def open_button(self):
        self.main_frame.config(bg=setting.AUTH_COLOR)

        self._set_title("내부인 퇴실")
        self._set_sub_title("문이 열립니다")
        log_manager.service.insert_log("SYSTEM", "DOOR_OPEN", "내부에서 문을 열었습니다.")
        hardware_manager.door.open_door()

        last_button_time = datetime.now()
        led_toggle = True
        toggle_level = 0
        while True:
            if hardware_manager.internal_button.read_button():
                last_button_time = datetime.now()
                led_toggle = True
                toggle_level = 0
                hardware_manager.internal_button.led_on()
                continue
            
            if datetime.now() - last_button_time > timedelta(seconds=3):
                break
                
            if toggle_level % 10 == 9:
                led_toggle = not led_toggle
            hardware_manager.internal_button.led_on() if led_toggle else hardware_manager.internal_button.led_off()

            toggle_level += 1
            time.sleep(0.05)
        
        hardware_manager.internal_button.led_on()
        hardware_manager.door.close_door()
        self.controller.after(0, lambda: self.controller.show_page("MainPage"))
    
    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))