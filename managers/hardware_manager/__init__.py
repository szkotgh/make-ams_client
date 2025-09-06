import RPi.GPIO as GPIO
import atexit
import setting
from managers.hardware_manager.internal_button import InternalButton
from managers.hardware_manager.external_button import ExternalButton
from managers.hardware_manager.speaker import Speaker
from managers.hardware_manager.status_led import StatusLED
from managers.hardware_manager.nfc import NFCReader
from managers.hardware_manager.qr import QRListener

print("[Hardware Manager] Initializing...")

try:
    GPIO.cleanup()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    internal_button = InternalButton()
    external_button = ExternalButton()
    speaker = Speaker()
    status_led = StatusLED()
    nfc = NFCReader()
    qr = QRListener()
except Exception as e:
    print(f"[Hardware Manager] Error initializing hardware manager: {e}")
    raise e

print("[Hardware Manager] Initialized")

def cleanup_gpio():
    print("[Hardware Manager] Cleanup GPIO")
    GPIO.cleanup()
    print("[Hardware Manager] Ended.")
atexit.register(cleanup_gpio)