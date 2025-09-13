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
        self._load_page("PageStart")
        self.show_page("PageStart")
        
        # Pre-load all authentication pages to ensure callbacks are registered
        print("[PageManager] Pre-loading pages for callback registration...")
        # Mark preloading state so pages can avoid activating their functionality
        self.is_preloading = True
        self.page_count = len(self.page_classes.keys())
        self.page_preload_index = 0
        for index, page_name in enumerate(self.page_classes.keys()):
            print(f"[PageManager] Pre-loading: {page_name} {index+1}/{self.page_count}")
            self._load_page(page_name)
            self.page_preload_index += 1
        # Preloading finished
        self.is_preloading = False
        # Notify pages that preloading has ended so they may enable interactions if needed
        for page in self.pages.values():
            if hasattr(page, "on_preload_end") and callable(getattr(page, "on_preload_end")):
                try:
                    page.on_preload_end()
                except Exception as e:
                    print(f"[PageManager] on_preload_end error in {page.__class__.__name__}: {e}")

    def _load_page(self, page_name):
        """Lazy load pages to improve memory efficiency"""
        if page_name not in self.pages:
            PageClass = self.page_classes.get(page_name)
            if PageClass:
                page = PageClass(parent=self.container, controller=self)
                self.pages[page_name] = page
                page.grid(row=0, column=0, sticky="nsew")
                print(f"[PageManager] Page loaded: {page_name}")
                # If we are in preloading phase, allow page to disable its interactions
                if hasattr(self, "is_preloading") and self.is_preloading:
                    if hasattr(page, "on_preload") and callable(getattr(page, "on_preload")):
                        try:
                            page.on_preload()
                        except Exception as e:
                            print(f"[PageManager] on_preload error in {page_name}: {e}")

    def show_page(self, page_name):
        # Load page first if not already loaded
        if page_name not in self.pages:
            self._load_page(page_name)
        
        self.now_page = page_name
        page = self.pages[page_name]
        page.tkraise()
        page.on_show()
