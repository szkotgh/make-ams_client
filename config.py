import json
import dotenv
import os

# init
dotenv.load_dotenv()
with open("./setting.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# System
SERVER_URL = config["connection"]["server_url"]
TIME_OUT = config["connection"]["time_out"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]
ADMIN_PW = os.environ["ADMIN_PASSWORD"]
DISPLAY_WIDTH = config["ui"]["display_width"]
DISPLAY_HEIGHT = config["ui"]["display_height"]
MAIN_GIF_INTERVAL = config["ui"]["main_gif_interval"]
CONNECTION_INTERVAL = config["connection"]["connection_interval"]

# Status
STATUS_ENABLE = config["status"]["enable"]
STATUS_DISABLE = config["status"]["disable"]
STATUS_OPEN = config["status"]["open"]
STATUS_RESTRIC = config["status"]["restrict"]
STATUS_CLOSE = config["status"]["close"]

def get_status_korean(status):
    status_map = {
        STATUS_ENABLE: "활성화",
        STATUS_DISABLE: "비활성화",
        STATUS_OPEN: "열림",
        STATUS_RESTRIC: "내부인",
        STATUS_CLOSE: "제한"
    }
    return status_map.get(status, "알 수 없음")

# UI
TITLE = config["ui"]["title"]
DEFAULT_FONT = config["ui"]["default_font"]
UNKNOWN_COLOR = config["ui"]["unknown_color"]
DISABLE_COLOR = config["ui"]["disable_color"]
ENABLE_COLOR = config["ui"]["enable_color"]
WARNING_COLOR = config["ui"]["warning_color"]

# File
FILE_PATH = config["file"]["file_path"]
MAIN_IMAGE_PATH = config["file"]["main_image_path"]
BUTTON_ENABLE_IMG_PATH = config["file"]["button_enable_img_path"]
BUTTON_DISABLE_IMG_PATH = config["file"]["button_disable_img_path"]
QR_ENABLE_IMG_PATH = config["file"]["qr_enable_img_path"]
QR_DISABLE_IMG_PATH = config["file"]["qr_disable_img_path"]
NFC_ENABLE_IMG_PATH = config["file"]["nfc_enable_img_path"]
NFC_DISABLE_IMG_PATH = config["file"]["nfc_disable_img_path"]
