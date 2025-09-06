import time
import managers.hardware_manager as hardware_manager
import setting

# regi button callback
def on_internal_button_pressed(ch):
    print(f"[Test Internal Button] Pressed: {ch}")

def on_external_button_pressed(ch):
    print(f"[Test External Button] Pressed: {ch}")

# hardware_manager.internal_button.regi_callback(on_internal_button_pressed)
# hardware_manager.external_button.regi_callback(on_external_button_pressed)


# test functions
def test_led():
    print("[Test LED]")
    print("Testing STATUS_LED_RED...")
    hardware_manager.status_led.on('red')
    time.sleep(1)
    hardware_manager.status_led.off('red')
    time.sleep(1)
    hardware_manager.status_led.blink('red')
    time.sleep(3)
    hardware_manager.status_led.off('red')
    time.sleep(1)
    print("done")

    print("Testing STATUS_LED_YELLOW...")
    hardware_manager.status_led.on('yellow')
    time.sleep(1)
    hardware_manager.status_led.off('yellow')
    time.sleep(1)
    hardware_manager.status_led.blink('yellow')
    time.sleep(3)
    hardware_manager.status_led.off('yellow')
    time.sleep(1)
    print("done")
    
    print("Testing STATUS_LED_GREEN...")
    hardware_manager.status_led.on('green')
    time.sleep(1)
    hardware_manager.status_led.off('green')
    time.sleep(1)
    hardware_manager.status_led.blink('green')
    time.sleep(3)
    hardware_manager.status_led.off('green')
    time.sleep(1)
    print("done")

def test_relay():
    print("[Test Relay]")
    print("Testing DOOR_RELAY...")
    hardware_manager.safe_door().open_door()
    time.sleep(3)
    hardware_manager.safe_door().close_door()
    time.sleep(3)
    print("done")

def test_qr():
    print("[Test QR]")

    is_testing = False
    def _get():
        return is_testing
    def _set():
        global is_testing
        is_testing = False
    
    def detect(qr_result):
        if _get():
            print(f"QR code detected. value={qr_result}")
            _set()
    
    print("Waiting for QR...")
    is_testing = True
    hardware_manager.safe_qr().regi_callback(detect)

    time.sleep(10)
        
    print("done")

def test_nfc():
    print("[Test NFC]")

    while True:
        print("Waiting for RFID/NFC card...")
        uid = hardware_manager.safe_nfc().read_nfc(timeout=10)
        if uid == False:
            print("NFC Module not initialized or not connected.")
            return
        if uid is not None:
            print(f"Tag successful. UID={uid}")
            break
        time.sleep(1)
    print("done")

def test_internal_sw():
    print("[Test Internal Switch LED]")
    print("Testing INTERNAL_SW_LED...")
    hardware_manager.internal_button.led_on()
    time.sleep(1)
    hardware_manager.internal_button.led_off()
    time.sleep(1)
    print("done")

def test_external_sw():
    print("[Test External Switch LED]")
    print("Testing EXTERNAL_SW_LED...")
    hardware_manager.external_button.led_on()
    time.sleep(1)
    hardware_manager.external_button.led_off()
    time.sleep(1)
    print("done")

def test_speaker():
    print("[Test Speaker]")
    print("Testing SPEAKER...")
    hardware_manager.speaker.play(setting.TEST_MUSIC)
    print("Sound sended.")
    print("done")

def test_all():
    test_led()
    test_relay()
    test_nfc()
    test_qr()
    test_internal_sw()
    test_external_sw()
    test_speaker()

test_options = [test_led, test_relay, test_qr, test_nfc, test_internal_sw, test_external_sw, test_speaker, test_all]

time.sleep(1)
while True:
    for i, option in enumerate(test_options, 1):
        print(f"[{i}] {option.__name__}")
    print("[exit] exit")
    choice = input("> ")

    if choice.isdigit() and 1 <= int(choice) <= len(test_options):
        test_options[int(choice) - 1]()
    elif choice == "exit":
        break

    print("-----------------------------")
