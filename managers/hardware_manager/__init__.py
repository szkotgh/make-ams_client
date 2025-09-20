import RPi.GPIO as GPIO
import atexit
import threading
from typing import Optional
import setting
from managers.hardware_manager.internal_button import InternalButton
from managers.hardware_manager.external_button import ExternalButton
from managers.hardware_manager.speaker import Speaker
from managers.hardware_manager.tts import TTSManager
from managers.hardware_manager.status_led import StatusLED
from managers.hardware_manager.nfc import NFCReader
from managers.hardware_manager.qr import QRListener
from managers.hardware_manager.door import Door

print("[Hardware Manager] Initializing...")
is_initialized: bool = False

internal_button: Optional[InternalButton] = None
external_button: Optional[ExternalButton] = None
speaker: Optional[Speaker] = None
tts: Optional[TTSManager] = None
status_led: Optional[StatusLED] = None
nfc: Optional[NFCReader] = None
qr: Optional[QRListener] = None
door: Optional[Door] = None

def initialize_hardware():
    global is_initialized, internal_button, external_button, speaker, tts, status_led, nfc, qr, door
    
    try:
        GPIO.cleanup()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        internal_button = InternalButton()
        external_button = ExternalButton()
        speaker = Speaker()
        tts = TTSManager()
        status_led = StatusLED()
        nfc = NFCReader()
        qr = QRListener()
        door = Door()
        
        is_initialized = True
        print("[Hardware Manager] Initialized successfully")
        
    except Exception as e:
        print(f"[Hardware Manager] Error initializing hardware manager: {e}")
        is_initialized = False

init_thread = threading.Thread(target=initialize_hardware, daemon=False)
init_thread.start()

def cleanup():
    print("[Hardware Manager] Cleanup GPIO")
    
    if not is_initialized:
        print("[Hardware Manager] Hardware not initialized, skipping cleanup")
        return
    
    try:
        if status_led is not None:
            status_led.all_off()
            status_led.blink('red')
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up status_led: {e}")
    
    try:
        if nfc is not None:
            nfc.cleanup()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up nfc: {e}")
    
    try:
        if qr is not None:
            qr.cleanup()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up qr: {e}")
    
    try:
        if door is not None:
            door.close_door(close_duration=0)
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up door: {e}")
    
    try:
        if speaker is not None:
            speaker.stop()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up speaker: {e}")
    
    try:
        if tts is not None:
            tts.cleanup()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up tts: {e}")
    
    try:
        if internal_button is not None:
            internal_button.led_off()
            internal_button.cleanup()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up internal_button: {e}")
    
    try:
        if external_button is not None:
            external_button.led_off()
            external_button.cleanup()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up external_button: {e}")
    
    try:
        if status_led is not None:
            status_led.cleanup()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up status_led: {e}")
    
    try:
        GPIO.cleanup()
    except Exception as e:
        print(f"[Hardware Manager] Error cleaning up GPIO: {e}")
    
    print("[Hardware Manager] Ended.")
atexit.register(cleanup)