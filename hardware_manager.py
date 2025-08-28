import os
import time
import RPi.GPIO as GPIO
import threading
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import binascii
import setting
import evdev
import pygame

GPIO.cleanup()
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

class SpeakerManager:
    def __init__(self):
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512,
            allowedchanges=pygame.AUDIO_ALLOW_FREQUENCY_CHANGE
        )
        self._lock = threading.Lock()
        self._volume = 1.0

    def set_volume(self, volume):
        with self._lock:
            self._volume = max(0.0, min(1.0, volume))
            try:
                pygame.mixer.music.set_volume(self._volume)
            except Exception as e:
                print(f"Error setting volume: {e}")

    def play(self, file_path):
        def _play():
            with self._lock:
                try:
                    if not os.path.exists(file_path):
                        print(f"Audio file not found: {file_path}")
                        return
                    pygame.mixer.music.stop()
                    time.sleep(0.05)
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.set_volume(self._volume)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"Error playing sound: {e}")

        # 스레드 생성 최적화 - 기존 스레드가 실행 중이면 재사용
        if not hasattr(self, '_play_thread') or not self._play_thread.is_alive():
            self._play_thread = threading.Thread(target=_play, daemon=True)
            self._play_thread.start()
        else:
            # 기존 스레드가 실행 중이면 직접 실행
            _play()

    def stop(self):
        with self._lock:
            try:
                pygame.mixer.music.stop()
            except Exception as e:
                print(f"Error stopping sound: {e}")

class StatusLED:
    def __init__(self):
        self.LED_RED = setting.STATUS_LED_RED
        self.LED_YELLOW = setting.STATUS_LED_YELLOW
        self.LED_GREEN = setting.STATUS_LED_GREEN

        GPIO.setup(self.LED_RED, GPIO.OUT)
        GPIO.setup(self.LED_YELLOW, GPIO.OUT)
        GPIO.setup(self.LED_GREEN, GPIO.OUT)

        self._states = {
            "red": {"thread": None, "stop_event": threading.Event()},
            "yellow": {"thread": None, "stop_event": threading.Event()},
            "green": {"thread": None, "stop_event": threading.Event()},
        }

    def _set_led(self, color, state: bool):
        pin = getattr(self, f"LED_{color.upper()}")
        GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

    def _stop(self, color: str):
        state = self._states[color]
        if state["thread"] and state["thread"].is_alive():
            state["stop_event"].set()
            state["thread"].join()
        state["thread"] = None
        state["stop_event"] = threading.Event()

    def on(self, color: str):
        self._stop(color)
        self._set_led(color, True)

    def off(self, color: str):
        self._stop(color)
        self._set_led(color, False)

    def blink(self, color: str):
        self._stop(color)
        stop_event = threading.Event()
        self._states[color]["stop_event"] = stop_event

        def _blink():
            state = False
            while not stop_event.is_set():
                state = not state
                self._set_led(color, state)
                time.sleep(0.5)
            self._set_led(color, False)

        t = threading.Thread(target=_blink, daemon=True)
        self._states[color]["thread"] = t
        t.start()

    def cleanup(self):
        for c in ["red", "yellow", "green"]:
            self.off(c)
        GPIO.cleanup()

