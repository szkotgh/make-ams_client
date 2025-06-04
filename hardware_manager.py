import RPi.GPIO as GPIO
import threading

class HardwareManager():
    def __init__(self, RELAY_PIN=17):
        self.RELAY_PIN = RELAY_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        self.set_door(False)
        
    def set_door(self, state: bool):
        GPIO.output(self.RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)
        pass
    
    def open_door(self, duration=1):
        self.set_door(True)
        def close_door():
            self.set_door(False)
        threading.Timer(duration, close_door).start()
    
    def hardware_close(self):
        GPIO.cleanup()
        pass

service = HardwareManager()