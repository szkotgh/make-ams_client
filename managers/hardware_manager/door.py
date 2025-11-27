import time
import setting
import threading
import RPi.GPIO as GPIO
import managers.hardware_manager as hardware_manager

class Door:
    def __init__(self):
        self.RELAY_PIN = setting.DOOR_RELAY
        self._door_close_thread = None
        self._cancel_close_flag = threading.Event()

        GPIO.setup(self.RELAY_PIN, GPIO.OUT)
        self.set_door(False)

    def set_door(self, state: bool):
        GPIO.output(self.RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)

    def open_door(self, sound_enable=True):
        self.cancel_close_door()
        if sound_enable:
            hardware_manager.speaker.play(setting.DOOR_OPEN_SOUND_PATH)
        self.set_door(True)

    def cancel_close_door(self):
        if self._door_close_thread and self._door_close_thread.is_alive():
            self._cancel_close_flag.set()
            self._door_close_thread.join(timeout=1.0)
            self._door_close_thread = None
        self._cancel_close_flag.clear()

    def close_door(self, close_duration=3, sound_enable=True, wait_duration=0):
        self.cancel_close_door()

        def _close():
            for _ in range(int(wait_duration * 10)):
                if self._cancel_close_flag.is_set():
                    return
                time.sleep(0.1)
            
            if self._cancel_close_flag.is_set():
                return
                
            if sound_enable:
                hardware_manager.speaker.play(setting.DOOR_CLOSE_SOUND_PATH)
            
            for _ in range(int(close_duration * 10)):
                if self._cancel_close_flag.is_set():
                    return
                time.sleep(0.1)
            
            if not self._cancel_close_flag.is_set():
                self.set_door(False)
        
        self._door_close_thread = threading.Thread(target=_close, daemon=True)
        self._door_close_thread.start()

    def auto_open_door(self, wait_duration=3, sound_enable=True):
        self.cancel_close_door()
        self.open_door(sound_enable=sound_enable)
        self.close_door(wait_duration=wait_duration, sound_enable=sound_enable)