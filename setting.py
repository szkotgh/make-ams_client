import json
import dotenv
import os
import utils

# init
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

dotenv.load_dotenv()
with open("./setting.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# GPIO
DOOR_RELAY = config["gpio"]["door_relay"]
STATUS_LED_RED = config["gpio"]["status_led_red"]
STATUS_LED_YELLOW = config["gpio"]["status_led_yellow"]
STATUS_LED_GREEN = config["gpio"]["status_led_green"]
INTERNAL_SW_BTN = config["gpio"]["internal_sw_btn"]
INTERNAL_SW_LED = config["gpio"]["internal_sw_led"]
EXTERNAL_SW_BTN = config["gpio"]["external_sw_btn"]
EXTERNAL_SW_LED = config["gpio"]["external_sw_led"]

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
STATUS_ENABLE = "enable"
STATUS_DISABLE = "disable"
STATUS_OPEN = "open"
STATUS_RESTRIC = "restrict"
STATUS_CLOSE = "close"

# UI
TITLE = config["ui"]["title"]
DEFAULT_FONT = config["ui"]["default_font"]
UNKNOWN_COLOR = config["ui"]["unknown_color"]
DISABLE_COLOR = config["ui"]["disable_color"]
ENABLE_COLOR = config["ui"]["enable_color"]
WARNING_COLOR = config["ui"]["warning_color"]
AUTH_COLOR = config["ui"]["auth_color"]

## logs
DB_PATH = f"{PROJECT_PATH}/db"
if not os.path.exists(DB_PATH): os.makedirs(DB_PATH)
LOG_DB_PATH = f"{DB_PATH}/log.db"

# Source Path
SRC_PATH = f"{PROJECT_PATH}/src"

## images
IMAGES_PATH = f"{SRC_PATH}/images"
ICON_PATH                    = f"{IMAGES_PATH}/icon.png"
ICON_ICO_PATH                = f"{IMAGES_PATH}/icon.ico"
MAIN_IMAGE_PATH              = f"{IMAGES_PATH}/main.gif"
DOOR_ICON_IMG_PATH           = f"{IMAGES_PATH}/door_icon.png"
BUTTON_ENABLE_IMG_PATH       = f"{IMAGES_PATH}/button_enable.png"
BUTTON_OPEN_REQUEST_IMG_PATH = f"{IMAGES_PATH}/button_open_request.png"
BUTTON_DISABLE_IMG_PATH      = f"{IMAGES_PATH}/button_disable.png"
QR_ICON_IMG_PATH             = f"{IMAGES_PATH}/qr_icon.png"
QR_ENABLE_IMG_PATH           = f"{IMAGES_PATH}/qr_enable.png"
QR_DISABLE_IMG_PATH          = f"{IMAGES_PATH}/qr_disable.png"
NFC_ICON_IMG_PATH            = f"{IMAGES_PATH}/nfc_icon.png"
NFC_ENABLE_IMG_PATH          = f"{IMAGES_PATH}/nfc_enable.png"
NFC_DISABLE_IMG_PATH         = f"{IMAGES_PATH}/nfc_disable.png"

## sounds
SOUNDS_PATH = f"{SRC_PATH}/sounds"
CLICK_SOUND_PATH      = f"{SOUNDS_PATH}/click.mp3"
WRONG_SOUND_PATH      = f"{SOUNDS_PATH}/wrong.mp3"
SUCCESS_SOUND_PATH    = f"{SOUNDS_PATH}/success.mp3"
TEST_MUSIC            = f"{SOUNDS_PATH}/test_music.mp3"
DOOR_OPEN_SOUND_PATH  = f"{SOUNDS_PATH}/door_open.mp3"
DOOR_CLOSE_SOUND_PATH = f"{SOUNDS_PATH}/door_close.mp3"
MINECRAFT_DEATH       = f"{SOUNDS_PATH}/minecraft_death.mp3"
WHY_YOU_LITTLE        = f"{SOUNDS_PATH}/why_you_little.mp3"
DTMG                  = f"{SOUNDS_PATH}/dtmg.mp3"
JTMG                  = f"{SOUNDS_PATH}/jtmg.mp3"
ELEVATOR_MUSIC        = f"{SOUNDS_PATH}/elevator_music.mp3"
