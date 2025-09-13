import setting
import threading
import RPi.GPIO as GPIO
import managers.hardware_manager as hardware_manager

class Door:
    def __init__(self):
        self.RELAY_PIN = setting.DOOR_RELAY
        self._door_close_cancel_flag = False
        self._door_timer = None

        GPIO.setup(self.RELAY_PIN, GPIO.OUT)
        self.set_door(False)

    def set_door(self, state: bool):
        GPIO.output(self.RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)

    def open_door(self, sound_enable=True):
        if sound_enable:
            hardware_manager.speaker.play(setting.DOOR_OPEN_SOUND_PATH)
        self.set_door(True)

    def close_door(self, close_duration=3, sound_enable=True):
        self._door_close_cancel_flag = False
        if sound_enable:
            hardware_manager.speaker.play(setting.DOOR_CLOSE_SOUND_PATH)

        def _close():
            if not self._door_close_cancel_flag:
                self.set_door(False)

        if hasattr(self, '_close_timer') and self._close_timer:
            self._close_timer.cancel()
        
        self._close_timer = threading.Timer(close_duration, _close)
        self._close_timer.start()

    def auto_open_door(self, wait_duration=3, sound_enable=True):
        if self._door_timer is not None:
            self._door_timer.cancel()
        self._door_close_cancel_flag = True
        self.open_door(sound_enable=sound_enable)
        self._door_timer = threading.Timer(wait_duration, lambda: self.close_door(sound_enable=sound_enable))
        self._door_timer.start()