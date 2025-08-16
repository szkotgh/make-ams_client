import os
import time
import threading
from datetime import datetime, timedelta
import hardware_manager
import log_manager

class TimerManager:
    def __init__(self):
        self.timers = {}
        
        def _update_timers():
            while True:
                now = datetime.now()
                for timer, end_time in list(self.timers.items()):
                    if now >= end_time:
                        timer.cancel()
                        del self.timers[timer]
                time.sleep(1)

        # register timer
        self.register_timer_at("00:00:00", self.reboot)
        
        threading.Thread(target=_update_timers, daemon=True).start()

    def register_timer_at(self, target_time_str, callback):
        now = datetime.now()
        target_time = datetime.strptime(target_time_str, "%H:%M:%S").time()
        target_datetime = datetime.combine(now.date(), target_time)

        if target_datetime <= now:
            target_datetime += timedelta(days=1)

        duration = (target_datetime - now).total_seconds()
        timer = threading.Timer(duration, callback)
        self.timers[timer] = target_datetime
        timer.start()

    def reboot(self):
        log_manager.service.insert_log("시스템", "재부팅", "시스템을 자동으로 재부팅합니다.")
        hardware_manager.service.hardware_close()
        log_manager.service.log_close()
        os.system("sudo reboot now")
        
service = TimerManager()