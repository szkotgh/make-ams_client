# System
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

CONNECTION_TEST_URL = "https://www.google.com/"
CONNECTION_TEST_INTERVAL = 0

# Status
STATUS_ENABLE = "enable"
STATUS_DISABLE = "disable"
STATUS_OPEN = "open"
STATUS_RESTRIC = "restriction"
STATUS_CLOSE = "close"
def get_status_korean(status):
    status_map = {
        STATUS_ENABLE: "활성화",
        STATUS_DISABLE: "비활성화",
        STATUS_OPEN: "열림",
        STATUS_RESTRIC: "외부인제한",
        STATUS_CLOSE: "제한"
    }
    return status_map.get(status, "알 수 없음")

# UI
TITLE = "메이크 출입 관리 시스템"
UNKNOWN_COLOR = "#979797"
DISABLE_COLOR = "#e60013"
ENABLE_COLOR = "#079a3e"
WARNING_COLOR = "#ffcc00"

# File
FILE_PATH = "./src/"
MAIN_IMAGE_PATH = "./src/main.gif"
BUTTON_ENABLE_IMG_PAGH = "./src/button_enable.png"
BUTTON_DISABLE_IMG_PAGH = "./src/button_disable.png"
QR_ENABLE_IMG_PAGH = "./src/qr_enable.png"
QR_DISABLE_IMG_PAGH = "./src/qr_disable.png"
NFC_ENABLE_IMG_PAGH = "./src/nfc_enable.png"
NFC_DISABLE_IMG_PAGH = "./src/nfc_disable.png"

