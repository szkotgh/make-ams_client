import threading
import time
import managers.hardware_manager as hardware_manager

class InternalButton():
    def __init__(self):
        self.BTN_PIN = hardware_manager.setting.INTERNAL_SW_BTN
        self.LED_PIN = hardware_manager.setting.INTERNAL_SW_LED
        self.GPIO = hardware_manager.GPIO
        self.callback_list = []
        self.thread = None
        self._lock = threading.Lock()
        self.is_initialized = False

        self.GPIO.setup(self.BTN_PIN, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.LED_PIN, self.GPIO.OUT)
        self.is_initialized = True

        self.start()

    def led_on(self):
        self.GPIO.output(self.LED_PIN, self.GPIO.HIGH)

    def led_off(self):
        self.GPIO.output(self.LED_PIN, self.GPIO.LOW)

    def read_button(self):
        if not self.is_initialized: return False
        return self.GPIO.input(self.BTN_PIN) == self.GPIO.LOW

    def register_callback(self, callback):
        print(f"[InternalButton] Registering callback: {callback}")
        self.callback_list.append(callback)
    
    def _detect_button(self):
        while True:
            # print(f"[InternalButton] Detecting button: {self.read_button()}")

            if self.read_button() == True:
                for callback in self.callback_list:
                    try:
                        threading.Thread(target=callback, daemon=True).start()
                    except Exception as e:
                        print(f"[InternalButton] Error executing callback: {e}")
                
                while self.read_button() == True:
                    time.sleep(0.05)
            
            time.sleep(0.05)

    def start(self):
        with self._lock:
            if self.thread is not None and self.thread.is_alive():
                return
        self.thread = threading.Thread(target=self._detect_button, daemon=True)
        self.thread.start()

    def cleanup(self):
        print("[InternalButton] Cleaning up...")
        self.is_initialized = False
        with self._lock:
            if self.thread is not None and self.thread.is_alive():
                self.thread.join(timeout=0.1)
            self.thread = None
        print("[InternalButton] Cleaned up.")