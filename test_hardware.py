import time
import managers.hardware_manager as hardware_manager
import setting

# regi button callback
def on_internal_button_pressed():
    print(f"[Test Internal Button] Pressed")

def on_external_button_pressed():
    print(f"[Test External Button] Pressed")

def on_nfc_read(uid):
    print(f"[Test NFC] Read: {uid}")

def on_qr_read(qr_result):
    print(f"[Test QR] Read: {qr_result}")


hardware_manager.internal_button.register_callback(on_internal_button_pressed)
hardware_manager.external_button.register_callback(on_external_button_pressed)
hardware_manager.nfc.register_callback(on_nfc_read)
hardware_manager.qr.register_callback(on_qr_read)


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

def test_door():
    print("[Test Door]")
    print("Testing DOOR_RELAY...")
    hardware_manager.door.open_door()
    time.sleep(3)
    hardware_manager.door.close_door()
    time.sleep(3)
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
    test_door()
    test_internal_sw()
    test_external_sw()
    test_speaker()

test_options = [test_led, test_door, test_internal_sw, test_external_sw, test_speaker, test_all]

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
