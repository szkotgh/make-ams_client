import os
import time
import threading
from datetime import datetime, timedelta
import hardware_manager
import managers.log_manager as log_manager

class TimerManager:
    def __init__(self):
        self.timers = {}
        self.lock = threading.Lock()

        self.register_timer_at("00:00:00", self.reboot)

        threading.Thread(target=self._update_timers, daemon=True).start()
        print("[TimerManager] Started.")

    def register_timer_at(self, target_time_str, callback):
        now = datetime.now()
        target_time = datetime.strptime(target_time_str, "%H:%M:%S").time()
        target_datetime = datetime.combine(now.date(), target_time)

        if target_datetime <= now:
            target_datetime += timedelta(days=1)

        duration = (target_datetime - now).total_seconds()
        timer = threading.Timer(duration, self._wrap_callback, args=(callback,))
        with self.lock:
            self.timers[timer] = {
                "end_time": target_datetime,
                "callback": callback,
                "is_used": False
            }
        timer.start()

    def _wrap_callback(self, callback):
        for t, info in list(self.timers.items()):
            if info["callback"] == callback:
                info["is_used"] = True
        callback()

    def _update_timers(self):
        last_date = datetime.now().date()
        while True:
            try:
                now = datetime.now()

                # reset all is_used at midnight
                if now.date() != last_date:
                    with self.lock:
                        for info in self.timers.values():
                            info["is_used"] = False
                    last_date = now.date()

                # Optimize timer update logic - remove unnecessary iterations
                timers_to_update = []
                with self.lock:
                    for timer, info in list(self.timers.items()):
                        if now >= info["end_time"]:
                            timers_to_update.append((timer, info))

                # Process only timers that need updates
                for timer, info in timers_to_update:
                    with self.lock:
                        if timer in self.timers:
                            target_time_str = info["end_time"].strftime("%H:%M:%S")
                            callback = info["callback"]
                            del self.timers[timer]
                            self.register_timer_at(target_time_str, callback)

                # Increase polling interval from 0.5s to 5s to drastically reduce CPU usage
                time.sleep(5)
                
            except Exception as e:
                print(f"TimerManager update error: {e}")
                time.sleep(5)

    def reboot(self):
        log_manager.service.insert_log("시스템", "재부팅", "시스템을 자동으로 재부팅합니다.")
        hardware_manager.close()
        log_manager.service.log_close()
        os.system("sudo reboot now")


service = TimerManager()
