import threading
import time
import evdev
import managers.hardware_manager as hardware_manager

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
        self.is_initialized = False
        
        self.start()

    def cleanup(self):
        print("[QRListener] Cleaning up...")
        self._stop_event.set()
        if self._device:
            try:
                self._device.close()
            except Exception:
                pass
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1)
        print("[QRListener] Cleaned up.")
        
    def register_callback(self, callback):
        print(f"[QRListener] Registering callback: {callback}")
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
                        try:
                            callback(self._result)
                        except Exception as e:
                            print(f"[QRListener] Error executing callback: {e}")
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
        reconnect_delay = 1
        print("[QRListener] Initializing...")
        
        while not self._stop_event.is_set():
            try:
                self._device = self._find_input_device()
                if not self._device:
                    print(f"[QRListener] not found. QR_DEVICE_NAME={self.qr_listener_name}. Retry in {reconnect_delay}s")
                    self.is_initialized = False
                    
                    time.sleep(reconnect_delay)
                    continue

                print("[QRListener] Initialized Successfully")
                self.is_initialized = True
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
                print(f"[QRListener] Initializing failed: {e}. Retrying in 1 second...")
                self.is_initialized = False
                time.sleep(1)

    def start(self):
        if self.listener_thread is not None:
            return
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()