import os
from page_manager import App
import log_manager
import hardware_manager
import timer_manager
import tkinter

if __name__ == "__main__":
    log_manager.service.insert_log("시스템", "시작", "프로그램이 실행되었습니다.")
    try:
        app = App()
        app.mainloop()
    except tkinter.TclError as e:
        print("Tkinter GUI Fail:", e)
    except Exception as e:
        print("Unknown Error:", e)
    finally:
        log_manager.service.insert_log("시스템", "종료", "프로그램을 다시 실행합니다.")
        log_manager.service.log_close()
        hardware_manager.service.hardware_close()
        os._exit(1)