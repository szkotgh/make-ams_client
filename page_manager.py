import tkinter as tk
from pages.page_start import PageStart
from pages.page_main import MainPage
from pages.page_admin_login import PageAdminLogin
from pages.page_admin_main import PageAdminMain
from pages.page_auth_button import PageAuthButton
from pages.page_auth_qr import PageAuthQR
from pages.page_auth_nfc import PageAuthNFC
import config

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(config.TITLE)
        self.geometry(f"{config.DISPLAY_WIDTH}x{config.DISPLAY_HEIGHT}")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.attributes("-fullscreen", True)

        # container frame(change zone)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.pages = {}

        # page initialization
        for PageClass in (PageStart, MainPage, PageAdminLogin, PageAdminMain, PageAuthButton, PageAuthQR, PageAuthNFC):
            page_name = PageClass.__name__
            page = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("PageStart")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()
        page.on_show()
