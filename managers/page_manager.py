import tkinter as tk
from pages.page_start import PageStart
from pages.page_main import MainPage
from pages.page_admin_login import PageAdminLogin
from pages.page_admin_main import PageAdminMain
from pages.page_admin_log import PageAdminLog
from pages.page_admin_force_open import PageAdminForceOpen
from pages.page_admin_test_qr import PageAdminTestQR
from pages.page_admin_test_nfc import PageAdminTestNFC
from pages.page_auth_external_button import PageAuthExternalButton
from pages.page_auth_internal_button import PageAuthInternalButton
from pages.page_auth_qr import PageAuthQR
from pages.page_auth_nfc import PageAuthNFC
from pages.page_remote_open import PageRemoteOpen
from pages.page_request_open_door import PageRequestOpenDoor
import setting

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(setting.TITLE)
        self.geometry(f"{setting.DISPLAY_WIDTH}x{setting.DISPLAY_HEIGHT}")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.attributes("-fullscreen", True)
        self.config(cursor="none")
        self.iconphoto(False, tk.PhotoImage(file=setting.ICON_PATH))
        def toggle_fullscreen():
            self.attributes("-fullscreen", False)
            self.after(100, lambda: self.attributes("-fullscreen", True))
        self.after(1000, toggle_fullscreen)
        
        # container frame(change zone)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.now_page = None
        self.pages = {}
        self.page_classes = {
            "PageStart": PageStart,
            "MainPage": MainPage,
            "PageAdminLogin": PageAdminLogin,
            "PageAdminMain": PageAdminMain,
            "PageAdminLog": PageAdminLog,
            "PageAdminForceOpen": PageAdminForceOpen,
            "PageAdminTestQR": PageAdminTestQR,
            "PageAdminTestNFC": PageAdminTestNFC,
            "PageAuthExternalButton": PageAuthExternalButton,
            "PageAuthInternalButton": PageAuthInternalButton,
            "PageAuthQR": PageAuthQR,
            "PageAuthNFC": PageAuthNFC,
            "PageRemoteOpen": PageRemoteOpen,
            "PageRequestOpenDoor": PageRequestOpenDoor
        }
        
        # Load start page first
        self.show_page("PageStart")

    def init_pages(self):
        for page_name, PageClass in self.page_classes.items():
            page = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")
            if hasattr(page, "page_init") and callable(getattr(page, "page_init")):
                print(f"[PageManager] Initializing page: {page_name}")
                page.page_init()
            else:
                print(f"[PageManager] No initialization method for page: {page_name}")

    def _load_page(self, page_name):
        """Lazy load pages to improve memory efficiency"""
        if page_name not in self.pages:
            PageClass = self.page_classes.get(page_name)
            if PageClass:
                page = PageClass(parent=self.container, controller=self)
                self.pages[page_name] = page
                page.grid(row=0, column=0, sticky="nsew")
                print(f"[PageManager] Page loaded: {page_name}")

    def show_page(self, page_name):
        # Load page first if not already loaded
        if page_name not in self.pages:
            self._load_page(page_name)
        
        self.now_page = page_name
        page = self.pages[page_name]
        page.tkraise()
        page.on_show()
