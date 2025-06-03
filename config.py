import json
import dotenv
import os
import utils

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
START_TIME = utils.get_now_datetime()

# Status
STATUS_ENABLE = config["status"]["enable"]
STATUS_DISABLE = config["status"]["disable"]
STATUS_OPEN = config["status"]["open"]
STATUS_RESTRIC = config["status"]["restrict"]
STATUS_CLOSE = config["status"]["close"]

# UI
TITLE = config["ui"]["title"]
DEFAULT_FONT = config["ui"]["default_font"]
UNKNOWN_COLOR = config["ui"]["unknown_color"]
DISABLE_COLOR = config["ui"]["disable_color"]
ENABLE_COLOR = config["ui"]["enable_color"]
WARNING_COLOR = config["ui"]["warning_color"]
AUTH_COLOR = config["ui"]["auth_color"]

# File
## logs
LOG_DB_PATH = "./src/log.db"
## images
FILE_PATH = "./src/"
MAIN_IMAGE_PATH = "./src/main.gif"
DOOR_ICON_IMG_PATH = "./src/door_icon.png"
BUTTON_ENABLE_IMG_PATH = "./src/button_enable.png"
BUTTON_DISABLE_IMG_PATH = "./src/button_disable.png"
QR_ICON_IMG_PATH = "./src/qr_icon.png"
QR_ENABLE_IMG_PATH = "./src/qr_enable.png"
QR_DISABLE_IMG_PATH = "./src/qr_disable.png"
NFC_ICON_IMG_PATH = "./src/nfc_icon.png"
NFC_ENABLE_IMG_PATH = "./src/nfc_enable.png"
NFC_DISABLE_IMG_PATH = "./src/nfc_disable.png"
## sounds
CLICK_SOUND_PATH = "./src/sounds/click.mp3"
WRONG_SOUND_PATH = "./src/sounds/wrong.mp3"
SUCCESS_SOUND_PATH = "./src/sounds/success.mp3"
MINECRAFT_DEATH = "./src/sounds/minecraft_death.mp3"
WHY_YOU_LITTLE = "./src/sounds/why_you_little.mp3"
DTMG = "./src/sounds/dtmg.mp3"
JTMG = "./src/sounds/jtmg.mp3"
