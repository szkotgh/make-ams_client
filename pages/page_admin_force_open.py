import tkinter as tk
from PIL import Image, ImageTk
import config
import log_manager
import hardware_manager
import speaker_manager

class PageAdminForceOpen(tk.Frame):
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

        self.title = tk.Label(content_frame, text="문 열어두기", font=(config.DEFAULT_FONT, 48, "bold"), fg="white", bg=config.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack(pady=50)
        self.sub_button = tk.Button(content_frame, text=" 다시 눌러 해제하십시오", font=(config.DEFAULT_FONT, 32, 'bold'), fg="black", height=2, width=18, command=self.status_release)
        self.sub_button.pack()

    def status_release(self):
        log_manager.service.insert_log("관리자", "승인", "관리자가 문 열어두기를 해제했습니다.")
        hardware_manager.service.close_door()
        self.controller.show_page("MainPage")

    def on_show(self):
        log_manager.service.insert_log("관리자", "승인", "관리자가 문 열어두기를 시작했습니다.")
        hardware_manager.service.open_door()