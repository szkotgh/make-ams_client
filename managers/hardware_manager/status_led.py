import threading
import time
import managers.hardware_manager as hardware_manager

class StatusLED:
    def __init__(self):
        self.LED_RED = hardware_manager.setting.STATUS_LED_RED
        self.LED_YELLOW = hardware_manager.setting.STATUS_LED_YELLOW
        self.LED_GREEN = hardware_manager.setting.STATUS_LED_GREEN
        self.GPIO = hardware_manager.GPIO

        self.GPIO.setup(self.LED_RED, self.GPIO.OUT)
        self.GPIO.setup(self.LED_YELLOW, self.GPIO.OUT)
        self.GPIO.setup(self.LED_GREEN, self.GPIO.OUT)

        self._states = {
            "red": {"thread": None, "stop_event": threading.Event()},
            "yellow": {"thread": None, "stop_event": threading.Event()},
            "green": {"thread": None, "stop_event": threading.Event()},
        }

    def _set_led(self, color, state: bool):
        pin = getattr(self, f"LED_{color.upper()}")
        self.GPIO.output(pin, self.GPIO.HIGH if state else self.GPIO.LOW)

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
        print("[StatusLED] Cleaning up...")
        for c in ["red", "yellow", "green"]:
            self.off(c)
        print("[StatusLED] Cleaned up.")