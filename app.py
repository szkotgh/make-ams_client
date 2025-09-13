import os
from managers.page_manager import App
import managers.log_manager as log_manager
import managers.hardware_manager as hardware_manager

if __name__ == "__main__":
    log_manager.service.insert_log("시스템", "시작", "프로그램이 시작되었습니다.")
    try:
        # Start GUI first for better user experience
        print("[App] Starting GUI...")
        hardware_manager.status_led.blink('green')
        app = App()
        
        print("[App] GUI started successfully, running mainloop...")
        hardware_manager.status_led.on('green')
        app.mainloop()
        
    except Exception as e:
        print("[App] Unknown Error:", e)
        log_manager.service.insert_log("시스템", "오류", f"{e}")
    finally:
        hardware_manager.status_led.blink('red')
        hardware_manager.cleanup()
        log_manager.service.insert_log("시스템", "종료", "프로그램을 다시 실행합니다.")
        log_manager.service.log_close()
        os._exit(1)