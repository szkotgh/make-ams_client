import os
import time
import RPi.GPIO as GPIO
import threading
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import binascii
import auth_manager
import config
import speaker_manager
import evdev

class QRListener:
    def __init__(self):
        self._lock = threading.Lock()
        self._active = False
        self._buffer = ""
        self._result = None
        self._device = None
        self.listener_thread = None

    def _handle_char(self, char):
        with self._lock:
            if char == '{':
                self._active = True
                self._buffer = ""
            elif self._active:
                if char == '}':
                    self._active = False
                    self._result = self._buffer
                    self._buffer = ""
                else:
                    self._buffer += char

    def get_qr_detect_result(self):
        if self._result is not None:
            result = self._result
            self._result = None
            return result
        return self._result

    def _find_input_device(self):
        for device in [evdev.InputDevice(path) for path in evdev.list_devices()]:
            if 'keyboard' in device.name.lower() or device.capabilities().get(evdev.ecodes.EV_KEY):
                return device
        return None

    def _listen(self):
        print("QR Listener Initializing...")
        try:
            self._device = self._find_input_device()
            if not self._device:
                print("No keyboard device found for QR Listener.")
                os._exit(1)
            print("QR Listener Initialized Successfully")
            keymap = {
                evdev.ecodes.KEY_1: '1', evdev.ecodes.KEY_2: '2', evdev.ecodes.KEY_3: '3',
                evdev.ecodes.KEY_4: '4', evdev.ecodes.KEY_5: '5', evdev.ecodes.KEY_6: '6',
                evdev.ecodes.KEY_7: '7', evdev.ecodes.KEY_8: '8', evdev.ecodes.KEY_9: '9',
                evdev.ecodes.KEY_0: '0',
                evdev.ecodes.KEY_A: 'a', evdev.ecodes.KEY_B: 'b', evdev.ecodes.KEY_C: 'c',
                evdev.ecodes.KEY_D: 'd', evdev.ecodes.KEY_E: 'e', evdev.ecodes.KEY_F: 'f',
                evdev.ecodes.KEY_G: 'g', evdev.ecodes.KEY_H: 'h', evdev.ecodes.KEY_I: 'i',
                evdev.ecodes.KEY_J: 'j', evdev.ecodes.KEY_K: 'k', evdev.ecodes.KEY_L: 'l',
                evdev.ecodes.KEY_M: 'm', evdev.ecodes.KEY_N: 'n', evdev.ecodes.KEY_O: 'o',
                evdev.ecodes.KEY_P: 'p', evdev.ecodes.KEY_Q: 'q', evdev.ecodes.KEY_R: 'r',
                evdev.ecodes.KEY_S: 's', evdev.ecodes.KEY_T: 't', evdev.ecodes.KEY_U: 'u',
                evdev.ecodes.KEY_V: 'v', evdev.ecodes.KEY_W: 'w', evdev.ecodes.KEY_X: 'x',
                evdev.ecodes.KEY_Y: 'y', evdev.ecodes.KEY_Z: 'z',
                evdev.ecodes.KEY_LEFTBRACE: '{', evdev.ecodes.KEY_RIGHTBRACE: '}',
                evdev.ecodes.KEY_MINUS: '-', evdev.ecodes.KEY_EQUAL: '=',
                evdev.ecodes.KEY_SEMICOLON: ';', evdev.ecodes.KEY_APOSTROPHE: '\'',
                evdev.ecodes.KEY_GRAVE: '`', evdev.ecodes.KEY_BACKSLASH: '\\',
                evdev.ecodes.KEY_COMMA: ',', evdev.ecodes.KEY_DOT: '.', evdev.ecodes.KEY_SLASH: '/',
                evdev.ecodes.KEY_SPACE: ' ',
            }
            shift_map = {
                evdev.ecodes.KEY_1: '!', evdev.ecodes.KEY_2: '@', evdev.ecodes.KEY_3: '#',
                evdev.ecodes.KEY_4: '$', evdev.ecodes.KEY_5: '%', evdev.ecodes.KEY_6: '^',
                evdev.ecodes.KEY_7: '&', evdev.ecodes.KEY_8: '*', evdev.ecodes.KEY_9: '(',
                evdev.ecodes.KEY_0: ')',
                evdev.ecodes.KEY_MINUS: '_', evdev.ecodes.KEY_EQUAL: '+',
                evdev.ecodes.KEY_LEFTBRACE: '{', evdev.ecodes.KEY_RIGHTBRACE: '}',
                evdev.ecodes.KEY_BACKSLASH: '|', evdev.ecodes.KEY_SEMICOLON: ':',
                evdev.ecodes.KEY_APOSTROPHE: '"', evdev.ecodes.KEY_GRAVE: '~',
                evdev.ecodes.KEY_COMMA: '<', evdev.ecodes.KEY_DOT: '>', evdev.ecodes.KEY_SLASH: '?',
            }
            shift = False
            for event in self._device.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    if key_event.keystate == evdev.KeyEvent.key_down:
                        if key_event.scancode in (evdev.ecodes.KEY_LEFTSHIFT, evdev.ecodes.KEY_RIGHTSHIFT):
                            shift = True
                        else:
                            char = ''
                            if shift and key_event.scancode in shift_map:
                                char = shift_map[key_event.scancode]
                            elif key_event.scancode in keymap:
                                char = keymap[key_event.scancode]
                            if char:
                                self._handle_char(char)
                    elif key_event.keystate == evdev.KeyEvent.key_up:
                        if key_event.scancode in (evdev.ecodes.KEY_LEFTSHIFT, evdev.ecodes.KEY_RIGHTSHIFT):
                            shift = False
        except Exception as e:
            print(f"QR Listener Initializing failed: {e}")
            os._exit(1)

    def start(self):
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()

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
                    # 에러 없이 호출되는가 검사
                    self.pn532.read_passive_target(timeout=0.1)
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
                    print("NFC Initialized Successfully")
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