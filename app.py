import os
import managers.log_manager as log_manager
import managers.schedule_manager as schedule_manager

if __name__ == "__main__":
    exit_code = 0
    log_manager.service.insert_log("SYSTEM", "START", "프로그램이 시작되었습니다.")
    
    # try:
    #     from managers.page_manager import App
    #     print("[App] Starting GUI...")
    #     app = App()
        
    #     print("[App] GUI started successfully, running mainloop...")
    #     app.mainloop()
        
    # except Exception as e:
    #     print("[App] Unknown Error:", e)
    #     log_manager.service.insert_log("SYSTEM", "ERROR", f"프로그램 실행 중 오류가 발생했습니다: {e}")
    #     exit_code = 1
    # finally:
    #     log_manager.service.insert_log("SYSTEM", "STOP", "프로그램이 종료되었습니다.")
    #     log_manager.service.log_close()
    #     import managers.hardware_manager as hardware_manager
    #     hardware_manager.cleanup()
    #     os._exit(exit_code)
        
    # for debug
    from managers.page_manager import App
    print("[App] Starting GUI...")
    app = App()
    
    print("[App] GUI started successfully, running mainloop...")
    app.mainloop()