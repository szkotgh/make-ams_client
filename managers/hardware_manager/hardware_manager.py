import managers.hardware_manager as hardware_manager


class DoorRelay:
    def __init__(self):
        self.RELAY_PIN = setting.DOOR_RELAY
        self._door_close_cancel_flag = False
        self._door_timer = None

        GPIO.setup(self.RELAY_PIN, GPIO.OUT)
        self.set_door(False)

    def set_door(self, state: bool):
        GPIO.output(self.RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)

    def open_door(self):
        # Use safe speaker manager access
        try:
            safe_speaker_manager().play(setting.DOOR_OPEN_SOUND_PATH)
        except Exception as e:
            print(f"Error playing door open sound: {e}")
        self.set_door(True)

    def close_door(self, close_duration=3):
        self._door_close_cancel_flag = False
        # Use safe speaker manager access
        try:
            safe_speaker_manager().play(setting.DOOR_CLOSE_SOUND_PATH)
        except Exception as e:
            print(f"Error playing door close sound: {e}")

        def _close():
            if not self._door_close_cancel_flag:
                self.set_door(False)

        # 기존 타이머가 있으면 취소
        if hasattr(self, '_close_timer') and self._close_timer:
            self._close_timer.cancel()
        
        self._close_timer = threading.Timer(close_duration, _close)
        self._close_timer.start()

    def auto_open_door(self, wait_duration=3):
        if self._door_timer is not None:
            self._door_timer.cancel()
        self._door_close_cancel_flag = True
        self.open_door()
        self._door_timer = threading.Timer(wait_duration, lambda: self.close_door())
        self._door_timer.start()

_speaker_manager = None
_status_led = None
_external_button = None
_internal_button = None
_door = None
_nfc = None
_qr = None

def get_speaker_manager():
    global _speaker_manager
    if _speaker_manager is None:
        _speaker_manager = SpeakerManager()
    return _speaker_manager

def get_status_led():
    global _status_led
    if _status_led is None:
        _status_led = StatusLED()
    return _status_led

def get_external_button():
    global _external_button
    if _external_button is None:
        _external_button = ExternalButtonSwitch()
    return _external_button

def get_internal_button():
    global _internal_button
    if _internal_button is None:
        _internal_button = InternalButtonSwitch()
    return _internal_button

def get_door():
    global _door
    if _door is None:
        _door = DoorRelay()
    return _door

def get_nfc():
    global _nfc
    if _nfc is None:
        _nfc = NFCReader()
    return _nfc

def get_qr():
    global _qr
    if _qr is None:
        _qr = QRListener()
    return _qr

def safe_speaker_manager():
    try:
        if not _hardware_initialized:
            print("Hardware not yet initialized, using dummy speaker manager")
            class DummySpeakerManager:
                def play(self, *args, **kwargs):
                    print("Speaker manager not available (hardware not initialized)")
                def stop(self, *args, **kwargs):
                    pass
                def set_volume(self, *args, **kwargs):
                    pass
            return DummySpeakerManager()
        
        if speaker_manager is None:
            return get_speaker_manager()
        return speaker_manager
    except Exception as e:
        print(f"Error accessing speaker manager: {e}")
        class DummySpeakerManager:
            def play(self, *args, **kwargs):
                print("Speaker manager not available")
            def stop(self, *args, **kwargs):
                pass
            def set_volume(self, *args, **kwargs):
                pass
        return DummySpeakerManager()

def safe_status_led():
    if status_led is None:
        return get_status_led()
    return status_led

def safe_external_button():
    if external_button is None:
        return get_external_button()
    return external_button

def safe_internal_button():
    if internal_button is None:
        return get_internal_button()
    return internal_button

def safe_door():
    try:
        if door is None:
            return get_door()
        return door
    except Exception as e:
        print(f"Error accessing door relay: {e}")
        class DummyDoorRelay:
            def open_door(self, *args, **kwargs):
                print("Door relay not available")
            def close_door(self, *args, **kwargs):
                print("Door relay not available")
            def auto_open_door(self, *args, **kwargs):
                print("Door relay not available")
            def set_door(self, *args, **kwargs):
                pass
        return DummyDoorRelay()

def safe_nfc():
    if nfc is None:
        return get_nfc()
    return nfc

def safe_qr():
    if qr is None:
        return get_qr()
    return qr

def _init_hardware_components():
    global speaker_manager, status_led, external_button, internal_button, door, nfc, qr
    
    # Start hardware initialization after 3 seconds
    import threading
    import time
    
    def delayed_init():
        global speaker_manager, status_led, external_button, internal_button, door, nfc, qr
        
        time.sleep(1)
        print("Starting hardware components initialization...")
        try:
            # Initialize in dependency order
            speaker_manager = get_speaker_manager()
            status_led = get_status_led()
            external_button = get_external_button()
            internal_button = get_internal_button()
            door = get_door()
            nfc = get_nfc()
            qr = get_qr()
            
            if qr is not None:
                print(f"QR listener initialized: {qr}")
                if hasattr(qr, 'initialized'):
                    print(f"QR listener ready status: {qr.initialized}")
            else:
                print("QR listener initialization failed")
                
            global _hardware_initialized
            _hardware_initialized = True
            print("Hardware components initialization completed successfully")
            
            _re_register_all_callbacks()
        except Exception as e:
            print(f"Error during hardware initialization: {e}")
            pass
    
    init_thread = threading.Thread(target=delayed_init, daemon=True, name="HardwareInit")
    init_thread.start()

_init_hardware_components()

speaker_manager = None
status_led = None
external_button = None
internal_button = None
door = None
nfc = None
qr = None

_hardware_initialized = False

_callback_registry = {
    'qr': [],
    'nfc': [],
    'external_button': [],
    'internal_button': []
}

def register_callback(component_type, callback):
    if component_type in _callback_registry:
        _callback_registry[component_type].append(callback)
        
        if _hardware_initialized:
            _register_callback_immediately(component_type, callback)

def _register_callback_immediately(component_type, callback):
    try:
        global qr, nfc, external_button, internal_button
        
        if component_type == 'qr' and qr is not None:
            if hasattr(qr, 'regi_callback'):
                qr.regi_callback(callback)
        elif component_type == 'nfc' and nfc is not None:
            pass
        elif component_type == 'external_button' and external_button is not None:
            external_button.regi_callback(callback)
            print(f"External button callback registered immediately: {callback}")
        elif component_type == 'internal_button' and internal_button is not None:
            internal_button.regi_callback(callback)
            print(f"Internal button callback registered immediately: {callback}")
    except Exception as e:
        print(f"Error registering callback immediately: {e}")

def _re_register_all_callbacks():
    for component_type, callbacks in _callback_registry.items():
        for callback in callbacks:
            _register_callback_immediately(component_type, callback)

def debug_callback_status():
    global qr, nfc, external_button, internal_button
    
    print(f"=== Hardware Status ===")
    print(f"Hardware initialized: {_hardware_initialized}")
    print(f"QR: {qr is not None}")
    print(f"NFC: {nfc is not None}")
    print(f"External Button: {external_button is not None}")
    print(f"Internal Button: {internal_button is not None}")
    print(f"=====================")



def close():
    try:
        if 'nfc' in globals() and nfc is not None:
            nfc.cleanup()
        if 'qr' in globals() and qr is not None:
            qr.cleanup()
        if 'status_led' in globals() and status_led is not None:
            status_led.cleanup()
        
        # Clean up GPIO
        GPIO.cleanup()
        print("Hardware manager cleanup completed successfully")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        # Clean up GPIO even on error
        try:
            GPIO.cleanup()
        except:
            pass