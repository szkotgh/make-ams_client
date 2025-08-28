import threading
import tkinter as tk
from PIL import Image, ImageTk
import auth_manager
import hardware_manager
import setting
import log_manager

class PageRequestOpenDoor(tk.Frame):
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

        self.title = tk.Label(content_frame, text="문 열기 요청", font=(setting.DEFAULT_FONT, 48, "bold"), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack()
        self.sub_title = tk.Label(content_frame, text="잠시만 기다려주세요.", font=(setting.DEFAULT_FONT, 32), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.sub_title.pack(pady=30)

    def on_show(self):
        threading.Thread(target=self._on_show, daemon=True).start()
            
    def _on_show(self):
        self._set_title("문 열기 요청")
        self.main_frame.config(bg=setting.AUTH_COLOR)

        self._set_sub_title("잠시만 기다려주세요.")
        self.auth_result = auth_manager.service.request_open_door()
        
        if not self.auth_result.success or self.auth_result.code != 200:
            self._set_title("문 열기 요청 실패")
            self._set_sub_title(f"{self.auth_result.message}")
            hardware_manager.safe_speaker_manager().play(setting.WRONG_SOUND_PATH)
            self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
            return
        
        self._set_title("문 열기 요청 성공")
        self._set_sub_title(f"{self.auth_result.message}")
        hardware_manager.safe_speaker_manager().play(setting.SUCCESS_SOUND_PATH)
        log_manager.service.insert_log("시스템", "문열림요청", "문 열림 요청을 전송하였습니다.")
        self.controller.after(3000, lambda: self.controller.show_page("MainPage"))
    
    def _set_title(self, text):
        self.title.after(0, lambda: self.title.config(text=text))

    def _set_sub_title(self, text):
        self.sub_title.after(0, lambda: self.sub_title.config(text=text))