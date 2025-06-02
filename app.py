import sys
from page_manager import App

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception:
        sys.exit(0)
