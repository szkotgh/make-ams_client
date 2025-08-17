import time
import hardware_manager
import setting

def test_led():
    print("[Test LED]")
    print("Testing STATUS_LED_RED...")
    hardware_manager.status_led.on('red')
    time.sleep(1)
    hardware_manager.status_led.off('red')
    time.sleep(1)
    print("done")

    print("Testing STATUS_LED_YELLOW...")
    hardware_manager.status_led.on('yellow')
    time.sleep(1)
    hardware_manager.status_led.off('yellow')
    time.sleep(1)
    print("done")
    
    print("Testing STATUS_LED_GREEN...")
    hardware_manager.status_led.on('green')
    time.sleep(1)
    hardware_manager.status_led.off('green')
    time.sleep(1)
    print("done")

def test_relay():
    print("[Test Relay]")
    print("Testing DOOR_RELAY...")
    hardware_manager.door.open_door()
    time.sleep(3)
    hardware_manager.door.close_door()
    time.sleep(3)
    print("done")

def test_nfc():
    print("[Test NFC]")

    while True:
        print("Waiting for RFID/NFC card...")
        uid = hardware_manager.nfc.read_nfc()
        if uid == False:
            print("NFC Module not initialized or not connected.")
            break
        if uid is not None:
            print("Found card with UID:", [hex(i) for i in uid])
            break
        time.sleep(1)
    print("done")

def test_internal_sw():
    print("[Test Internal Switch]")
    print("Testing INTERNAL_SW_LED...")
    hardware_manager.internal_button.led_on()
    time.sleep(1)
    hardware_manager.internal_button.led_off()
    time.sleep(1)
    print("done")

    print("Waiting for INTERNAL_SW_BTN...")
    while not hardware_manager.internal_button.read_button():
        time.sleep(0.1)
    print("done")

def test_external_sw():
    print("[Test External Switch]")
    print("Testing EXTERNAL_SW_LED...")
    hardware_manager.external_button.led_on()
    time.sleep(1)
    hardware_manager.external_button.led_off()
    time.sleep(1)
    print("done")

    print("Waiting for EXTERNAL_SW_BTN...")
    while not hardware_manager.external_button.read_button():
        time.sleep(0.1)
    print("done")

def test_speaker():
    print("[Test Speaker]")
    print("Testing SPEAKER...")
    hardware_manager.speaker_manager.play(setting.TEST_MUSIC)
    print("Sound sended.")
    print("done")

def test_all():
    test_led()
    test_relay()
    test_nfc()
    test_internal_sw()
    test_external_sw()
    test_speaker()

test_options = [test_led, test_relay, test_nfc, test_internal_sw, test_external_sw, test_speaker, test_all]

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
