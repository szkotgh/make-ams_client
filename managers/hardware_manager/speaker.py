import os
import threading
import time
from pygame import mixer

class Speaker:
    def __init__(self):
        self.is_initialized = False
        os.environ['SDL_AUDIODRIVER'] = 'alsa'

        max_retry = 5
        for attempt in range(max_retry):
            try:
                mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512
                )
                self.is_initialized = True
                print(f"[Speaker] Initialized successfully")
                break
            except Exception as e:
                print(f"[Speaker] Failed to initialize mixer: {e}, retrying... ({attempt + 1}/{max_retry})")
                if attempt < max_retry - 1:
                    time.sleep(5)
                else:
                    self.is_initialized = False
                    print(f"[Speaker] Failed to initialize mixer: {e}, giving up")
        self._lock = threading.Lock()
        self._volume = 1.0
        self._play_thread = None
        self._current_file = None

    def set_volume(self, volume):
        with self._lock:
            self._volume = max(0.0, min(1.0, volume))
            try:
                mixer.music.set_volume(self._volume)
            except Exception as e:
                logging.warning(f"[Speaker] Error setting volume: {e}")

    def get_volume(self):
        return self._volume

    def play(self, file_path):
        print(f"[Speaker] Playing sound: {file_path}")
        if not self.is_initialized:
            logging.warning(f"[Speaker] Speaker is not initialized")
            return

        if not os.path.exists(file_path):
            logging.warning(f"[Speaker] Audio file not found: {file_path}")
            return

        def _play():
            with self._lock:
                try:
                    if mixer.music.get_busy():
                        mixer.music.stop()
                        while mixer.music.get_busy():
                            time.sleep(0.01)

                    mixer.music.load(file_path)
                    mixer.music.set_volume(self._volume)
                    mixer.music.play()
                    self._current_file = file_path
                except Exception as e:
                    logging.warning(f"[Speaker] Error playing sound: {e}")

        if self._play_thread is None or not self._play_thread.is_alive():
            self._play_thread = threading.Thread(target=_play, daemon=True)
            self._play_thread.start()
        else:
            self._play_thread = threading.Thread(target=_play, daemon=True)
            self._play_thread.start()

    def stop(self):
        with self._lock:
            try:
                mixer.music.stop()
                while mixer.music.get_busy():
                    time.sleep(0.01)
            except Exception as e:
                logging.warning(f"[Speaker] Error stopping sound: {e}")

