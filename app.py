import os
from page_manager import App
import log_manager
import hardware_manager
import tkinter

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except tkinter.TclError as e:
        print("Tkinter GUI Fail:", e)
    except Exception as e:
        print("Unknown Error:", e)
    finally:
        log_manager.service.log_close()
        hardware_manager.service.hardware_close()
        os._exit(1) # 항상 재시작