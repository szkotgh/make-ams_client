import managers.hardware_manager as hardware_manager

class ExternalButton():
    def __init__(self):
        self.BTN_PIN = hardware_manager.setting.EXTERNAL_SW_BTN
        self.LED_PIN = hardware_manager.setting.EXTERNAL_SW_LED
        self.GPIO = hardware_manager.GPIO

        self.GPIO.setup(self.BTN_PIN, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.LED_PIN, self.GPIO.OUT)

    def led_on(self):
        self.GPIO.output(self.LED_PIN, self.GPIO.HIGH)

    def led_off(self):
        self.GPIO.output(self.LED_PIN, self.GPIO.LOW)

    def read_button(self):
        return self.GPIO.input(self.BTN_PIN) == self.GPIO.LOW

    def regi_callback(self, callback):
        self.GPIO.add_event_detect(
            self.BTN_PIN,
            self.GPIO.FALLING,
            callback=callback,
            bouncetime=100
        )
