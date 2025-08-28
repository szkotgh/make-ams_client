import os
import threading
import time
from page_manager import App
import log_manager
import hardware_manager
import timer_manager

def initialize_hardware_after_gui():
    """Initialize hardware after GUI is fully loaded - CPU priority adjustment"""
    time.sleep(2)
    try:
        # Initialize hardware manager in background
        print("Initializing hardware manager...")
        # Hardware initialization already runs at import time, so only perform additional tasks
        print("Hardware manager initialization completed")
    except Exception as e:
        print(f"Hardware initialization error: {e}")

if __name__ == "__main__":
    log_manager.service.insert_log("시스템", "시작", "프로그램이 실행되었습니다.")
    try:
        # Start GUI first for better user experience
        print("Starting GUI...")
        app = App()
        
        # Initialize hardware in separate thread with delay
        hardware_thread = threading.Thread(
            target=initialize_hardware_after_gui, 
            daemon=True,
            name="HardwareInit"
        )
        hardware_thread.start()
        
        print("GUI started successfully, running mainloop...")
        app.mainloop()
        
    except Exception as e:
        print("Unknown Error:", e)
        log_manager.service.insert_log("시스템", "오류", f"{e}")
    finally:
        log_manager.service.insert_log("시스템", "종료", "프로그램을 다시 실행합니다.")
        log_manager.service.log_close()
        hardware_manager.close()
        os._exit(1)