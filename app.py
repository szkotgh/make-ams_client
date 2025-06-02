import sys
from page_manager import App
import tkinter

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except tkinter.TclError as e:
        print("Tkinter GUI Fail:", e)
        sys.exit(1)
    except Exception:
        sys.exit(1)