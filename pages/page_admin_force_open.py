import tkinter as tk
from PIL import Image, ImageTk
import setting
import managers.log_manager as log_manager
import managers.hardware_manager as hardware_manager

class PageAdminForceOpen(tk.Frame):
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

        self.title = tk.Label(content_frame, text="환영합니다", font=(setting.DEFAULT_FONT, 48, "bold"), fg="white", bg=setting.AUTH_COLOR, anchor="center", justify="center")
        self.title.pack(pady=50)
        
        self.sub_button = tk.Button(content_frame, text="해제", font=(setting.DEFAULT_FONT, 16, 'bold'), fg="black", height=1, width=8, command=self.status_release)
        self.sub_button.pack()

    def status_release(self):
        log_manager.service.insert_log("관리자", "승인", "문 열어두기를 해제했습니다.")
        hardware_manager.door.close_door()
        self.controller.show_page("MainPage")

    def on_show(self):
        log_manager.service.insert_log("관리자", "승인", "문 열어두기를 시작했습니다.")
        hardware_manager.door.open_door()