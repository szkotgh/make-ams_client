import os
from page_manager import App
import log_manager
import hardware_manager
import timer_manager

if __name__ == "__main__":
    log_manager.service.insert_log("시스템", "시작", "프로그램이 실행되었습니다.")
    # try:
    app = App()
    app.mainloop()
    # except Exception as e:
    #     print("Unknown Error:", e)
    #     log_manager.service.insert_log("시스템", "오류", f"{e}")
    # finally:
    #     log_manager.service.insert_log("시스템", "종료", "프로그램을 다시 실행합니다.")
    #     log_manager.service.log_close()
    #     hardware_manager.close()
    #     os._exit(1)