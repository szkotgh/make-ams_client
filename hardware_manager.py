import time
import RPi.GPIO as GPIO
import threading
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import binascii
import auth_manager
import config
import speaker_manager
import page_manager

class HardwareManager():
    def __init__(self, DOOR_RELAY_PIN, BUTTON_PIN, BUTTON_LED_PIN):
        self.DOOR_RELAY_PIN = DOOR_RELAY_PIN
        self.BUTTON_PIN = BUTTON_PIN
        self.BUTTON_LED_PIN = BUTTON_LED_PIN
        
        self.nfc_initialized = False
        self._door_close_cancel_flag = False
        
        # Initialize PN532 NFC reader
        threading.Thread(target=self._init_nfc, daemon=True).start()
        
        # Initialize GPIO
        self._init_gpio()
        self.last_button_status = False
        threading.Thread(target=self.thread_set_button_led, daemon=True).start()
    
    def _init_nfc(self):
        last_init_time = 0
        check_interval = 10
        reinit_interval = 3600

        while True:
            now = time.time()
            need_reinit = False

            if now - last_init_time > reinit_interval or not self.nfc_initialized:
                need_reinit = True
            elif self.nfc_initialized:
                try:
                    test_uid = self.pn532.read_passive_target(timeout=0.1)
                    # test_uid는 None이어도 괜찮음. 중요한 건 에러 없이 호출되는가
                except Exception as e:
                    print(f"NFC Test Failed: {e}")
                    self.nfc_initialized = False
                    need_reinit = True

            if need_reinit:
                print("NFC Initializing...")
                try:
                    if hasattr(self, "i2c"):
                        try:
                            self.i2c.deinit()
                        except Exception:
                            pass
                    self.i2c = busio.I2C(board.SCL, board.SDA)
                    self.pn532 = PN532_I2C(self.i2c, debug=False)
                    self.pn532.SAM_configuration()
                    self.nfc_initialized = True
                    last_init_time = now
                except Exception as e:
                    print(f"NFC Initialize failed: {e}")
                    self.nfc_initialized = False

            time.sleep(check_interval)

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DOOR_RELAY_PIN, GPIO.OUT)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BUTTON_LED_PIN, GPIO.OUT)
        self.set_door(False)
    
    def thread_set_button_led(self):
        while True:
            time.sleep(0.1)
            current_status = auth_manager.service.get_button_status() == config.STATUS_ENABLE
            if current_status != self.last_button_status:
                self.set_button_led(current_status)
                self.last_button_status = current_status
    
    def set_door(self, state: bool):
        GPIO.output(self.DOOR_RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)
        pass
    
    def open_door(self):
        speaker_manager.service.play(config.DOOR_OPEN_SOUND_PATH)
        self.set_door(True)
        
    def close_door(self, close_duration=3):
        self._door_close_cancel_flag = False
        speaker_manager.service.play(config.DOOR_CLOSE_SOUND_PATH)
        def close_door_inner():
            if not self._door_close_cancel_flag:
                self.set_door(False)
        threading.Timer(close_duration, close_door_inner).start()
    
    def auto_open_door(self, wait_duration=3):
        if hasattr(self, '_door_timer') and self._door_timer is not None:
            self._door_timer.cancel()
        self._door_close_cancel_flag = True
        self.open_door()
        self._door_timer = threading.Timer(wait_duration, self.close_door)
        self._door_timer.start()
    
    def read_nfc(self, timeout=0.5):
        if self.nfc_initialized is False:
            return None
        
        uid = self.pn532.read_passive_target(timeout=timeout)
        if uid is None:
            return None
        return binascii.hexlify(uid).decode('utf-8')

    def read_button(self):
        return GPIO.input(self.BUTTON_PIN) == GPIO.LOW
    
    def set_button_led(self, state: bool):
        GPIO.output(self.BUTTON_LED_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    def hardware_close(self):
        GPIO.cleanup()
        pass

service = HardwareManager(DOOR_RELAY_PIN=23, BUTTON_PIN=24, BUTTON_LED_PIN=25)