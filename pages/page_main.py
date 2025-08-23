import threading
import tkinter as tk
from PIL import Image, ImageTk
import setting
import time
import auth_manager
import log_manager
import hardware_manager
import utils

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # main frame
        main_frame = tk.Frame(self, padx=0, pady=0)
        main_frame.pack(fill="both", expand=True)

        # top frame
        top_frame = tk.Frame(main_frame, bg="#000000")
        top_frame.pack(side="top", fill="x")
        top_frame.columnconfigure(0, weight=1)
        top_frame.rowconfigure(0, weight=1)

        ## time label
        self.time_label = tk.Label(top_frame, font=(setting.DEFAULT_FONT, 18), bg="#000000", fg="#ffffff")
        self.time_label.grid(row=0, column=0, sticky="w", padx=10)
        self.time_label.bind("<Button-1>", lambda e: controller.show_page("PageAdminLogin"))
        def update_time(blink=False):
            now = time.strftime("%H:%M" if blink else "%H %M")
            self.time_label.config(text=now)
            self.time_label.after(1000, lambda: update_time(not blink))
        update_time()
        top_frame.columnconfigure(0, weight=20)
        top_frame.columnconfigure(1, weight=70)
        top_frame.columnconfigure(2, weight=5)
        top_frame.columnconfigure(3, weight=5)
        
        ## title label
        tk.Label(top_frame, text=setting.TITLE, font=(setting.DEFAULT_FONT, 14), bg="#000000", fg="#ffffff").grid(row=0, column=1, sticky="nsew")
        
        ## connection status label
        self.conn_status_label = tk.Label(top_frame, font=(setting.DEFAULT_FONT, 14), bg="#000000", fg=setting.UNKNOWN_COLOR, text="con_status")
        self.conn_status_label.grid(row=0, column=2, sticky="e")

        ## door status label
        self.door_status_label = tk.Label(top_frame, font=(setting.DEFAULT_FONT, 14), bg="#000000", fg=setting.UNKNOWN_COLOR, text="door_status")
        self.door_status_label.grid(row=0, column=3, sticky="e", padx=10)

        # left frame
        left_frame = tk.Frame(main_frame, padx=0, pady=0)
        left_frame.pack(side="left", fill="both", expand=True)

        ## GIF Update
        img = Image.open(setting.MAIN_IMAGE_PATH)
        frames = []
        for frame in range(getattr(img, "n_frames", 1)):
            img.seek(frame)
            frame_image = img.copy().resize((652, 445))
            frames.append(ImageTk.PhotoImage(frame_image))
        self.img_label = tk.Label(left_frame, padx=0, pady=0)
        self.img_label.pack(fill="both", expand=True)
        self.img_label.frames = frames
        def update_gif(ind=0):
            frame = self.img_label.frames[ind]
            self.img_label.config(image=frame)
            ind = (ind + 1) % len(self.img_label.frames)
            self.img_label.after(setting.MAIN_GIF_INTERVAL, update_gif, ind)
        update_gif()

        # right frame
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="y", anchor="e")
        right_frame.rowconfigure((0, 1, 2), weight=1)
        right_frame.columnconfigure(0, weight=1)

        ## b1
        self.button1 = tk.Button(right_frame, command=self.button_auth)
        self.button1.grid(row=0, column=0, sticky="nsew")
        ## b2
        self.button2 = tk.Button(right_frame, command=self.qr_auth)
        self.button2.grid(row=1, column=0, sticky="nsew")
        ## b3
        self.button3 = tk.Button(right_frame, command=self.nfc_auth)
        self.button3.grid(row=2, column=0, sticky="nsew")

        def update_status():
            # Update connection status label
            connection_status = auth_manager.service.get_connection_status()
            if connection_status["success"]:
                if connection_status['ping'] < 500:
                    self.conn_status_label.config(text=f"연결됨 ({connection_status['ping']}ms)", fg=setting.ENABLE_COLOR)
                elif connection_status['ping'] < 1000:
                    self.conn_status_label.config(text=f"연결됨 ({connection_status['ping']}ms)", fg=setting.WARNING_COLOR)
                else:
                    self.conn_status_label.config(text=f"연결됨 ({connection_status['ping']}ms)", fg=setting.DISABLE_COLOR)
            else:
                self.conn_status_label.config(text="통신불량", fg=setting.DISABLE_COLOR)
            self.conn_status_label.update_idletasks()

            # Update door status label
            door_status = auth_manager.service.get_door_status()
            if door_status == setting.STATUS_OPEN:
                self.door_status_label.config(text=f"{utils.get_status_korean(door_status)} 상태", fg=setting.ENABLE_COLOR)
            elif door_status == setting.STATUS_RESTRIC:
                self.door_status_label.config(text=f"{utils.get_status_korean(door_status)} 상태", fg=setting.WARNING_COLOR)
            elif door_status == setting.STATUS_CLOSE:
                self.door_status_label.config(text=f"{utils.get_status_korean(door_status)} 상태", fg=setting.DISABLE_COLOR)
            else:
                self.door_status_label.config(text="알수없음", fg=setting.UNKNOWN_COLOR)

            # Update button1
            if auth_manager.service.get_button_status() == setting.STATUS_ENABLE:
                img_btn1 = Image.open(setting.BUTTON_ENABLE_IMG_PATH)
                self.button1.config(state=tk.NORMAL)
            else:
                if auth_manager.service.open_request_enabled == setting.STATUS_ENABLE:
                    img_btn1 = Image.open(setting.BUTTON_OPEN_REQUEST_IMG_PATH)
                    self.button1.config(state=tk.NORMAL)
                else:
                    img_btn1 = Image.open(setting.BUTTON_DISABLE_IMG_PATH)
                    self.button1.config(state=tk.DISABLED)
            img_btn1 = img_btn1.resize((140, 140))
            img_btn1 = ImageTk.PhotoImage(img_btn1)
            self.img_btn1 = img_btn1
            self.button1.config(image=self.img_btn1)

            # Update button2
            if auth_manager.service.get_qr_status() == setting.STATUS_ENABLE:
                img_btn2 = Image.open(setting.QR_ENABLE_IMG_PATH)
                self.button2.config(state=tk.NORMAL)
            else:
                img_btn2 = Image.open(setting.QR_DISABLE_IMG_PATH)
                self.button2.config(state=tk.DISABLED)
            img_btn2 = img_btn2.resize((140, 140))
            img_btn2 = ImageTk.PhotoImage(img_btn2)
            self.img_btn2 = img_btn2
            self.button2.config(image=self.img_btn2)
            
            # Update button3
            if auth_manager.service.get_nfc_status() == setting.STATUS_ENABLE:
                img_btn3 = Image.open(setting.NFC_ENABLE_IMG_PATH)
                self.button3.config(state=tk.NORMAL)
            else:
                img_btn3 = Image.open(setting.NFC_DISABLE_IMG_PATH)
                self.button3.config(state=tk.DISABLED)
            img_btn3 = img_btn3.resize((140, 140))
            img_btn3 = ImageTk.PhotoImage(img_btn3)
            self.img_btn3 = img_btn3
            self.button3.config(image=self.img_btn3)

            self.conn_status_label.after(100, update_status)
        update_status()

    def button_auth(self):
        if auth_manager.service.get_button_status() == setting.STATUS_ENABLE:
            log_manager.service.insert_log("사용자", "인증", "사용자가 버튼 인증을 시도했습니다.")
            hardware_manager.speaker_manager.play(setting.CLICK_SOUND_PATH)
            self.controller.show_page("PageAuthExternalButton")
        else:
            if auth_manager.service.open_request_enabled == setting.STATUS_ENABLE:
                log_manager.service.insert_log("사용자", "인증", "사용자가 문열기 요청을 시도했습니다")
                hardware_manager.speaker_manager.play(setting.CLICK_SOUND_PATH)
                self.controller.show_page("PageRequestOpenDoor")
            else:
                pass
    
    def qr_auth(self):
        log_manager.service.insert_log("사용자", "인증", "사용자가 QR 인증을 시도했습니다.")
        hardware_manager.speaker_manager.play(setting.CLICK_SOUND_PATH)
        self.controller.show_page("PageAuthQR")
        
    def nfc_auth(self):
        log_manager.service.insert_log("사용자", "인증", "사용자가 NFC 인증을 시도했습니다.")
        hardware_manager.speaker_manager.play(setting.CLICK_SOUND_PATH)
        self.controller.show_page("PageAuthNFC")
    
    def on_show(self):
        pass