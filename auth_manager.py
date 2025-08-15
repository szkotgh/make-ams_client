import json
import threading
import requests
import config
import log_manager

class AuthResultDTO:
    def __init__(self, success: bool, detail: str, user_name: str, user_id: str):
        self.success = success
        self.detail = detail
        self.user_name = user_name
        self.user_id = user_id

class AuthManager:
    def __init__(self):
        self.AUTH_TOKEN = config.AUTH_TOKEN

        self.connection_success = False
        self.connection_ping = -1

        self.door_status = config.STATUS_CLOSE
        self.button_status = config.STATUS_DISABLE
        self.qr_status_server = config.STATUS_DISABLE
        self.nfc_status_server = config.STATUS_DISABLE
        self.qr_status_hw = config.STATUS_DISABLE
        self.nfc_status_hw = config.STATUS_DISABLE

        self.start_connection()
    
    def start_connection(self):
        def check_connection():
            try:
                response = requests.get(config.SERVER_URL+"/device/status", timeout=config.TIME_OUT, headers={"Authorization": f"Bearer {self.AUTH_TOKEN}", "User-Agent": "MAKE-AMS Device"})
                ping_ms = int(response.elapsed.total_seconds()*1000)

                if response.ok:
                    self.connection_success = True
                    self.connection_ping = ping_ms

                    self.door_status = config.STATUS_OPEN
                    self.button_status = config.STATUS_ENABLE
                    self.qr_status_server = config.STATUS_ENABLE
                    self.nfc_status_server = config.STATUS_ENABLE
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
                self.qr_status_server = config.STATUS_DISABLE
                self.nfc_status_server = config.STATUS_DISABLE
            ## 알 수 없는 상태: 모든 기능 제한(관리자 예외)
            else:
                self.button_status = config.STATUS_DISABLE
                self.qr_status_server = config.STATUS_DISABLE
                self.nfc_status_server = config.STATUS_DISABLE

            threading.Timer(config.CONNECTION_INTERVAL, check_connection).start()

        check_connection()

    # 버튼 눌렀을 때
    def request_button_auth(self) -> AuthResultDTO:
        url = config.SERVER_URL + "/auth/button"
        data = {}
        
        try:
            response = requests.post(url, timeout=config.TIME_OUT, headers={"Authorization": f"Bearer {self.AUTH_TOKEN}", "User-Agent": "MAKE-AMS Device"}, json=data)

            result_json = response.json()
            result_success = result_json["success"]
            result_detail = result_json["detail"]
            result_user_name = result_json["user_name"]
            result_user_id = result_json["user_id"]
            
            return AuthResultDTO(result_success, result_detail, result_user_name, result_user_id)
        
        except requests.exceptions.ConnectionError as e:
            log_manager.service.insert_log("auth_manager", "에러", f"서버와 연결에 실패했습니다: {e}")
            return AuthResultDTO(False, "서버와 연결에 실패했습니다.", "", "")
        except requests.exceptions.Timeout as e:
            log_manager.service.insert_log("auth_manager", "에러", f"요청 시간이 초과되었습니다: {e}")
            return AuthResultDTO(False, "요청 시간이 초과되었습니다.", "", "")
        except Exception as e:
            log_manager.service.insert_log("auth_manager", "에러", f"알 수 없는 오류입니다: {e}")
            return AuthResultDTO(False, "알 수 없는 오류입니다.", "", "")

    # QR 인식했을 때
    def request_qr_auth(self, qr_value: str):
        url = config.SERVER_URL + "/auth/qr"
        body = {
            "value": qr_value
        }

        try:
            response = requests.post(url, timeout=config.TIME_OUT, headers={"Authorization": f"Bearer {self.AUTH_TOKEN}", "User-Agent": "MAKE-AMS Device"}, json=body)
            
            result_json = response.json()
            result_success = result_json["success"]
            result_detail = result_json["detail"]
            result_user_name = result_json["user_name"]
            result_user_id = result_json["user_id"]
            
            return AuthResultDTO(result_success, result_detail, result_user_name, result_user_id)
        
        except requests.exceptions.ConnectionError as e:
            log_manager.service.insert_log("auth_manager", "에러", f"서버와 연결에 실패했습니다: {e}")
            return AuthResultDTO(False, "서버와 연결에 실패했습니다.", "", "")
        except requests.exceptions.Timeout as e:
            log_manager.service.insert_log("auth_manager", "에러", f"요청 시간이 초과되었습니다: {e}")
            return AuthResultDTO(False, "요청 시간이 초과되었습니다.", "", "")
        except Exception as e:
            log_manager.service.insert_log("auth_manager", "에러", f"알 수 없는 오류입니다: {e}")
            return AuthResultDTO(False, "알 수 없는 오류입니다.", "", "")
    
    # NFC 인식했을 때
    def request_nfc_auth(self, nfc_value: str) -> AuthResultDTO:
        url = config.SERVER_URL + "/auth/nfc"
        body = {
            "value": nfc_value
        }
        
        try:
            response = requests.post(url, timeout=config.TIME_OUT, headers={"Authorization": f"Bearer {self.AUTH_TOKEN}", "User-Agent": "MAKE-AMS Device"}, json=body)
            response.raise_for_status()
            
            result_json = response.json()
            result_success = result_json["success"]
            result_detail = result_json["detail"]
            result_user_name = result_json["user_name"]
            result_user_id = result_json["user_id"]
            
            return AuthResultDTO(result_success, result_detail, result_user_name, result_user_id)
        
        except requests.exceptions.ConnectionError as e:
            log_manager.service.insert_log("auth_manager", "에러", f"서버와 연결에 실패했습니다: {e}")
            return AuthResultDTO(False, "서버와 연결에 실패했습니다.", "", "")
        except requests.exceptions.Timeout as e:
            log_manager.service.insert_log("auth_manager", "에러", f"요청 시간이 초과되었습니다: {e}")
            return AuthResultDTO(False, "요청 시간이 초과되었습니다.", "", "")
        except Exception as e:
            log_manager.service.insert_log("auth_manager", "에러", f"알 수 없는 오류입니다: {e}")
            return AuthResultDTO(False, "알 수 없는 오류입니다.", "", "")

    def get_connection_status(self):
        return {"success": self.connection_success, "ping": self.connection_ping}

    def get_door_status(self):
        return self.door_status
    
    def get_button_status(self):
        return self.button_status
    
    def get_qr_status(self):
        return config.STATUS_ENABLE if self.is_qr_enabled() else config.STATUS_DISABLE
    
    def get_nfc_status(self):
        return config.STATUS_ENABLE if self.is_nfc_enabled() else config.STATUS_DISABLE

    def is_qr_enabled(self):
        return self.qr_status_server == config.STATUS_ENABLE and self.qr_status_hw == config.STATUS_ENABLE

    def is_nfc_enabled(self):
        return self.nfc_status_server == config.STATUS_ENABLE and self.nfc_status_hw == config.STATUS_ENABLE

service = AuthManager()