import time
import RPi.GPIO as GPIO
import threading

import config
import speaker_manager

class HardwareManager():
    def __init__(self, RELAY_PIN=17):
        self.RELAY_PIN = RELAY_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        self.set_door(False)
        
    def set_door(self, state: bool):
        GPIO.output(self.RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)
        pass
    
    def open_door(self, wait_duration=1, close_duration=3):
        speaker_manager.service.play(config.DOOR_OPEN_SOUND_PATH)
        self.set_door(True)
        def close_door():
            speaker_manager.service.play(config.DOOR_CLOSE_SOUND_PATH)
            time.sleep(close_duration)
            self.set_door(False)
        threading.Timer(wait_duration, close_door).start()
    
    def hardware_close(self):
        GPIO.cleanup()
        pass

service = HardwareManager()