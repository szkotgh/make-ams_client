import threading
import time
import binascii
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

import managers.hardware_manager as hardware_manager

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
                        import managers.auth_manager as auth_manager, setting
                        auth_manager.service.nfc_status_hw = setting.STATUS_ENABLE
                    except Exception as e:
                        self.initialized = False
                        consecutive_errors += 1
                        import managers.auth_manager as auth_manager, setting
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
