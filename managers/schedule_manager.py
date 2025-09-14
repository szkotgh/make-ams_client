import subprocess
import time
import threading
import schedule
import managers.hardware_manager as hardware_manager
import managers.log_manager as log_manager

class ScheduleManager:
    def __init__(self):
        print("[ScheduleManager] Initializing...")
        
        # Register reboot task at midnight
        schedule.every().day.at("00:00:00").do(self.reboot)

        # Run scheduler loop in background thread
        threading.Thread(target=self._run_scheduler, daemon=True).start()
        print("[ScheduleManager] Initialized")

    def _run_scheduler(self):
        print("[ScheduleManager] Started")
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(f"[ScheduleManager] scheduler error: {e}")
                time.sleep(5)

    def reboot(self):
        print("[ScheduleManager] Run: reboot")
        hardware_manager.cleanup()
        log_manager.service.insert_log("SYSTEM", "REBOOT", "시스템을 자동으로 재부팅합니다.")
        log_manager.service.log_close()
        subprocess.run("sudo reboot now", shell=True)

service = ScheduleManager()