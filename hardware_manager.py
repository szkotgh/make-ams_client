import time
import RPi.GPIO as GPIO
import threading
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import binascii
import config
import speaker_manager
import page_manager

class HardwareManager():
    def __init__(self, DOOR_RELAY_PIN=17):
        self.DOOR_RELAY_PIN = DOOR_RELAY_PIN
        
        # Initialize PN532 NFC reader
        self._init_nfc()
        
        # Initialize GPIO
        self._init_gpio()
    
    def _init_nfc(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pn532 = PN532_I2C(self.i2c, debug=False)
        self.pn532.SAM_configuration()
        
    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DOOR_RELAY_PIN, GPIO.OUT)
        self.set_door(False)
    
    def set_door(self, state: bool):
        GPIO.output(self.DOOR_RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)
        pass
    
    def open_door(self):
        speaker_manager.service.play(config.DOOR_OPEN_SOUND_PATH)
        self.set_door(True)
        
    def close_door(self, close_duration=3):
        speaker_manager.service.play(config.DOOR_CLOSE_SOUND_PATH)
        def close_door():
            self.set_door(False)
        threading.Timer(close_duration, close_door).start()
    
    def auto_open_door(self, wait_duration=3):
        self.open_door()
        threading.Timer(wait_duration, self.close_door).start()
    
    def read_nfc(self, timeout=0.5):
        uid = self.pn532.read_passive_target(timeout=timeout)
        if uid is None:
            return None
        return binascii.hexlify(uid).decode('utf-8')
    
    def hardware_close(self):
        GPIO.cleanup()
        pass

service = HardwareManager()