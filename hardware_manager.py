# import RPi.GPIO as GPIO
import time

class HardwareManager():
    def __init__(self, RELAY_PIN=17):
        self.RELAY_PIN = RELAY_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        
    def set_door(self, state: bool):
        GPIO.output(self.RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)
        pass
    
    def open_door(self):
        self.set_door(True)
        time.sleep(0.1)
        self.set_door(False)
    
    def hardware_close(self):
        GPIO.cleanup()
        pass

service = HardwareManager()