import threading
import requests
import setting
import managers.log_manager as log_manager
import managers.hardware_manager as hardware_manager

class AuthResultDTO:
    def __init__(self, code: int, message: str, data=None, success: bool=False):
        self.code = code
        self.message = message
        self.data = data
        self.success = success

class AuthManager:
    def __init__(self):
        self.AUTH_TOKEN = setting.AUTH_TOKEN

        self.connection_success = False
        self.connection_ping = -1

        self.door_access_level = setting.STATUS_CLOSE
        self.button_status_enabled = setting.STATUS_DISABLE
        self.qr_status_enabled = setting.STATUS_DISABLE
        self.nfc_status_enabled = setting.STATUS_DISABLE
        self.qr_status_hw = setting.STATUS_DISABLE
        self.nfc_status_hw = setting.STATUS_DISABLE
        self.remote_open_callback = None
        self.remote_open_enabled = setting.STATUS_DISABLE
        self.remote_open_by = None
        self.open_request_enabled = setting.STATUS_DISABLE
        
        self.start_connection()
    
    def regi_remote_open_callback(self, callback):
        self.remote_open_callback = callback
    
    def start_connection(self):
        def check_connection():
            try:
                response = requests.get(setting.SERVER_URL+"/device/status", timeout=setting.TIME_OUT, headers={"Authorization": f"Bearer {self.AUTH_TOKEN}", "User-Agent": "MAKE-AMS Device"})
                ping_ms = int(response.elapsed.total_seconds()*1000)

                result_json = response.json()
                result_code = result_json["code"]
                _ = result_json["message"]
                result_data = result_json["data"]

                if result_code == 200:
                    self.connection_success = True
                    self.connection_ping = ping_ms

                    self.door_access_level = result_data['door_access_level']
                    self.button_status_enabled = result_data['button_status_enabled']
                    self.qr_status_enabled = result_data['qr_status_enabled']
                    self.nfc_status_enabled = result_data['nfc_status_enabled']
                    self.remote_open_enabled = result_data['remote_open_enabled']
                    self.remote_open_by = result_data['remote_open_door_by']
                    self.open_request_enabled = result_data['open_request_enabled']
                    
                    if self.remote_open_enabled == setting.STATUS_ENABLE:
                        threading.Thread(target=self.remote_open_callback, args=(self.remote_open_by,)).start()
                else:
                    self.connection_success = False
            except Exception:
                self.connection_success = False
            
            ## 인터넷 연결 불량: 전체 기능 제한
            if not self.connection_success:
                self.door_access_level = setting.STATUS_CLOSE
                self.open_request_enabled = setting.STATUS_DISABLE

            ## 열림 상태: 작업 안함
            if self.door_access_level == setting.STATUS_OPEN:
                hardware_manager.external_button.led_on()
            ## 내부인 상태: 버튼 기능 제한
            elif self.door_access_level == setting.STATUS_RESTRIC:
                self.button_status_enabled = setting.STATUS_DISABLE
                hardware_manager.external_button.led_off()
            ## 제한 상태: 모든 기능 제한(관리자 예외)
            elif self.door_access_level == setting.STATUS_CLOSE:
                self.button_status_enabled = setting.STATUS_DISABLE
                self.qr_status_enabled = setting.STATUS_DISABLE
                self.nfc_status_enabled = setting.STATUS_DISABLE
                hardware_manager.external_button.led_off()
            ## 알 수 없는 상태: 모든 기능 제한(관리자 예외)
            else:
                self.button_status_enabled = setting.STATUS_DISABLE
                self.qr_status_enabled = setting.STATUS_DISABLE
                self.nfc_status_enabled = setting.STATUS_DISABLE
                hardware_manager.external_button.led_off()

            threading.Timer(setting.CONNECTION_INTERVAL, check_connection).start()

        check_connection()

    # 버튼 눌렀을 때
    def request_button_auth(self) -> AuthResultDTO:
        url = f"{setting.SERVER_URL}/device/auth/button"
        header = {
            "Authorization": f"Bearer {self.AUTH_TOKEN}",
            "User-Agent": "MAKE-AMS Device"
        }
        data = {}
        
        try:
            response = requests.post(url, timeout=setting.TIME_OUT, headers=header, json=data)

            result_json = response.json()
            result_code = result_json["code"]
            result_message = result_json["message"]
            result_data = result_json["data"]
            
            return AuthResultDTO(code=result_code, message=result_message, data=result_data, success=True)
        
        except requests.exceptions.ConnectionError as e:
            log_manager.service.insert_log("auth_manager", "에러", f"서버와 연결에 실패했습니다: {e}")
            return AuthResultDTO(code=-1, message="서버와 연결에 실패했습니다.",  success=False)
        except requests.exceptions.Timeout as e:
            log_manager.service.insert_log("auth_manager", "에러", f"요청 시간이 초과되었습니다: {e}")
            return AuthResultDTO(code=-1, message="요청 시간이 초과되었습니다.",  success=False)
        except Exception as e:
            log_manager.service.insert_log("auth_manager", "에러", f"알 수 없는 오류입니다: {e}")
            return AuthResultDTO(code=-1, message="알 수 없는 오류입니다.",  success=False)

    # QR 인식했을 때
    def request_qr_auth(self, qr_value: str):
        url = f"{setting.SERVER_URL}/device/auth/qr"
        header = {
            "Authorization": f"Bearer {self.AUTH_TOKEN}",
            "User-Agent": "MAKE-AMS Device"
        }
        body = {
            "value": qr_value
        }

        try:
            response = requests.post(url, timeout=setting.TIME_OUT, headers=header, json=body)

            result_json = response.json()
            result_code = result_json["code"]
            result_message = result_json["message"]
            result_data = result_json["data"]
            
            return AuthResultDTO(code=result_code, message=result_message, data=result_data, success=True)
        
        except requests.exceptions.ConnectionError as e:
            log_manager.service.insert_log("auth_manager", "에러", f"서버와 연결에 실패했습니다: {e}")
            return AuthResultDTO(code=-1, message="서버와 연결에 실패했습니다.",  success=False)
        except requests.exceptions.Timeout as e:
            log_manager.service.insert_log("auth_manager", "에러", f"요청 시간이 초과되었습니다: {e}")
            return AuthResultDTO(code=-1, message="요청 시간이 초과되었습니다.",  success=False)
        except Exception as e:
            log_manager.service.insert_log("auth_manager", "에러", f"알 수 없는 오류입니다: {e}")
            return AuthResultDTO(code=-1, message="알 수 없는 오류입니다.",  success=False)
    
    # NFC 인식했을 때
    def request_nfc_auth(self, nfc_value: str) -> AuthResultDTO:
        url = f"{setting.SERVER_URL}/device/auth/nfc"
        header = {
            "Authorization": f"Bearer {self.AUTH_TOKEN}",
            "User-Agent": "MAKE-AMS Device"
        }
        body = {
            "value": nfc_value
        }
        
        try:
            response = requests.post(url, timeout=setting.TIME_OUT, headers=header, json=body)

            result_json = response.json()
            result_code = result_json["code"]
            result_message = result_json["message"]
            result_data = result_json["data"]
            
            return AuthResultDTO(code=result_code, message=result_message, data=result_data, success=True)
        
        except requests.exceptions.ConnectionError as e:
            log_manager.service.insert_log("auth_manager", "에러", f"서버와 연결에 실패했습니다: {e}")
            return AuthResultDTO(code=-1, message="서버와 연결에 실패했습니다.", success=False)
        except requests.exceptions.Timeout as e:
            log_manager.service.insert_log("auth_manager", "에러", f"요청 시간이 초과되었습니다: {e}")
            return AuthResultDTO(code=-1, message="요청 시간이 초과되었습니다.", success=False)
        except Exception as e:
            log_manager.service.insert_log("auth_manager", "에러", f"알 수 없는 오류입니다: {e}")
            return AuthResultDTO(code=-1, message=f"알 수 없는 오류입니다.", success=False)

    def request_open_door(self) -> AuthResultDTO:
        url = f"{setting.SERVER_URL}/device/request_open_door"
        header = {
            "Authorization": f"Bearer {self.AUTH_TOKEN}",
            "User-Agent": "MAKE-AMS Device"
        }
        body = {
        }

        try:
            response = requests.post(url, timeout=setting.TIME_OUT, headers=header, json=body)

            result_json = response.json()
            result_code = result_json["code"]
            result_message = result_json["message"]
            result_data = result_json["data"]

            return AuthResultDTO(code=result_code, message=result_message, data=result_data, success=True)
        
        except requests.exceptions.ConnectionError as e:
            log_manager.service.insert_log("auth_manager", "에러", f"서버와 연결에 실패했습니다: {e}")
            return AuthResultDTO(code=-1, message="서버와 연결에 실패했습니다.", success=False)
        except requests.exceptions.Timeout as e:
            log_manager.service.insert_log("auth_manager", "에러", f"요청 시간이 초과되었습니다: {e}")
            return AuthResultDTO(code=-1, message="요청 시간이 초과되었습니다.", success=False)
        except Exception as e:
            log_manager.service.insert_log("auth_manager", "에러", f"알 수 없는 오류입니다: {e}")
            return AuthResultDTO(code=-1, message=f"알 수 없는 오류입니다.", success=False)

    def get_connection_status(self):
        return {"success": self.connection_success, "ping": self.connection_ping}

    def get_door_status(self):
        return self.door_access_level
    
    def get_button_status(self):
        return self.button_status_enabled
    
    def get_qr_status(self):
        return setting.STATUS_ENABLE if self.is_qr_enabled() else setting.STATUS_DISABLE
    
    def get_nfc_status(self):
        return setting.STATUS_ENABLE if self.is_nfc_enabled() else setting.STATUS_DISABLE

    def is_qr_enabled(self):
        return self.qr_status_enabled == setting.STATUS_ENABLE and self.qr_status_hw == setting.STATUS_ENABLE

    def is_nfc_enabled(self):
        return self.nfc_status_enabled == setting.STATUS_ENABLE and self.nfc_status_hw == setting.STATUS_ENABLE

service = AuthManager()