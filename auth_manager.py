import threading
import time
import dotenv
import requests
import auth_manager
import config

class AuthManager:
    def __init__(self):
        self.door_status = config.STATUS_CLOSE
        self.button_status = config.STATUS_DISABLE
        self.qr_status = config.STATUS_ENABLE
        self.nfc_status = config.STATUS_DISABLE

        self.connection_success = False
        self.connection_status = config.STATUS_CLOSE
        self.connection_ping = 0

        self.start_connection()
    
    def start_connection(self):
        def check_connection():
            try:
                response = requests.get(config.CONNECTION_TEST_URL, timeout=1)
                ping = int(response.elapsed.total_seconds()*1000)
                if response.ok:
                    self.connection_success = True
                    self.connection_ping = ping
                    self.connection_status = config.STATUS_CLOSE

                    self.door_status = config.STATUS_RESTRIC
                    self.button_status = config.STATUS_DISABLE
                    self.qr_status = config.STATUS_ENABLE
                    self.nfc_status = config.STATUS_DISABLE

                    if self.door_status == config.STATUS_RESTRIC:
                        self.button_status = config.STATUS_DISABLE
                    elif self.door_status == config.STATUS_CLOSE:
                        self.button_status = config.STATUS_DISABLE
                        self.qr_status = config.STATUS_DISABLE
                        self.nfc_status = config.STATUS_DISABLE
                else:
                    self.connection_success = False
            except Exception:
                self.connection_success = False
            
            threading.Timer(config.CONNECTION_TEST_INTERVAL, check_connection).start()

        check_connection()

    def get_connection_status(self):
        return {"success": self.connection_success, "status": self.connection_status, "ping": self.connection_ping}

    def get_door_status(self):
        return self.door_status
    
    def get_button_status(self):
        return self.button_status
    
    def get_qr_status(self):
        return self.qr_status
    
    def get_nfc_status(self):
        return self.nfc_status
    
service = AuthManager()