import RPi.GPIO as GPIO
import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

NFC_SDA = 2
NFC_SCL = 3

STATUS_LED_RED = 16
STATUS_LED_YELLOW = 20
STATUS_LED_GREEN = 21

INTERNAL_SW_BTN = 19
INTERNAL_SW_LED = 26

EXTERNAL_SW_BTN = 23
EXTERNAL_SW_LED = 24

DOOR_RELAY = 17

GPIO.setmode(GPIO.BCM)

GPIO.setup(STATUS_LED_RED, GPIO.OUT)
GPIO.setup(STATUS_LED_YELLOW, GPIO.OUT)
GPIO.setup(STATUS_LED_GREEN, GPIO.OUT)

GPIO.setup(INTERNAL_SW_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INTERNAL_SW_LED, GPIO.OUT)


GPIO.setup(EXTERNAL_SW_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(EXTERNAL_SW_LED, GPIO.OUT)

GPIO.setup(DOOR_RELAY, GPIO.OUT)

def test_led():
    print("[Test LED]")
    print("Testing STATUS_LED_RED...")
    GPIO.output(STATUS_LED_RED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(STATUS_LED_RED, GPIO.LOW)
    time.sleep(1)
    print("done")

    print("Testing STATUS_LED_YELLOW...")
    GPIO.output(STATUS_LED_YELLOW, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(STATUS_LED_YELLOW, GPIO.LOW)
    time.sleep(1)
    print("done")
    
    print("Testing STATUS_LED_GREEN...")
    GPIO.output(STATUS_LED_GREEN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(STATUS_LED_GREEN, GPIO.LOW)
    time.sleep(1)
    print("done")

def test_relay():
    print("[Test Relay]")
    print("Testing DOOR_RELAY...")
    GPIO.output(DOOR_RELAY, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(DOOR_RELAY, GPIO.LOW)
    time.sleep(1)
    print("done")

def test_nfc():
    print("[Test NFC]")
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pn532 = PN532_I2C(i2c, debug=False)
        pn532.SAM_configuration()
    except Exception as e:
        print(f"NFC Initialization Error: {e}")
        return

    while True:
        print("Waiting for RFID/NFC card...")
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            print("Found card with UID:", [hex(i) for i in uid])
        time.sleep(1)
    print("done")

def test_internal_sw():
    print("[Test Internal Switch]")
    print("Testing INTERNAL_SW_LED...")
    GPIO.output(INTERNAL_SW_LED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(INTERNAL_SW_LED, GPIO.LOW)
    time.sleep(1)
    print("done")

    print("Waiting for INTERNAL_SW_BTN...")
    while GPIO.input(INTERNAL_SW_BTN) == GPIO.HIGH:
        time.sleep(0.1)
    print("done")

def test_external_sw():
    print("[Test External Switch]")
    print("Testing EXTERNAL_SW_LED...")
    GPIO.output(EXTERNAL_SW_LED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(EXTERNAL_SW_LED, GPIO.LOW)
    time.sleep(1)
    print("done")

    print("Waiting for EXTERNAL_SW_BTN...")
    while GPIO.input(EXTERNAL_SW_BTN) == GPIO.HIGH:
        time.sleep(0.1)
    print("done")

while True:
    print("1. test led")
    print("2. test relay")
    print("3. test nfc")
    print("4. test internal switch")
    print("5. test external switch")
    print("6. test all")
    print("7. exit")
    choice = input("> ")

    if choice == "1":
        test_led()
    elif choice == "2":
        test_relay()
    elif choice == "3":
        test_nfc()
    elif choice == "4":
        test_internal_sw()
    elif choice == "5":
        test_external_sw()
    elif choice == "6":
        test_led()
        test_relay()
        test_nfc()
        test_internal_sw()
        test_external_sw()
    elif choice == "7":
        break

    print("-----------------------------")