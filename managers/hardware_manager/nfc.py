import threading
import time
import binascii
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

class NFCReader:
    def __init__(self):
        self._stop_event = threading.Event()
        self._init_thread = threading.Thread(target=self._init_nfc, daemon=False)
        self._init_thread.start()
        self.nfc_thread = None
        self.callback_list = []
        self.is_initialized = False
        self.start()

    def cleanup(self):
        print("[NFCReader] Cleaning up...")
        self._stop_event.set()
        if self._init_thread.is_alive():
            self._init_thread.join(timeout=0.1)
        if hasattr(self, "i2c"):
            try:
                self.i2c.deinit()
            except Exception:
                pass
        if self.nfc_thread is not None and self.nfc_thread.is_alive():
            self.nfc_thread.join(timeout=0.1)
        print("[NFCReader] Cleaned up.")
        self.is_initialized = False

    def _init_nfc(self):
        check_interval = 10

        while not self._stop_event.is_set():
            try:
                now = time.time()
                need_reinit = False

                try:
                    self.pn532.read_passive_target(timeout=0.5)
                except Exception:
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
                        self.is_initialized = True
                        last_init_time = now
                    except Exception as e:
                        self.is_initialized = False
                        need_reinit = True
                        print(f"[NFCReader] Failed to initialize: {e}")
                
                time.sleep(check_interval)
                    
            except Exception as e:
                print(f"[NFCReader] Initialization error: {e}")
                self.is_initialized = False
                time.sleep(check_interval)

    def register_callback(self, callback):
        '''
        callback: function(uid: str | None)
        '''
        print(f"[NFCReader] Registering callback: {callback}")
        self.callback_list.append(callback)

    def start(self):
        if self.nfc_thread is not None and self.nfc_thread.is_alive():
            return
        self.nfc_thread = threading.Thread(target=self._thread_nfc, daemon=False)
        self.nfc_thread.start()
        print("[NFCReader] Started")

    def read_nfc(self, timeout=0.5):
        if not self.is_initialized or not self.nfc_thread.is_alive():
            return False

        try:
            uid = self.pn532.read_passive_target(timeout=timeout)
        except Exception as e:
            print(f"[NFCReader] Error reading NFC: {e}")
            return None
        if uid is None:
            return None
        return binascii.hexlify(uid).decode("utf-8")

    def _thread_nfc(self):
        while not self._stop_event.is_set():
            uid = self.read_nfc(timeout=1)
            if uid is not None and self.is_initialized:
                print(f"[NFCReader] NFC read: {uid}")
                for callback in self.callback_list:
                    try:
                        threading.Thread(target=callback, args=(uid,), daemon=False).start()
                    except Exception as e:
                        print(f"[NFCReader] Error executing callback: {e}")
            time.sleep(1)