class ExternalButtonSwitch():
    def __init__(self):
        self.BTN_PIN = setting.EXTERNAL_SW_BTN
        self.LED_PIN = setting.EXTERNAL_SW_LED
        
        GPIO.setup(self.BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

    def led_on(self):
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        
    def led_off(self):
        GPIO.output(self.LED_PIN, GPIO.LOW)

    def read_button(self):
        return GPIO.input(self.BTN_PIN) == GPIO.LOW

    def regi_callback(self, callback):
        def run_callback(ch):
            # Increase debouncing time to reduce CPU usage
            if GPIO.input(self.BTN_PIN) == GPIO.LOW: 
                callback()

        GPIO.add_event_detect(
            self.BTN_PIN,
            GPIO.FALLING,
            callback=run_callback,
            bouncetime=100  # Increased from 50ms to 100ms to reduce CPU usage
        )

class InternalButtonSwitch():
    def __init__(self):
        self.BTN_PIN = setting.INTERNAL_SW_BTN
        self.LED_PIN = setting.INTERNAL_SW_LED
        
        GPIO.setup(self.BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

    def led_on(self):
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        
    def led_off(self):
        GPIO.output(self.LED_PIN, GPIO.LOW)

    def read_button(self):
        return GPIO.input(self.BTN_PIN) == GPIO.LOW

    def regi_callback(self, callback):
        def run_callback(ch):
            # Increase debouncing time to reduce CPU usage
            if GPIO.input(self.BTN_PIN) == GPIO.LOW: 
                callback()

        GPIO.add_event_detect(
            self.BTN_PIN,
            GPIO.FALLING,
            callback=run_callback,
            bouncetime=100  # Increased from 50ms to 100ms to reduce CPU usage
        )

class DoorRelay:
    def __init__(self):
        self.RELAY_PIN = setting.DOOR_RELAY
        self._door_close_cancel_flag = False
        self._door_timer = None

        GPIO.setup(self.RELAY_PIN, GPIO.OUT)
        self.set_door(False)

    def set_door(self, state: bool):
        GPIO.output(self.RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)

    def open_door(self):
        speaker_manager.play(setting.DOOR_OPEN_SOUND_PATH)
        self.set_door(True)

    def close_door(self, close_duration=3):
        self._door_close_cancel_flag = False
        speaker_manager.play(setting.DOOR_CLOSE_SOUND_PATH)

        def _close():
            if not self._door_close_cancel_flag:
                self.set_door(False)

        # 기존 타이머가 있으면 취소
        if hasattr(self, '_close_timer') and self._close_timer:
            self._close_timer.cancel()
        
        self._close_timer = threading.Timer(close_duration, _close)
        self._close_timer.start()

    def auto_open_door(self, wait_duration=3):
        if self._door_timer is not None:
            self._door_timer.cancel()
        self._door_close_cancel_flag = True
        self.open_door()
        self._door_timer = threading.Timer(wait_duration, lambda: self.close_door())
        self._door_timer.start()

class NFCReader:
    def __init__(self):
        self.initialized = False
        self._stop_event = threading.Event()
        self._init_thread = threading.Thread(target=self._init_nfc, daemon=True)
        self._init_thread.start()

    def cleanup(self):
        """Clean up resources and terminate threads"""
        self._stop_event.set()
        if self._init_thread.is_alive():
            self._init_thread.join(timeout=5)
        if hasattr(self, "i2c"):
            try:
                self.i2c.deinit()
            except Exception:
                pass

    def _init_nfc(self):
        # Lower thread priority to improve GUI performance
        import os
        try:
            os.nice(10)  # Set low priority
        except:
            pass
            
        last_init_time = 0
        check_interval = 30  # Increased from 10s to 30s to reduce CPU usage
        reinit_interval = 3600
        consecutive_errors = 0
        max_errors = 3

        while not self._stop_event.is_set():
            try:
                now = time.time()
                need_reinit = False

                # Increase hardware status check interval to reduce CPU usage
                if not self.initialized or now - last_init_time > reinit_interval:
                    need_reinit = True
                elif self.initialized and consecutive_errors < max_errors:
                    try:
                        # Reduce timeout from 0.1s to 0.05s to improve responsiveness
                        self.pn532.read_passive_target(timeout=0.05)
                        consecutive_errors = 0  # Reset error counter on success
                    except Exception:
                        consecutive_errors += 1
                        if consecutive_errors >= max_errors:
                            need_reinit = True

                if need_reinit:
                    try:
                        if hasattr(self, "i2c"):
                            try:
                                self.i2c.deinit()
                            except Exception:
                                pass
                        self.i2c = busio.I2C(board.SCL, board.SDA)
                        self.pn532 = PN532_I2C(self.i2c, debug=False)
                        self.pn532.SAM_configuration()
                        self.initialized = True
                        last_init_time = now
                        consecutive_errors = 0
                        import auth_manager, setting
                        auth_manager.service.nfc_status_hw = setting.STATUS_ENABLE
                    except Exception as e:
                        self.initialized = False
                        consecutive_errors += 1
                        import auth_manager, setting
                        auth_manager.service.nfc_status_hw = setting.STATUS_DISABLE

                # Wait longer when there are many errors
                if consecutive_errors > 0:
                    time.sleep(check_interval * 2)
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                # Log and continue on exception
                print(f"NFC initialization error: {e}")
                time.sleep(check_interval)

    def read_nfc(self, timeout=0.5):
        if not self.initialized:
            return False

        uid = self.pn532.read_passive_target(timeout=timeout)
        if uid is None:
            return None
        return binascii.hexlify(uid).decode("utf-8")

class QRListener:
    def __init__(self):
        self._lock = threading.Lock()
        self._active = False
        self._buffer = ""
        self._result = None
        self._device = None
        self.listener_thread = None
        self._stop_event = threading.Event()
        self.qr_listener_name = "USBKey Chip USBKey Module"
        self.callback_list = []
        
        self.start()

    def cleanup(self):
        """Clean up resources and terminate threads"""
        self._stop_event.set()
        if self._device:
            try:
                self._device.close()
            except Exception:
                pass
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=5)

    def regi_callback(self, callback):
        self.callback_list.append(callback)

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
                    # Execute callbacks
                    for callback in self.callback_list:
                        callback(self._result)
                else:
                    self._buffer += char

    def get_qr_detect_result(self):
        if self._result is not None:
            result = self._result
            self._result = None
            return result
        return self._result

    def _find_input_device(self):
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            if device.name == self.qr_listener_name:
                return device
        return None

    def _listen(self):
        # Lower thread priority to improve GUI performance
        import os
        try:
            os.nice(10)  # Set low priority
        except:
            pass
            
        print("QR Listener Initializing...")
        retry_count = 0
        max_retries = 5
        base_delay = 5  # Increased from 1s to 5s to reduce CPU usage
        
        while not self._stop_event.is_set():
            try:
                self._device = self._find_input_device()
                if not self._device:
                    retry_count += 1
                    delay = min(base_delay * (2 ** retry_count), 60)  # Apply exponential backoff
                    print(f"QR Listener not found. QR_DEVICE_NAME={self.qr_listener_name}. Retry {retry_count}/{max_retries} in {delay}s")
                    import auth_manager, setting
                    auth_manager.service.qr_status_hw = setting.STATUS_DISABLE
                    
                    if retry_count >= max_retries:
                        print("QR Listener max retries reached. Waiting longer before next attempt...")
                        time.sleep(120)  # Wait 2 minutes before retry
                        retry_count = 0
                    else:
                        time.sleep(delay)
                    continue

                print("QR Listener Initialized Successfully")
                retry_count = 0  # Reset retry counter on success
                import auth_manager, setting
                auth_manager.service.qr_status_hw = setting.STATUS_ENABLE
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
                break
            except Exception as e:
                print(f"QR Listener Initializing failed: {e}. Retrying in 1 second...")
                import auth_manager, setting
                auth_manager.service.qr_status_hw = setting.STATUS_DISABLE
                time.sleep(1)

    def start(self):
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()

_speaker_manager = None
_status_led = None
_external_button = None
_internal_button = None
_door = None
_nfc = None
_qr = None

def get_speaker_manager():
    global _speaker_manager
    if _speaker_manager is None:
        _speaker_manager = SpeakerManager()
    return _speaker_manager

def get_status_led():
    global _status_led
    if _status_led is None:
        _status_led = StatusLED()
    return _status_led

def get_external_button():
    global _external_button
    if _external_button is None:
        _external_button = ExternalButtonSwitch()
    return _external_button

def get_internal_button():
    global _internal_button
    if _internal_button is None:
        _internal_button = InternalButtonSwitch()
    return _internal_button

def get_door():
    global _door
    if _door is None:
        _door = DoorRelay()
    return _door

def get_nfc():
    global _nfc
    if _nfc is None:
        _nfc = NFCReader()
    return _nfc

def get_qr():
    global _qr
    if _qr is None:
        _qr = QRListener()
    return _qr

# 기존 코드와의 호환성을 위한 별칭 - 지연 초기화로 변경
def _init_hardware_components():
    """하드웨어 컴포넌트를 지연 초기화하여 GUI 우선 실행 보장"""
    global speaker_manager, status_led, external_button, internal_button, door, nfc, qr
    
    # 3초 후 하드웨어 초기화 시작
    import threading
    import time
    
    def delayed_init():
        time.sleep(3)
        print("Starting hardware components initialization...")
        speaker_manager = get_speaker_manager()
        status_led = get_status_led()
        external_button = get_external_button()
        internal_button = get_internal_button()
        door = get_door()
        nfc = get_nfc()
        qr = get_qr()
        print("Hardware components initialization completed")
    
    init_thread = threading.Thread(target=delayed_init, daemon=True, name="HardwareInit")
    init_thread.start()

# 하드웨어 초기화를 별도 스레드에서 지연 실행
_init_hardware_components()

# 초기값 설정 (실제 객체는 지연 초기화됨)
speaker_manager = None
status_led = None
external_button = None
internal_button = None
door = None
nfc = None
qr = None

def close():
    """모든 하드웨어 리소스 정리 및 스레드 종료"""
    try:
        # 각 컴포넌트의 cleanup 메서드 호출 - None 체크 추가
        if 'nfc' in globals() and nfc is not None:
            nfc.cleanup()
        if 'qr' in globals() and qr is not None:
            qr.cleanup()
        if 'status_led' in globals() and status_led is not None:
            status_led.cleanup()
        
        # GPIO 정리
        GPIO.cleanup()
        print("Hardware manager cleanup completed successfully")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        # 오류 발생 시에도 GPIO는 정리
        try:
            GPIO.cleanup()
        except:
            pass