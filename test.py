import hardware_manager
import time

service = hardware_manager.StatusLED()


print("1")
service.blink("red")
time.sleep(3)

print("2")
service.blink("green")
time.sleep(1)

service.cleanup()

service.