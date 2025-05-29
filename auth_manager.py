import json
import threading
import requests
import config

class AuthManager:
    def __init__(self):
        self.AUTH_TOKEN = config.AUTH_TOKEN

        self.connection_success = False
        self.connection_ping = -1

        self.door_status = config.STATUS_CLOSE
        self.button_status = config.STATUS_DISABLE
        self.qr_status = config.STATUS_DISABLE
        self.nfc_status = config.STATUS_DISABLE

        self.start_connection()
    
    def start_connection(self):
        def check_connection():
            try:
                response = requests.get(config.SERVER_URL+"/", timeout=config.TIME_OUT)
                ping = int(response.elapsed.total_seconds()*1000)

                if response.ok:
                    self.connection_success = True
                    self.connection_ping = ping

                    self.door_status = config.STATUS_OPEN
                    self.button_status = config.STATUS_ENABLE
                    self.qr_status = config.STATUS_ENABLE
                    self.nfc_status = config.STATUS_ENABLE
                else:
                    self.connection_success = False
            except Exception as e:
                self.connection_success = False
            
            ## 인터넷 연결 불량: 전체 기능 제한
            if not self.connection_success:
                self.door_status = config.STATUS_CLOSE

            ## 열림 상태: 작업 안함
            if self.door_status == config.STATUS_OPEN:
                pass
            ## 내부인 상태: 버튼 기능 제한
            elif self.door_status == config.STATUS_RESTRIC:
                self.button_status = config.STATUS_DISABLE
            ## 제한 상태: 모든 기능 제한(관리자 예외)
            elif self.door_status == config.STATUS_CLOSE:
                self.button_status = config.STATUS_DISABLE
                self.qr_status = config.STATUS_DISABLE
                self.nfc_status = config.STATUS_DISABLE
            ## 알 수 없는 상태: 모든 기능 제한(관리자 예외)
            else:
                self.button_status = config.STATUS_DISABLE
                self.qr_status = config.STATUS_DISABLE
                self.nfc_status = config.STATUS_DISABLE

            threading.Timer(config.CONNECTION_INTERVAL, check_connection).start()

        check_connection()

    # 버튼 눌렀을 때
    def request_button_auth(self):
        url = config.SERVER_URL + "/auth/button"
        try:
            response = requests.post(url, timeout=config.TIME_OUT, headers={"Authorization": self.AUTH_TOKEN})
            return True if response.ok else False
        except Exception as e:
            return False

    # QR 인식했을 때
    def request_qr_auth(self):
        url = config.SERVER_URL + "/auth/qr"
        try:
            response = requests.post(url, timeout=config.TIME_OUT, headers={"Authorization": self.AUTH_TOKEN})
            return True if response.ok else False
        except Exception as e:
            return False
    
    # NFC 인식했을 때
    def request_nfc_auth(self):
        url = config.SERVER_URL + "/auth/nfc"
        try:
            response = requests.post(url, timeout=config.TIME_OUT, headers={"Authorization": self.AUTH_TOKEN})
            return True if response.ok else False
        except Exception as e:
            return False

    def get_connection_status(self):
        return {"success": self.connection_success, "ping": self.connection_ping}

    def get_door_status(self):
        return self.door_status
    
    def get_button_status(self):
        return self.button_status
    
    def get_qr_status(self):
        return self.qr_status
    
    def get_nfc_status(self):
        return self.nfc_status
    
service = AuthManager()